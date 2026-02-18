import unittest
import shutil
import os
import time
import json
from pathlib import Path
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from aicache.core import Cache


class TestCache(unittest.TestCase):
    def setUp(self):
        # Use a temporary directory for the cache to avoid interfering with the real cache
        self.test_cache_dir = Path.cwd() / "temp_test_cache"
        self.test_cache_dir.mkdir(exist_ok=True)
        self.cache = Cache(cache_dir=self.test_cache_dir)

    def tearDown(self):
        # Clean up the temporary cache directory
        shutil.rmtree(self.test_cache_dir)

    def test_set_and_get_simple(self):
        """Test setting and getting a cache entry without context."""
        prompt = "What is the capital of France?"
        response = "Paris"
        self.cache.set(prompt, response)
        cached_data = self.cache.get(prompt)
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data["prompt"], prompt)
        self.assertEqual(cached_data["response"], response)

    def test_set_and_get_with_context(self):
        """Test that context creates a distinct cache entry."""
        prompt = "Translate 'hello'"
        response_en = "hello"
        response_fr = "bonjour"
        context_en = {"lang": "en"}
        context_fr = {"lang": "fr"}

        self.cache.set(prompt, response_en, context_en)
        self.cache.set(prompt, response_fr, context_fr)

        # Verify that the correct response is returned for each context
        self.assertEqual(self.cache.get(prompt, context_en)["response"], response_en)
        self.assertEqual(self.cache.get(prompt, context_fr)["response"], response_fr)

    def test_get_non_existent(self):
        """Test getting a cache entry that does not exist."""
        self.assertIsNone(self.cache.get("non_existent_prompt"))

    def test_list_and_inspect_and_delete(self):
        """Test the full workflow: list, inspect, and delete."""
        prompt = "test_list_inspect_delete"
        response = "data"
        self.cache.set(prompt, response)

        # Test list
        entries = self.cache.list(verbose=False)
        self.assertEqual(len(entries), 1)
        cache_key = entries[0]

        # Test list verbose
        verbose_entries = self.cache.list(verbose=True)
        self.assertEqual(len(verbose_entries), 1)
        self.assertEqual(verbose_entries[0]["cache_key"], cache_key)
        self.assertEqual(verbose_entries[0]["prompt"], prompt)

        # Test inspect
        inspected_data = self.cache.inspect(cache_key)
        self.assertIsNotNone(inspected_data)
        self.assertEqual(inspected_data["response"], response)

        # Test delete
        self.assertTrue(self.cache.delete(cache_key))
        self.assertIsNone(self.cache.inspect(cache_key))
        self.assertEqual(len(self.cache.list()), 0)

    def test_clear(self):
        """Test clearing the entire cache."""
        self.cache.set("prompt1", "response1")
        self.cache.set("prompt2", "response2")
        self.assertEqual(len(self.cache.list()), 2)
        self.cache.clear()
        self.assertEqual(len(self.cache.list()), 0)

    def test_prune(self):
        """Test pruning of expired cache entries."""
        prompt = "expiring_prompt"
        response = "expiring_response"
        self.cache.set(prompt, response)

        # Entry should not be pruned immediately
        self.assertEqual(self.cache.prune(max_age_days=1), 0)

        # Manually set the timestamp to be old
        cache_key = self.cache._get_cache_key(prompt)
        cache_file = (
            self.cache.cache_dir / f"{cache_key}.json"
        )  # Fixed: add .json extension
        with open(cache_file, "r+") as f:
            data = json.load(f)
            data["timestamp"] = time.time() - (31 * 86400)  # 31 days ago
            f.seek(0)
            json.dump(data, f)
            f.truncate()

        # Now the entry should be pruned
        self.assertEqual(self.cache.prune(max_age_days=30), 1)
        self.assertEqual(len(self.cache.list()), 0)

    def test_stats(self):
        """Test cache statistics."""
        self.cache.set("stats_prompt_1", "response1")
        self.cache.set("stats_prompt_2", "response2")
        stats = self.cache.stats()
        self.assertEqual(stats["num_entries"], 2)
        self.assertGreater(stats["total_size"], 0)


if __name__ == "__main__":
    unittest.main()
