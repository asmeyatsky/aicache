# Comprehensive Testing Guide for aicache

This document provides a comprehensive testing strategy for aicache, covering all core functionality, advanced features, and integration points.

## Table of Contents
1. [Core Cache Functionality](#1-core-cache-functionality)
2. [CLI Wrapper Testing](#2-cli-wrapper-testing)
3. [Enhanced Cache Features](#3-enhanced-cache-features)
4. [Behavioral Learning System](#4-behavioral-learning-system)
5. [Predictive Caching](#5-predictive-caching)
6. [Intent-Based Caching](#6-intent-based-caching)
7. [Semantic Search](#7-semantic-search)
8. [Multi-Modal Content Caching](#8-multi-modal-content-caching)
9. [Configuration Management](#9-configuration-management)
10. [Team Collaboration](#10-team-collaboration)
11. [Streaming Support](#11-streaming-support)
12. [Performance and Scalability](#12-performance-and-scalability)
13. [Security Testing](#13-security-testing)
14. [Installation and Setup](#14-installation-and-setup)

## 1. Core Cache Functionality

### 1.1 Basic Cache Operations

**Test Case 1.1.1: Cache Entry Creation**
- Run: `aicache set "What is the capital of France?" "Paris"`
- Expected: Confirmation message "Cache entry set."
- Run: `aicache list`
- Expected: Entry appears in list

**Test Case 1.1.2: Cache Entry Retrieval**
- Run: `aicache get "What is the capital of France?"`  
- Expected: Returns JSON with prompt, response, and context

**Test Case 1.1.3: Cache Miss Handling**
- Run: `aicache get "What is the capital of Germany?"`
- Expected: Returns "No cache entry found."

### 1.2 Context-Aware Caching

**Test Case 1.2.1: Model Context Differentiation**
- Run: `aicache set "Tell me a joke" "Why did the chicken cross the road?" --context '{"model": "gpt-4"}'`
- Run: `aicache set "Tell me a joke" "To get to the other side!" --context '{"model": "claude-3"}'`
- Run: `aicache list -v`
- Expected: Two separate entries with different contexts

**Test Case 1.2.2: Complex Context Handling**
- Run: `aicache set "Python function example" "def hello(): pass" --context '{"language": "python", "framework": "flask", "temperature": 0.7}'`
- Run: `aicache get "Python function example" --context '{"language": "python", "framework": "flask", "temperature": 0.7}'`
- Expected: Returns the correct entry with all context preserved

### 1.3 Cache Management

**Test Case 1.3.1: Cache Inspection**
- Run: `aicache inspect <cache_key>`
- Expected: Detailed entry information including prompt, response, context, and timestamp

**Test Case 1.3.2: Cache Deletion**
- Run: `aicache list` to get cache key
- Run: `aicache clear --interactive` and select entry
- Expected: Entry is removed from cache

**Test Case 1.3.3: Full Cache Clear**
- Run: `aicache clear`
- Expected: All entries removed, confirmed by `aicache list` returning empty

### 1.4 Cache Statistics

**Test Case 1.4.1: Statistics Collection**
- Run: `aicache stats`
- Expected: Shows total entries, total size, and any expired entries

**Test Case 1.4.2: Cache Pruning**
- Create a config with small max_size_mb
- Add multiple entries to exceed limit
- Run: `aicache prune`
- Expected: Older entries are removed to maintain size limit

## 2. CLI Wrapper Testing

### 2.1 Wrapper Installation

**Test Case 2.1.1: List Available Wrappers**
- Run: `aicache install --list`
- Expected: Shows available CLI tools (openai, llm, gcloud) with their status

**Test Case 2.1.2: Install Specific Wrapper**
- Run: `aicache install llm`
- Expected: Wrapper installed in ~/.local/bin/llm

**Test Case 2.1.3: Install All Wrappers**
- Run: `aicache install --setup-wrappers`
- Expected: All available wrappers installed

### 2.2 Wrapper Functionality

**Test Case 2.2.1: Wrapped Command Execution (Cache Miss)**
- Run: `llm "Tell me a joke about computers"`
- Expected: Command executes, shows "[cached MISS]" message

**Test Case 2.2.2: Wrapped Command Execution (Cache Hit)**
- Run: `llm "Tell me a joke about computers"` (same command again)
- Expected: Command returns instantly with "[cached HIT]" message

**Test Case 2.2.3: Context Preservation**
- Run: `llm -m gpt-4 "What is 2+2?"`
- Run: `llm -m claude-3 "What is 2+2?"`
- Run: `aicache list`
- Expected: Two separate entries for same prompt with different models

### 2.3 Generic Wrapper Creation

**Test Case 2.3.1: Create Custom Wrapper**
- Run: `aicache create-generic-wrapper mycli --path /usr/local/bin/mycli --prompt-regex "(?:.*\")(.+)(?:\".*)"`
- Expected: Custom wrapper script created in custom_wrappers directory

## 3. Enhanced Cache Features

### 3.1 Enhanced Cache Initialization

**Test Case 3.1.1: Enhanced Cache Creation**
- In Python: `cache = EnhancedCache("test")`
- Expected: Cache initialized with enhanced features

**Test Case 3.1.2: Enhanced Cache Operations**
- Test set/get operations with enhanced cache
- Expected: Same functionality as basic cache but with enhanced metadata

### 3.2 Project Context Detection

**Test Case 3.2.1: JavaScript Project Detection**
- Create directory with package.json
- Run enhanced cache operations
- Expected: Context includes language=javascript, detected framework

**Test Case 3.2.2: Python Project Detection**
- Create directory with requirements.txt
- Run enhanced cache operations
- Expected: Context includes language=python, detected framework

## 4. Behavioral Learning System

### 4.1 Behavioral Analytics

**Test Case 4.1.1: Analytics Collection**
- Run multiple cache operations with different contexts
- Run: `aicache analytics --behavioral`
- Expected: Shows total queries, cache hit rate, unique users/sessions

**Test Case 4.1.2: Pattern Recognition**
- Run: `aicache analytics --patterns`
- Expected: Shows learned patterns from usage

### 4.2 Behavioral Learning Integration

**Test Case 4.2.1: Learning Session**
- Run multiple related queries in sequence
- Expected: System learns patterns and suggests prefetches

## 5. Predictive Caching

### 5.1 Prediction Engine

**Test Case 5.1.1: Query Prediction**
- Run: `aicache predict "Python function"`
- Expected: Shows predicted next queries with confidence scores

### 5.2 Prefetch System

**Test Case 5.2.1: Manual Prefetch**
- Run: `aicache prefetch "Python decorators tutorial"`
- Expected: Prefetch scheduled and visible in stats

**Test Case 5.2.2: Prefetch Statistics**
- Run: `aicache analytics --prefetch`
- Expected: Shows prefetch statistics including success rate and queue size

## 6. Intent-Based Caching

### 6.1 Intent Analysis

**Test Case 6.1.1: Intent-Based Retrieval**
- Store entries with similar intents
- Query with related intent
- Expected: System matches based on intent rather than exact text

## 7. Semantic Search

### 7.1 Semantic Matching

**Test Case 7.1.1: Semantic Similarity**
- Store entry: "How to create a Python function?"
- Query: "How to write a Python function?"
- Expected: System finds semantically similar entry

## 8. Multi-Modal Content Caching

### 8.1 Image Caching

**Test Case 8.1.1: Image Storage**
- Run: `aicache cache-image my_image_key /path/to/image.png`
- Expected: Image stored and key registered

**Test Case 8.1.2: Image Retrieval**
- Run: `aicache get-image my_image_key`
- Expected: Returns path to cached image

### 8.2 Notebook Caching

**Test Case 8.2.1: Notebook Storage**
- Run: `aicache cache-notebook my_notebook_key /path/to/notebook.ipynb`
- Expected: Notebook stored and key registered

**Test Case 8.2.2: Notebook Retrieval**
- Run: `aicache get-notebook my_notebook_key`
- Expected: Returns path to cached notebook

### 8.3 Audio/Video Caching

**Test Case 8.3.1: Audio Storage and Retrieval**
- Run: `aicache cache-audio my_audio_key /path/to/audio.mp3`
- Run: `aicache get-audio my_audio_key`
- Expected: Audio stored and retrievable

**Test Case 8.3.2: Video Storage and Retrieval**
- Run: `aicache cache-video my_video_key /path/to/video.mp4`
- Run: `aicache get-video my_video_key`
- Expected: Video stored and retrievable

## 9. Configuration Management

### 9.1 Configuration File

**Test Case 9.1.1: Config File Creation**
- Run: `aicache install --config`
- Expected: Default config file created at ~/.config/aicache/config.yaml

**Test Case 9.1.2: Configuration Validation**
- Run: `python -c "from aicache.config import validate_config; print(validate_config())"`
- Expected: Returns validation results with no errors

## 10. Team Collaboration

### 10.1 Team Features

**Test Case 10.1.1: Team Configuration**
- Enable team collaboration in config
- Set team_id and user_id
- Expected: Team features become available

## 11. Streaming Support

### 11.1 Streaming Features

**Test Case 11.1.1: Streaming Configuration**
- Enable streaming in config
- Expected: WebSocket server can be started for streaming support

## 12. Performance and Scalability

### 12.1 Performance Testing

**Test Case 12.1.1: Cache Speed**
- Time multiple cache operations
- Expected: Sub-millisecond response times for cache hits

**Test Case 12.1.2: Memory Usage**
- Monitor memory during heavy cache usage
- Expected: Stable memory consumption with proper cleanup

## 13. Security Testing

### 13.1 Security Features

**Test Case 13.1.1: Data Encryption**
- Enable encryption in config
- Store sensitive data
- Expected: Data stored in encrypted format

### 13.2 Access Control

**Test Case 13.2.1: Configuration Security**
- Test config file permissions
- Expected: Config files have appropriate restricted permissions

## 14. Installation and Setup

### 14.1 Installation Process

**Test Case 14.1.1: Clean Installation**
- Install aicache in fresh environment
- Expected: All components install without errors

**Test Case 14.1.2: PATH Setup**
- Verify ~/.local/bin is in PATH
- Expected: aicache command is accessible from any directory

### 14.2 Dependency Management

**Test Case 14.2.1: Dependency Installation**
- Run: `python install_dependencies.py`
- Expected: All required dependencies installed

### 14.3 Uninstallation

**Test Case 14.3.1: Wrapper Removal**
- Run: `aicache uninstall llm`
- Expected: llm wrapper removed from ~/.local/bin

## Automated Testing

### Unit Tests

Run the existing unit test suite:
```bash
python -m unittest tests/test_core.py
python -m unittest tests/test_cli.py
```

### Integration Tests

Run the comprehensive test suite:
```bash
python test_suite.py
```

### Phase Tests

Run phase-specific tests:
```bash
python test_phase2.py
python test_phase3.py
```

## Manual Testing Checklist

Before each release, manually verify:

- [ ] Basic cache operations (set/get/list/clear)
- [ ] CLI wrapper functionality with popular tools (llm, openai)
- [ ] Context-aware caching with different models
- [ ] Semantic search capabilities
- [ ] Behavioral learning system
- [ ] Predictive prefetching
- [ ] Multi-modal content caching (images, notebooks)
- [ ] Configuration management
- [ ] Installation and uninstallation processes
- [ ] Performance under normal and heavy load
- [ ] Security features (encryption, access control)
- [ ] Team collaboration features (if enabled)

## Troubleshooting

### Common Issues

1. **Cache Miss When Expected Hit**
   - Verify exact prompt and context match
   - Check for trailing spaces or special characters
   - Use `aicache list -v` to see stored entries

2. **Wrapper Not Working**
   - Verify ~/.local/bin is in PATH
   - Check wrapper script permissions (should be executable)
   - Ensure original CLI tool is installed

3. **Performance Degradation**
   - Check cache size with `aicache stats`
   - Run `aicache prune` if cache is too large
   - Verify system has adequate resources

### Log Analysis

Enable debug logging to troubleshoot issues:
```bash
export AICACHE_LOG_LEVEL=DEBUG
```

## Performance Benchmarks

### Baseline Performance Targets

- Cache Hit Response Time: < 5ms
- Cache Miss Processing: < 100ms overhead
- Memory Usage: < 100MB for 10,000 entries
- Disk Usage: Efficient compression (typically 50-70% reduction)

### Scaling Tests

Test with:
- 1,000 cache entries
- 10,000 cache entries
- 100,000 cache entries
- Mixed read/write patterns
- Concurrent access scenarios

## Security Validation

### Data Protection

- [ ] Verify encryption of sensitive cache entries
- [ ] Check file permissions on cache directories
- [ ] Validate secure handling of API keys and credentials
- [ ] Test data retention policies

### Access Control

- [ ] Verify user isolation in multi-user environments
- [ ] Test team sharing permissions
- [ ] Validate configuration file access restrictions

This comprehensive testing guide ensures thorough validation of all aicache functionality across different environments and use cases.