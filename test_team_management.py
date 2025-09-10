#!/usr/bin/env python3
"""
Test for Phase 4: Team Management Interface Structure
"""

import sys
import os

def test_team_management_structure():
    print("🧪 Testing Phase 4: Team Management Interface Structure")
    print("=" * 60)
    
    # Check if team-management directory exists
    management_dir = "team-management"
    if not os.path.exists(management_dir):
        print("❌ team-management directory not found")
        return False
    
    print("✅ team-management directory exists")
    
    # Check requirements.txt
    requirements_path = os.path.join(management_dir, "requirements.txt")
    if not os.path.exists(requirements_path):
        print("❌ requirements.txt not found")
        return False
    
    print("✅ requirements.txt exists")
    
    # Check src directory
    src_dir = os.path.join(management_dir, "src")
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
    subdirs = ["controllers", "services", "models", "realtime", "utils"]
    
    for subdir in subdirs:
        subdir_path = os.path.join(src_dir, subdir)
        if not os.path.exists(subdir_path):
            print(f"❌ src/{subdir} directory not found")
            return False
    
    print("✅ Subdirectories exist")
    
    print("\n🎉 Team Management Interface Structure Test Complete!")
    print("=" * 60)
    print("Summary:")
    print("  ✅ Directory structure: Correct")
    print("  ✅ Configuration files: Present")
    print("  ✅ Source files: Present")
    print("  ✅ Subdirectories: Present")
    
    return True

if __name__ == "__main__":
    try:
        success = test_team_management_structure()
        if success:
            print("\n🎯 Team management interface structure is ready!")
            sys.exit(0)
        else:
            print("\n❌ Team management interface structure has issues!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)