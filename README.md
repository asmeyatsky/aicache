# aicache

🚀 **AI CLI Session Caching with Token Optimization Analytics**

This project is a production-grade caching system for AI CLIs (Gemini, Claude, Qwen, and OpenAI) that improves developer workflow efficiency while providing comprehensive token cost transparency through TOON (Token Optimization Object Notation).

**Key Innovation**: Automatically track, analyze, and optimize token spending with interactive dashboards, CLI tools, and data-driven insights on every cache operation.

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
- **🎯 TOON Analytics**: Comprehensive Token Optimization Object Notation system for transparent cost tracking and analytics (see below).

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

### 🎯 TOON Commands (Token Optimization Analytics)

TOON provides transparent token cost tracking and optimization insights for every cache operation:

*   `aicache toon list [--limit=50] [-v|--verbose]`: List recent TOON operations with detailed breakdown.
*   `aicache toon inspect <operation_id>`: View complete details of a specific TOON operation.
*   `aicache toon last`: Show the most recent TOON operation.
*   `aicache toon analytics [--period=1d|7d|30d|1w|1m]`: View aggregated cache analytics and metrics.
*   `aicache toon query [--type=exact_hit|semantic_hit|...] [--min-tokens=100] [--min-similarity=0.9]`: Advanced querying with filters.
*   `aicache toon export [--format=json|csv|jsonl|msgpack] [--limit=500] [-o|--output=file]`: Export TOON data for analysis.
*   `aicache toon insights [--days=1]`: Get data-driven recommendations for optimization.
*   `aicache toon delete <operation_id>`: Delete a specific TOON operation.
*   `aicache toon clear [--confirm]`: Clear all TOON operations.

## 🎯 TOON: Token Optimization Object Notation

TOON is a comprehensive system that transforms cache operations from a black box into transparent, auditable, cost-optimized intelligence. Every cache operation generates a TOON object that captures:

### What TOON Tracks

✅ **Financial Transparency**
- Exact token/cost savings per operation
- Daily cost tracking and ROI calculations
- Projected monthly/annual savings

✅ **Performance Metrics**
- Hit rates (exact matches, semantic matches, intent-based)
- Response times and efficiency scoring
- Cache age, TTL, and eviction risk

✅ **Decision Context**
- Why each cache decision was made (exact hit, semantic, intent, miss)
- Semantic similarity scores and confidence levels
- Optimization insights and recommendations

✅ **Historical Analytics**
- Trends in cache performance (improving/declining)
- Pattern detection and usage patterns
- Complete audit trail of all operations

### TOON Features

🔹 **Automatic Generation** - TOON is created automatically on every cache operation (0 breaking changes)
🔹 **CLI Tools** - 9 commands for inspection, analysis, and export
🔹 **Interactive Dashboard** - Beautiful HTML reports with 4 real-time charts
🔹 **Automated Reports** - Daily/weekly/monthly report generation
🔹 **Advanced Querying** - Filter TOONs by type, tokens saved, similarity, time range
🔹 **Multiple Exports** - JSON, CSV, JSONL, and binary msgpack formats
🔹 **Data-Driven Insights** - Actionable recommendations for optimization

### Quick TOON Example

```bash
# View recent cache operations and their savings
aicache toon list --verbose

# Get detailed breakdown of today's analytics
aicache toon analytics --period=1d

# Export data for external analysis
aicache toon export --format=csv --limit=500 > cache_analysis.csv

# Get AI-powered insights for optimization
aicache toon insights --days=7
```

### Real Impact

With TOON, you can answer questions like:
- "How much am I saving with caching?" → $1.35/day, $40.50/month
- "What's my cache hit rate?" → 87.5% (exact: 65%, semantic: 22%)
- "Which caching strategy works best?" → Data-driven recommendations
- "Is cache performance improving?" → Yes, trending up 5% this week

### TOON Documentation

For comprehensive guides on using TOON, see:
- [TOON_INTRODUCTION.md](docs/TOON_INTRODUCTION.md) - Overview and benefits
- [TOON_SPECIFICATION.md](docs/TOON_SPECIFICATION.md) - Complete technical specification
- [TOON_INTEGRATION_GUIDE.md](docs/TOON_INTEGRATION_GUIDE.md) - Integration examples
- [TOON_QUICK_REFERENCE.md](docs/TOON_QUICK_REFERENCE.md) - CLI command reference
- [TOON_INDEX.md](TOON_INDEX.md) - Navigation guide

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
