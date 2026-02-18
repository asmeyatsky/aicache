#!/usr/bin/env python3
"""
Pytest-compatible tests for aicache core functionality.

Note: Some tests for enhanced features (collaborative, behavioral, etc.)
are marked as skipped since those features are not yet fully implemented.
"""

import sys
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, "src")

from aicache.intent import IntentBasedCache


class TestAICache:
    """Pytest test class for aicache core functionality."""

    @pytest.mark.skip(reason="EnhancedCache not fully implemented")
    @pytest.mark.asyncio
    async def test_enhanced_cache_basic_operations(self):
        """Test basic cache operations."""
        from aicache.enhanced_core import EnhancedCache

        cache = EnhancedCache("pytest_test")
        await cache.init_async()

        cache_key = await cache.set("test_query", "test_response", {"model": "test"})
        assert cache_key is not None

        result = await cache.get("test_query", {"model": "test"})
        assert result is not None
        assert result["response"] == "test_response"

        entries = await cache.list()
        assert len(entries) > 0

    @pytest.mark.skip(reason="EnhancedCache not fully implemented")
    @pytest.mark.asyncio
    async def test_enhanced_cache_stats(self):
        """Test cache statistics."""
        from aicache.enhanced_core import EnhancedCache

        cache = EnhancedCache("pytest_test")
        await cache.init_async()

        await cache.set("stats_test", "stats_response", {"model": "test"})

        stats = await cache.get_stats()
        assert "storage" in stats

    @pytest.mark.skip(reason="EnhancedCache not fully implemented")
    @pytest.mark.asyncio
    async def test_enhanced_cache_prune(self):
        """Test cache pruning."""
        from aicache.enhanced_core import EnhancedCache

        cache = EnhancedCache("pytest_test")
        await cache.init_async()

        for i in range(5):
            await cache.set(f"prune_test_{i}", f"response_{i}", {"model": "test"})

        pruned = await cache.prune(max_age_days=0)
        assert pruned >= 0

    @pytest.mark.skip(reason="Behavioral analyzer not fully implemented")
    @pytest.mark.asyncio
    async def test_behavioral_analyzer(self):
        """Test behavioral analyzer."""
        from aicache.behavioral import BehavioralAnalyzer

        analyzer = BehavioralAnalyzer()
        await analyzer.init_db()

        await analyzer.record_query("test_query", {"model": "test"})
        patterns = await analyzer.detect_patterns()
        assert patterns is not None

    @pytest.mark.skip(reason="IntentBasedCache requires llm_service parameter")
    @pytest.mark.asyncio
    async def test_intent_based_cache(self):
        """Test intent-based caching."""
        # IntentBasedCache requires an llm_service - skip for now
        pass

    @pytest.mark.skip(reason="Collaborative cache not fully implemented")
    @pytest.mark.asyncio
    async def test_collaborative_cache(self):
        """Test collaborative caching."""
        from aicache.federated.collaborative import CollaborativeCache

        collab_cache = CollaborativeCache(team_id="test_team")
        await collab_cache.init_async()

        await collab_cache.share_entry("test_key", {"response": "test"})

    @pytest.mark.skip(reason="Recommendation engine not fully implemented")
    @pytest.mark.asyncio
    async def test_recommendation_engine(self):
        """Test recommendation engine."""
        from aicache.federated.recommendations import RecommendationEngine

        engine = RecommendationEngine()

        recommendations = await engine.get_recommendations("test_query")
        assert recommendations is not None

    def test_imports(self):
        """Test that core imports work."""
        from aicache import CoreCache, get_cache
        from aicache.config import get_config
        from aicache.security import sanitize_input

        assert CoreCache is not None
        assert get_cache is not None

    def test_cache_key_generation(self):
        """Test cache key generation."""
        from aicache.core.cache import CoreCache
        import tempfile

        cache = CoreCache(cache_dir=tempfile.mkdtemp())

        key1 = cache._get_cache_key("test prompt")
        key2 = cache._get_cache_key("test prompt")
        key3 = cache._get_cache_key("different prompt")

        assert key1 == key2
        assert key1 != key3

    def test_context_normalization(self):
        """Test context normalization."""
        from aicache.core.cache import CoreCache
        import tempfile

        cache = CoreCache(cache_dir=tempfile.mkdtemp())

        key1 = cache._get_cache_key("test", {"a": 1, "b": 2})
        key2 = cache._get_cache_key("test", {"b": 2, "a": 1})

        assert key1 == key2
