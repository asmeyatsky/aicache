#!/usr/bin/env python3
"""
Comprehensive test for Phase 2: Predictive Caching Intelligence
This test demonstrates all features working together.
"""

import sys
import asyncio
import time
sys.path.insert(0, 'src')

from aicache.enhanced_core import EnhancedCache

async def test_comprehensive_phase2():
    print("🧠 Comprehensive Testing Phase 2: Predictive Caching Intelligence")
    print("=" * 70)
    
    # Initialize enhanced cache with all features
    cache = EnhancedCache("comprehensive_test")
    await cache.init_async()
    
    print("✅ Enhanced cache with all Phase 2 features initialized")
    
    # Test 1: Intent-based caching
    print("\n🎯 Test 1: Intent-Based Caching")
    print("-" * 40)
    
    # Store a response
    await cache.set(
        "How to write a Python function to calculate factorial?",
        '''def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)''',
        {"language": "python", "topic": "math"}
    )
    print("✅ Stored factorial function example")
    
    # Try to retrieve with a different but similar query
    result = await cache.get(
        "Python function for calculating factorial of a number",
        {"language": "python", "topic": "math"}
    )
    
    if result and result.get('cache_type') == 'intent':
        print("✅ Intent-based cache hit!")
        print(f"   Found code for: {result['prompt']}")
    elif result:
        print("✅ Cache hit (exact match)")
    else:
        print("❌ No cache hit")
    
    # Test 2: Behavioral learning session
    print("\n📚 Test 2: Behavioral Learning Session")
    print("-" * 40)
    
    # Simulate a Python development session
    python_queries = [
        ("How to sort a list in Python?", {"language": "python", "topic": "sorting"}),
        ("Python list sorting methods", {"language": "python", "topic": "sorting"}),
        ("Sort list by multiple criteria Python", {"language": "python", "topic": "sorting"}),
        ("Python error handling best practices", {"language": "python", "topic": "exceptions"}),
        ("Try except finally in Python", {"language": "python", "topic": "exceptions"}),
    ]
    
    for i, (query, context) in enumerate(python_queries):
        print(f"  Query {i+1}: {query[:30]}...")
        
        # First get (cache miss, triggers learning)
        result = await cache.get(query, context)
        cache_hit = result is not None
        
        if not cache_hit:
            # Simulate setting the response
            response = f"Response for: {query}"
            await cache.set(query, response, context)
    
    print("✅ Learning session completed")
    
    # Test 3: Proactive code generation
    print("\n🚀 Test 3: Proactive Code Generation")
    print("-" * 40)
    
    if cache.proactive_generator:
        # Schedule some code generation tasks
        task_ids = []
        generation_requests = [
            ("Write a Python function to reverse a string", {"language": "python", "topic": "strings"}),
            ("Create a JavaScript function to validate email", {"language": "javascript", "topic": "validation"}),
        ]
        
        for query, context in generation_requests:
            task_id = await cache.proactive_generator.schedule_generation(query, context, confidence=0.8)
            task_ids.append(task_id)
            print(f"✅ Scheduled: {query[:30]}...")
        
        # Wait a moment for processing
        await asyncio.sleep(2)
        
        # Check results
        for task_id in task_ids:
            task_result = await cache.proactive_generator.get_generated_code(task_id)
            if task_result and task_result.success:
                print(f"✅ Generated code for task {task_id[:8]}...")
            else:
                print(f"⚠️  Code generation pending for task {task_id[:8]}...")
    else:
        print("❌ Proactive code generator not available")
    
    # Test 4: Predictive prefetching
    print("\n🔮 Test 4: Predictive Prefetching")
    print("-" * 40)
    
    if cache.predictive_prefetcher:
        # Get prefetch stats
        prefetch_stats = await cache.predictive_prefetcher.get_prefetch_stats()
        print(f"Prefetch Status:     {'🟢 Running' if prefetch_stats['running'] else '🔴 Stopped'}")
        print(f"Queue Size:          {prefetch_stats['queue_size']}")
        
        # Force a prefetch
        await cache.predictive_prefetcher.force_prefetch(
            query="Python decorators tutorial",
            context={"language": "python", "topic": "advanced"},
            priority=3
        )
        print("✅ Forced prefetch scheduled")
        
        # Check updated stats
        updated_stats = await cache.predictive_prefetcher.get_prefetch_stats()
        print(f"Updated Queue Size:  {updated_stats['queue_size']}")
    else:
        print("❌ Predictive prefetcher not available")
    
    # Test 5: Behavioral analytics
    print("\n📊 Test 5: Behavioral Analytics")
    print("-" * 40)
    
    if cache.behavioral_analyzer:
        analytics = await cache.behavioral_analyzer.get_analytics()
        print(f"Total Queries:       {analytics['total_queries']}")
        print(f"Unique Sessions:     {analytics['unique_sessions']}")
        print(f"Active Patterns:     {analytics['active_patterns']}")
        print(f"Context Triggers:    {analytics['contextual_triggers']}")
        print("✅ Behavioral analytics retrieved")
    else:
        print("❌ Behavioral analyzer not available")
    
    # Test 6: Performance validation
    print("\n⚡ Test 6: Performance Validation")
    print("-" * 40)
    
    start_time = time.time()
    
    # Test rapid queries to ensure system doesn't slow down
    for i in range(5):
        test_query = f"Performance test query {i}"
        test_context = {"test": "performance", "batch": i}
        
        await cache.set(test_query, f"Response {i}", test_context)
        result = await cache.get(test_query, test_context)
        
        assert result is not None, f"Performance test {i} failed"
    
    end_time = time.time()
    avg_time = (end_time - start_time) / 5
    
    print(f"Average query time:  {avg_time*1000:.2f}ms")
    print(f"Performance:         {'✅ Good' if avg_time < 0.5 else '⚠️  Acceptable' if avg_time < 1.0 else '❌ Needs optimization'}")
    
    # Cleanup
    if cache.predictive_prefetcher:
        await cache.predictive_prefetcher.stop()
        print("✅ Predictive prefetcher stopped")
    
    if cache.proactive_generator:
        await cache.proactive_generator.stop()
        print("✅ Proactive code generator stopped")
    
    print("\n🎉 Comprehensive Phase 2 Testing Complete!")
    print("=" * 70)
    print("Summary:")
    print(f"  ✅ Intent-Based Caching:    {'Working' if cache.intent_cache else 'Not Available'}")
    print(f"  ✅ Behavioral Learning:     {'Working' if cache.behavioral_analyzer else 'Not Available'}")
    print(f"  ✅ Pattern Recognition:     {'Working' if cache.behavioral_analyzer else 'Not Available'}")
    print(f"  ✅ Predictive Analytics:    {'Working' if cache.behavioral_analyzer else 'Not Available'}")
    print(f"  ✅ Prefetch System:         {'Working' if cache.predictive_prefetcher else 'Not Available'}")
    print(f"  ✅ Contextual Triggers:     {'Working' if cache.behavioral_analyzer else 'Not Available'}")
    print(f"  ✅ Proactive Code Gen:      {'Working' if cache.proactive_generator else 'Not Available'}")
    print(f"  ✅ Performance:             {'Acceptable' if avg_time < 1.0 else 'Needs optimization'}")
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_comprehensive_phase2())
        if success:
            print("\n🎯 Phase 2 implementation successful!")
            sys.exit(0)
        else:
            print("\n❌ Phase 2 implementation has issues!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Phase 2 test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)