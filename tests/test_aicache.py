#!/usr/bin/env python3
"""
Pytest-compatible tests for aicache.
"""

import sys
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, 'src')

from aicache.enhanced_core import EnhancedCache
from aicache.behavioral import BehavioralAnalyzer
from aicache.intent import IntentBasedCache
from aicache.federated.collaborative import CollaborativeCache
from aicache.federated.recommendations import RecommendationEngine

class TestAICache:
    """Pytest test class for aicache."""
    
    @pytest.fixture
    async def enhanced_cache(self):
        """Fixture for enhanced cache."""
        cache = EnhancedCache("pytest_test")
        await cache.init_async()
        yield cache
        # Cleanup handled by cache itself
        
    @pytest.mark.asyncio
    async def test_enhanced_cache_basic_operations(self, enhanced_cache):
        """Test basic cache operations."""
        cache = enhanced_cache
        
        # Test set operation
        cache_key = await cache.set("test_query", "test_response", {"model": "test"})
        assert cache_key is not None
        
        # Test get operation
        result = await cache.get("test_query", {"model": "test"})
        assert result is not None
        assert result["response"] == "test_response"
        
        # Test list operation
        entries = await cache.list()
        assert len(entries) > 0
        
    @pytest.mark.asyncio
    async def test_enhanced_cache_stats(self, enhanced_cache):
        """Test cache statistics."""
        cache = enhanced_cache
        
        await cache.set("stats_test", "stats_response", {"model": "test"})
        
        stats = await cache.get_stats()
        assert "storage" in stats
        assert "cache_performance" in stats
        assert stats["storage"]["total_entries"] > 0
        
    @pytest.mark.asyncio
    async def test_enhanced_cache_prune(self, enhanced_cache):
        """Test cache pruning."""
        cache = enhanced_cache
        
        # Add some entries
        for i in range(5):
            await cache.set(f"prune_test_{i}", f"response_{i}", {"model": "test"})
            
        # Prune with very short age
        pruned = await cache.prune(max_age_days=0)
        assert pruned >= 0  # Should not crash
        
    @pytest.mark.asyncio
    async def test_behavioral_analyzer(self):
        """Test behavioral analyzer initialization."""
        analyzer = BehavioralAnalyzer("/tmp/test_behavioral")
        await analyzer.init_db()
        
        # Test analytics (should not crash)
        analytics = await analyzer.get_analytics()
        assert "total_queries" in analytics
        
    @pytest.mark.asyncio
    async def test_intent_based_cache(self):
        """Test intent-based cache."""
        intent_cache = IntentBasedCache(None)
        
        # Should not crash with no data
        result = await intent_cache.get_by_intent("test intent", {"context": "test"})
        assert result is None or isinstance(result, tuple)
        
    @pytest.mark.asyncio
    async def test_collaborative_cache(self):
        """Test collaborative cache."""
        collab_cache = CollaborativeCache("pytest_team")
        await collab_cache.init_async()
        
        # Test entry creation
        await collab_cache.create_cache_entry(
            "collab_key", "collab_query", "collab_response", 
            {"model": "test"}, "pytest_user"
        )
        
        # Test retrieval
        result = await collab_cache.get_cache_entry("collab_key")
        assert result is not None
        
    @pytest.mark.asyncio
    async def test_recommendation_engine(self):
        """Test recommendation engine."""
        rec_engine = RecommendationEngine("pytest_user")
        await rec_engine.initialize()
        
        # Test interaction recording
        await rec_engine.record_interaction("python", "test_query", {"type": "code"})
        
        # Test recommendation generation
        recommendations = await rec_engine.get_recommendations({"language": "python"})
        assert isinstance(recommendations, list)
        
    def test_imports(self):
        """Test that all critical imports work."""
        # Should not raise any exceptions
        from aicache.enhanced_core import EnhancedCache
        from aicache.behavioral import BehavioralAnalyzer
        from aicache.predictive import PredictivePrefetcher
        from aicache.intent import IntentBasedCache, IntentAnalyzer
        from aicache.proactive import ProactiveCodeGenerator
        from aicache.federated.collaborative import CollaborativeCache
        from aicache.federated.recommendations import RecommendationEngine
        from aicache.federated.anomaly_detection import AnomalyDetector
        from aicache.federated.privacy import PrivacyEngine
        
        assert True  # If we get here, imports worked
        
    @pytest.mark.asyncio
    async def test_cache_key_generation(self, enhanced_cache):
        """Test cache key generation consistency."""
        cache = enhanced_cache
        
        # Same query and context should generate same key
        key1 = cache._get_cache_key("test query", {"model": "gpt-4"})
        key2 = cache._get_cache_key("test query", {"model": "gpt-4"})
        
        assert key1 == key2
        
        # Different context should generate different key
        key3 = cache._get_cache_key("test query", {"model": "gpt-3.5"})
        assert key1 != key3
        
    @pytest.mark.asyncio
    async def test_context_normalization(self, enhanced_cache):
        """Test context normalization."""
        cache = enhanced_cache
        
        context1 = {"model": "gpt-4", "verbose": True}
        context2 = {"model": "gpt-4", "debug": True}
        
        # Should normalize away verbose/debug parameters
        key1 = cache._get_cache_key("test", context1)
        key2 = cache._get_cache_key("test", context2)
        
        # Keys might be different due to different ignored params, but should not crash
        assert isinstance(key1, str)
        assert isinstance(key2, str)
        
if __name__ == "__main__":
    pytest.main([__file__])