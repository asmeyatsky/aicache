# aicache Roadmap

## Introduction

The vision for `aicache` is to become an indispensable tool for developers who use AI CLIs, significantly improving their workflow efficiency, reducing costs, and providing a more seamless and stateful experience. This roadmap outlines the planned features and improvements to achieve this vision.

## Phase 1: Core Functionality & Usability (Short-Term)

This phase focuses on improving the existing features, making the tool more robust, and enhancing the user experience.

*   **Improved Argument Parsing in Wrappers:**
    *   [ ] Implement intelligent parsing of command-line arguments for `gcloud` and `llm` to identify the prompt, model, temperature, and other relevant parameters.
    *   [ ] Ignore irrelevant arguments (e.g., `--verbose`, `--debug`) when generating the cache key.
    *   [ ] Normalize arguments to handle different forms (e.g., `-m` vs. `--model`).
*   **Enhanced Cache Management CLI:**
    *   [ ] `aicache inspect <cache_key>`: A command to view the details of a specific cache entry (prompt, response, context, timestamp).
    *   [ ] `aicache list --verbose`: An option to show more details for each cache entry in the list view.
    *   [ ] `aicache clear --interactive`: An interactive mode for the `clear` command that allows users to select which entries to delete.
*   **Improved Installation and Setup:**
    *   [ ] Create a `Makefile` for easier installation and setup of the wrapper scripts.
    *   [ ] Add more detailed instructions and examples to the `README.md`.
*   **Shell Completions:**
    *   [ ] Implement shell completions for `bash`, `zsh`, and `fish` to improve the usability of the `aicache` CLI.

## Phase 2: Advanced Caching & Configuration (Mid-Term)

This phase introduces more advanced caching strategies and a flexible configuration system.

*   **Configuration System:**
    *   [ ] Implement support for a configuration file (e.g., `~/.config/aicache/config.yaml`).
    *   [ ] Allow users to configure the cache directory, TTL, and other settings.
*   **Advanced Caching Strategies:**
    *   [ ] **Cache Expiration (TTL):** Implement a Time-to-Live (TTL) for cache entries to automatically expire old entries.
    *   [ ] **Cache Pruning:** Implement a `aicache prune` command to manually prune the cache based on age or size.
    *   [ ] **Cache Size Limits:** Allow users to set a maximum size for the cache directory.
    *   [ ] **Content-based Hashing:** For file inputs, hash the file's content instead of its name to make the cache more robust.
*   **Cache Statistics:**
    *   [ ] `aicache stats`: A command to display cache statistics, such as hit/miss ratio, total size, and number of entries.

## Phase 3: Ecosystem & Broader Integration (Long-Term)

This phase focuses on expanding the tool to support more CLIs and becoming a more general-purpose caching solution.

*   **Broader AI CLI Support:**
    *   [ ] Create wrapper scripts for other popular AI CLIs (e.g., OpenAI, other Anthropic models).
    *   [ ] Develop a plugin system to make it easier to add support for new CLIs.
*   **Generic CLI Caching:**
    *   [ ] Create a generic wrapper script that can be configured to work with any command-line tool.
    *   [ ] Add features to support caching for a wider range of CLI tools, not just AI CLIs.
*   **Community and Contribution:**
    *   [ ] Improve the `CONTRIBUTING.md` with more detailed guidelines for developers.
    *   [ ] Create a small website or a more detailed GitHub Pages site for documentation.

## Future Ideas & Moonshots

These are ambitious, long-term ideas that could be explored in the future.

*   **Semantic Caching:**
    *   [ ] Integrate a sentence-embedding model to enable semantic caching, allowing the tool to find cached responses for semantically similar prompts.
*   **Shared Cache:**
    *   [ ] Explore the possibility of a shared cache for teams, allowing developers to share and reuse cached AI responses. This would require a backend service and authentication.
*   **GUI for Cache Management:**
    *   [ ] A simple graphical user interface (GUI) to visualize, search, and manage the cache.
*   **Streaming and Partial Caching:**
    *   [ ] For CLIs that support streaming responses, implement partial caching to store and resume streams.
