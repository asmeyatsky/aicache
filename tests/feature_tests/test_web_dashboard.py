#!/usr/bin/env python3
"""
Test for Phase 4: Web Dashboard Structure
"""

import sys
import os

def test_web_dashboard_structure():
    print("🧪 Testing Phase 4: Web Dashboard Structure")
    print("=" * 50)
    
    # Check if web-dashboard directory exists
    dashboard_dir = "web-dashboard"
    if not os.path.exists(dashboard_dir):
        print("❌ web-dashboard directory not found")
        return False
    
    print("✅ web-dashboard directory exists")
    
    # Check package.json
    package_json_path = os.path.join(dashboard_dir, "package.json")
    if not os.path.exists(package_json_path):
        print("❌ package.json not found")
        return False
    
    print("✅ package.json exists")
    
    # Check requirements.txt
    requirements_path = os.path.join(dashboard_dir, "requirements.txt")
    if not os.path.exists(requirements_path):
        print("❌ requirements.txt not found")
        return False
    
    print("✅ requirements.txt exists")
    
    # Check src directory
    src_dir = os.path.join(dashboard_dir, "src")
    if not os.path.exists(src_dir):
        print("❌ src directory not found")
        return False
    
    print("✅ src directory exists")
    
    # Check frontend and backend directories
    frontend_dir = os.path.join(src_dir, "frontend")
    backend_dir = os.path.join(src_dir, "backend")
    
    if not os.path.exists(frontend_dir):
        print("❌ src/frontend directory not found")
        return False
        
    if not os.path.exists(backend_dir):
        print("❌ src/backend directory not found")
        return False
    
    print("✅ Frontend and backend directories exist")
    
    # Check main entry points
    frontend_index = os.path.join(frontend_dir, "index.js")
    backend_main = os.path.join(backend_dir, "main.py")
    
    if not os.path.exists(frontend_index):
        print("❌ src/frontend/index.js not found")
        return False
        
    if not os.path.exists(backend_main):
        print("❌ src/backend/main.py not found")
        return False
    
    print("✅ Main entry points exist")
    
    # Check subdirectories
    frontend_subdirs = ["components", "pages", "services", "utils"]
    backend_subdirs = ["api", "models", "realtime"]
    
    for subdir in frontend_subdirs:
        if not os.path.exists(os.path.join(frontend_dir, subdir)):
            print(f"❌ src/frontend/{subdir} directory not found")
            return False
    
    for subdir in backend_subdirs:
        if not os.path.exists(os.path.join(backend_dir, subdir)):
            print(f"❌ src/backend/{subdir} directory not found")
            return False
    
    print("✅ Subdirectories exist")
    
    print("\n🎉 Web Dashboard Structure Test Complete!")
    print("=" * 50)
    print("Summary:")
    print("  ✅ Directory structure: Correct")
    print("  ✅ Configuration files: Present")
    print("  ✅ Source files: Present")
    print("  ✅ Subdirectories: Present")
    
    return True

if __name__ == "__main__":
    try:
        success = test_web_dashboard_structure()
        if success:
            print("\n🎯 Web dashboard structure is ready!")
            sys.exit(0)
        else:
            print("\n❌ Web dashboard structure has issues!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)