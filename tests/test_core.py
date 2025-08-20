import unittest
import shutil
import os
from pathlib import Path
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from aicache.core import Cache

class TestCache(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = Path.cwd() / "test_project"
        self.test_dir.mkdir()
        (self.test_dir / ".git").mkdir()
        # To make this test self-contained, we need to be inside the test directory
        # so that the Cache class can find the .git directory.
        # We will change back to the original directory in tearDown.
        self.original_dir = Path.cwd()
        os.chdir(self.test_dir)
        self.cache = Cache()

    def tearDown(self):
        # Change back to the original directory and remove the temporary directory
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_cache_creation(self):
        self.assertTrue((self.test_dir / ".aicache").is_dir())

    def test_set_and_get(self):
        prompt = "Hello"
        response = "World"
        self.cache.set(prompt, response)
        cached_data = self.cache.get(prompt)
        self.assertEqual(cached_data["prompt"], prompt)
        self.assertEqual(cached_data["response"], response)

    def test_list(self):
        self.cache.set("prompt1", "response1")
        self.cache.set("prompt2", "response2")
        self.assertEqual(len(self.cache.list()), 2)

    def test_clear(self):
        self.cache.set("prompt1", "response1")
        self.cache.clear()
        self.assertEqual(len(self.cache.list()), 0)

    def test_get_cache_key(self):
        key1 = self.cache._get_cache_key("prompt", "context")
        key2 = self.cache._get_cache_key("prompt", "context")
        self.assertEqual(key1, key2)
        key3 = self.cache._get_cache_key("prompt", "different_context")
        self.assertNotEqual(key1, key3)

if __name__ == '__main__':
    unittest.main()
