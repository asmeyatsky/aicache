#!/usr/bin/env python3
"""
Test for intent-based caching functionality
"""

import sys
import asyncio
sys.path.insert(0, 'src')

from aicache.enhanced_core import EnhancedCache
from aicache.intent import IntentAnalyzer, IntentBasedCache

async def test_intent_caching():
    print("🧪 Testing Intent-Based Caching...")
    
    # Initialize enhanced cache
    cache = EnhancedCache("test_intent")
    await cache.init_async()
    print("✅ Enhanced cache initialized")
    
    # Test intent analyzer directly
    if cache.intent_cache:
        print("✅ Intent-based cache available")
        
        # Test intent analysis
        query = "How to write a Python function to sort a list?"
        context = {"language": "python", "topic": "sorting"}
        
        intent_entry = await cache.intent_cache.intent_analyzer.analyze_intent(query, context)
        if intent_entry:
            print(f"✅ Intent analysis completed")
            print(f"   Intent: {intent_entry.intent_description[:50]}...")
            print(f"   Canonical query: {intent_entry.canonical_query}")
            print(f"   Related queries: {len(intent_entry.related_queries)}")
        else:
            print("⚠️  Intent analysis not available (LLM service disabled)")
    else:
        print("⚠️  Intent-based cache not available (LLM service disabled)")
    
    # Test basic cache operations still work
    await cache.set("test_query", "test_response", {"model": "test"}, cost_estimate=0.01)
    print("✅ Set operation completed")
    
    result = await cache.get("test_query", {"model": "test"})
    if result:
        print(f"✅ Get operation: {result['response']}")
    else:
        print("❌ Get operation failed")
    
    print("🎉 Intent-based caching test completed!")

if __name__ == "__main__":
    asyncio.run(test_intent_caching())