"""Domain layer: Core business logic for AI caching."""

from .models import (
    CacheEntry,
    CacheMetadata,
    CachePolicy,
    CacheResult,
    CacheInvalidationEvent,
    SemanticMatch,
    TokenUsageMetrics,
    CacheMetrics,
    EvictionPolicy,
    InvalidationStrategy,
)
from .ports import (
    StoragePort,
    SemanticIndexPort,
    TokenCounterPort,
    EventPublisherPort,
    QueryNormalizerPort,
    CacheMetricsPort,
    EmbeddingGeneratorPort,
    RepositoryPort,
)
from .services import (
    QueryNormalizationService,
    TokenCountingService,
    SemanticCachingService,
    CacheEvictionService,
    CacheInvalidationService,
    CacheTTLService,
)

__all__ = [
    # Models
    "CacheEntry",
    "CacheMetadata",
    "CachePolicy",
    "CacheResult",
    "CacheInvalidationEvent",
    "SemanticMatch",
    "TokenUsageMetrics",
    "CacheMetrics",
    "EvictionPolicy",
    "InvalidationStrategy",
    # Ports
    "StoragePort",
    "SemanticIndexPort",
    "TokenCounterPort",
    "EventPublisherPort",
    "QueryNormalizerPort",
    "CacheMetricsPort",
    "EmbeddingGeneratorPort",
    "RepositoryPort",
    # Services
    "QueryNormalizationService",
    "TokenCountingService",
    "SemanticCachingService",
    "CacheEvictionService",
    "CacheInvalidationService",
    "CacheTTLService",
]
