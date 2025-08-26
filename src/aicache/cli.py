import argparse
import json
import sys
import os
from pathlib import Path
import shutil # Added for create-generic-wrapper
import re # Added for create-generic-wrapper

from .core import Cache
from .plugins import REGISTERED_PLUGINS

def main():
    invoked_as = os.path.basename(sys.argv[0])

    if invoked_as in REGISTERED_PLUGINS:
        # This is a wrapped CLI call (e.g., gcloud, llm, openai)
        wrapper = REGISTERED_PLUGINS[invoked_as]()
        args = sys.argv[1:] # Arguments passed to the wrapped CLI

        prompt_content, context = wrapper.parse_arguments(args)

        if not prompt_content:
            # If no prompt content found, just execute the command without caching
            stdout, return_code, stderr = wrapper.execute_cli(args)
            if stdout:
                print(stdout)
            if stderr:
                print(stderr, file=sys.stderr)
            sys.exit(return_code)

        cache = Cache()
        cached_response = cache.get(prompt_content, context)

        if cached_response:
            print("--- (aicache HIT) ---", file=sys.stderr)
            print(cached_response["response"])
            sys.exit(0)
        else:
            print("--- (aicache MISS) ---", file=sys.stderr)
            stdout, return_code, stderr = wrapper.execute_cli(args)
            if return_code == 0:
                cache.set(prompt_content, stdout, context)
                print(stdout)
            if stderr:
                print(stderr, file=sys.stderr)
            sys.exit(return_code)

    else:
        # This is the aicache CLI being called directly
        parser = argparse.ArgumentParser(description="AI Cache CLI")
        subparsers = parser.add_subparsers(dest="command")

        # Get command
        get_parser = subparsers.add_parser("get")
        get_parser.add_argument("prompt")
        get_parser.add_argument("--context", default=None)

        # Set command
        set_parser = subparsers.add_parser("set")
        set_parser.add_argument("prompt")
        set_parser.add_argument("response")
        set_parser.add_argument("--context", default=None)

        # List command
        list_parser = subparsers.add_parser("list")
        list_parser.add_argument("-v", "--verbose", action="store_true")

        # Clear command
        clear_parser = subparsers.add_parser("clear")
        clear_parser.add_argument("-i", "--interactive", action="store_true")

        # Inspect command
        inspect_parser = subparsers.add_parser("inspect")
        inspect_parser.add_argument("cache_key")

        # Generate completions command
        completions_parser = subparsers.add_parser("generate-completions")

        # Prune command
        prune_parser = subparsers.add_parser("prune")

        # Stats command
        stats_parser = subparsers.add_parser("stats")

        # Create Generic Wrapper command
        create_generic_wrapper_parser = subparsers.add_parser("create-generic-wrapper")
        create_generic_wrapper_parser.add_argument("cli_name")
        create_generic_wrapper_parser.add_argument("--path", required=True)
        create_generic_wrapper_parser.add_argument("--prompt-regex", required=True)
        create_generic_wrapper_parser.add_argument("--model-arg", default=None)

        args = parser.parse_args()
        cache = Cache()

        if args.command == "get":
            result = cache.get(args.prompt, args.context)
            if result:
                print(json.dumps(result, indent=4))
            else:
                print("No cache entry found.")
        elif args.command == "set":
            cache.set(args.prompt, args.response, args.context)
            print("Cache entry set.")
        elif args.command == "list":
            entries = cache.list(verbose=args.verbose)
            if args.verbose:
                for entry in entries:
                    print(json.dumps(entry, indent=4))
            else:
                for entry in entries:
                    print(entry)
        elif args.command == "clear":
            if args.interactive:
                entries = cache.list(verbose=True)
                if not entries:
                    print("Cache is empty.")
                    return

                print("Select cache entries to delete (e.g., 1,3-5):")
                for i, entry in enumerate(entries):
                    print(f"{i+1}: {entry['cache_key']} - {entry['prompt']}")

                try:
                    selection = input("Enter numbers: ")
                    selected_indices = set()
                    for part in selection.split(','):
                        if '-' in part:
                            start, end = map(int, part.split('-'))
                            selected_indices.update(range(start - 1, end))
                        else:
                            selected_indices.add(int(part) - 1)

                    for i in sorted(list(selected_indices), reverse=True):
                        cache.delete(entries[i]['cache_key'])
                    print("Selected cache entries deleted.")

                except (ValueError, IndexError):
                    print("Invalid selection.")
            else:
                cache.clear()
                print("Cache cleared.")
        elif args.command == "inspect":
            result = cache.inspect(args.cache_key)
            if result:
                print(json.dumps(result, indent=4))
            else:
                print("No cache entry found for this key.")
        elif args.command == "generate-completions":
            completion_script = """
_aicache_completions()
{
    local cur_word prev_word
    cur_word=\"${COMP_WORDS[COMP_CWORD]}\"
    prev_word=\"${COMP_WORDS[COMP_CWORD-1]}\"

    case "${prev_word}" in
        aicache)
            COMPREPLY=( $(compgen -W "get set list clear inspect generate-completions prune stats create-generic-wrapper" -- ${cur_word}) )
            ;;
        list)
            COMPREPLY=( $(compgen -W "--verbose -v" -- ${cur_word}) )
            ;;
        clear)
            COMPREPLY=( $(compgen -W "--interactive -i" -- ${cur_word}) )
            ;;
        *)
            COMPREPLY=()
            ;;
    esac
}

complete -F _aicache_completions aicache
"""
            print(completion_script)
        elif args.command == "prune":
            pruned_count = cache.prune()
            print(f"Pruned {pruned_count} expired cache entries.")
        elif args.command == "stats":
            stats = cache.stats()
            print("Cache Statistics:")
            print(f"  Total entries: {stats['num_entries']}")
            print(f"  Total size: {stats['total_size']} bytes")
            if stats['num_expired'] > 0:
                print(f"  Expired entries: {stats['num_expired']}")
        elif args.command == "create-generic-wrapper":
            # Generate the content of the generic wrapper script
            wrapper_content = f"""#!/usr/bin/env python3

import shutil
import re
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from aicache.core import Cache
from aicache.plugins.base import CLIWrapper as BaseCLIWrapper # Import BaseCLIWrapper

class CustomCLIWrapper:
    def __init__(self):
        self.cli_name = "{args.cli_name}"
        self.real_cli_path = "{args.path}"
        self.prompt_regex = r"{args.prompt_regex}"
        self.model_arg = "{args.model_arg}" if "{args.model_arg}" != "None" else None

    def get_cli_name(self) -> str:
        return self.cli_name

    def parse_arguments(self, args: list) -> tuple[str, dict]:
        prompt_content = ""
        model = None

        # Extract prompt using regex
        args_str = " ".join(args)
        match = re.search(self.prompt_regex, args_str)
        if match:
            prompt_content = match.group(1)

        # Extract model if model_arg is provided
        if self.model_arg:
            i = 0
            while i < len(args):
                if args[i] == self.model_arg:
                    if i + 1 < len(args):
                        model = args[i+1]
                        break
                    else:
                        i += 1
                else:
                    i += 1

        context = {{'model': model}}
        return prompt_content, context

    def execute_cli(self, args: list) -> tuple[str, int, str]:
        if not shutil.which(self.real_cli_path):
            return "", 1, f"Error: {{self.real_cli_path}} executable not found."

        # Use the _run_cli_command from the BaseCLIWrapper
        base_wrapper_instance = BaseCLIWrapper()
        return base_wrapper_instance._run_cli_command(self.real_cli_path, args)

# Main execution logic for the generated wrapper
def generated_wrapper_main(): # Renamed to avoid conflict with main()
    wrapper = CustomCLIWrapper()
    args = sys.argv[1:]

    prompt_content, context = wrapper.parse_arguments(args)

    cache = Cache()
    cached_response = cache.get(prompt_content, context)

    if cached_response:
        print("--- (aicache HIT) ---", file=sys.stderr)
        print(cached_response["response"])
        sys.exit(0)
    else:
        print("--- (aicache MISS) ---", file=sys.stderr)
        stdout, return_code, stderr = wrapper.execute_cli(args)
        if return_code == 0:
            cache.set(prompt_content, stdout, context)
            print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)
        sys.exit(return_code)

if __name__ == "__main__":
    generated_wrapper_main() # Call the renamed main function
"""
            # Write the wrapper content to a file
            output_dir = Path.cwd() / "custom_wrappers"
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / f"{args.cli_name}_wrapper.py"
            with open(output_file, "w") as f:
                f.write(wrapper_content)
            
            # Make it executable
            os.chmod(output_file, 0o755)

            print(f"Generic wrapper for '{args.cli_name}' created at: {output_file}")
            print(f"To use it, add '{output_dir}' to your PATH before the real CLI's path, or create a symlink:")
            print(f"ln -s {output_file} ~/.local/bin/{args.cli_name}")
        else:
            parser.print_help()

if __name__ == "__main__":
    main()
