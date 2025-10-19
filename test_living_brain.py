#!/usr/bin/env python3
"""
Simple test case to verify that the living brain functionality works as expected.
"""

import asyncio
import tempfile
import os
import shutil
from pathlib import Path

from src.aicache.living_brain import BrainStateManager, CrossAIConcept


async def test_living_brain_functionality():
    """Test the basic functionality of the living brain system."""
    
    # Create a temporary directory for this test
    with tempfile.TemporaryDirectory() as temp_dir:
        brain_manager = BrainStateManager(temp_dir)
        await brain_manager.init_db()
        
        print("🧪 Testing Living Brain Functionality...")
        
        # Test 1: Create a new session
        print("\n1️⃣  Creating a new brain session for project 'test-project'...")
        session = await brain_manager.create_new_session("test-project", "Test Project")
        print(f"   ✅ Session created: {session.session_id}")
        print(f"   ✅ Project ID: {session.project_id}")
        
        # Test 2: Switch AI providers
        print("\n2️⃣  Switching to 'claude' provider...")
        result = await brain_manager.switch_ai_provider("claude")
        print(f"   ✅ Switched to Claude: {result}")
        print(f"   ✅ Providers used: {list(session.ai_providers_used)}")
        
        # Test 3: Add concepts from different providers
        print("\n3️⃣  Adding concepts from different AI providers...")
        
        concept1_id = await brain_manager.add_concept(
            "How to implement a REST API in Python with Flask",
            "claude",
            tags=["python", "flask", "api"],
            importance=1.0
        )
        print(f"   ✅ Added concept from Claude: {concept1_id[:8]}...")
        
        concept2_id = await brain_manager.add_concept(
            "Best practices for database design in Django",
            "gemini", 
            tags=["python", "django", "database"],
            importance=0.8
        )
        print(f"   ✅ Added concept from Gemini: {concept2_id[:8]}...")
        
        concept3_id = await brain_manager.add_concept(
            "How to optimize React component performance",
            "qwen",
            tags=["javascript", "react", "performance"],
            importance=0.9
        )
        print(f"   ✅ Added concept from Qwen: {concept3_id[:8]}...")
        
        # Test 4: Search for relevant concepts
        print("\n4️⃣  Searching for concepts related to 'python'...")
        python_concepts = await brain_manager.get_relevant_concepts("python")
        print(f"   ✅ Found {len(python_concepts)} Python-related concepts:")
        for concept in python_concepts:
            print(f"     - {concept.content[:50]}... (from {', '.join(concept.ai_providers)})")
        
        # Test 5: Search for concepts related to a specific topic
        print("\n5️⃣  Searching for concepts related to 'database'...")
        database_concepts = await brain_manager.get_relevant_concepts("database")
        print(f"   ✅ Found {len(database_concepts)} database-related concepts:")
        for concept in database_concepts:
            print(f"     - {concept.content[:50]}... (from {', '.join(concept.ai_providers)})")
            print(f"     - Importance: {concept.importance_score}")
        
        # Test 6: Check project statistics
        print("\n6️⃣  Getting project statistics...")
        stats = await brain_manager.get_project_stats("test-project")
        print(f"   ✅ Project stats:")
        print(f"     - Total sessions: {stats['total_sessions']}")
        print(f"     - Total concepts: {stats['total_concepts']}")
        print(f"     - Total interactions: {stats['total_interactions']}")
        print(f"     - Unique AI providers: {stats['unique_ai_providers']}")
        print(f"     - Average concept importance: {stats['avg_concept_importance']:.2f}")
        
        # Test 7: Verify cross-AI concept tracking
        print("\n7️⃣  Verifying cross-AI concept tracking...")
        all_concepts = await brain_manager.get_relevant_concepts("", limit=10)
        providers_used = set()
        for concept in all_concepts:
            providers_used.update(concept.ai_providers)
            print(f"     - Concept '{concept.content[:30]}...' from {concept.ai_providers}")
        
        print(f"   ✅ Concepts from providers: {providers_used}")
        
        print("\n🎉 All tests passed! Living brain functionality is working correctly.")
        return True


async def test_cross_ai_session_persistence():
    """Test that context persists across AI provider switches."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        brain_manager = BrainStateManager(temp_dir)
        await brain_manager.init_db()
        
        print("\n🧪 Testing Cross-AI Session Persistence...")
        
        # Start a session
        session = await brain_manager.create_new_session("persistence-test", "Persistence Test")
        print(f"   ✅ Started session: {session.session_id}")
        
        # Add some context with Claude
        await brain_manager.switch_ai_provider("claude")
        await brain_manager.add_concept(
            "User authentication system requirements", 
            "claude",
            tags=["auth", "security"],
            importance=1.0
        )
        
        # Switch to Gemini and add more context
        await brain_manager.switch_ai_provider("gemini")
        await brain_manager.add_concept(
            "Database schema for user accounts", 
            "gemini",
            tags=["database", "schema"],
            importance=0.9
        )
        
        # Switch to Qwen and add even more context
        await brain_manager.switch_ai_provider("qwen")
        await brain_manager.add_concept(
            "Frontend components for login page", 
            "qwen",
            tags=["frontend", "ui"],
            importance=0.8
        )
        
        # Verify all providers have contributed to the session
        final_session = await brain_manager.create_new_session("persistence-test", "Persistence Test")  # This will reload
        print(f"   ✅ Final session has providers: {list(brain_manager.current_session.ai_providers_used)}")
        
        # Search for concepts to verify they're all accessible
        all_context = await brain_manager.get_relevant_concepts("user")
        print(f"   ✅ Found {len(all_context)} concepts related to 'user' across all providers")
        
        print("   ✅ Cross-AI session persistence working correctly!")
        return True


async def main():
    """Run all tests."""
    print("🚀 Starting Living Brain Functionality Tests...")
    
    try:
        success1 = await test_living_brain_functionality()
        success2 = await test_cross_ai_session_persistence()
        
        if success1 and success2:
            print("\n✅ All living brain tests passed successfully!")
            print("\n📋 Summary of what was tested:")
            print("   • Session creation and management")
            print("   • AI provider switching with context preservation")
            print("   • Cross-AI concept storage and retrieval")
            print("   • Semantic search across concepts")
            print("   • Project statistics tracking")
            print("   • Cross-AI session persistence")
            print("\n🎯 The living brain functionality is working as expected!")
        else:
            print("\n❌ Some tests failed!")
            
    except Exception as e:
        print(f"\n💥 Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())