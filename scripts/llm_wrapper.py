#!/usr/bin/env python3

import sys
import subprocess
import os
import shutil
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from aicache.core import Cache

def main():
    # 1. Find the real llm executable
    real_llm_path = shutil.which("llm")
    if not real_llm_path:
        print("Error: llm executable not found.", file=sys.stderr)
        sys.exit(1)

    # 2. Parse arguments
    args = sys.argv[1:]
    prompt_args = []
    model = None
    i = 0
    while i < len(args):
        if args[i] in ("-m", "--model"):
            if i + 1 < len(args):
                model = args[i+1]
                i += 2
            else:
                # Let llm handle the error
                prompt_args.append(args[i])
                i += 1
        else:
            prompt_args.append(args[i])
            i += 1

    # Handle stdin
    prompt_content = ""
    if not sys.stdin.isatty():
        prompt_content = sys.stdin.read()
    else:
        prompt_content = " ".join(prompt_args)


    # 3. Create cache key
    cache = Cache()
    # We need to provide the context to get() and set() as a dictionary
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
    if not sys.stdin.isatty():
        process = subprocess.run([real_llm_path] + args, input=prompt_content, capture_output=True, text=True)
    else:
        process = subprocess.run([real_llm_path] + args, capture_output=True, text=True)

    if process.returncode == 0:
        response = process.stdout
        cache.set(prompt_content, response, context)
        print(response)
    else:
        print(process.stderr, file=sys.stderr)
        sys.exit(process.returncode)


if __name__ == "__main__":
    main()
