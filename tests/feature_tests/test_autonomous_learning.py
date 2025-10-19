#!/usr/bin/env python3
"""
Test for Phase 5: Autonomous Learning System Structure
"""

import sys
import os

def test_autonomous_learning_structure():
    print("🧪 Testing Phase 5: Autonomous Learning System Structure")
    print("=" * 60)
    
    # Check if autonomous-learning directory exists
    learning_dir = "autonomous-learning"
    if not os.path.exists(learning_dir):
        print("❌ autonomous-learning directory not found")
        return False
    
    print("✅ autonomous-learning directory exists")
    
    # Check requirements.txt
    requirements_path = os.path.join(learning_dir, "requirements.txt")
    if not os.path.exists(requirements_path):
        print("❌ requirements.txt not found")
        return False
    
    print("✅ requirements.txt exists")
    
    # Check src directory
    src_dir = os.path.join(learning_dir, "src")
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
    subdirs = ["core", "meta_learning", "nas", "prompt_engineering", "self_modification", "utils", "tests"]
    
    for subdir in subdirs:
        subdir_path = os.path.join(src_dir, subdir)
        if not os.path.exists(subdir_path):
            print(f"❌ src/{subdir} directory not found")
            return False
    
    print("✅ Subdirectories exist")
    
    print("\n🎉 Autonomous Learning System Structure Test Complete!")
    print("=" * 60)
    print("Summary:")
    print("  ✅ Directory structure: Correct")
    print("  ✅ Configuration files: Present")
    print("  ✅ Source files: Present")
    print("  ✅ Subdirectories: Present")
    
    return True

if __name__ == "__main__":
    try:
        success = test_autonomous_learning_structure()
        if success:
            print("\n🎯 Autonomous learning system structure is ready!")
            sys.exit(0)
        else:
            print("\n❌ Autonomous learning system structure has issues!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)