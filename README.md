# aicache

AI CLI Session Caching.

This project is a caching system for AI CLIs (Gemini, Claude, Qwen, and OpenAI) to improve developer workflow efficiency.

## Features

- Automatic session caching for `gcloud`, `llm`, `openai`, `claude`, `gemini`, and `qwen` CLIs.
- Intelligent argument parsing to create accurate cache keys.
- Persistence of cache across sessions.
- A rich set of commands to manage the cache (`list`, `inspect`, `clear`).
- Interactive cache clearing.
- Shell completions for `bash`.
- Custom wrapper support for additional AI CLI tools.

## Getting Started

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/asmeyatsky/aicache.git
    cd aicache
    ```

2.  **Run the setup:**
    ```bash
    make setup
    ```
    This will install the `aicache` package in a virtual environment and create wrapper scripts for `gcloud`, `llm`, `openai`, `claude`, `gemini`, and `qwen` in `~/.local/bin`.

3.  **Update your shell's configuration:**
    Make sure `~/.local/bin` is in your `$PATH` and has precedence over the default paths. Add the following line to your `~/.bashrc`, `~/.zshrc`, or other shell configuration file:
    ```bash
    export PATH="$HOME/.local/bin:$PATH"
    ```
    Restart your shell for the changes to take effect.

### Usage

Once installed, the `aicache` wrappers for `gcloud`, `llm`, `openai`, `claude`, `gemini`, and `qwen` will work automatically. When you run a command with any of these AI CLIs, the wrapper will cache the response. The next time you run the same command, the response will be served from the cache.

### CLI Commands

`aicache` provides a command-line interface to manage the cache:

*   `aicache list`: List all cached entries.
    *   `--verbose`: Show more details for each entry.
*   `aicache inspect <cache_key>`: Inspect a specific cache entry.
*   `aicache clear`: Clear the entire cache.
    *   `--interactive`: Interactively select which entries to delete.
*   `aicache generate-completions`: Generate a bash script for shell completions.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
