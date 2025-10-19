#!/usr/bin/env python3
"""
Test for Phase 4: Advanced Analytics Framework Structure
"""

import sys
import os

def test_analytics_framework_structure():
    print("🧪 Testing Phase 4: Advanced Analytics Framework Structure")
    print("=" * 60)
    
    # Check if analytics-framework directory exists
    framework_dir = "analytics-framework"
    if not os.path.exists(framework_dir):
        print("❌ analytics-framework directory not found")
        return False
    
    print("✅ analytics-framework directory exists")
    
    # Check requirements.txt
    requirements_path = os.path.join(framework_dir, "requirements.txt")
    if not os.path.exists(requirements_path):
        print("❌ requirements.txt not found")
        return False
    
    print("✅ requirements.txt exists")
    
    # Check src directory
    src_dir = os.path.join(framework_dir, "src")
    if not os.path.exists(src_dir):
        print("❌ src directory not found")
        return False
    
    print("✅ src directory exists")
    
    # Check main application file
    main_path = os.path.join(src_dir, "main.py")
    if not os.path.exists(main_path):
        print("❌ src/main.py not found")
        return False
    
    print("✅ src/main.py exists")
    
    # Check subdirectories
    subdirs = ["collectors", "processors", "engines", "models", "visualizations", "utils"]
    
    for subdir in subdirs:
        subdir_path = os.path.join(src_dir, subdir)
        if not os.path.exists(subdir_path):
            print(f"❌ src/{subdir} directory not found")
            return False
    
    print("✅ Subdirectories exist")
    
    print("\n🎉 Advanced Analytics Framework Structure Test Complete!")
    print("=" * 60)
    print("Summary:")
    print("  ✅ Directory structure: Correct")
    print("  ✅ Configuration files: Present")
    print("  ✅ Source files: Present")
    print("  ✅ Subdirectories: Present")
    
    return True

if __name__ == "__main__":
    try:
        success = test_analytics_framework_structure()
        if success:
            print("\n🎯 Advanced analytics framework structure is ready!")
            sys.exit(0)
        else:
            print("\n❌ Advanced analytics framework structure has issues!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)