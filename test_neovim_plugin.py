#!/usr/bin/env python3
"""
Test for Phase 4: Neovim Plugin Structure
"""

import sys
import os

def test_neovim_plugin_structure():
    print("🧪 Testing Phase 4: Neovim Plugin Structure")
    print("=" * 50)
    
    # Check if neovim-plugin directory exists
    plugin_dir = "neovim-plugin"
    if not os.path.exists(plugin_dir):
        print("❌ neovim-plugin directory not found")
        return False
    
    print("✅ neovim-plugin directory exists")
    
    # Check lua directory structure
    lua_dir = os.path.join(plugin_dir, "lua", "aicache")
    if not os.path.exists(lua_dir):
        print("❌ lua/aicache directory not found")
        return False
    
    print("✅ lua/aicache directory exists")
    
    # Check main plugin files
    main_files = ["init.lua", "commands.lua", "cache.lua", "context.lua"]
    for main_file in main_files:
        if not os.path.exists(os.path.join(lua_dir, main_file)):
            print(f"❌ {main_file} not found")
            return False
    
    print("✅ Main plugin files exist")
    
    # Check UI directory and files
    ui_dir = os.path.join(lua_dir, "ui")
    if not os.path.exists(ui_dir):
        print("❌ ui directory not found")
        return False
    
    ui_files = ["status.lua", "float.lua"]
    for ui_file in ui_files:
        if not os.path.exists(os.path.join(ui_dir, ui_file)):
            print(f"❌ ui/{ui_file} not found")
            return False
    
    print("✅ UI directory and files exist")
    
    # Check plugin directory
    plugin_vim_dir = os.path.join(plugin_dir, "plugin")
    if not os.path.exists(plugin_vim_dir):
        print("❌ plugin directory not found")
        return False
    
    plugin_vim = os.path.join(plugin_vim_dir, "aicache.vim")
    if not os.path.exists(plugin_vim):
        print("❌ plugin/aicache.vim not found")
        return False
    
    print("✅ Plugin entry point exists")
    
    print("\n🎉 Neovim Plugin Structure Test Complete!")
    print("=" * 50)
    print("Summary:")
    print("  ✅ Directory structure: Correct")
    print("  ✅ Main plugin files: Present")
    print("  ✅ UI components: Present")
    print("  ✅ Plugin entry point: Present")
    
    return True

if __name__ == "__main__":
    try:
        success = test_neovim_plugin_structure()
        if success:
            print("\n🎯 Neovim plugin structure is ready!")
            sys.exit(0)
        else:
            print("\n❌ Neovim plugin structure has issues!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)