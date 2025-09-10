#!/usr/bin/env python3
"""
Test for Phase 5: Self-Healing Cache System Structure
"""

import sys
import os

def test_self_healing_structure():
    print("🧪 Testing Phase 5: Self-Healing Cache System Structure")
    print("=" * 60)
    
    # Check if self-healing directory exists
    healing_dir = "self-healing"
    if not os.path.exists(healing_dir):
        print("❌ self-healing directory not found")
        return False
    
    print("✅ self-healing directory exists")
    
    # Check requirements.txt
    requirements_path = os.path.join(healing_dir, "requirements.txt")
    if not os.path.exists(requirements_path):
        print("❌ requirements.txt not found")
        return False
    
    print("✅ requirements.txt exists")
    
    # Check src directory
    src_dir = os.path.join(healing_dir, "src")
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
    subdirs = ["health_monitor", "diagnostics", "healing", "audit", "utils", "tests"]
    
    for subdir in subdirs:
        subdir_path = os.path.join(src_dir, subdir)
        if not os.path.exists(subdir_path):
            print(f"❌ src/{subdir} directory not found")
            return False
    
    print("✅ Subdirectories exist")
    
    print("\n🎉 Self-Healing Cache System Structure Test Complete!")
    print("=" * 60)
    print("Summary:")
    print("  ✅ Directory structure: Correct")
    print("  ✅ Configuration files: Present")
    print("  ✅ Source files: Present")
    print("  ✅ Subdirectories: Present")
    
    return True

if __name__ == "__main__":
    try:
        success = test_self_healing_structure()
        if success:
            print("\n🎯 Self-healing cache system structure is ready!")
            sys.exit(0)
        else:
            print("\n❌ Self-healing cache system structure has issues!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)