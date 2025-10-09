import argparse
import json
import sys
import os
from pathlib import Path
import shutil # Added for create-generic-wrapper
import re # Added for create-generic-wrapper
import time
import asyncio

from .core import Cache
from .plugins import REGISTERED_PLUGINS
from .living_brain import BrainStateManager

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

        # Use basic cache for wrapped CLIs to avoid async issues
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

        # Cache image command
        cache_image_parser = subparsers.add_parser("cache-image")
        cache_image_parser.add_argument("key")
        cache_image_parser.add_argument("path")

        # Get image command
        get_image_parser = subparsers.add_parser("get-image")
        get_image_parser.add_argument("key")

        # Cache notebook command
        cache_notebook_parser = subparsers.add_parser("cache-notebook")
        cache_notebook_parser.add_argument("key")
        cache_notebook_parser.add_argument("path")

        # Get notebook command
        get_notebook_parser = subparsers.add_parser("get-notebook")
        get_notebook_parser.add_argument("key")

        # Cache audio command
        cache_audio_parser = subparsers.add_parser("cache-audio")
        cache_audio_parser.add_argument("key")
        cache_audio_parser.add_argument("path")

        # Get audio command
        get_audio_parser = subparsers.add_parser("get-audio")
        get_audio_parser.add_argument("key")

        # Cache video command
        cache_video_parser = subparsers.add_parser("cache-video")
        cache_video_parser.add_argument("key")
        cache_video_parser.add_argument("path")

        # Get video command
        get_video_parser = subparsers.add_parser("get-video")
        get_video_parser.add_argument("key")

        # Install command
        install_parser = subparsers.add_parser("install")
        install_parser.add_argument("--setup-wrappers", action="store_true", help="Install CLI wrappers")
        install_parser.add_argument("--force", action="store_true", help="Force overwrite existing wrappers")
        install_parser.add_argument("--list", action="store_true", help="List available CLI tools")
        install_parser.add_argument("--config", action="store_true", help="Create default config file")
        install_parser.add_argument("tool", nargs="?", help="Specific tool to install wrapper for")

        # Uninstall command  
        uninstall_parser = subparsers.add_parser("uninstall")
        uninstall_parser.add_argument("tool", help="Tool to remove wrapper for")

        # Analytics command
        analytics_parser = subparsers.add_parser("analytics")
        analytics_parser.add_argument("--behavioral", action="store_true", help="Show behavioral analytics")
        analytics_parser.add_argument("--prefetch", action="store_true", help="Show prefetch statistics")
        analytics_parser.add_argument("--patterns", action="store_true", help="Show learned patterns")
        analytics_parser.add_argument("--export", help="Export analytics to file")

        # Predict command
        predict_parser = subparsers.add_parser("predict")
        predict_parser.add_argument("query", help="Query to predict next steps for")
        predict_parser.add_argument("--context", help="Context for prediction")
        predict_parser.add_argument("--confidence", type=float, default=0.6, help="Minimum confidence threshold")

        # Prefetch command
        prefetch_parser = subparsers.add_parser("prefetch")
        prefetch_parser.add_argument("query", help="Query to prefetch")
        prefetch_parser.add_argument("--context", help="Context for prefetch")
        prefetch_parser.add_argument("--priority", type=int, choices=[1,2,3], default=2, help="Prefetch priority")

        args = parser.parse_args()
        
        cache = Cache()  # Use basic cache for general CLI commands to avoid initialization overhead

        # For advanced commands that require EnhancedCache features, initialize it
        advanced_commands = {"analytics", "predict", "prefetch"}
        if args.command in advanced_commands:
            try:
                from .enhanced_core import EnhancedCache
                cache = EnhancedCache()
                # Initialize the async components - handle possible running event loop
                try:
                    import asyncio
                    asyncio.run(cache.init_async())
                except RuntimeError:
                    # Event loop is already running, try to handle gracefully
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(lambda: asyncio.run(cache.init_async()))
                        future.result()
            except ImportError:
                cache = Cache()
                print("Warning: Enhanced features not available. Using basic cache.")
        
        if args.command == "get":
            import json
            # Parse context if it's a JSON string
            context = args.context
            if context and isinstance(context, str):
                try:
                    context = json.loads(context)
                except json.JSONDecodeError:
                    print(f"Warning: Invalid JSON context, using as string: {context}")
            
            result = cache.get(args.prompt, context)
            if result:
                print(json.dumps(result, indent=4))
            else:
                print("No cache entry found.")
        elif args.command == "set":
            # Parse context if it's a JSON string
            context = args.context
            if context and isinstance(context, str):
                try:
                    context = json.loads(context)
                except json.JSONDecodeError:
                    print(f"Warning: Invalid JSON context, using as string: {context}")
            
            cache.set(args.prompt, args.response, context)
            print("Cache entry set.")
        elif args.command == "list":
            import json
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
            import json
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
    prev_word=\"${COMP_WORDS[COMP_CWORD-1]}\" # Corrected: escaped '$'

    case "${prev_word}" in
        aicache)
            COMPREPLY=( $(compgen -W \"get set list clear inspect generate-completions prune stats create-generic-wrapper cache-image get-image cache-notebook get-notebook cache-audio get-audio cache-video get-video\" -- ${cur_word}) ) # Corrected: escaped '"'
            ;; 
        list)
            COMPREPLY=( $(compgen -W \"--verbose -v\" -- ${cur_word}) ) # Corrected: escaped '"'
            ;; 
        clear)
            COMPREPLY=( $(compgen -W \"--interactive -i\" -- ${cur_word}) ) # Corrected: escaped '"'
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
            print(f"Pruned {pruned_count} entries.")
        elif args.command == "stats":
            stats = cache.stats()
            print("Cache Statistics:")
            print(f"  Total entries: {stats['num_entries']}")
            print(f"  Total size: {stats['total_size']} bytes")
            if stats.get('num_expired', 0) > 0:
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
        self.cli_name = \"{args.cli_name}\" # Corrected: escaped '"'
        self.real_cli_path = \"{args.path}\" # Corrected: escaped '"'
        self.prompt_regex = r\"{args.prompt_regex}\" # Corrected: escaped '"'
        self.model_arg = \"{args.model_arg}\" if \"{args.model_arg}\" != \"None\" else None # Corrected: escaped '"'

    def get_cli_name() -> str:
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

    async def execute_cli(self, args: list) -> tuple[str, int, str]:
        if not shutil.which(self.real_cli_path):
            return "", 1, f"Error: {{self.real_cli_path}} executable not found."

        # Use the _run_cli_command from the BaseCLIWrapper
        base_wrapper_instance = BaseCLIWrapper()
        return await base_wrapper_instance._run_cli_command(self.real_cli_path, args)

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
        elif args.command == "cache-image":
            cache.set_image(args.key, args.path)
            print(f"Image cached with key: {args.key}")
        elif args.command == "get-image":
            image_path = cache.get_image(args.key)
            if image_path:
                print(f"Image path: {image_path}")
            else:
                print("No image found for this key.")
        elif args.command == "cache-notebook":
            cache.set_notebook(args.key, args.path)
            print(f"Notebook cached with key: {args.key}")
        elif args.command == "get-notebook":
            notebook_path = cache.get_notebook(args.key)
            if notebook_path:
                print(f"Notebook path: {notebook_path}")
            else:
                print("No notebook found for this key.")
        elif args.command == "cache-audio":
            cache.set_audio(args.key, args.path)
            print(f"Audio file cached with key: {args.key}")
        elif args.command == "get-audio":
            audio_path = cache.get_audio(args.key)
            if audio_path:
                print(f"Audio path: {audio_path}")
            else:
                print("No audio file found for this key.")
        elif args.command == "cache-video":
            cache.set_video(args.key, args.path)
            print(f"Video file cached with key: {args.key}")
        elif args.command == "get-video":
            video_path = cache.get_video(args.key)
            if video_path:
                print(f"Video path: {video_path}")
            else:
                print("No video file found for this key.")
        elif args.command == "install":
            from .installer import AICacheInstaller
            installer = AICacheInstaller()
            
            if args.list:
                # List available CLI tools
                wrappers = installer.list_wrappers()
                print("Available CLI Tools:")
                print("-" * 50)
                for wrapper in wrappers:
                    print(f"{wrapper['name']:12} | {wrapper['status']} | {wrapper['description']}")
                
                # Check PATH setup
                path_info = installer.check_path_setup()
                if not path_info['in_path']:
                    print(f"\n⚠️  {path_info['local_bin_path']} is not in your PATH")
                    print("Setup instructions:")
                    for instruction in path_info['setup_instructions']:
                        print(f"  {instruction}")
                        
            elif args.config:
                # Create config file
                config_path = installer.create_config_file()
                print(f"✅ Created config file at {config_path}")
                
            elif args.setup_wrappers:
                # Install all available wrappers
                results = installer.install_all_available(force=args.force)
                installed = [k for k, v in results.items() if v]
                skipped = [k for k, v in results.items() if not v]
                
                if installed:
                    print(f"✅ Installed wrappers: {', '.join(installed)}")
                if skipped:
                    print(f"⏭️  Skipped: {', '.join(skipped)}")
                    
                # Check PATH
                path_info = installer.check_path_setup()
                if not path_info['in_path']:
                    print(f"\n⚠️  Don't forget to add {path_info['local_bin_path']} to your PATH!")
                    
            elif args.tool:
                # Install specific tool wrapper
                success = installer.install_wrapper(args.tool, force=args.force)
                if success:
                    print(f"✅ Installed {args.tool} wrapper")
                else:
                    print(f"❌ Failed to install {args.tool} wrapper")
            else:
                install_parser.print_help()
                
        elif args.command == "uninstall":
            from .installer import AICacheInstaller
            installer = AICacheInstaller()
            
            success = installer.uninstall_wrapper(args.tool)
            if success:
                print(f"✅ Removed {args.tool} wrapper")
            else:
                print(f"❌ Failed to remove {args.tool} wrapper")
        elif args.command == "analytics":
            # Check if enhanced cache is available
            if not hasattr(cache, 'behavioral_analyzer') or not cache.behavioral_analyzer:
                print("❌ Behavioral analytics not available. Enhanced cache required.")
                return
            
            if args.behavioral or not any([args.prefetch, args.patterns]):
                # Show behavioral analytics
                analytics = cache.behavioral_analyzer.get_analytics()
                print("📊 Behavioral Analytics:")
                print("-" * 40)
                print(f"Total Queries:      {analytics['total_queries']}")
                print(f"Cache Hit Rate:     {analytics['cache_hit_rate']:.2%}")
                print(f"Unique Users:       {analytics['unique_users']}")
                print(f"Unique Sessions:    {analytics['unique_sessions']}")
                print(f"Queries/Session:    {analytics['queries_per_session']:.1f}")
                print(f"Active Patterns:    {analytics['active_patterns']}")
                print(f"Total Patterns:     {analytics['total_patterns']}")
                print(f"Context Triggers:   {analytics['contextual_triggers']}")
            
            if args.prefetch and cache.predictive_prefetcher:
                # Show prefetch statistics
                prefetch_stats = cache.predictive_prefetcher.get_prefetch_stats()
                print("\n🚀 Prefetch Statistics:")
                print("-" * 40)
                print(f"Total Prefetches:   {prefetch_stats['total_prefetches']}")
                print(f"Success Rate:       {prefetch_stats['success_rate']:.2%}")
                print(f"Avg Execution:      {prefetch_stats['avg_execution_time']:.2f}s")
                print(f"Total Cost:         ${prefetch_stats['total_estimated_cost']:.2f}")
                print(f"Current Hour Cost:  ${prefetch_stats['current_hour_cost']:.2f}")
                print(f"Active Prefetches:  {prefetch_stats['active_prefetches']}")
                print(f"Queue Size:         {prefetch_stats['queue_size']}")
                print(f"Status:             {'🟢 Running' if prefetch_stats['running'] else '🔴 Stopped'}")
                
                if prefetch_stats['trigger_stats']:
                    print("\nTrigger Performance:")
                    for reason, stats in prefetch_stats['trigger_stats'].items():
                        success_rate = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
                        print(f"  {reason}: {stats['successful']}/{stats['total']} ({success_rate:.1%})")
            
            if args.patterns:
                # Show learned patterns (top 10)
                print("\n🧠 Top Learned Patterns:")
                print("-" * 40)
                sorted_patterns = sorted(cache.behavioral_analyzer.patterns.items(), 
                                       key=lambda x: x[1].frequency, reverse=True)[:10]
                for i, (pattern_hash, pattern) in enumerate(sorted_patterns, 1):
                    sequence_preview = " → ".join(pattern.sequence[:3])
                    if len(pattern.sequence) > 3:
                        sequence_preview += "..."
                    print(f"{i:2}. {sequence_preview}")
                    print(f"    Frequency: {pattern.frequency}, Success: {pattern.success_rate:.1%}")
            
            if args.export:
                # Export analytics to file
                all_analytics = {
                    'behavioral': analytics,
                    'timestamp': time.time()
                }
                if cache.predictive_prefetcher:
                    all_analytics['prefetch'] = cache.predictive_prefetcher.get_prefetch_stats()
                
                import json
                with open(args.export, 'w') as f:
                    json.dump(all_analytics, f, indent=2)
                print(f"✅ Analytics exported to {args.export}")
                
        elif args.command == "predict":
            if not hasattr(cache, 'behavioral_analyzer') or not cache.behavioral_analyzer:
                print("❌ Prediction not available. Enhanced cache with behavioral learning required.")
                return
            
            # Parse context
            context = {}
            if args.context:
                try:
                    context = json.loads(args.context)
                except json.JSONDecodeError:
                    print(f"Warning: Invalid JSON context: {args.context}")
            
            # Get predictions
            recent_queries = [cache.behavioral_analyzer._get_query_hash(args.query, context)]
            predictions = cache.behavioral_analyzer.predict_next_queries(
                user_id=cache.current_user_id,
                session_id=cache.current_session_id or "predict-session",
                recent_queries=recent_queries,
                context=context
            )
            
            print(f"🔮 Predictions for: {args.query}")
            print("-" * 50)
            
            if predictions:
                for i, (query_hash, confidence) in enumerate(predictions, 1):
                    if confidence >= args.confidence:
                        print(f"{i}. Query Hash: {query_hash}")
                        print(f"   Confidence: {confidence:.2%}")
            else:
                print("No predictions found above confidence threshold.")
                
        elif args.command == "prefetch":
            if not hasattr(cache, 'predictive_prefetcher') or not cache.predictive_prefetcher:
                print("❌ Prefetch not available. Enhanced cache with behavioral learning required.")
                return
            
            # Parse context
            context = {}
            if args.context:
                try:
                    context = json.loads(args.context)
                except json.JSONDecodeError:
                    print(f"Warning: Invalid JSON context: {args.context}")
            
            # Schedule prefetch
            asyncio.run(cache.predictive_prefetcher.force_prefetch(
                query=args.query,
                context=context,
                priority=args.priority
            ))
            
            print(f"🚀 Prefetch scheduled for: {args.query}")
            print(f"   Priority: {args.priority}")
            print(f"   Context: {context}")
        elif args.command == "brain":
            brain_manager = BrainStateManager()
            try:
                import asyncio
                asyncio.run(brain_manager.init_db())
            except RuntimeError:
                # Event loop is already running, try to handle gracefully
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(lambda: asyncio.run(brain_manager.init_db()))
                    future.result()
            
            if args.brain_command == "init":
                # Initialize a new brain session
                session = asyncio.run(brain_manager.create_new_session(args.project_id, args.name))
                print(f"🧠 Brain session initialized: {session.session_id}") 
                print(f"   Project: {session.project_id}")
                
            elif args.brain_command == "switch":
                # Switch AI provider in current session
                success = asyncio.run(brain_manager.switch_ai_provider(args.provider))
                if success:
                    print(f"🔄 Switched to AI provider: {args.provider}")
                else:
                    print(f"❌ Failed to switch to {args.provider}")
                    
            elif args.brain_command == "context":
                # Show current brain context
                if brain_manager.current_context:
                    context = brain_manager.current_context
                    print(f"🧠 Current Brain Context:")
                    print(f"   Session ID: {context.session_id}")
                    print(f"   Project: {context.project_id}")
                    print(f"   Current Task: {context.current_task}")
                    print(f"   Active Provider: {context.active_ai_provider}")
                    print(f"   Working Directory: {context.current_working_directory}")
                    print(f"   Related Files: {len(context.relevant_files)} files")
                    print(f"   Conversation History: {len(context.conversation_history)} exchanges")
                else:
                    print("No active brain session. Initialize one first with 'aicache brain init'.")
                    
            elif args.brain_command == "concepts":
                if args.concepts_command == "add":
                    concept_id = asyncio.run(brain_manager.add_concept(
                        args.content, 
                        args.provider, 
                        args.tags, 
                        args.importance
                    ))
                    print(f"💡 Added concept to brain: {concept_id[:8]}...")
                    
                elif args.concepts_command == "search":
                    concepts = asyncio.run(brain_manager.get_relevant_concepts(
                        args.query, 
                        args.limit
                    ))
                    if concepts:
                        print(f"💡 Found {len(concepts)} relevant concepts:")
                        for i, concept in enumerate(concepts, 1):
                            print(f"  {i}. ({concept.importance_score:.2f}) {concept.content[:100]}...")
                            print(f"     Providers: {', '.join(concept.ai_providers)}")
                            print()
                    else:
                        print(f"No relevant concepts found for: {args.query}")
                        
            elif args.brain_command == "stats":
                if args.project_id:
                    stats = asyncio.run(brain_manager.get_project_stats(args.project_id))
                    print(f"📊 Stats for project {args.project_id}:")
                    print(f"   Total sessions: {stats['total_sessions']}")
                    print(f"   Total interactions: {stats['total_interactions']}")
                    print(f"   Total concepts: {stats['total_concepts']}")
                    print(f"   Avg concept importance: {stats['avg_concept_importance']:.2f}")
                    print(f"   AI providers used: {stats['unique_ai_providers']}")
                else:
                    active_sessions = asyncio.run(brain_manager.get_active_sessions())
                    print(f"📊 Active brain sessions: {len(active_sessions)}")
                    for session in active_sessions:
                        print(f"   - {session.session_id[:8]}... for {session.project_id}")
                        print(f"     Providers: {', '.join(session.ai_providers_used)}")
                        print(f"     Interactions: {session.total_interactions}")
            else:
                print("Invalid brain command. Use 'aicache brain --help' for options.")
        else:
            parser.print_help()

if __name__ == "__main__":
    main()