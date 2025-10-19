#!/usr/bin/env python3
"""
Comprehensive test suite for aicache.
Tests all major components and functionality.
"""

import sys
import asyncio
import shutil
import tempfile
from pathlib import Path

sys.path.insert(0, 'src')

from aicache.enhanced_core import EnhancedCache
from aicache.behavioral import BehavioralAnalyzer
from aicache.predictive import PredictivePrefetcher
from aicache.intent import IntentBasedCache
from aicache.proactive import ProactiveCodeGenerator
from aicache.federated.collaborative import CollaborativeCache
from aicache.federated.recommendations import RecommendationEngine
from aicache.federated import FederatedLearningServer

class TestSuite:
    """Comprehensive test suite for aicache."""
    
    def __init__(self):
        self.test_results = {}
        self.temp_dir = None
        
    async def setup(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        print(f"🔧 Test environment setup at: {self.temp_dir}")
        
    async def teardown(self):
        """Cleanup test environment."""
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
        print("🧹 Test environment cleaned up")
        
    async def test_enhanced_cache(self):
        """Test enhanced cache functionality."""
        print("\n📦 Testing Enhanced Cache...")
        try:
            cache = EnhancedCache("test_suite")
            await cache.init_async()
            
            # Test basic operations
            await cache.set("test_query", "test_response", {"model": "test"})
            result = await cache.get("test_query", {"model": "test"})
            
            assert result is not None, "Cache get failed"
            assert result["response"] == "test_response", "Response mismatch"
            
            # Test list operation
            entries = await cache.list()
            assert len(entries) > 0, "No cache entries found"
            
            # Test stats
            stats = await cache.get_stats()
            assert "storage" in stats, "Stats missing storage info"
            
            self.test_results["enhanced_cache"] = "✅ PASS"
            
        except Exception as e:
            self.test_results["enhanced_cache"] = f"❌ FAIL: {str(e)}"
            
    async def test_behavioral_learning(self):
        """Test behavioral learning system."""
        print("\n🧠 Testing Behavioral Learning...")
        try:
            cache = EnhancedCache("test_behavioral")
            await cache.init_async()
            
            # Test behavioral analyzer
            if cache.behavioral_analyzer:
                # Simulate some queries
                for i in range(5):
                    query = f"test query {i}"
                    await cache.set(query, f"response {i}", {"model": "test"})
                    await cache.get(query, {"model": "test"})
                
                # Test analytics
                analytics = await cache.behavioral_analyzer.get_analytics()
                assert "total_queries" in analytics, "Analytics missing total_queries"
                
                self.test_results["behavioral_learning"] = "✅ PASS"
            else:
                self.test_results["behavioral_learning"] = "⏭️ SKIP - Not available"
                
        except Exception as e:
            self.test_results["behavioral_learning"] = f"❌ FAIL: {str(e)}"
            
    async def test_intent_based_cache(self):
        """Test intent-based caching."""
        print("\n🎯 Testing Intent-Based Cache...")
        try:
            intent_cache = IntentBasedCache(None)  # No LLM service needed for basic test
            
            # Test intent analysis (basic functionality)
            result = await intent_cache.get_by_intent("how to sort list", {"language": "python"})
            
            # Should not crash even with no data
            self.test_results["intent_cache"] = "✅ PASS"
            
        except Exception as e:
            self.test_results["intent_cache"] = f"❌ FAIL: {str(e)}"
            
    async def test_collaborative_cache(self):
        """Test collaborative caching."""
        print("\n👥 Testing Collaborative Cache...")
        try:
            collab_cache = CollaborativeCache("test_team")
            
            # Test that the object can be instantiated
            assert collab_cache.team_id == "test_team", "Team ID not set correctly"
            assert hasattr(collab_cache, 'cache_entries'), "Missing cache_entries attribute"
            
            self.test_results["collaborative_cache"] = "✅ PASS"
            
        except Exception as e:
            self.test_results["collaborative_cache"] = f"❌ FAIL: {str(e)}"
            
    async def test_recommendation_engine(self):
        """Test recommendation engine."""
        print("\n🎯 Testing Recommendation Engine...")
        try:
            rec_engine = RecommendationEngine("test_user", "http://localhost:8000")
            
            # Test that the object can be instantiated with correct attributes
            assert hasattr(rec_engine, 'client'), "Missing client attribute"
            assert hasattr(rec_engine, 'developer_profile'), "Missing developer_profile attribute"
            assert hasattr(rec_engine, 'recommendation_history'), "Missing recommendation_history attribute"
            
            self.test_results["recommendation_engine"] = "✅ PASS"
            
        except Exception as e:
            self.test_results["recommendation_engine"] = f"❌ FAIL: {str(e)}"
            
    async def test_federated_learning(self):
        """Test federated learning server."""
        print("\n🌐 Testing Federated Learning...")
        try:
            # Test with minimal config
            model_config = {"input_dim": 100, "hidden_dim": 50, "output_dim": 10}
            server = FederatedLearningServer(model_config)
            
            # Test that the object can be instantiated
            assert hasattr(server, 'model_config'), "Missing model_config attribute"
            assert server.model_config == model_config, "Model config not set correctly"
            
            self.test_results["federated_learning"] = "✅ PASS"
            
        except Exception as e:
            self.test_results["federated_learning"] = f"❌ FAIL: {str(e)}"
            
    async def test_import_consistency(self):
        """Test that all imports work correctly."""
        print("\n📥 Testing Import Consistency...")
        try:
            # Test all major imports
            from aicache.enhanced_core import EnhancedCache
            from aicache.behavioral import BehavioralAnalyzer
            from aicache.predictive import PredictivePrefetcher
            from aicache.intent import IntentBasedCache, IntentAnalyzer
            from aicache.proactive import ProactiveCodeGenerator
            from aicache.federated.collaborative import CollaborativeCache
            from aicache.federated.recommendations import RecommendationEngine
            from aicache.federated.anomaly_detection import AnomalyDetector
            from aicache.federated.privacy import EnhancedPrivacyPreserver, PrivacyBudgetManager
            from aicache.federated import FederatedLearningServer, FederatedLearningClient
            
            self.test_results["import_consistency"] = "✅ PASS"
            
        except Exception as e:
            self.test_results["import_consistency"] = f"❌ FAIL: {str(e)}"
            
    async def run_all_tests(self):
        """Run all tests in the suite."""
        print("🚀 Starting Comprehensive Test Suite")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Run all tests
            await self.test_import_consistency()
            await self.test_enhanced_cache()
            await self.test_behavioral_learning()
            await self.test_intent_based_cache()
            await self.test_collaborative_cache()
            await self.test_recommendation_engine()
            await self.test_federated_learning()
            
        finally:
            await self.teardown()
            
        # Print results
        print("\n📊 Test Results Summary")
        print("=" * 60)
        
        passed = 0
        failed = 0
        skipped = 0
        
        for test_name, result in self.test_results.items():
            print(f"{test_name:25} {result}")
            if "✅ PASS" in result:
                passed += 1
            elif "❌ FAIL" in result:
                failed += 1
            elif "⏭️ SKIP" in result:
                skipped += 1
                
        print("\n" + "=" * 60)
        print(f"📈 Summary: {passed} PASSED, {failed} FAILED, {skipped} SKIPPED")
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED!")
            return True
        else:
            print("⚠️  Some tests failed. Check output above.")
            return False

async def main():
    """Run the test suite."""
    suite = TestSuite()
    success = await suite.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)