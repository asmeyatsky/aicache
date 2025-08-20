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
    # 1. Find the real gcloud executable
    real_gcloud_path = shutil.which("gcloud")
    if not real_gcloud_path:
        print("Error: gcloud executable not found.", file=sys.stderr)
        sys.exit(1)

    # 2. Parse arguments to find the JSON request file
    args = sys.argv[1:]
    json_request_file = None
    for arg in args:
        if arg.startswith("--json-request="):
            json_request_file = arg.split("=", 1)[1]
            break

    if not json_request_file:
        # If no json-request file, we can't cache, so just execute the command
        subprocess.run([real_gcloud_path] + args)
        sys.exit(0)

    # 3. Read the JSON request file and extract prompt and model
    try:
        with open(json_request_file, 'r') as f:
            request_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file is not found or invalid JSON, execute the real command
        subprocess.run([real_gcloud_path] + args)
        sys.exit(0)

    # The prompt is usually in instances[0]['prompt']
    # This might need to be adjusted based on the actual gcloud AI platform API
    prompt = request_data.get("instances", [{}])[0].get("prompt", "")
    
    # The model is part of the command line arguments, not the json file
    # e.g. gcloud ai models predict --model="gemini-1.0-pro-001"
    model = None
    for arg in args:
        if arg.startswith("--model="):
            model = arg.split("=", 1)[1]
            break

    # 4. Create cache key
    cache = Cache()
    context = {"model": model, "request_data": request_data}
    
    # 5. Check cache
    cached_response = cache.get(prompt, context)
    if cached_response:
        print("--- (aicache HIT) ---", file=sys.stderr)
        print(cached_response["response"])
        sys.exit(0)

    # 6. Cache miss
    print("--- (aicache MISS) ---", file=sys.stderr)
    
    # Execute real command
    process = subprocess.run([real_gcloud_path] + args, capture_output=True, text=True)

    if process.returncode == 0:
        response = process.stdout
        cache.set(prompt, response, context)
        print(response)
    else:
        print(process.stderr, file=sys.stderr)
        sys.exit(process.returncode)


if __name__ == "__main__":
    main()
