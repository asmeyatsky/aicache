"""
AI Cache Module - Architectural Documentation

This document describes the architectural intent of the AI caching solution,
following skill2026.md principles and incorporating 2026 LLM caching trends.

================================================================================
ARCHITECTURAL INTENT
================================================================================

1. Core Purpose:
   - Provide transparent caching layer for AI queries
   - Support exact-match, semantic-similarity, and prompt caching
   - Track token usage and cost savings automatically
   - Enable progressive transparency of cache decisions

2. Design Decisions:
   - Immutable cache entries prevent accidental corruption
   - Semantic matching abstracted for multi-backend support
   - All cache decisions logged for auditability
   - TTL enforcement at query time (lazy expiration)
   - Cost tracking integrates with token counting abstraction

================================================================================
2026 LLM CACHING TRENDS INCORPORATED
================================================================================

1. Prompt Caching (Provider-Specific):
   - OpenAI: Automatic caching when >=1024 tokens shared (50% savings)
   - Anthropic: Explicit cache_prefix required (90% savings, 5-10min TTL)
   - Google: Implicit + explicit caching (75% savings)
   - See: domain/prompt_caching.py

2. Multi-Provider Caching:
   - Automatic failover between providers
   - Unified port interface: PromptCachePort
   - See: MultiProviderPromptCachePort

3. Context Window Management:
   - Explicit token budget management
   - Priority-based context inclusion
   - See: application/schemas.py ContextBuilderConfig

================================================================================
SKILL2026.MD PRINCIPLES APPLIED
================================================================================

1. Separation of Concerns:
   - Domain layer has ZERO dependencies on infrastructure
   - Application layer orchestrates domain objects
   - Infrastructure layer implements port interfaces
   - MCP servers live in infrastructure layer

2. Domain-Driven Design:
   - Rich domain models: CacheEntry, CachePolicy, SemanticMatch
   - Ubiquitous language: cache hit, miss, eviction, TTL
   - Aggregates: CacheEntry is the root aggregate
   - Bounded contexts: CacheManagement, QueryOptimization, CostTracking

3. Hexagonal Architecture:
   - Domain Layer (Core): models, ports, services
   - Application Layer: use_cases, orchestration, schemas
   - Infrastructure Layer: adapters, mcp_servers
   - Presentation Layer: cli, api (future)

4. MCP-Native Integration:
   - Bounded context as MCP server (one per context)
   - Tools = write operations
   - Resources = read operations
   - Prompts = reusable patterns

5. Parallelism-First Design:
   - DAG-based workflow orchestration
   - Independent operations parallelized automatically
   - Backpressure at orchestration layer
   - Fan-out/fan-in patterns for batch operations

================================================================================
PERFORMANCE CHARACTERISTICS
================================================================================

- Exact match lookups: O(1) with hash-based storage
- Semantic matches: O(log n) with vector indexing
- Memory: Configurable with LRU/LFU policies
- Latency: <5ms for cache hits (p99)
- Prompt caching: 50-90% cost reduction (2026)
- Token counting overhead: <2ms per query

================================================================================
KNOWN LIMITATIONS
================================================================================

- Semantic matching quality depends on embedding model
- Distributed caching requires eventual consistency handling
- Context window changes can invalidate cached responses
- Prompt caching TTL varies by provider

================================================================================
KEY FILES
================================================================================

Domain Layer:
  - models.py: Immutable domain entities (CacheEntry, CachePolicy, etc.)
  - ports.py: Interface abstractions (StoragePort, SemanticIndexPort, etc.)
  - services.py: Domain logic (SemanticCachingService, EvictionService, etc.)
  - prompt_caching.py: 2026 provider-specific prompt caching

Application Layer:
  - use_cases.py: QueryCacheUseCase, StoreCacheUseCase, etc.
  - orchestration.py: DAG-based parallel workflow execution
  - schemas.py: Pydantic schemas for AI-structured output

Infrastructure Layer:
  - adapters.py: Port implementations (InMemoryStorageAdapter, etc.)
  - mcp_server_2026.py: MCP server following skill2026.md

================================================================================
TESTING STRATEGY
================================================================================

- Unit tests: Domain logic (no mocks)
- Use case tests: Mocked ports
- Integration tests: Adapters with real dependencies
- MCP tests: Schema compliance + round-trip
- Orchestration tests: Parallel execution verification

Minimum coverage target: 80%

================================================================================
"""
