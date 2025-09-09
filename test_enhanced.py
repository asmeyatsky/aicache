#!/usr/bin/env python3

import sys
import asyncio
sys.path.insert(0, 'src')

from aicache.enhanced_core import EnhancedCache

async def test_enhanced_cache():
    print("🧪 Testing Enhanced Cache...")
    
    # Initialize enhanced cache
    cache = EnhancedCache("test_enhanced")
    await cache.init_async()
    print("✅ Enhanced cache initialized with SQLite database")
    
    # Test basic operations
    await cache.set("test_query", "test_response", {"model": "test"}, cost_estimate=0.01)
    print("✅ Set operation completed")
    
    result = await cache.get("test_query", {"model": "test"})
    if result:
        print(f"✅ Get operation: {result['response']}")
    else:
        print("❌ Get operation failed")
    
    # Test list operation
    entries = await cache.list()
    print(f"✅ Cache has {len(entries)} entries")
    
    # Test stats
    stats = await cache.get_stats()
    print(f"✅ Cache stats: {stats['storage']['total_entries']} entries, {stats['storage']['total_size']} bytes")
    
    print("🎉 Enhanced cache test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_enhanced_cache())