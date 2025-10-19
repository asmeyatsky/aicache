#!/usr/bin/env python3
"""
Test for Phase 4: Serverless Cache Structure
"""

import sys
import os

def test_serverless_cache_structure():
    print("🧪 Testing Phase 4: Serverless Cache Structure")
    print("=" * 50)
    
    # Check if serverless-cache directory exists
    cache_dir = "serverless-cache"
    if not os.path.exists(cache_dir):
        print("❌ serverless-cache directory not found")
        return False
    
    print("✅ serverless-cache directory exists")
    
    # Check requirements.txt
    requirements_path = os.path.join(cache_dir, "requirements.txt")
    if not os.path.exists(requirements_path):
        print("❌ requirements.txt not found")
        return False
    
    print("✅ requirements.txt exists")
    
    # Check serverless.yml
    serverless_path = os.path.join(cache_dir, "serverless.yml")
    if not os.path.exists(serverless_path):
        print("❌ serverless.yml not found")
        return False
    
    print("✅ serverless.yml exists")
    
    # Check src directory
    src_dir = os.path.join(cache_dir, "src")
    if not os.path.exists(src_dir):
        print("❌ src directory not found")
        return False
    
    print("✅ src directory exists")
    
    # Check main handler file
    main_path = os.path.join(src_dir, "main.py")
    if not os.path.exists(main_path):
        print("❌ src/main.py not found")
        return False
    
    print("✅ src/main.py exists")
    
    # Check subdirectories
    handlers_subdir = os.path.join(src_dir, "handlers")
    engine_subdir = os.path.join(src_dir, "engine")
    storage_subdir = os.path.join(src_dir, "storage")
    events_subdir = os.path.join(src_dir, "events")
    utils_subdir = os.path.join(src_dir, "utils")
    
    if not os.path.exists(handlers_subdir):
        print("❌ src/handlers directory not found")
        return False
        
    if not os.path.exists(engine_subdir):
        print("❌ src/engine directory not found")
        return False
        
    if not os.path.exists(storage_subdir):
        print("❌ src/storage directory not found")
        return False
        
    if not os.path.exists(events_subdir):
        print("❌ src/events directory not found")
        return False
        
    if not os.path.exists(utils_subdir):
        print("❌ src/utils directory not found")
        return False
    
    print("✅ Subdirectories exist")
    
    print("\n🎉 Serverless Cache Structure Test Complete!")
    print("=" * 50)
    print("Summary:")
    print("  ✅ Directory structure: Correct")
    print("  ✅ Configuration files: Present")
    print("  ✅ Source files: Present")
    print("  ✅ Subdirectories: Present")
    
    return True

if __name__ == "__main__":
    try:
        success = test_serverless_cache_structure()
        if success:
            print("\n🎯 Serverless cache structure is ready!")
            sys.exit(0)
        else:
            print("\n❌ Serverless cache structure has issues!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)