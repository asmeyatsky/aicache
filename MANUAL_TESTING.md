
# How to Test `aicache`

This document provides a set of manual test cases to help you verify that `aicache` is working correctly.

## Prerequisites

1.  Make sure you have completed the setup steps in the `README.md`, especially adding the local binaries to your `PATH`:
    ```bash
    export PATH="$HOME/.local/bin:$PATH"
    ```
2.  Ensure you have restarted your terminal after updating your shell configuration.
3.  For these tests, we will use the `llm` command wrapper. You can install the underlying `llm` tool if you don't have it, but it's not strictly necessary as `aicache` will simply pass the command through.

---

## Test Case 1: Your First Cached Command

This test verifies that a command is executed and its output is stored in the cache.

1.  **Clear the cache** to ensure you're starting from a clean slate.
    ```bash
    aicache clear
    ```

2.  **Run a command.** We'll ask for a joke using the `llm` tool with the `gpt-4` model. The first time you run this, it will execute the real command (or fail if you don't have `llm` configured, which is fine for this test).
    ```bash
    llm -m gpt-4 "Tell me a short joke about a computer."
    ```
    You should see some output, either a joke or a command-not-found error.

3.  **Run the *exact same* command again.**
    ```bash
    llm -m gpt-4 "Tell me a short joke about a computer."
    ```
    This time, the output should be returned instantly, prefixed with `[cached]`. This confirms the response was served from the cache.

---

## Test Case 2: Inspecting the Cache Contents

This test shows you how to view and inspect the entries in your cache.

1.  **List the cache entries.** You should see one entry corresponding to the command you just ran.
    ```bash
    aicache list
    ```
    The output will look something like this, with a unique hash:
    ```
    e.g., 2d1b8a... | gpt-4 | Tell me a short joke about a computer.
    ```

2.  **Inspect the specific entry.** Copy the hash from the `list` command and use it with the `inspect` command.
    ```bash
    # Replace <hash> with the actual hash from your output
    aicache inspect <hash>
    ```
    This will print the full details of the cache entry, including the prompt, the full response, the context (model), and other metadata.

---

## Test Case 3: Context-Aware Caching

This test verifies that `aicache` correctly separates entries based on their context (e.g., using a different model).

1.  **Run the same prompt but with a different model.** Here, we'll use `claude-3` instead of `gpt-4`.
    ```bash
    llm -m claude-3 "Tell me a short joke about a computer."
    ```
    This command will execute live, as it's considered a new prompt-context combination.

2.  **List the cache again.**
    ```bash
    aicache list
    ```
    You will now see **two** distinct entries for the same prompt, because they were run with different models (`gpt-4` and `claude-3`). This demonstrates the core feature that allows you to maintain separate contexts.

---

## Test Case 4: Clearing the Cache

This test verifies that you can successfully clear all entries from the cache.

1.  **Run the clear command.**
    ```bash
    aicache clear --confirm
    ```
    *(Note: The `--confirm` flag skips the interactive "Are you sure?" prompt.)*

2.  **List the cache one last time.**
    ```bash
    aicache list
    ```
    The output should now be empty, confirming that the cache has been cleared.

You can find this documentation in the `MANUAL_TESTING.md` file in the project's root directory. I hope this helps you get started and test the functionality!