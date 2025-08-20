#!/usr/bin/env python3

import sys
import subprocess
import os
import shutil
import json
import re

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from aicache.core import Cache

def main():
    # 1. Find the real openai executable
    real_openai_path = shutil.which("openai")
    if not real_openai_path:
        print("Error: openai executable not found.", file=sys.stderr)
        sys.exit(1)

    # 2. Parse arguments
    args = sys.argv[1:]
    model = None
    prompt_content = None

    # Look for --model and --messages arguments
    i = 0
    while i < len(args):
        if args[i] == "--model":
            if i + 1 < len(args):
                model = args[i+1]
                i += 2
            else:
                i += 1 # Let openai handle the error
        elif args[i] == "--messages":
            if i + 1 < len(args):
                messages_str = args[i+1]
                # Extract content from "role=user,content='...'"
                match = re.search(r"content='([^']+)'", messages_str)
                if match:
                    prompt_content = match.group(1)
                i += 2
            else:
                i += 1 # Let openai handle the error
        else:
            i += 1

    if not prompt_content:
        # If no prompt content found, just execute the command without caching
        subprocess.run([real_openai_path] + args)
        sys.exit(0)

    # 3. Create cache key
    cache = Cache()
    context = {"model": model}
    
    # 4. Check cache
    cached_response = cache.get(prompt_content, context)
    if cached_response:
        print("--- (aicache HIT) ---", file=sys.stderr)
        print(cached_response["response"])
        sys.exit(0)

    # 5. Cache miss
    print("--- (aicache MISS) ---", file=sys.stderr)
    
    # Execute real command
    process = subprocess.run([real_openai_path] + args, capture_output=True, text=True)

    if process.returncode == 0:
        response = process.stdout
        cache.set(prompt_content, response, context)
        print(response)
    else:
        print(process.stderr, file=sys.stderr)
        sys.exit(process.returncode)


if __name__ == "__main__":
    main()
