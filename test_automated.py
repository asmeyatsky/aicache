#!/usr/bin/env python3
"""
Automated test script for aicache core functionality.
"""

import os
import sys
import subprocess
import tempfile
import shutil
import json
from pathlib import Path

def run_command(cmd, cwd=None, capture_output=True):
    """Run a command and return the result."""
    # Replace 'aicache' with 'python3 -m aicache' if it's at the start of the command
    if cmd.startswith("aicache "):
        cmd = "python3 -m aicache " + cmd[8:]
    elif cmd == "aicache":
        cmd = "python3 -m aicache"
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=capture_output, 
            text=True, 
            cwd=cwd,
            timeout=30
        )
        return result
    except subprocess.TimeoutExpired:
        print(f"Command timed out: {cmd}")
        return None
    except Exception as e:
        print(f"Error running command '{cmd}': {e}")
        return None

def test_basic_cache_operations():
    """Test basic cache operations."""
    print("Testing basic cache operations...")
    
    # Clear cache first
    result = run_command("aicache clear")
    if result is None or result.returncode != 0:
        print("❌ Failed to clear cache")
        return False
    
    # Test set operation
    result = run_command('aicache set "test prompt" "test response"')
    if result is None or result.returncode != 0:
        print("❌ Failed to set cache entry")
        return False
    
    # Test get operation
    result = run_command('aicache get "test prompt"')
    if result is None or result.returncode != 0:
        print("❌ Failed to get cache entry")
        return False
    
    # Parse JSON response
    try:
        data = json.loads(result.stdout)
        if data.get("response") != "test response":
            print("❌ Cache entry response mismatch")
            return False
    except json.JSONDecodeError:
        print("❌ Failed to parse JSON response")
        return False
    
    # Test list operation
    result = run_command("aicache list")
    if result is None or result.returncode != 0:
        print("❌ Failed to list cache entries")
        return False
    
    if not result.stdout.strip():
        print("❌ No cache entries found in list")
        return False
    
    print("✅ Basic cache operations passed")
    return True

def test_context_awareness():
    """Test context-aware caching."""
    print("Testing context-aware caching...")
    
    # Clear cache
    run_command("aicache clear")
    
    # Set entries with different contexts
    result1 = run_command('aicache set "test query" "response 1" --context \'{"model": "gpt-4"}\'')
    result2 = run_command('aicache set "test query" "response 2" --context \'{"model": "claude-3"}\'')
    
    if result1 is None or result1.returncode != 0 or result2 is None or result2.returncode != 0:
        print("❌ Failed to set context-aware entries")
        return False
    
    # Get entries with specific contexts
    result1 = run_command('aicache get "test query" --context \'{"model": "gpt-4"}\'')
    result2 = run_command('aicache get "test query" --context \'{"model": "claude-3"}\'')
    
    if result1 is None or result2 is None:
        print("❌ Failed to get context-aware entries")
        return False
    
    try:
        data1 = json.loads(result1.stdout)
        data2 = json.loads(result2.stdout)
        
        if data1.get("response") != "response 1":
            print("❌ Context-aware entry 1 mismatch")
            return False
            
        if data2.get("response") != "response 2":
            print("❌ Context-aware entry 2 mismatch")
            return False
    except json.JSONDecodeError:
        print("❌ Failed to parse JSON responses")
        return False
    
    print("✅ Context-aware caching passed")
    return True

def test_cache_management():
    """Test cache management operations."""
    print("Testing cache management...")
    
    # Clear cache
    run_command("aicache clear")
    
    # Add test entries
    run_command('aicache set "entry 1" "response 1"')
    run_command('aicache set "entry 2" "response 2"')
    
    # Test stats
    result = run_command("aicache stats")
    if result is None or result.returncode != 0:
        print("❌ Failed to get cache stats")
        return False
    
    if "Total entries: 2" not in result.stdout:
        print("❌ Stats don't show correct entry count")
        return False
    
    # Test list verbose
    result = run_command("aicache list -v")
    if result is None or result.returncode != 0:
        print("❌ Failed to list cache entries verbose")
        return False
    
    # Test inspection
    result = run_command("aicache list")
    if result is None or not result.stdout.strip():
        print("❌ No entries to inspect")
        return False
    
    # Get first entry key
    cache_key = result.stdout.strip().split('\n')[0]
    result = run_command(f"aicache inspect {cache_key}")
    if result is None or result.returncode != 0:
        print("❌ Failed to inspect cache entry")
        return False
    
    print("✅ Cache management operations passed")
    return True

def test_installation_features():
    """Test installation and wrapper features."""
    print("Testing installation features...")
    
    # Test list wrappers
    result = run_command("aicache install --list")
    if result is None or result.returncode != 0:
        print("❌ Failed to list available wrappers")
        return False
    
    # Test config creation
    result = run_command("aicache install --config")
    if result is None or result.returncode != 0:
        print("❌ Failed to create config file")
        return False
    
    print("✅ Installation features passed")
    return True

def main():
    """Run all tests."""
    print("🚀 Starting aicache automated tests")
    print("=" * 50)
    
    # Check if aicache is available
    result = run_command("aicache --help", capture_output=True)
    if result is None or result.returncode != 0:
        print("❌ aicache command not found. Please ensure it's installed and in PATH.")
        return False
    
    # Run tests
    tests = [
        test_basic_cache_operations,
        test_context_awareness,
        test_cache_management,
        test_installation_features
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)