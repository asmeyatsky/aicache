# Changelog

All notable changes to aicache will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Open source release with MIT License
- Security policy document
- Code of Conduct for contributors
- Support documentation
- Dynamic path discovery for CLI executables instead of hardcoded paths

### Changed
- Removed all personal hardcoded paths from plugin files
- Improved privacy settings for analytics (opt-in by default)

### Fixed
- Removed sensitive information and hardcoded paths
- Updated all plugin files to use shutil.which() for executable path discovery

## [0.1.0] - 2024-XX-XX

### Added
- Core caching functionality for AI CLIs (gcloud, llm, openai, claude, gemini, qwen)
- Intelligent argument parsing to create accurate cache keys
- Persistent storage across sessions
- Comprehensive management commands (`list`, `inspect`, `clear`, `prune`, `stats`)
- Interactive cache management tools
- Shell integration and completions
- Semantic search with AI-powered matching
- Behavioral analytics and learning user patterns
- Predictive prefetching based on usage patterns
- Multi-modal support for images, notebooks, audio, and video files
- PII detection and data sanitization
- Performance optimization with compression algorithms
- Team collaboration features
- IDE integrations (VS Code, JetBrains, Neovim, JupyterLab)
- Web dashboard for analytics and management
- Self-healing mechanisms for error recovery

[Unreleased]: https://github.com/asmeyatsky/aicache/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/asmeyatsky/aicache/releases/tag/v0.1.0