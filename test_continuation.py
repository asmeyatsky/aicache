#!/usr/bin/env python3
"""
Test script for the LLM Continuation Feature with Vector Database Support.

This script demonstrates the new continuation functionality that allows
seamless transfer of context between different LLMs using vector database storage.
"""

import asyncio
import tempfile
import os
from pathlib import Path

# Add the src directory to the Python path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from aicache.living_brain import BrainStateManager
from aicache.continuation import ContinuationManager, get_continuation_manager
from aicache.enhanced_core import EnhancedCache


async def test_continuation_feature():
    """Test the continuation feature with vector database support."""
    
    print("🧪 Testing LLM Continuation Feature with Vector Database Support")
    print("=" * 70)
    
    # Initialize brain manager
    print("\n🧠 Initializing Brain State Manager...")
    brain_manager = BrainStateManager()
    await brain_manager.init_db()
    
    # Initialize continuation manager
    print("\n🔄 Initializing Continuation Manager...")
    continuation_manager = get_continuation_manager()
    await continuation_manager.init_db()
    await continuation_manager.set_brain_manager(brain_manager)
    
    # Create a source session (simulating a Claude session)
    print("\n📝 Creating source session (simulating Claude session)...")
    source_session = await brain_manager.create_new_session(
        project_id="test-project-123",
        project_name="Test Project for Continuation"
    )
    
    # Add some conversation history to the source session
    print("\n💬 Adding conversation history to source session...")
    brain_manager.current_context.add_conversation_turn(
        "user", 
        "Can you help me implement a Python function to calculate Fibonacci numbers?",
        "claude"
    )
    brain_manager.current_context.add_conversation_turn(
        "assistant", 
        "Sure! Here's a Python function to calculate Fibonacci numbers:\n\n```python\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n```",
        "claude"
    )
    brain_manager.current_context.add_conversation_turn(
        "user", 
        "That's great! Can you also provide an optimized version using memoization?",
        "claude"
    )
    brain_manager.current_context.add_conversation_turn(
        "assistant", 
        "Certainly! Here's an optimized version using memoization:\n\n```python\nfrom functools import lru_cache\n\n@lru_cache(maxsize=None)\ndef fibonacci_memo(n):\n    if n <= 1:\n        return n\n    return fibonacci_memo(n-1) + fibonacci_memo(n-2)\n```",
        "claude"
    )
    
    # Add some concepts to the knowledge base
    print("\n💡 Adding concepts to knowledge base...")
    await brain_manager.add_concept(
        "Python function to calculate Fibonacci numbers",
        "claude",
        tags=["python", "algorithm", "math"],
        importance=0.9
    )
    await brain_manager.add_concept(
        "Memoization technique for optimizing recursive functions",
        "claude", 
        tags=["optimization", "memoization", "performance"],
        importance=0.8
    )
    
    # Update the session context
    await brain_manager.update_session_context(brain_manager.current_context)
    
    print(f"   Added 2 conversation turns and 2 concepts to session {source_session.session_id}")
    
    # Create a continuation package to transfer to Gemini
    print("\n📦 Creating continuation package for transfer to Gemini...")
    package_id = await continuation_manager.create_continuation_package(
        session_id=source_session.session_id,
        target_llm="gemini",
        max_conversation_length=10,
        max_concepts=20
    )
    
    if package_id:
        print(f"   ✅ Successfully created continuation package: {package_id}")
    else:
        print("   ❌ Failed to create continuation package")
        return
    
    # List available continuation packages
    print("\n📋 Listing available continuation packages...")
    packages = await continuation_manager.list_packages(target_llm="gemini")
    for pkg in packages:
        print(f"   - {pkg['package_id'][:8]}... | Source: {pkg['source_session_id'][:8]}... | Task: {pkg['current_task'] or 'N/A'}")
    
    # Inspect the created package
    print(f"\n🔍 Inspecting continuation package {package_id[:8]}...")
    package = await continuation_manager.load_continuation_package(package_id)
    if package:
        print(f"   Source LLM: {package.source_llm}")
        print(f"   Target LLM: {package.target_llm}")
        print(f"   Concepts included: {len(package.summary_concepts)}")
        print(f"   Conversation turns: {len(package.recent_conversation)}")
        print(f"   Current task: {package.current_task}")
    else:
        print("   ❌ Could not load package for inspection")
    
    # Create a target session (simulating a Gemini session)
    print(f"\n🎯 Creating target session (simulating Gemini session)...")
    target_session = await brain_manager.create_new_session(
        project_id="test-project-123-gemini",
        project_name="Test Project Continued in Gemini"
    )
    target_session_id = target_session.session_id
    print(f"   Created target session: {target_session_id}")
    
    # Apply the continuation package to the target session
    print(f"\n🔄 Applying continuation package {package_id[:8]}... to target session {target_session_id[:8]}...")
    success = await continuation_manager.apply_continuation_package(
        package_id=package_id,
        target_session_id=target_session_id
    )
    
    if success:
        print("   ✅ Successfully applied continuation package!")
        
        # Verify that the context was transferred
        print("\n📋 Verifying context transfer...")
        target_context = await brain_manager.load_session_context(target_session_id)
        if target_context:
            print(f"   Current task: {target_context.current_task}")
            print(f"   Conversation history length: {len(target_context.conversation_history)}")
            print(f"   Relevant files: {len(target_context.relevant_files)}")
            
            # Show the last few conversation turns
            print("\n   Last 3 conversation turns:")
            for turn in target_context.conversation_history[-3:]:
                print(f"     {turn['role']}: {turn['content'][:100]}...")
        else:
            print("   ❌ Could not load target context for verification")
    else:
        print("   ❌ Failed to apply continuation package")
    
    # Test semantic search for continuation packages
    print(f"\n🔍 Testing semantic search for continuation packages...")
    search_results = await continuation_manager.search_continuation_packages(
        query="fibonacci function implementation",
        target_llm="gemini",
        limit=5
    )
    
    print(f"   Found {len(search_results)} relevant packages:")
    for i, (pkg, score) in enumerate(search_results, 1):
        print(f"     {i}. Score: {score:.3f} | Package: {pkg.package_id[:8]}... | Task: {pkg.current_task or 'N/A'}")
    
    print(f"\n🎉 Continuation feature test completed successfully!")
    print("=" * 70)
    

if __name__ == "__main__":
    asyncio.run(test_continuation_feature())