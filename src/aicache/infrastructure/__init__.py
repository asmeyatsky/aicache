"""Infrastructure layer: Adapter implementations for external dependencies."""

from .adapters import (
    InMemoryStorageAdapter,
    FileSystemStorageAdapter,
    SimpleQueryNormalizerAdapter,
    OpenAITokenCounterAdapter,
    InMemoryEventPublisherAdapter,
    InMemoryCacheMetricsAdapter,
    SimpleSemanticIndexAdapter,
    SimpleEmbeddingGeneratorAdapter,
)

__all__ = [
    "InMemoryStorageAdapter",
    "FileSystemStorageAdapter",
    "SimpleQueryNormalizerAdapter",
    "OpenAITokenCounterAdapter",
    "InMemoryEventPublisherAdapter",
    "InMemoryCacheMetricsAdapter",
    "SimpleSemanticIndexAdapter",
    "SimpleEmbeddingGeneratorAdapter",
]
