#!/usr/bin/env python3
"""
Test for proactive code generation functionality
"""

import sys
import asyncio
sys.path.insert(0, 'src')

from aicache.enhanced_core import EnhancedCache
from aicache.proactive import ProactiveCodeGenerator

async def test_proactive_generation():
    print("🧪 Testing Proactive Code Generation...")
    
    # Initialize enhanced cache
    cache = EnhancedCache("test_proactive")
    await cache.init_async()
    print("✅ Enhanced cache initialized")
    
    # Test proactive generator
    if cache.proactive_generator:
        print("✅ Proactive code generator available")
        
        # Test generation stats
        stats = await cache.proactive_generator.get_generation_stats()
        print(f"✅ Generation stats: {stats['total_tasks']} tasks")
        
        # Test scheduling a generation task
        task_id = await cache.proactive_generator.schedule_generation(
            "Write a Python function to calculate factorial",
            {"language": "python", "topic": "math"},
            confidence=0.8
        )
        print(f"✅ Scheduled generation task: {task_id}")
        
        # Test stats again
        stats = await cache.proactive_generator.get_generation_stats()
        print(f"✅ Updated stats: {stats['queue_size']} tasks in queue")
        
    else:
        print("⚠️  Proactive code generator not available (LLM service disabled)")
    
    # Test basic cache operations still work
    await cache.set("test_query", "test_response", {"model": "test"}, cost_estimate=0.01)
    print("✅ Set operation completed")
    
    result = await cache.get("test_query", {"model": "test"})
    if result:
        print(f"✅ Get operation: {result['response']}")
    else:
        print("❌ Get operation failed")
    
    # Cleanup
    if cache.proactive_generator:
        await cache.proactive_generator.stop()
        print("✅ Proactive generator stopped")
    
    print("🎉 Proactive code generation test completed!")

if __name__ == "__main__":
    asyncio.run(test_proactive_generation())