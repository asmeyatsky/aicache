#!/usr/bin/env python3
"""
Test for Phase 5: Decentralized Identity System Structure
"""

import sys
import os

def test_decentralized_identity_structure():
    print("🧪 Testing Phase 5: Decentralized Identity System Structure")
    print("=" * 60)
    
    # Check if decentralized-identity directory exists
    identity_dir = "decentralized-identity"
    if not os.path.exists(identity_dir):
        print("❌ decentralized-identity directory not found")
        return False
    
    print("✅ decentralized-identity directory exists")
    
    # Check config directory
    config_dir = os.path.join(identity_dir, "config")
    if not os.path.exists(config_dir):
        print("❌ config directory not found")
        return False
    
    print("✅ config directory exists")
    
    # Check configuration file
    config_file = os.path.join(config_dir, "default.yaml")
    if not os.path.exists(config_file):
        print("❌ config/default.yaml not found")
        return False
    
    print("✅ config/default.yaml exists")
    
    # Check src directory
    src_dir = os.path.join(identity_dir, "src")
    if not os.path.exists(src_dir):
        print("❌ src directory not found")
        return False
    
    print("✅ src directory exists")
    
    # Check main source files
    required_files = [
        "extension.ts",
        "aicacheClient.ts",
        "cachePanelViewProvider.ts",
        "teamPresenceViewProvider.ts"
    ]
    
    for required_file in required_files:
        file_path = os.path.join(src_dir, required_file)
        if not os.path.exists(file_path):
            print(f"❌ src/{required_file} not found")
            return False
    
    print("✅ Main source files exist")
    
    # Check subdirectories
    subdirs = ["identity", "crypto", "verification", "integration", "utils"]
    
    for subdir in subdirs:
        subdir_path = os.path.join(src_dir, subdir)
        if not os.path.exists(subdir_path):
            print(f"❌ src/{subdir} directory not found")
            return False
    
    print("✅ Subdirectories exist")
    
    # Check media directory
    media_dir = os.path.join(identity_dir, "media")
    if not os.path.exists(media_dir):
        print("❌ media directory not found")
        return False
    
    print("✅ media directory exists")
    
    # Check media files
    media_files = ["reset.css", "vscode.css", "main.css", "team.css", "main.js", "team.js"]
    
    for media_file in media_files:
        file_path = os.path.join(media_dir, media_file)
        if not os.path.exists(file_path):
            print(f"❌ media/{media_file} not found")
            return False
    
    print("✅ Media files exist")
    
    print("\n🎉 Decentralized Identity System Structure Test Complete!")
    print("=" * 60)
    print("Summary:")
    print("  ✅ Directory structure: Correct")
    print("  ✅ Configuration files: Present")
    print("  ✅ Source files: Present")
    print("  ✅ Subdirectories: Present")
    print("  ✅ Media files: Present")
    
    return True

if __name__ == "__main__":
    try:
        success = test_decentralized_identity_structure()
        if success:
            print("\n🎯 Decentralized identity system structure is ready!")
            sys.exit(0)
        else:
            print("\n❌ Decentralized identity system structure has issues!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)