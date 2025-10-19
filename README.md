# aicache

AI CLI Session Caching.

This project is a caching system for AI CLIs (Gemini, Claude, Qwen, and OpenAI) to improve developer workflow efficiency.

## 🚀 Features

- **Advanced Caching**: Automatic session caching for `gcloud`, `llm`, `openai`, `claude`, `gemini`, and `qwen` CLIs.
- **Intelligent Parsing**: Intelligent argument parsing to create accurate cache keys.
- **Persistent Storage**: Persistence of cache across sessions.
- **Comprehensive Management**: A rich set of commands to manage the cache (`list`, `inspect`, `clear`, `prune`, `stats`).
- **Interactive Tools**: Interactive cache clearing and management.
- **Shell Integration**: Completions for `bash` and custom wrapper support.
- **Semantic Search**: AI-powered semantic matching for similar queries using embedding models.
- **Behavioral Analytics**: Learning user patterns to optimize caching strategies.
- **Predictive Prefetching**: Proactively caching likely future queries based on patterns.
- **Multi-Modal Support**: Cache support for images, notebooks, audio, and video files.
- **Enhanced Security**: PII detection and data sanitization for sensitive information.
- **Performance Optimization**: Efficient compression and storage algorithms.

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- The AI CLI tools you want to cache (e.g., `gemini`, `claude`, `qwen`, etc.) must be installed and available in your PATH

### Quick Setup

1. **Install from PyPI (recommended):**
    ```bash
    pip install aicache
    ```

2. **Or install from source:**
    ```bash
    git clone https://github.com/asmeyatsky/aicache.git
    cd aicache
    pip install .
    ```

3. **Setup CLI wrappers:**
    ```bash
    aicache install --setup-wrappers
    ```

4. **Update your shell's configuration:**
    Make sure `~/.local/bin` is in your `$PATH` and has precedence over the default paths. Add the following line to your `~/.bashrc`, `~/.zshrc`, or other shell configuration file:
    ```bash
    export PATH="$HOME/.local/bin:$PATH"
    ```
    Restart your shell for the changes to take effect.

## 🛠️ Usage

Once installed, the `aicache` wrappers for `gcloud`, `llm`, `openai`, `claude`, `gemini`, and `qwen` will work automatically. When you run a command with any of these AI CLIs, the wrapper will cache the response. The next time you run the same command, the response will be served from the cache.

### CLI Commands

`aicache` provides a comprehensive command-line interface to manage the cache:

*   `aicache list`: List all cached entries.
    *   `--verbose`: Show more details for each entry.
*   `aicache inspect <cache_key>`: Inspect a specific cache entry.
*   `aicache clear`: Clear the entire cache.
    *   `--interactive`: Interactively select which entries to delete.
*   `aicache generate-completions`: Generate a bash script for shell completions.
*   `aicache stats`: Show cache statistics and performance metrics.
*   `aicache prune`: Remove expired or low-priority cache entries.
*   `aicache install`: Install/uninstall CLI wrappers and configuration.
    *   `--setup-wrappers`: Install all available CLI wrappers
    *   `--config`: Create default configuration file
    *   `--list`: List available CLI tools
*   `aicache analytics`: Show behavioral analytics and usage patterns.
    *   `--behavioral`: Show behavioral analytics
    *   `--patterns`: Show learned usage patterns
    *   `--prefetch`: Show prefetch statistics
*   `aicache predict <query>`: Predict likely next queries based on patterns.
*   `aicache prefetch <query>`: Prefetch a specific query proactively.
*   `aicache create-generic-wrapper`: Create custom wrapper for any CLI tool.
*   `aicache cache-image/cache-notebook/cache-audio/cache-video`: Commands for multi-modal caching.

## 📊 Configuration

aicache can be configured using a YAML configuration file. By default, it looks for `~/.config/aicache/config.yaml`. You can create a default configuration file using:

```bash
aicache install --config
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to:
- Set up a development environment
- Submit pull requests
- Report bugs
- Request features
- Follow our code of conduct

## 🛡️ Security

Please see our [Security Policy](SECURITY.md) for information on how to report security vulnerabilities.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all contributors who help maintain and improve aicache
- Inspired by the need for efficient AI CLI workflows in development environments
