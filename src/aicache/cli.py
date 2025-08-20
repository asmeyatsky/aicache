import argparse
import json
from .core import Cache

def main():
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
    cur_word="${COMP_WORDS[COMP_CWORD]}"
    prev_word="${COMP_WORDS[COMP_CWORD-1]}"

    case "${prev_word}" in
        aicache)
            COMPREPLY=( $(compgen -W "get set list clear inspect generate-completions prune" -- ${cur_word}) )
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
    else:
        parser.print_help()

if __name__ == "__main__":
    main()