#!/usr/bin/env python3
"""
Test for Phase 4: JetBrains Plugin Structure
"""

import sys
import os

def test_jetbrains_plugin_structure():
    print("🧪 Testing Phase 4: JetBrains Plugin Structure")
    print("=" * 50)
    
    # Check if jetbrains-plugin directory exists
    plugin_dir = "jetbrains-plugin"
    if not os.path.exists(plugin_dir):
        print("❌ jetbrains-plugin directory not found")
        return False
    
    print("✅ jetbrains-plugin directory exists")
    
    # Check build files
    build_files = ["build.gradle", "settings.gradle"]
    for build_file in build_files:
        if not os.path.exists(os.path.join(plugin_dir, build_file)):
            print(f"❌ {build_file} not found")
            return False
    
    print("✅ Build files exist")
    
    # Check src directory structure
    src_dir = os.path.join(plugin_dir, "src", "main", "java", "com", "aicache", "plugin")
    if not os.path.exists(src_dir):
        print("❌ src directory structure not found")
        return False
    
    print("✅ src directory structure exists")
    
    # Check main plugin class
    main_class = os.path.join(src_dir, "AicachePlugin.java")
    if not os.path.exists(main_class):
        print("❌ AicachePlugin.java not found")
        return False
    
    print("✅ AicachePlugin.java exists")
    
    # Check services
    services_dir = os.path.join(src_dir, "services")
    if not os.path.exists(services_dir):
        print("❌ services directory not found")
        return False
    
    service_class = os.path.join(services_dir, "AicacheService.java")
    if not os.path.exists(service_class):
        print("❌ AicacheService.java not found")
        return False
    
    print("✅ Services directory and classes exist")
    
    # Check actions
    actions_dir = os.path.join(src_dir, "actions")
    if not os.path.exists(actions_dir):
        print("❌ actions directory not found")
        return False
    
    action_classes = ["QueryCacheAction.java", "RefreshCacheAction.java"]
    for action_class in action_classes:
        if not os.path.exists(os.path.join(actions_dir, action_class)):
            print(f"❌ {action_class} not found")
            return False
    
    print("✅ Actions directory and classes exist")
    
    # Check UI components
    ui_dir = os.path.join(src_dir, "ui")
    if not os.path.exists(ui_dir):
        print("❌ ui directory not found")
        return False
    
    ui_class = os.path.join(ui_dir, "AicacheToolWindowFactory.java")
    if not os.path.exists(ui_class):
        print("❌ AicacheToolWindowFactory.java not found")
        return False
    
    print("✅ UI directory and classes exist")
    
    # Check resources
    meta_inf_dir = os.path.join(plugin_dir, "src", "main", "resources", "META-INF")
    if not os.path.exists(meta_inf_dir):
        print("❌ META-INF directory not found")
        return False
    
    plugin_xml = os.path.join(meta_inf_dir, "plugin.xml")
    if not os.path.exists(plugin_xml):
        print("❌ plugin.xml not found")
        return False
    
    print("✅ Resources and plugin.xml exist")
    
    print("\n🎉 JetBrains Plugin Structure Test Complete!")
    print("=" * 50)
    print("Summary:")
    print("  ✅ Directory structure: Correct")
    print("  ✅ Build files: Present")
    print("  ✅ Main plugin class: Present")
    print("  ✅ Services: Present")
    print("  ✅ Actions: Present")
    print("  ✅ UI components: Present")
    print("  ✅ Resources: Present")
    
    return True

if __name__ == "__main__":
    try:
        success = test_jetbrains_plugin_structure()
        if success:
            print("\n🎯 JetBrains plugin structure is ready!")
            sys.exit(0)
        else:
            print("\n❌ JetBrains plugin structure has issues!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)