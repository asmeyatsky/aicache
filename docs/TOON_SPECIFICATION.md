# Token Optimization Object Notation (TOON) Specification

## Overview

**TOON (Token Optimization Object Notation)** is a structured notation system for capturing, analyzing, and optimizing token usage in AI caching operations. Every cache interaction generates a TOON object that provides comprehensive insights into:

- Token economics (savings, costs, ROI)
- Optimization effectiveness (hit rates, efficiency scores)
- Cache operation decisions (strategy, confidence, reasoning)
- Semantic matching analysis (similarity scores, thresholds)
- Actionable insights and recommendations

## Purpose

TOON solves the need for **transparent, auditable, and actionable token optimization data**. It bridges the gap between cache operations and business intelligence, enabling:

1. **Cost Accounting**: Track exact token savings per operation
2. **Performance Analysis**: Understand cache hit patterns and trends
3. **Optimization Insights**: Get recommendations for improving cache efficiency
4. **Audit Trail**: Maintain complete record of cache decisions
5. **ROI Calculation**: Measure return on investment from caching
6. **Semantic Analysis**: Understand how semantic matching impacts savings

## TOON Structure

Every TOON object contains six primary sections:

### 1. Operation Metadata
```json
{
  "operation_id": "uuid-v4-string",
  "timestamp": "2024-01-15T10:30:00Z",
  "operation_type": "exact_hit|semantic_hit|intent_hit|exact_miss|semantic_miss|cache_error",
  "strategy_used": "exact|semantic|intent|none",
  "duration_ms": 4.5
}
```

**Fields:**
- `operation_id`: Unique identifier for this cache operation
- `timestamp`: ISO8601 timestamp of operation
- `operation_type`: Type of operation performed
- `strategy_used`: Caching strategy that produced this result
- `duration_ms`: Milliseconds to complete operation

### 2. Query Information
```json
{
  "query": {
    "original": "What is machine learning?",
    "normalized": "what is machine learning",
    "hash": "sha256:abc123...",
    "embedding_dimension": 384,
    "intent": "definition_request",
    "semantic_tags": ["ml", "ai", "learning"]
  }
}
```

**Fields:**
- `original`: Exact user query
- `normalized`: Query after normalization for comparison
- `hash`: SHA256 hash for efficient caching
- `embedding_dimension`: Dimension of semantic embedding (if used)
- `intent`: Extracted semantic intent
- `semantic_tags`: Relevant semantic tags

### 3. Token Economics
```json
{
  "tokens": {
    "without_cache": {
      "prompt": 15,
      "completion": 0,
      "total": 15
    },
    "with_cache": {
      "prompt": 0,
      "completion": 0,
      "total": 0
    },
    "saved": {
      "prompt": 15,
      "completion": 0,
      "total": 15,
      "percent": 100.0
    },
    "costs": {
      "without_cache": 0.000225,
      "with_cache": 0.0,
      "saved": 0.000225
    },
    "model": "claude-3-opus"
  }
}
```

**Fields:**
- `without_cache.{prompt|completion|total}`: Tokens if cache miss
- `with_cache.{prompt|completion|total}`: Tokens with cache hit
- `saved.{prompt|completion|total}`: Token count saved
- `saved.percent`: Percentage of tokens saved (0-100)
- `costs`: Dollar amounts for each scenario
- `model`: AI model used for cost calculation

### 4. Semantic Match Data
```json
{
  "semantic_match": {
    "enabled": true,
    "similarity_score": 0.92,
    "confidence": 0.95,
    "matched_entry_key": "sha256:xyz789...",
    "semantic_distance": 0.08,
    "threshold_used": 0.85,
    "threshold_met": true
  }
}
```

**Fields:**
- `enabled`: Whether semantic matching was attempted
- `similarity_score`: Cosine similarity (0-1, where 1 is identical)
- `confidence`: Model's confidence in match (0-1)
- `matched_entry_key`: Cache entry that was matched
- `semantic_distance`: 1 - similarity_score (distance metric)
- `threshold_used`: Similarity threshold used for matching
- `threshold_met`: Whether similarity exceeded threshold

### 5. Cache Metadata
```json
{
  "cache_metadata": {
    "cache_key": "sha256:...",
    "cache_age_seconds": 3600,
    "ttl_remaining_seconds": 82800,
    "access_count": 5,
    "last_accessed": "2024-01-15T09:30:00Z",
    "created_at": "2024-01-15T06:30:00Z",
    "memory_size_bytes": 1024,
    "eviction_policy": "lru"
  }
}
```

**Fields:**
- `cache_key`: Key of matched cache entry
- `cache_age_seconds`: Seconds since cache entry created
- `ttl_remaining_seconds`: Seconds until expiration (null if no TTL)
- `access_count`: Number of times this entry accessed
- `last_accessed`: ISO8601 of most recent access
- `created_at`: ISO8601 of cache entry creation
- `memory_size_bytes`: Size of cached response
- `eviction_policy`: Policy used for cache eviction

### 6. Optimization Insights
```json
{
  "optimization_insights": {
    "optimization_level": "high|medium|low|critical|none",
    "roi_score": 0.85,
    "suggested_actions": [
      "increase_ttl_for_freshness",
      "similar_queries_found",
      "high_reuse_detected"
    ],
    "eviction_risk": "low|medium|high",
    "cache_efficiency_score": 1.0,
    "predictability_score": 0.7,
    "pattern_detected": false,
    "similar_queries_found": 0
  }
}
```

**Fields:**
- `optimization_level`: Effectiveness of optimization (critical/high/medium/low/none)
- `roi_score`: Return on investment score (0-1)
- `suggested_actions`: Recommended actions for improvement
- `eviction_risk`: Risk that entry will be evicted soon
- `cache_efficiency_score`: How efficient this cache hit was (0-1)
- `predictability_score`: Likelihood of future similar queries (0-1)
- `pattern_detected`: Whether query matches learned patterns
- `similar_queries_found`: Count of semantically similar queries in cache

## Operation Types

### Cache Hits
- **EXACT_HIT**: Cache entry found via exact key match (normalized)
- **SEMANTIC_HIT**: Cache entry found via semantic similarity matching
- **INTENT_HIT**: Cache entry found via intent-based matching

### Cache Misses
- **EXACT_MISS**: No exact cache entry found
- **SEMANTIC_MISS**: No semantic match within threshold
- **CACHE_ERROR**: Error during cache operation

## Optimization Levels

| Level | Token Savings | Meaning |
|-------|---------------|---------|
| CRITICAL | ≥80% | Exceptional savings, highly optimized |
| HIGH | 60-79% | Significant cost reduction |
| MEDIUM | 40-59% | Moderate improvement |
| LOW | 1-39% | Minor savings |
| NONE | 0% | No optimization (cache miss) |

## Caching Strategies

| Strategy | Description |
|----------|-------------|
| EXACT | Key-based lookup with normalization |
| SEMANTIC | Vector similarity matching |
| INTENT | Intent extraction and matching |
| NONE | Cache miss, full query execution |

## TOON Analytics

TOON provides aggregate analytics across multiple operations:

### Aggregate Metrics
```json
{
  "version": "1.0",
  "period": {
    "start": "2024-01-15T00:00:00Z",
    "end": "2024-01-15T23:59:59Z"
  },
  "operations": {
    "total": 1000,
    "exact_hits": 650,
    "semantic_hits": 250,
    "intent_hits": 50,
    "misses": 50,
    "hit_rate_percent": 95.0,
    "semantic_hit_rate_percent": 25.0
  },
  "tokens": {
    "total_saved": 45000,
    "average_savings_percent": 72.5
  },
  "costs": {
    "total_saved": 0.675
  },
  "insights": {
    "average_roi_score": 0.725,
    "cache_efficiency_trend": 0.05
  }
}
```

## Integration Points

### With Existing aicache Components

1. **QueryCacheUseCase**: Generates TOON after cache lookup
2. **SemanticCachingService**: Provides similarity scores
3. **TokenCountingService**: Calculates token savings
4. **CacheMetricsPort**: Records TOON statistics
5. **CacheEvictionService**: Tracks eviction risk

### Export Formats

TOON supports multiple export formats for integration:

- **JSON**: Full TOON with all metadata
- **JSONL**: One TOON per line (streaming)
- **CSV**: Compact tabular format
- **Binary**: msgpack format for efficient storage

## Usage Examples

### Inspecting a Single TOON

```bash
aicache toon inspect <operation_id>
```

Output:
```json
{
  "version": "1.0",
  "operation_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00Z",
  "operation_type": "semantic_hit",
  "tokens": {
    "saved": {
      "total": 15,
      "percent": 100.0
    },
    "costs": {
      "saved": 0.000225
    }
  },
  "optimization_insights": {
    "optimization_level": "high",
    "roi_score": 0.85
  }
}
```

### Viewing TOON Analytics

```bash
aicache toon analytics --period=1d
```

Output:
```
Cache Performance Analytics (Last 24 hours)
=========================================

Operations: 1,250 total
  Exact Hits: 812 (64.96%)
  Semantic Hits: 313 (25.04%)
  Intent Hits: 75 (6.0%)
  Misses: 50 (4.0%)

Token Savings:
  Total: 89,750 tokens
  Average: 71.8% per operation
  Total Cost: $1.348

Efficiency:
  ROI Score: 0.718
  Trend: +0.05 (improving)

Recommendations:
  - Semantic caching highly effective
  - Maintain current similarity threshold
  - Monitor cache staleness
```

### Exporting TOON Data

```bash
# Export last 100 TOONs as JSON
aicache toon export --format=json --limit=100 > toons.json

# Export as CSV for analysis
aicache toon export --format=csv > toons.csv

# Export analytics
aicache toon export-analytics --format=json > analytics.json
```

### Querying TOONs

```bash
# Get all semantic hits
aicache toon query --type=semantic_hit

# Get high-savings operations
aicache toon query --min-tokens=100

# Get operations from last hour
aicache toon query --since=1h

# Complex query
aicache toon query \
  --type=semantic_hit \
  --min-similarity=0.90 \
  --min-tokens=50 \
  --limit=50
```

## TOON Files Location

TOON data is stored in the following structure:

```
~/.cache/aicache/toon_data/
├── 00/
│   ├── 001234567890abcdef.json
│   └── ...
├── 01/
│   ├── 112345678901bcdef0.json
│   └── ...
└── ff/
    └── ffedcba9876543210.json
```

Files are organized by first 2 characters of operation ID for efficient retrieval.

## Benefits of TOON

1. **Financial Transparency**: Exact cost savings per operation
2. **Performance Tracking**: Monitor cache efficiency over time
3. **Decision Auditability**: Understand why each cache decision was made
4. **Trend Analysis**: Identify patterns and opportunities
5. **ROI Justification**: Prove value of caching investment
6. **Optimization Guidance**: Data-driven recommendations
7. **Debugging Aid**: Troubleshoot cache issues with complete context
8. **Analytics Integration**: Export for BI tools and dashboards

## Performance Impact

TOON generation is designed to be low-overhead:

- **Generation**: <1ms for typical TOON object
- **Storage**: ~2KB per TOON in JSON, ~400 bytes in msgpack
- **Serialization**: ~0.5ms for JSON, <0.1ms for msgpack
- **Query Speed**: <50ms for typical TOON queries

## Security Considerations

- TOON objects may contain sensitive query information
- Configure appropriate file permissions on TOON data directory
- Consider enabling encryption for sensitive deployments
- Regular purging of old TOON data recommended
- PII detection can be enabled to sanitize queries

## Future Enhancements

1. **Machine Learning Integration**: Use TOON data for predictive caching
2. **Distributed Analytics**: Aggregate TOON across multiple nodes
3. **Custom Metrics**: User-defined optimization metrics
4. **Visualization Dashboard**: Real-time TOON metrics visualization
5. **Alert Thresholds**: Alerts when efficiency drops below threshold
6. **Cost Budget**: Track against spending budgets
7. **Team Analytics**: Aggregate TOON across team members

## Implementation Status

- ✅ TOON domain models (immutable aggregates)
- ✅ TOON generation service
- ✅ TOON analytics aggregation
- ✅ File system persistence
- ✅ JSON/CSV/JSONL export
- ✅ Query builder for filtering
- 🚧 CLI commands (in progress)
- 🚧 Web dashboard (planned)
- 🚧 ML-based recommendations (planned)

## References

- See `src/aicache/domain/toon.py` for domain models
- See `src/aicache/domain/toon_service.py` for generation service
- See `src/aicache/infrastructure/toon_adapters.py` for persistence
- See `tests/test_toon.py` for comprehensive examples
