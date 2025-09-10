#!/usr/bin/env python3
"""
Test for Phase 4: GitHub App Structure
"""

import sys
import os

def test_github_app_structure():
    print("🧪 Testing Phase 4: GitHub App Structure")
    print("=" * 50)
    
    # Check if github-app directory exists
    app_dir = "github-app"
    if not os.path.exists(app_dir):
        print("❌ github-app directory not found")
        return False
    
    print("✅ github-app directory exists")
    
    # Check package.json
    package_json_path = os.path.join(app_dir, "package.json")
    if not os.path.exists(package_json_path):
        print("❌ package.json not found")
        return False
    
    print("✅ package.json exists")
    
    # Check src directory
    src_dir = os.path.join(app_dir, "src")
    if not os.path.exists(src_dir):
        print("❌ src directory not found")
        return False
    
    print("✅ src directory exists")
    
    # Check main application file
    index_js_path = os.path.join(src_dir, "index.js")
    if not os.path.exists(index_js_path):
        print("❌ src/index.js not found")
        return False
    
    print("✅ src/index.js exists")
    
    # Check subdirectories
    events_dir = os.path.join(src_dir, "events")
    utils_dir = os.path.join(src_dir, "utils")
    
    if not os.path.exists(events_dir):
        print("❌ src/events directory not found")
        return False
        
    if not os.path.exists(utils_dir):
        print("❌ src/utils directory not found")
        return False
    
    print("✅ Subdirectories exist")
    
    print("\n🎉 GitHub App Structure Test Complete!")
    print("=" * 50)
    print("Summary:")
    print("  ✅ Directory structure: Correct")
    print("  ✅ Configuration files: Present")
    print("  ✅ Source files: Present")
    print("  ✅ Subdirectories: Present")
    
    return True

if __name__ == "__main__":
    try:
        success = test_github_app_structure()
        if success:
            print("\n🎯 GitHub App structure is ready!")
            sys.exit(0)
        else:
            print("\n❌ GitHub App structure has issues!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)