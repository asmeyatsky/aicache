#!/usr/bin/env python3
"""
Test for Phase 4: JupyterLab Extension Structure
"""

import sys
import os

def test_jupyterlab_extension_structure():
    print("🧪 Testing Phase 4: JupyterLab Extension Structure")
    print("=" * 50)
    
    # Check if jupyterlab-extension directory exists
    extension_dir = "jupyterlab-extension"
    if not os.path.exists(extension_dir):
        print("❌ jupyterlab-extension directory not found")
        return False
    
    print("✅ jupyterlab-extension directory exists")
    
    # Check package.json
    package_json_path = os.path.join(extension_dir, "package.json")
    if not os.path.exists(package_json_path):
        print("❌ package.json not found")
        return False
    
    print("✅ package.json exists")
    
    # Check tsconfig.json
    tsconfig_path = os.path.join(extension_dir, "tsconfig.json")
    if not os.path.exists(tsconfig_path):
        print("❌ tsconfig.json not found")
        return False
    
    print("✅ tsconfig.json exists")
    
    # Check src directory
    src_dir = os.path.join(extension_dir, "src")
    if not os.path.exists(src_dir):
        print("❌ src directory not found")
        return False
    
    print("✅ src directory exists")
    
    # Check main extension file
    index_ts_path = os.path.join(src_dir, "index.ts")
    if not os.path.exists(index_ts_path):
        print("❌ src/index.ts not found")
        return False
    
    print("✅ src/index.ts exists")
    
    # Check ui directory
    ui_dir = os.path.join(src_dir, "ui")
    if not os.path.exists(ui_dir):
        print("❌ src/ui directory not found")
        return False
    
    print("✅ src/ui directory exists")
    
    # Check style directory
    style_dir = os.path.join(extension_dir, "style")
    if not os.path.exists(style_dir):
        print("❌ style directory not found")
        return False
    
    print("✅ style directory exists")
    
    print("\n🎉 JupyterLab Extension Structure Test Complete!")
    print("=" * 50)
    print("Summary:")
    print("  ✅ Directory structure: Correct")
    print("  ✅ Configuration files: Present")
    print("  ✅ Source files: Present")
    print("  ✅ UI directory: Present")
    print("  ✅ Style directory: Present")
    
    return True

if __name__ == "__main__":
    try:
        success = test_jupyterlab_extension_structure()
        if success:
            print("\n🎯 JupyterLab extension structure is ready!")
            sys.exit(0)
        else:
            print("\n❌ JupyterLab extension structure has issues!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)