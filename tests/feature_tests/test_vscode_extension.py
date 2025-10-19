#!/usr/bin/env python3
"""
Test for Phase 4: VS Code Extension Structure
"""

import sys
import os
import json

def test_vscode_extension_structure():
    print("🧪 Testing Phase 4: VS Code Extension Structure")
    print("=" * 50)
    
    # Check if vscode-extension directory exists
    extension_dir = "vscode-extension"
    if not os.path.exists(extension_dir):
        print("❌ vscode-extension directory not found")
        return False
    
    print("✅ vscode-extension directory exists")
    
    # Check package.json
    package_json_path = os.path.join(extension_dir, "package.json")
    if not os.path.exists(package_json_path):
        print("❌ package.json not found")
        return False
    
    try:
        with open(package_json_path, 'r') as f:
            package_data = json.load(f)
        
        # Check required fields
        required_fields = ['name', 'version', 'engines', 'main', 'contributes']
        for field in required_fields:
            if field not in package_data:
                print(f"❌ Required field '{field}' missing from package.json")
                return False
                
        print("✅ package.json is valid")
    except Exception as e:
        print(f"❌ Invalid package.json: {e}")
        return False
    
    # Check src directory and main files
    src_dir = os.path.join(extension_dir, "src")
    if not os.path.exists(src_dir):
        print("❌ src directory not found")
        return False
    
    print("✅ src directory exists")
    
    # Check main extension file
    extension_file = os.path.join(src_dir, "extension.ts")
    if not os.path.exists(extension_file):
        print("❌ src/extension.ts not found")
        return False
    
    print("✅ src/extension.ts exists")
    
    # Check aicache client
    client_file = os.path.join(src_dir, "aicacheClient.ts")
    if not os.path.exists(client_file):
        print("❌ src/aicacheClient.ts not found")
        return False
    
    print("✅ src/aicacheClient.ts exists")
    
    # Check view providers
    cache_panel_file = os.path.join(src_dir, "cachePanelViewProvider.ts")
    team_panel_file = os.path.join(src_dir, "teamPresenceViewProvider.ts")
    
    if not os.path.exists(cache_panel_file):
        print("❌ src/cachePanelViewProvider.ts not found")
        return False
        
    if not os.path.exists(team_panel_file):
        print("❌ src/teamPresenceViewProvider.ts not found")
        return False
    
    print("✅ View provider files exist")
    
    # Check media directory
    media_dir = os.path.join(extension_dir, "media")
    if not os.path.exists(media_dir):
        print("❌ media directory not found")
        return False
    
    print("✅ media directory exists")
    
    # Check CSS files
    css_files = ["reset.css", "vscode.css", "main.css", "team.css"]
    for css_file in css_files:
        if not os.path.exists(os.path.join(media_dir, css_file)):
            print(f"❌ media/{css_file} not found")
            return False
    
    print("✅ CSS files exist")
    
    # Check JavaScript files
    js_files = ["main.js", "team.js"]
    for js_file in js_files:
        if not os.path.exists(os.path.join(media_dir, js_file)):
            print(f"❌ media/{js_file} not found")
            return False
    
    print("✅ JavaScript files exist")
    
    print("\n🎉 VS Code Extension Structure Test Complete!")
    print("=" * 50)
    print("Summary:")
    print("  ✅ Directory structure: Correct")
    print("  ✅ package.json: Valid")
    print("  ✅ Extension files: Present")
    print("  ✅ Client files: Present")
    print("  ✅ View providers: Present")
    print("  ✅ Media files: Present")
    
    return True

if __name__ == "__main__":
    try:
        success = test_vscode_extension_structure()
        if success:
            print("\n🎯 VS Code extension structure is ready!")
            sys.exit(0)
        else:
            print("\n❌ VS Code extension structure has issues!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)