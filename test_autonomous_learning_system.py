#!/usr/bin/env python3
"""
Test for Phase 5: Autonomous Learning System Structure
"""

import sys
import os

def test_autonomous_learning_structure():
    print("🧪 Testing Phase 5: Autonomous Learning System Structure")
    print("=" * 60)
    
    # Check if emergent-behavior directory exists
    behavior_dir = "emergent-behavior"
    if not os.path.exists(behavior_dir):
        print("❌ emergent-behavior directory not found")
        return False
    
    print("✅ emergent-behavior directory exists")
    
    # Check requirements.txt
    requirements_path = os.path.join(behavior_dir, "requirements.txt")
    if not os.path.exists(requirements_path):
        print("❌ requirements.txt not found")
        return False
    
    print("✅ requirements.txt exists")
    
    # Check src directory
    src_dir = os.path.join(behavior_dir, "src")
    if not os.path.exists(src_dir):
        print("❌ src directory not found")
        return False
    
    print("✅ src directory exists")
    
    # Check core module
    core_dir = os.path.join(src_dir, "core")
    if not os.path.exists(core_dir):
        print("❌ src/core directory not found")
        return False
    
    print("✅ src/core directory exists")
    
    # Check learning controller
    learning_controller_path = os.path.join(core_dir, "learning_controller.py")
    if not os.path.exists(learning_controller_path):
        print("❌ src/core/learning_controller.py not found")
        return False
    
    print("✅ src/core/learning_controller.py exists")
    
    # Check other required directories
    required_dirs = ["optimization", "meta_learning", "self_healing", "emergent_intelligence", "creative_solver", "utils"]
    
    for dir_name in required_dirs:
        dir_path = os.path.join(src_dir, dir_name)
        if not os.path.exists(dir_path):
            print(f"❌ src/{dir_name} directory not found")
            return False
    
    print("✅ All required directories exist")
    
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