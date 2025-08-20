#!/bin/bash

# 1. Find the real llm executable
REAL_LLM_PATH=$(which llm)

if [ -z "$REAL_LLM_PATH" ]; then
    echo "Error: llm executable not found." >&2
    exit 1
fi

# 2. Parse arguments to build a cache key.
# We also need to handle stdin.
if [ -t 0 ]; then
    # Input is from arguments
    PROMPT_CONTENT="$*"
else
    # Input is from stdin (piped)
    PROMPT_CONTENT=$(cat)
fi

CACHE_KEY=$(echo -n "$PROMPT_CONTENT" | shasum -a 256 | awk '{print $1}')

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
# Handle both piped and argument-based input
if [ -n "$PROMPT_CONTENT" ] && [ ! -t 0 ]; then
    # We read from stdin, so we must pipe it to the real command
    REAL_RESPONSE=$(echo -n "$PROMPT_CONTENT" | "$REAL_LLM_PATH" "$@")
else
    # Arguments were passed directly
    REAL_RESPONSE=$("$REAL_LLM_PATH" "$@")
fi
EXIT_CODE=$?

# On success, update the cache
if [ $EXIT_CODE -eq 0 ]; then
    aicache set "$CACHE_KEY" "$REAL_RESPONSE"
fi

# Print the response for the user
echo "$REAL_RESPONSE"
exit $EXIT_CODE
