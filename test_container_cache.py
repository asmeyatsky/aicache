#!/usr/bin/env python3
"""
Test for Phase 4: Container Cache Structure
"""

import sys
import os

def test_container_cache_structure():
    print("🧪 Testing Phase 4: Container Cache Structure")
    print("=" * 50)
    
    # Check if container-cache directory exists
    cache_dir = "container-cache"
    if not os.path.exists(cache_dir):
        print("❌ container-cache directory not found")
        return False
    
    print("✅ container-cache directory exists")
    
    # Check requirements.txt
    requirements_path = os.path.join(cache_dir, "requirements.txt")
    if not os.path.exists(requirements_path):
        print("❌ requirements.txt not found")
        return False
    
    print("✅ requirements.txt exists")
    
    # Check config directory
    config_dir = os.path.join(cache_dir, "config")
    if not os.path.exists(config_dir):
        print("❌ config directory not found")
        return False
    
    print("✅ config directory exists")
    
    # Check default config
    default_config_path = os.path.join(config_dir, "default.yaml")
    if not os.path.exists(default_config_path):
        print("❌ config/default.yaml not found")
        return False
    
    print("✅ config/default.yaml exists")
    
    # Check src directory
    src_dir = os.path.join(cache_dir, "src")
    if not os.path.exists(src_dir):
        print("❌ src directory not found")
        return False
    
    print("✅ src directory exists")
    
    # Check main server file
    server_path = os.path.join(src_dir, "server.py")
    if not os.path.exists(server_path):
        print("❌ src/server.py not found")
        return False
    
    print("✅ src/server.py exists")
    
    # Check subdirectories
    cache_subdir = os.path.join(src_dir, "cache")
    clients_subdir = os.path.join(src_dir, "clients")
    utils_subdir = os.path.join(src_dir, "utils")
    
    if not os.path.exists(cache_subdir):
        print("❌ src/cache directory not found")
        return False
        
    if not os.path.exists(clients_subdir):
        print("❌ src/clients directory not found")
        return False
        
    if not os.path.exists(utils_subdir):
        print("❌ src/utils directory not found")
        return False
    
    print("✅ Subdirectories exist")
    
    print("\n🎉 Container Cache Structure Test Complete!")
    print("=" * 50)
    print("Summary:")
    print("  ✅ Directory structure: Correct")
    print("  ✅ Configuration files: Present")
    print("  ✅ Source files: Present")
    print("  ✅ Subdirectories: Present")
    
    return True

if __name__ == "__main__":
    try:
        success = test_container_cache_structure()
        if success:
            print("\n🎯 Container cache structure is ready!")
            sys.exit(0)
        else:
            print("\n❌ Container cache structure has issues!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)