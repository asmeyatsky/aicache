#!/usr/bin/env python3
"""
Test for Phase 5: Emergent Behavior Detection System Structure
"""

import sys
import os

def test_emergent_behavior_structure():
    print("🧪 Testing Phase 5: Emergent Behavior Detection System Structure")
    print("=" * 70)
    
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
    
    # Check observer module
    observer_dir = os.path.join(src_dir, "observer")
    if not os.path.exists(observer_dir):
        print("❌ src/observer directory not found")
        return False
    
    print("✅ src/observer directory exists")
    
    # Check behavior observer file
    behavior_observer_path = os.path.join(observer_dir, "behavior_observer.py")
    if not os.path.exists(behavior_observer_path):
        print("❌ src/observer/behavior_observer.py not found")
        return False
    
    print("✅ src/observer/behavior_observer.py exists")
    
    # Check other required directories
    required_dirs = ["analyzer", "modeler", "insight", "recommender", "utils"]
    
    for dir_name in required_dirs:
        dir_path = os.path.join(src_dir, dir_name)
        if not os.path.exists(dir_path):
            print(f"❌ src/{dir_name} directory not found")
            return False
    
    print("✅ All required directories exist")
    
    print("\n🎉 Emergent Behavior Detection System Structure Test Complete!")
    print("=" * 70)
    print("Summary:")
    print("  ✅ Directory structure: Correct")
    print("  ✅ Configuration files: Present")
    print("  ✅ Source files: Present")
    print("  ✅ Subdirectories: Present")
    
    return True

if __name__ == "__main__":
    try:
        success = test_emergent_behavior_structure()
        if success:
            print("\n🎯 Emergent behavior detection system structure is ready!")
            sys.exit(0)
        else:
            print("\n❌ Emergent behavior detection system structure has issues!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)