# Architectural Principles and Code Generation Standards for World-Class AI Caching Solutions

## Overview

This specification enforces strict architectural principles and code generation standards to ensure all code for AI caching solutions follows enterprise-grade patterns optimized for performance, scalability, reliability, and observability. This document extends the foundational architectural principles with AI caching-specific patterns.

## 🏗️ Four Core Architectural Principles (Extended)

### 1. Separation of Concerns (SoC) - AI Caching Variant
- **Principle**: Each module/component should have a single, well-defined responsibility
- **Implementation**:
  - Separate cache storage, eviction policies, TTL management, and query optimization layers
  - Use dependency injection to manage storage backends, serializers, and event publishers
  - Create focused, single-purpose classes for hashing, key generation, and cache invalidation
  - Avoid mixing concerns (e.g., compression logic in query layer, TTL logic in storage layer)

**AI-Specific Extensions**:
- **Semantic Cache Layer**: Separate embedding generation and semantic similarity matching from data retrieval
- **Query Normalization**: Isolate query parsing, normalization, and optimization logic
- **Token Management**: Create dedicated components for token counting, cost tracking, and budget enforcement
- **Cache Metrics**: Separate instrumentation from caching logic (hit rate, miss rate, eviction tracking)

### 2. Domain-Driven Design (DDD) - AI Caching Model
- **Principle**: Software design should reflect the caching domain
- **Implementation**:
  - Create rich domain models for cache entries, cache policies, and TTL strategies
  - Use ubiquitous language: "cache entry", "eviction policy", "semantic match", "token budget", "cache invalidation event"
  - Implement aggregates: CacheEntry (root), CachePolicy (root), QueryCache (root), SemanticCache (root)
  - Define bounded contexts: CacheManagement, QueryOptimization, CostTracking, IntelligenceIndexing

**AI-Caching Bounded Contexts**:
```
CacheManagement
├── Cache Entry Lifecycle
├── TTL and Expiration
└── Eviction Policies

QueryOptimization
├── Query Normalization
├── Semantic Matching
└── Hit Detection

CostTracking
├── Token Accounting
├── Budget Enforcement
└── ROI Calculation

IntelligenceIndexing
├── Embedding Generation
├── Vector Search
└── Similarity Computation

DataGovernance
├── Privacy Protection
├── Data Classification
└── Retention Policies
```

### 3. Clean/Hexagonal Architecture - AI Caching Edition
- **Principle**: Cache business logic should be independent of storage backends and AI frameworks
- **Implementation**:
  ```
  Domain Layer (Core)
  ├── CacheEntryAggregate
  ├── EvictionPolicyValueObject
  ├── SemanticSimilarityDomainService
  ├── QueryNormalizationService
  ├── TokenBudgetService
  ├── RepositoryPort
  ├── SemanticIndexPort
  ├── TokenCounterPort
  └── EventPublisherPort

  Application Layer
  ├── CreateCacheEntryUseCase
  ├── QueryCacheUseCase
  ├── InvalidateCacheUseCase
  ├── OptimizeQueryUseCase
  ├── TrackTokenUsageUseCase
  ├── PurgeExpiredEntriesUseCase
  ├── CalculateCacheMetricsUseCase
  ├── GetCacheInsightsUseCase
  └── CacheOperationDTOs

  Infrastructure Layer
  ├── StorageAdapters
  │   ├── RedisAdapter
  │   ├── PostgresAdapter
  │   ├── InMemoryAdapter
  │   └── MemcachedAdapter
  ├── SemanticIndexAdapters
  │   ├── PineconeAdapter
  │   ├── WeaviateAdapter
  │   ├── FaissAdapter
  │   └── ChromaAdapter
  ├── TokenCounterAdapters
  │   ├── OpenAITokenAdapter
  │   ├── AnthropicTokenAdapter
  │   └── TikTokenAdapter
  ├── EventPublisherAdapters
  │   ├── KafkaAdapter
  │   ├── RabbitMQAdapter
  │   └── PubSubAdapter
  └── ConfigurationManager

  Presentation/Integration Layer
  ├── REST API Controllers
  ├── GraphQL Resolvers
  ├── CLI Commands
  ├── Webhook Handlers
  └── Monitoring Endpoints
  ```

### 4. High Cohesion, Low Coupling - AI Caching Optimization
- **Principle**: Related functionality grouped together, minimal inter-module dependencies
- **Implementation**:
  - Group cache operations (read, write, invalidate) in single modules
  - Use interfaces to abstract storage and semantic backends
  - Minimize dependencies between query optimization and cost tracking
  - Favor composition: CacheEntry composed of metadata, value, policy, metrics

**AI-Specific Cohesion Groups**:
- **CacheOperations**: Read, write, delete, update operations
- **Eviction**: LRU, LFU, FIFO, custom policies
- **Semantics**: Embedding, similarity, threshold matching
- **Lifecycle**: TTL, expiration, refresh strategies
- **Observability**: Metrics, logging, tracing, alerting

## 🛡️ Nine Non-Negotiable Rules

### Rule 1: Zero Business Logic in Storage Adapters
```python
# ❌ WRONG - Cache logic in storage layer
class RedisAdapter:
    def get(self, key: str):
        value = self.redis.get(key)
        # Don't put TTL logic here!
        if self._is_expired(value):
            self.redis.delete(key)
        return value

# ✅ CORRECT - Logic in domain/application layer
class RedisAdapter(StoragePort):
    def get(self, key: str) -> Optional[bytes]:
        return self.redis.get(key)

    def delete(self, key: str) -> bool:
        return bool(self.redis.delete(key))

class QueryCacheUseCase:
    def execute(self, query: str) -> CacheResult:
        entry = self.repository.get(key)
        if entry and not self._is_expired(entry):
            return CacheResult.hit(entry.value)
        return CacheResult.miss()
```

### Rule 2: Semantic Matching Must Be Abstracted Behind Ports
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class SemanticMatch:
    similarity_score: float
    matched_entry_key: str
    confidence: float

class SemanticIndexPort(ABC):
    @abstractmethod
    async def index_query(self, query_id: str, embedding: List[float]) -> None:
        """Index a query embedding"""
        pass

    @abstractmethod
    async def find_similar(self, embedding: List[float],
                          threshold: float = 0.85) -> List[SemanticMatch]:
        """Find semantically similar cached queries"""
        pass

# Adapters
class PineconeSemanticIndexAdapter(SemanticIndexPort):
    async def find_similar(self, embedding: List[float],
                          threshold: float = 0.85) -> List[SemanticMatch]:
        # Pinecone-specific implementation
        pass

class FaissSemanticIndexAdapter(SemanticIndexPort):
    async def find_similar(self, embedding: List[float],
                          threshold: float = 0.85) -> List[SemanticMatch]:
        # Local FAISS implementation
        pass
```

### Rule 3: Token Counting Must Be Model-Agnostic
```python
from abc import ABC, abstractmethod

class TokenCounterPort(ABC):
    @abstractmethod
    def count_prompt_tokens(self, text: str) -> int:
        pass

    @abstractmethod
    def count_completion_tokens(self, text: str) -> int:
        pass

    @abstractmethod
    def estimate_cost(self, model: str, tokens: int, type: str) -> float:
        pass

class OpenAITokenAdapter(TokenCounterPort):
    def count_prompt_tokens(self, text: str) -> int:
        # Use tiktoken for OpenAI models
        pass

class AnthropicTokenAdapter(TokenCounterPort):
    def count_prompt_tokens(self, text: str) -> int:
        # Use Anthropic's token counter
        pass

class TokenCountingDomainService:
    def __init__(self, counter: TokenCounterPort):
        self.counter = counter

    def calculate_savings(self, cache_hit: bool, model: str,
                         tokens_without_cache: int) -> float:
        if cache_hit:
            return self.counter.estimate_cost(model, tokens_without_cache, "prompt")
        return 0.0
```

### Rule 4: Cache Invalidation Must Be Explicit and Traceable
```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class InvalidationStrategy(Enum):
    IMMEDIATE = "immediate"
    DELAYED = "delayed"
    CONDITIONAL = "conditional"

@dataclass(frozen=True)
class CacheInvalidationEvent:
    cache_key: str
    reason: str
    triggered_by: str
    timestamp: datetime
    strategy: InvalidationStrategy
    affected_entries: int = 0

class CacheInvalidationDomainService:
    def __init__(self, event_publisher: EventPublisherPort):
        self.event_publisher = event_publisher

    async def invalidate_semantic_neighbors(self, query: str,
                                           threshold: float = 0.75) -> int:
        """Invalidate all semantically similar cache entries"""
        similar = await self.semantic_index.find_similar(query, threshold)
        invalidated = 0

        for match in similar:
            await self.repository.delete(match.matched_entry_key)
            invalidated += 1

        event = CacheInvalidationEvent(
            cache_key=query,
            reason="semantic_invalidation",
            triggered_by="cache_service",
            timestamp=datetime.now(),
            strategy=InvalidationStrategy.IMMEDIATE,
            affected_entries=invalidated
        )
        await self.event_publisher.publish(event)

        return invalidated
```

### Rule 5: Immutable Cache Entries
```python
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from typing import Optional

@dataclass(frozen=True)
class CacheEntry:
    """Immutable cache entry aggregate root"""
    key: str
    value: bytes
    embedding: Optional[List[float]]
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed_at: Optional[datetime] = None
    ttl_seconds: Optional[int] = None
    metadata: dict = None

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now() >= self.expires_at

    def touch(self) -> 'CacheEntry':
        """Record access without mutation"""
        return replace(
            self,
            access_count=self.access_count + 1,
            last_accessed_at=datetime.now()
        )

    def refresh_ttl(self) -> 'CacheEntry':
        """Refresh expiration time"""
        if self.ttl_seconds is None:
            return self
        return replace(
            self,
            expires_at=datetime.now() + timedelta(seconds=self.ttl_seconds)
        )
```

### Rule 6: Comprehensive Cache Metrics and Observability
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class CacheMetrics:
    total_hits: int
    total_misses: int
    total_evictions: int
    average_response_time_ms: float
    total_tokens_saved: int
    total_cost_saved: float
    hit_rate: float
    memory_usage_bytes: int
    semantic_matches: int
    false_positives: int

class CacheMetricsPort(ABC):
    @abstractmethod
    def record_hit(self, entry_key: str, response_time_ms: float,
                  tokens_saved: int, cost_saved: float) -> None:
        pass

    @abstractmethod
    def record_miss(self, query: str, reason: str) -> None:
        pass

    @abstractmethod
    def record_eviction(self, entry_key: str, policy: str) -> None:
        pass

    @abstractmethod
    def get_metrics(self) -> CacheMetrics:
        pass

class CacheMetricsDomainService:
    def __init__(self, metrics_port: CacheMetricsPort):
        self.metrics_port = metrics_port

    def calculate_roi(self) -> float:
        """Return on investment calculation"""
        metrics = self.metrics_port.get_metrics()
        if metrics.total_hits + metrics.total_misses == 0:
            return 0.0
        return metrics.total_cost_saved / (metrics.total_hits + metrics.total_misses)
```

### Rule 7: Query Normalization Must Preserve Semantics
```python
from abc import ABC, abstractmethod

class QueryNormalizerPort(ABC):
    @abstractmethod
    def normalize(self, query: str) -> str:
        """Normalize query for comparison without losing meaning"""
        pass

    @abstractmethod
    def extract_intent(self, query: str) -> str:
        """Extract core intent from query"""
        pass

class QueryNormalizationDomainService:
    def __init__(self, normalizer: QueryNormalizerPort):
        self.normalizer = normalizer

    def should_use_cached_response(self, query: str,
                                  cached_entry: CacheEntry,
                                  similarity_threshold: float = 0.85) -> bool:
        """Decide if cached entry applies to new query"""
        # Exact match after normalization
        if self.normalizer.normalize(query) == cached_entry.normalized_query:
            return True

        # Intent-based matching
        if self.normalizer.extract_intent(query) == cached_entry.intent:
            # Use semantic similarity as tiebreaker
            return True

        return False
```

### Rule 8: Enforce TTL and Eviction Policies at Domain Level
```python
from enum import Enum
from typing import Callable

class EvictionPolicy(Enum):
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    CUSTOM = "custom"

@dataclass(frozen=True)
class CachePolicy:
    """Domain value object for cache policy"""
    max_size_bytes: int
    default_ttl_seconds: Optional[int]
    eviction_policy: EvictionPolicy
    semantic_match_threshold: float = 0.85
    enable_compression: bool = True
    enable_semantic_caching: bool = True

    def validate(self) -> bool:
        return (
            self.max_size_bytes > 0 and
            self.semantic_match_threshold > 0 and
            self.semantic_match_threshold <= 1.0
        )

class CacheEvictionDomainService:
    def __init__(self, policy: CachePolicy):
        self.policy = policy

    async def evict_if_necessary(self, current_size: int,
                                new_entry_size: int) -> List[str]:
        """Evict entries based on policy if cache is full"""
        if current_size + new_entry_size <= self.policy.max_size_bytes:
            return []

        if self.policy.eviction_policy == EvictionPolicy.LRU:
            return await self._evict_lru(current_size, new_entry_size)
        elif self.policy.eviction_policy == EvictionPolicy.LFU:
            return await self._evict_lfu(current_size, new_entry_size)
        # ... other policies
```

### Rule 9: Document Cache Architecture and Trade-offs
```python
"""
AI Query Cache Module

Architectural Intent:
- Provide transparent caching layer for AI queries
- Support both exact-match and semantic-similarity matching
- Track token usage and cost savings automatically
- Enable progressive transparency of cache decisions

Design Decisions:
1. Immutable cache entries prevent accidental corruption
2. Semantic matching is abstracted for multi-backend support
3. All cache decisions are logged for auditability
4. TTL enforcement happens at query time (lazy expiration)
5. Cost tracking integrates with token counting abstraction

Performance Characteristics:
- Exact match lookups: O(1) with hash-based storage
- Semantic matches: O(log n) with vector indexing
- Memory: Configurable with LRU/LFU policies
- Latency: <5ms for cache hits (99th percentile)

Known Limitations:
- Semantic matching quality depends on embedding model
- Distributed caching requires eventual consistency handling
- Context window changes can invalidate cached responses

Trade-offs Made:
- Favored hit rate over perfect invalidation
- Semantic caching adds latency for cache misses
- Full immutability requires more memory
"""
```

## 📋 AI Caching Implementation Checklist

When generating AI caching code, verify:

### Architecture Verification
- [ ] Domain layer has NO dependencies on storage backends
- [ ] Semantic index is abstracted behind port interface
- [ ] Token counter is model-agnostic
- [ ] All cache decisions are traceable via events
- [ ] Application layer orchestrates domain objects

### Cache Design
- [ ] Cache entries are immutable aggregates
- [ ] TTL and expiration are domain concepts
- [ ] Eviction policies follow domain service pattern
- [ ] Query normalization preserves semantic meaning
- [ ] Invalidation strategies are explicit

### Semantic Caching
- [ ] Embeddings are computed once and reused
- [ ] Similarity threshold is configurable
- [ ] False positive handling is implemented
- [ ] Embedding model is abstracted
- [ ] Semantic cache metrics are tracked separately

### Cost Tracking
- [ ] Token counting is model-agnostic
- [ ] Cost savings are calculated on cache hit
- [ ] Budget enforcement prevents overspend
- [ ] Token usage is auditable
- [ ] ROI metrics are available

### Observability
- [ ] Cache hit/miss rates are tracked
- [ ] Eviction events are logged
- [ ] Query normalization decisions are recorded
- [ ] Semantic similarity scores are captured
- [ ] Cost savings are attributed to cache source

### Testing Requirements
- [ ] Unit tests for immutable cache entries
- [ ] Domain service tests with mocked adapters
- [ ] Integration tests for storage adapters
- [ ] Semantic matching tests with known embeddings
- [ ] Token counting validation per model
- [ ] End-to-end cache flow tests
- [ ] Minimum 85% code coverage

## 🎯 Advanced AI Caching Patterns

### Semantic Cache with Confidence Scoring
```python
@dataclass(frozen=True)
class SemanticCacheResult:
    cache_hit: bool
    similarity_score: Optional[float]
    confidence: float  # Model's confidence in similarity
    value: Optional[bytes] = None
    original_entry_key: Optional[str] = None

class SemanticCacheDomainService:
    async def find_applicable_cache(self, query: str,
                                   embeddings: List[float],
                                   min_similarity: float = 0.85) -> SemanticCacheResult:
        """Find cache entry with confidence scoring"""
        matches = await self.semantic_index.find_similar(embeddings, min_similarity)

        if not matches:
            return SemanticCacheResult(cache_hit=False, confidence=0.0)

        best_match = matches[0]
        # Higher similarity = higher confidence
        confidence = best_match.similarity_score

        return SemanticCacheResult(
            cache_hit=True,
            similarity_score=best_match.similarity_score,
            confidence=confidence,
            value=await self.repository.get(best_match.matched_entry_key),
            original_entry_key=best_match.matched_entry_key
        )
```

### Progressive Cache Warming
```python
class CacheWarmingDomainService:
    async def warm_cache_async(self, common_queries: List[str]) -> int:
        """Asynchronously pre-cache common queries"""
        warmed = 0
        for query in common_queries:
            try:
                # Execute and cache without blocking
                await self.query_cache_use_case.execute(query)
                warmed += 1
            except Exception as e:
                self.logger.warning(f"Failed to warm cache for query: {e}")
        return warmed
```

### Cache Cascade with Fallback Strategies
```python
class CascadedCacheQueryUseCase:
    async def execute(self, query: str) -> CacheResult:
        """Try multiple cache strategies in order"""
        # Strategy 1: Exact match with normalization
        exact_match = await self.exact_cache.query(query)
        if exact_match.hit:
            return exact_match

        # Strategy 2: Semantic similarity
        semantic_match = await self.semantic_cache.query(query)
        if semantic_match.hit and semantic_match.confidence > 0.90:
            return semantic_match

        # Strategy 3: Intent-based matching
        intent_match = await self.intent_cache.query(query)
        if intent_match.hit:
            return intent_match

        # Miss - execute query and cache
        return await self.miss_handling_use_case.execute(query)
```

### Distributed Cache Consistency
```python
@dataclass(frozen=True)
class CacheInvalidationBroadcast:
    cache_key: str
    version: int
    timestamp: datetime
    originating_node: str

class DistributedCacheConsistencyPort(ABC):
    @abstractmethod
    async def broadcast_invalidation(self, event: CacheInvalidationBroadcast) -> None:
        pass

    @abstractmethod
    async def resolve_conflict(self, local_version: int,
                              remote_version: int) -> int:
        pass

class DistributedCacheDomainService:
    async def invalidate_across_cluster(self, cache_key: str) -> None:
        """Propagate invalidation to all cache nodes"""
        broadcast = CacheInvalidationBroadcast(
            cache_key=cache_key,
            version=self._get_next_version(),
            timestamp=datetime.now(),
            originating_node=self.node_id
        )
        await self.consistency_port.broadcast_invalidation(broadcast)
```

## 🏆 Performance Targets

For enterprise-grade AI caching:
- **Cache Hit Response Latency**: < 5ms (p99)
- **Cache Miss + Semantic Lookup**: < 100ms (p99)
- **Semantic Similarity Computation**: < 50ms for 1000 cached queries
- **TTL Enforcement Overhead**: < 1% of query time
- **Token Counting Overhead**: < 2ms per query
- **Memory Efficiency**: 2-5x reduction in token usage through caching
- **Cost Reduction**: 30-70% reduction in AI service costs

## 🚀 Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│           Application Layer                          │
│  ┌──────────────────────────────────────────────┐  │
│  │  REST API | GraphQL | SDK | CLI              │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│      Application Services (Use Cases)               │
│  ┌──────────────────────────────────────────────┐  │
│  │ QueryCacheUseCase | InvalidateUseCase | ... │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│    Domain Services (Business Logic)                 │
│  ┌──────────────────────────────────────────────┐  │
│  │ SemanticCache | Eviction | TokenCounting     │  │
│  │ QueryNormalization | Invalidation           │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┼────────────┬───────────┐
        │            │            │           │
   ┌────▼───┐  ┌─────▼──┐  ┌─────▼───┐  ┌───▼────┐
   │ Storage│  │Semantic│  │  Token  │  │ Event  │
   │ Ports  │  │ Index  │  │Counter  │  │Publish │
   │ Ports  │  │ Ports  │  │ Ports   │  │ Ports  │
   └────┬───┘  └─────┬──┘  └─────┬───┘  └───┬────┘
        │            │            │           │
   ┌────▼───────┬────▼────┬───────▼───┬──────▼────┐
   │  Redis     │ Pinecone│ OpenAI    │  Kafka    │
   │  Postgres  │ Weaviate│ Anthropic │  RabbitMQ │
   │  DynamoDB  │ Faiss   │ TikToken  │  PubSub   │
   └────────────┴─────────┴───────────┴───────────┘
```

## 📚 AI Caching Principles Summary

1. **Immutability**: Cache entries never change in place
2. **Abstraction**: All integrations behind port interfaces
3. **Traceability**: Every cache decision is logged/published
4. **Composability**: Domain services combine via use cases
5. **Observability**: Metrics capture all cache dynamics
6. **Semantics**: Preserve meaning through normalization
7. **Economics**: Track cost savings automatically
8. **Resilience**: Graceful degradation on failures
9. **Scalability**: Distributed by design

## ⚠️ Critical Anti-Patterns in AI Caching

1. **Silent Cache Failures**: Not logging cache misses/invalidations
2. **Semantic Leakage**: Assuming different phrasings are identical
3. **Memory Bloat**: Unbounded cache growth without eviction
4. **Token Miscounting**: Using different counters for different models
5. **Stale Context**: Not refreshing TTLs when context changes
6. **Cost Opacity**: Not tracking savings from cache hits
7. **Embedding Drift**: Not updating embeddings as models change
8. **Invalidation Amnesia**: Cache staying active after upstream changes
9. **Distributed Chaos**: No consistency protocol for multi-node caches

## 🎖️ Enterprise-Grade AI Cache Certification

Code generated with this specification must:
1. Pass architectural fitness functions for clean layers
2. Maintain immutable domain models throughout
3. Achieve 85%+ test coverage with semantic matching tests
4. Trace every cache decision with events
5. Support multiple storage backends without code changes
6. Provide metrics on hit rate, cost savings, and semantic quality
7. Handle distributed invalidation correctly
8. Document all architectural trade-offs
9. Implement graceful degradation on adapter failures
10. Enable observability at every layer

---

**Version**: 1.0
**Date**: 2025-10-29
**Status**: Production Ready
**Scope**: World-class AI caching solutions

This specification defines enterprise-grade standards for building AI caching solutions that are performant, scalable, observable, and maintainable.
