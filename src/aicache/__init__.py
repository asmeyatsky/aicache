# AI Cache - Stop paying for duplicate AI queries

__version__ = "0.2.0"

# Primary CLI entry point
from .modern_cli import main

# Core components
from .core.cache import CoreCache, get_cache
from .cache_factory import CacheFactory, create_cache

# Security utilities
from .security import (
    SecurityUtils,
    sanitize_input,
    detect_pii,
    mask_pii,
    is_safe_prompt,
    validate_context,
)

# Domain models
from .domain.models import (
    CacheEntry,
    CachePolicy,
    CacheMetrics,
    TokenUsageMetrics,
    SemanticMatch,
    CacheResult,
    EvictionPolicy,
)

# Domain ports (interfaces)
from .domain.ports import (
    StoragePort,
    SemanticIndexPort,
    TokenCounterPort,
    EventPublisherPort,
    QueryNormalizerPort,
    CacheMetricsPort,
    EmbeddingGeneratorPort,
    RepositoryPort,
)

# Configuration
from .config import get_config, get_config_manager
