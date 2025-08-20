#!/bin/bash

# 1. Find the real gcloud executable
REAL_GCLOUD_PATH=$(which gcloud)

if [ -z "$REAL_GCLOUD_PATH" ]; then
    echo "Error: gcloud executable not found." >&2
    exit 1
fi

# 2. Parse arguments to build a cache key.
# For simplicity, we'll hash all arguments.
CACHE_KEY_INPUT="$@"
# If one of the arguments is a file, we should include the file content in the cache key.
if [[ "$@" == *"--json-request="* ]]; then
    # Extract the file path from the arguments
    REQUEST_FILE=$(echo "$@" | grep -o -E '--json-request=[^ ]+' | cut -d'=' -f2)
    if [ -f "$REQUEST_FILE" ]; then
        CACHE_KEY_INPUT+=$(cat "$REQUEST_FILE")
    fi
fi

CACHE_KEY=$(echo -n "$CACHE_KEY_INPUT" | shasum -a 256 | awk '{print $1}')

# 3. Check the cache
CACHED_RESPONSE=$(aicache get "$CACHE_KEY")

# 4. Cache Hit
if [ $? -eq 0 ]; then
    echo "--- (aicache HIT) ---" >&2
    echo "$CACHED_RESPONSE"
    exit 0
fi

# 5. Cache Miss
echo "--- (aicache MISS) ---" >&2

# Execute the real command and capture its output
REAL_RESPONSE=$("$REAL_GCLOUD_PATH" "$@")
EXIT_CODE=$?

# On success, update the cache
if [ $EXIT_CODE -eq 0 ]; then
    aicache set "$CACHE_KEY" "$REAL_RESPONSE"
fi

# Print the response for the user
echo "$REAL_RESPONSE"
exit $EXIT_CODE
