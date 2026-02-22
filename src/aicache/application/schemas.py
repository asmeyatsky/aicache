"""
Structured Output Schemas - AI-Native Patterns (2026)

This module defines Pydantic schemas for AI-generated structured data.
Following skill2026.md: Always define explicit schemas for AI output.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum


class CacheTier(str, Enum):
    """Cache tier levels."""

    HOT = "hot"  # Frequently accessed
    WARM = "warm"  # Occasionally accessed
    COLD = "cold"  # Rarely accessed


class CacheHitType(str, Enum):
    """Type of cache hit."""

    EXACT = "exact"  # Exact match
    SEMANTIC = "semantic"  # Semantic similarity match
    PREFIX = "prefix"  # Prompt prefix match (2026)
    CONTEXT = "context"  # Context reuse (2026)


class CacheAnalysis(BaseModel):
    """
    Schema for AI-generated cache analysis.

    Used as structured output for analyzing cache patterns.
    """

    cache_efficiency_score: float = Field(
        ge=0.0, le=1.0, description="Overall cache efficiency from 0-1"
    )
    hit_rate_prediction: float = Field(
        ge=0.0, le=1.0, description="Predicted hit rate for similar queries"
    )
    recommended_ttl_seconds: int = Field(
        ge=0, description="Recommended TTL based on query patterns"
    )
    suggested_optimizations: List[str] = Field(
        default_factory=list, description="List of optimization suggestions"
    )
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in the analysis")


class CacheEntryMetadata(BaseModel):
    """
    Detailed metadata for a cache entry.
    """

    entry_key: str = Field(description="Unique cache entry identifier")
    created_at: datetime = Field(description="When entry was created")
    last_accessed: Optional[datetime] = Field(
        default=None, description="Last access time"
    )
    access_count: int = Field(ge=0, description="Number of times accessed")
    tier: CacheTier = Field(description="Current cache tier")
    size_bytes: int = Field(ge=0, description="Size in bytes")
    expires_at: Optional[datetime] = Field(default=None, description="Expiration time")
    is_expired: bool = Field(description="Whether entry has expired")
    embedding_available: bool = Field(description="If semantic embedding exists")


class CacheHealthReport(BaseModel):
    """
    Health report for cache system.
    """

    status: Literal["healthy", "degraded", "critical"] = Field(
        description="Overall health status"
    )
    hit_rate: float = Field(ge=0.0, le=1.0, description="Current hit rate")
    avg_response_time_ms: float = Field(ge=0.0, description="Average response time")
    memory_usage_percent: float = Field(
        ge=0.0, le=100.0, description="Memory usage percentage"
    )
    issues: List[str] = Field(
        default_factory=list, description="List of identified issues"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="List of recommendations"
    )


class CacheQueryRequest(BaseModel):
    """
    Structured request for cache query.
    """

    query: str = Field(description="The query to look up")
    context: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional context dictionary"
    )
    enable_semantic: bool = Field(default=True, description="Enable semantic matching")
    threshold: float = Field(
        ge=0.0,
        le=1.0,
        default=0.85,
        description="Similarity threshold for semantic match",
    )


class CacheQueryResponse(BaseModel):
    """
    Structured response for cache query.
    """

    hit: bool = Field(description="Whether cache hit occurred")
    hit_type: Optional[CacheHitType] = Field(
        default=None, description="Type of hit if applicable"
    )
    value: Optional[str] = Field(default=None, description="Cached response value")
    confidence: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="Confidence in semantic match"
    )
    cache_key: Optional[str] = Field(default=None, description="Cache key used")
    latency_ms: float = Field(ge=0.0, description="Query latency in ms")
    tokens_saved: Optional[int] = Field(
        default=None, ge=0, description="Tokens saved from cache"
    )
    cost_saved: Optional[float] = Field(
        default=None, ge=0.0, description="Cost saved from cache"
    )


class CacheStatsReport(BaseModel):
    """
    Comprehensive cache statistics report.
    """

    period_start: datetime = Field(description="Report period start")
    period_end: datetime = Field(description="Report period end")

    total_requests: int = Field(ge=0, description="Total cache requests")
    total_hits: int = Field(ge=0, description="Total cache hits")
    total_misses: int = Field(ge=0, description="Total cache misses")
    hit_rate: float = Field(ge=0.0, le=1.0, description="Hit rate percentage")

    exact_hits: int = Field(ge=0, description="Exact match hits")
    semantic_hits: int = Field(ge=0, description="Semantic match hits")
    prefix_hits: int = Field(ge=0, description="Prompt prefix hits (2026)")
    context_hits: int = Field(ge=0, description="Context reuse hits (2026)")

    total_tokens_saved: int = Field(ge=0, description="Total tokens saved")
    total_cost_saved: float = Field(ge=0.0, description="Total cost saved ($)")

    avg_latency_ms: float = Field(ge=0.0, description="Average latency")
    p50_latency_ms: float = Field(ge=0.0, description="P50 latency")
    p95_latency_ms: float = Field(ge=0.0, description="P95 latency")
    p99_latency_ms: float = Field(ge=0.0, description="P99 latency")

    cache_size_bytes: int = Field(ge=0, description="Current cache size")
    cache_entry_count: int = Field(ge=0, description="Number of entries")
    eviction_count: int = Field(ge=0, description="Number of evictions")


class CacheWarmupPlan(BaseModel):
    """
    Plan for cache warming operations.
    """

    priority_queries: List[str] = Field(description="High-priority queries to warm")
    estimated_time_seconds: float = Field(ge=0.0, description="Estimated warming time")
    expected_hit_rate_after_warmup: float = Field(
        ge=0.0, le=1.0, description="Expected hit rate after warming"
    )
    concurrent_warmup_limit: int = Field(
        ge=1, description="Max concurrent warmup operations"
    )


class InvalidationPattern(BaseModel):
    """
    Pattern for cache invalidation.
    """

    pattern: str = Field(description="Pattern to match (regex or prefix)")
    pattern_type: Literal["prefix", "regex", "exact"] = Field(
        description="Type of pattern matching"
    )
    reason: str = Field(description="Reason for invalidation")
    affected_entries: int = Field(ge=0, description="Number of entries affected")


class MultiProviderCacheStatus(BaseModel):
    """
    Status of multi-provider caching (2026).
    """

    providers: Dict[str, bool] = Field(description="Provider availability status")
    active_provider: str = Field(description="Currently active provider")
    failover_enabled: bool = Field(description="Whether automatic failover is enabled")
    total_cost_saved: float = Field(
        ge=0.0, description="Total cost saved across providers"
    )
    provider_savings: Dict[str, float] = Field(description="Savings per provider")


class ContextBuilderConfig(BaseModel):
    """
    Configuration for AI context building.

    2026 Pattern: Explicit context management for AI operations.
    """

    max_tokens: int = Field(
        ge=1000, le=1_000_000, default=100_000, description="Maximum tokens in context"
    )
    system_priority: int = Field(
        ge=0,
        le=10,
        default=0,
        description="System prompt priority (higher = more important)",
    )
    domain_context_priority: int = Field(
        ge=0, le=10, default=1, description="Domain context priority"
    )
    include_cache_stats: bool = Field(
        default=True, description="Include cache statistics in context"
    )
    include_recent_history: bool = Field(
        default=True, description="Include recent query history"
    )
    history_length: int = Field(
        ge=0, le=100, default=10, description="Number of recent queries to include"
    )
