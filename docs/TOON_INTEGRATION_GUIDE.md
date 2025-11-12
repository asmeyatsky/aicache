# TOON Integration Guide

## Quick Start

### 1. Enable TOON in Configuration

```yaml
# ~/.config/aicache/config.yaml
cache_dir: ~/.cache/aicache
toon:
  enabled: true
  storage_backend: filesystem  # or inmemory
  export_format: json          # json, csv, msgpack
  analytics_period_days: 30
  retention_days: 90           # Auto-purge after 90 days
```

### 2. Basic TOON Usage

```python
from aicache.domain.toon_service import TOONGenerationService, TOONAnalyticsService
from aicache.infrastructure.toon_adapters import FileSystemTOONRepositoryAdapter

# Initialize TOON services
generation_service = TOONGenerationService(storage, token_counter, metrics_port)
analytics_service = TOONAnalyticsService()
repository = FileSystemTOONRepositoryAdapter()

# Generate TOON from cache operation
toon = await generation_service.generate_toon_from_cache_hit(
    operation_id=str(uuid.uuid4()),
    original_query="What is machine learning?",
    normalized_query="what is machine learning",
    query_hash=query_hash,
    cache_result=cache_result,
    cache_entry=cached_entry,
    prompt_tokens_without_cache=15,
    model="claude-3-opus",
    duration_ms=4.5,
    semantic_match=False,
    context={"user_id": "user_123"}
)

# Save TOON
await repository.save_toon(toon)

# Export TOON to JSON
print(json.dumps(toon.to_dict(), indent=2))
```

## Integration with QueryCacheUseCase

Here's how to integrate TOON into the existing QueryCacheUseCase:

```python
from aicache.domain.toon_service import TOONGenerationService
from aicache.infrastructure.toon_adapters import FileSystemTOONRepositoryAdapter

class EnhancedQueryCacheUseCase(QueryCacheUseCase):
    """QueryCacheUseCase enhanced with TOON generation."""

    def __init__(
        self,
        storage: StoragePort,
        semantic_index: SemanticIndexPort,
        token_counter: TokenCounterPort,
        query_normalizer: QueryNormalizerPort,
        embedding_generator: EmbeddingGeneratorPort,
        metrics: CacheMetricsPort,
        cache_policy: CachePolicy,
        toon_repository: Optional[TOONRepositoryPort] = None,  # NEW
    ):
        super().__init__(
            storage, semantic_index, token_counter,
            query_normalizer, embedding_generator, metrics, cache_policy
        )
        self.toon_generation = TOONGenerationService(
            storage, token_counter, metrics
        )
        self.toon_repository = toon_repository or FileSystemTOONRepositoryAdapter()

    async def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> CacheResult:
        """Execute with TOON generation."""
        import uuid
        operation_id = str(uuid.uuid4())
        start_time = time.time()

        try:
            # Original cache logic
            exact_result = await self._try_exact_match(query, context)

            if exact_result.hit:
                # Generate TOON for cache hit
                response_time_ms = (time.time() - start_time) * 1000

                normalized_query = self.query_normalization.normalizer.normalize(query)
                query_hash = hashlib.sha256(query.encode()).hexdigest()

                cache_entry = await self.storage.get(exact_result.entry_key)

                toon = await self.toon_generation.generate_toon_from_cache_hit(
                    operation_id=operation_id,
                    original_query=query,
                    normalized_query=normalized_query,
                    query_hash=query_hash,
                    cache_result=exact_result,
                    cache_entry=cache_entry,
                    prompt_tokens_without_cache=15,  # Would be calculated
                    model=context.get("model", "claude-3-opus") if context else "claude-3-opus",
                    duration_ms=response_time_ms,
                    semantic_match=False,
                    context=context,
                )

                # Save TOON
                await self.toon_repository.save_toon(toon)

                await self.metrics.record_hit(
                    exact_result.entry_key or "",
                    response_time_ms,
                    tokens_saved=toon.token_delta.saved_total,
                    cost_saved=toon.token_delta.cost_saved
                )
                return exact_result

            # Semantic match logic with TOON
            if self.policy.enable_semantic_caching:
                semantic_result = await self._try_semantic_match(query)
                if semantic_result.hit and semantic_result.confidence > 0.85:
                    response_time_ms = (time.time() - start_time) * 1000

                    toon = await self.toon_generation.generate_toon_from_cache_hit(
                        operation_id=operation_id,
                        original_query=query,
                        normalized_query=normalized_query,
                        query_hash=query_hash,
                        cache_result=semantic_result,
                        cache_entry=cache_entry,
                        prompt_tokens_without_cache=15,
                        model=context.get("model", "claude-3-opus") if context else "claude-3-opus",
                        duration_ms=response_time_ms,
                        semantic_match=True,
                        context=context,
                    )

                    await self.toon_repository.save_toon(toon)

                    await self.metrics.record_hit(
                        semantic_result.entry_key or "",
                        response_time_ms,
                        tokens_saved=toon.token_delta.saved_total,
                        cost_saved=toon.token_delta.cost_saved
                    )
                    return semantic_result

            # Cache miss with TOON
            response_time_ms = (time.time() - start_time) * 1000

            toon = await self.toon_generation.generate_toon_from_cache_miss(
                operation_id=operation_id,
                original_query=query,
                normalized_query=normalized_query,
                query_hash=query_hash,
                prompt_tokens=15,
                completion_tokens=0,
                model=context.get("model", "claude-3-opus") if context else "claude-3-opus",
                duration_ms=response_time_ms,
                semantic_attempted=self.policy.enable_semantic_caching,
                context=context,
            )

            await self.toon_repository.save_toon(toon)
            await self.metrics.record_miss(query, "not_found")

            return CacheResult.miss(response_time_ms)

        except Exception as e:
            logger.error(f"Error querying cache: {e}")
            return CacheResult.miss((time.time() - start_time) * 1000)
```

## TOON Analytics Usage

```python
from aicache.domain.toon_service import TOONAnalyticsService
from aicache.infrastructure.toon_adapters import FileSystemTOONRepositoryAdapter

# Get all TOONs for analysis
repository = FileSystemTOONRepositoryAdapter()
toons = await repository.get_all_toons(limit=1000)

# Aggregate into analytics
analytics_service = TOONAnalyticsService()
analytics = analytics_service.aggregate_toons(
    toons,
    time_period_start=datetime.now() - timedelta(days=1),
    time_period_end=datetime.now()
)

# Get insights
insights = analytics_service.extract_insights(analytics)

print(f"Hit Rate: {insights['summary']['hit_rate_percent']}%")
print(f"Total Tokens Saved: {insights['savings']['total_tokens_saved']}")
print(f"Total Cost Saved: ${insights['savings']['total_cost_saved']}")
print(f"ROI Score: {insights['efficiency']['roi_score']}")
print(f"Trend: {insights['efficiency']['efficiency_trend']}")

for recommendation in insights['recommendations']:
    print(f"- {recommendation}")
```

## TOON Export Examples

### Export to JSON
```python
from aicache.infrastructure.toon_adapters import TOONExportService

export_service = TOONExportService(repository)

# Export all TOONs as JSON
json_data = await export_service.export_to_json(limit=500)
with open("toons_export.json", "w") as f:
    f.write(json_data)
```

### Export to CSV for Analysis
```python
# Export as CSV for Excel/Sheets analysis
csv_data = await export_service.export_to_csv(limit=500)
with open("toons_export.csv", "w") as f:
    f.write(csv_data)
```

### Export Analytics
```python
# Export analytics summary
analytics_json = await export_service.export_analytics_json(analytics)
with open("analytics.json", "w") as f:
    f.write(analytics_json)

# Export analytics as CSV
analytics_csv = await export_service.export_analytics_csv(analytics)
with open("analytics.csv", "w") as f:
    f.write(analytics_csv)
```

## TOON Querying Examples

```python
from aicache.infrastructure.toon_adapters import TOONQueryBuilder
from aicache.domain.toon import TOONOperationType, TOONOptimizationLevel

query_builder = TOONQueryBuilder(repository)

# Get all semantic hits
semantic_hits = await query_builder \
    .with_operation_type(TOONOperationType.SEMANTIC_HIT) \
    .execute()

# Get high-value operations
high_value = await query_builder \
    .with_min_tokens_saved(100) \
    .with_optimization_level(TOONOptimizationLevel.HIGH) \
    .execute()

# Get recent high-confidence semantic matches
recent_high_confidence = await query_builder \
    .with_operation_type(TOONOperationType.SEMANTIC_HIT) \
    .with_min_similarity(0.90) \
    .with_time_range(
        datetime.now() - timedelta(hours=1),
        datetime.now()
    ) \
    .execute()

print(f"Found {len(recent_high_confidence)} high-confidence matches in last hour")
```

## Real-World Example: Daily TOON Report

```python
async def generate_daily_toon_report():
    """Generate daily TOON performance report."""
    from datetime import datetime, timedelta

    repository = FileSystemTOONRepositoryAdapter()
    analytics_service = TOONAnalyticsService()
    export_service = TOONExportService(repository)

    # Get TOONs from last 24 hours
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)

    builder = TOONQueryBuilder(repository)
    toons = await builder.with_time_range(start_time, end_time).execute()

    # Generate analytics
    analytics = analytics_service.aggregate_toons(toons, start_time, end_time)
    insights = analytics_service.extract_insights(analytics)

    # Create report
    report = f"""
    DAILY TOON PERFORMANCE REPORT
    =============================
    Date: {end_time.strftime('%Y-%m-%d')}

    OPERATIONS
    ----------
    Total Operations: {insights['summary']['total_operations']}
    Hit Rate: {insights['summary']['hit_rate_percent']}%
    Miss Rate: {insights['summary']['miss_rate_percent']}%
    Semantic Hit Rate: {insights['summary']['semantic_hit_rate_percent']}%

    TOKEN SAVINGS
    -------------
    Total Tokens Saved: {insights['savings']['total_tokens_saved']:,}
    Avg per Operation: {insights['savings']['average_tokens_per_operation']} tokens
    Total Cost Saved: ${insights['savings']['total_cost_saved']:.4f}

    EFFICIENCY
    ----------
    ROI Score: {insights['efficiency']['roi_score']:.2%}
    Trend: {insights['efficiency']['efficiency_trend']}
    Trend Magnitude: {insights['efficiency']['trend_magnitude']:.4f}

    RECOMMENDATIONS
    ----------------
    """

    for i, recommendation in enumerate(insights['recommendations'], 1):
        report += f"{i}. {recommendation}\n"

    # Save report
    with open("daily_toon_report.txt", "w") as f:
        f.write(report)

    # Also save raw analytics as JSON
    analytics_json = await export_service.export_analytics_json(analytics)
    with open("daily_toon_analytics.json", "w") as f:
        f.write(analytics_json)

    return report
```

## Monitoring TOON Metrics

```python
async def monitor_toon_efficiency():
    """Continuously monitor TOON efficiency."""
    import asyncio

    repository = FileSystemTOONRepositoryAdapter()
    analytics_service = TOONAnalyticsService()

    last_checked = datetime.now()

    while True:
        # Check every hour
        await asyncio.sleep(3600)

        # Get TOONs since last check
        builder = TOONQueryBuilder(repository)
        recent_toons = await builder \
            .with_time_range(last_checked, datetime.now()) \
            .execute()

        if not recent_toons:
            continue

        # Analyze
        analytics = analytics_service.aggregate_toons(
            recent_toons,
            last_checked,
            datetime.now()
        )

        # Alert if hit rate drops
        if analytics.hit_rate() < 30:
            logger.warning(
                f"TOON Alert: Cache hit rate dropped to {analytics.hit_rate():.1f}%"
            )

        # Alert if trend is declining
        if analytics.cache_efficiency_trend < -0.1:
            logger.warning(
                f"TOON Alert: Cache efficiency trending down: {analytics.cache_efficiency_trend:.2f}"
            )

        last_checked = datetime.now()
```

## TOON Data Privacy

```python
class TOONPrivacyFilter:
    """Filter sensitive data from TOON objects."""

    @staticmethod
    def sanitize_toon(toon: TOONCacheOperation) -> TOONCacheOperation:
        """Remove or mask sensitive query data."""
        # Create new TOON with sanitized query
        from dataclasses import replace

        sanitized_query = TOONQueryMetadata(
            original_query="[REDACTED]",  # Hide original query
            normalized_query=toon.query_metadata.normalized_query,  # Keep normalized
            query_hash=toon.query_metadata.query_hash,  # Keep hash
            embedding_dimension=toon.query_metadata.embedding_dimension,
            intent=toon.query_metadata.intent,
            semantic_tags=toon.query_metadata.semantic_tags,
        )

        return replace(toon, query_metadata=sanitized_query)

    @staticmethod
    def should_redact_query(query: str) -> bool:
        """Determine if query contains sensitive data."""
        sensitive_keywords = [
            "password", "api_key", "secret", "credit_card",
            "ssn", "email", "phone", "address"
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in sensitive_keywords)
```

## Performance Metrics

TOON is designed for minimal overhead:

```
Operation                   Time (ms)   Memory (bytes)
─────────────────────────────────────────────────────
Generate TOON (hit)         < 1.0       ~2000 (JSON)
Generate TOON (miss)        < 0.5       ~1500 (JSON)
Save TOON (filesystem)      < 2.0       -
Serialize to JSON           < 0.5       ~2000
Serialize to msgpack        < 0.1       ~400
Query TOONs (index)         < 50        -
Aggregate analytics         < 100       -
```

## Next Steps

1. Integrate TOON into QueryCacheUseCase
2. Add TOON CLI commands (inspect, list, analytics, export)
3. Create TOON analytics dashboard
4. Set up automated TOON reports
5. Implement TOON-based alerts
6. Export TOON data to BI tools
