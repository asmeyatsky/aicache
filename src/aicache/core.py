import os
import hashlib
import json
import time
from pathlib import Path
from .config import get_config

class Cache:
    def __init__(self, cache_dir=None):
        if cache_dir is None:
            cache_dir = os.path.expanduser("~/.cache/aicache")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, prompt, context=None):
        """Creates a unique, deterministic cache key from the prompt and context."""
        hasher = hashlib.sha256()
        hasher.update(prompt.encode('utf-8'))
        if context:
            # Sort context dict by key for consistent hash
            sorted_context = json.dumps(context, sort_keys=True)
            hasher.update(sorted_context.encode('utf-8'))
        return hasher.hexdigest()

    def get(self, prompt, context=None):
        """Gets a cache entry by prompt and context."""
        cache_key = self._get_cache_key(prompt, context)
        cache_file = self.cache_dir / cache_key
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return None
        return None

    def set(self, prompt, response, context=None):
        """Sets a cache entry by prompt, response, and context."""
        cache_key = self._get_cache_key(prompt, context)
        cache_file = self.cache_dir / cache_key
        with open(cache_file, 'w') as f:
            json.dump({
                "prompt": prompt,
                "response": response,
                "context": context,
                "timestamp": time.time(),
            }, f)

    def list(self, verbose=False):
        """Lists all cache entries."""
        entries = []
        for f in self.cache_dir.iterdir():
            if not f.is_file():
                continue
            if verbose:
                with open(f, 'r') as cache_file:
                    try:
                        data = json.load(cache_file)
                        entries.append({
                            "cache_key": f.name,
                            "prompt": data.get("prompt"),
                            "context": data.get("context"),
                            "timestamp": data.get("timestamp"),
                        })
                    except json.JSONDecodeError:
                        entries.append({"cache_key": f.name, "error": "Invalid JSON"})
            else:
                entries.append(f.name)
        return entries

    def clear(self):
        """Clears the entire cache."""
        for f in self.cache_dir.iterdir():
            if f.is_file():
                f.unlink()

    def inspect(self, cache_key):
        """Inspects a specific cache entry by its key."""
        cache_file = self.cache_dir / cache_key
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {"error": "Invalid JSON"}
        return None

    def delete(self, cache_key):
        """Deletes a specific cache entry by its key."""
        cache_file = self.cache_dir / cache_key
        if cache_file.exists() and cache_file.is_file():
            cache_file.unlink()
            return True
        return False

    def prune(self, max_age_days=30):
        """Removes cache entries older than a certain number of days."""
        pruned_count = 0
        for f in self.cache_dir.iterdir():
            if not f.is_file():
                continue
            try:
                with open(f, 'r') as cache_file:
                    data = json.load(cache_file)
                    timestamp = data.get("timestamp")
                    if timestamp and (time.time() - timestamp) > (max_age_days * 86400):
                        f.unlink()
                        pruned_count += 1
            except (json.JSONDecodeError, FileNotFoundError):
                continue
        return pruned_count

    def stats(self):
        """Gets statistics about the cache."""
        num_entries = 0
        total_size = 0
        for f in self.cache_dir.iterdir():
            if f.is_file():
                num_entries += 1
                total_size += f.stat().st_size
        return {"num_entries": num_entries, "total_size": total_size}
