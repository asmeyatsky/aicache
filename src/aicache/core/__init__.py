# Core cache module

from .cache import CoreCache, CacheEntry, get_cache

# Backward compatibility - also expose as Cache
Cache = CoreCache

__all__ = ["CoreCache", "Cache", "CacheEntry", "get_cache"]
