import os
import hashlib
import json
import time
from pathlib import Path
from .config import get_config

class Cache:
    def __init__(self, project_path=None):
        self.config = get_config()
        
        # Try to find a project-specific cache first
        try:
            project_root = self._find_project_root()
            self.cache_dir = project_root / ".aicache"
        except FileNotFoundError:
            # If not in a project, use the global cache directory
            self.cache_dir = Path(self.config["cache_dir"]).expanduser()

        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _find_project_root(self):
        # Find the project root by looking for a .git directory
        current_dir = Path.cwd()
        while current_dir != current_dir.parent:
            if (current_dir / ".git").is_dir():
                return current_dir
            current_dir = current_dir.parent
        raise FileNotFoundError("Could not find the project root. Make sure you are in a git repository.")

    def _get_cache_key(self, prompt, context):
        # Create a unique key for the cache entry
        hasher = hashlib.sha256()
        hasher.update(prompt.encode('utf-8'))
        if context:
            hasher.update(str(context).encode('utf-8'))
        return hasher.hexdigest()

    def get(self, prompt, context=None):
        # Get a cache entry
        cache_key = self._get_cache_key(prompt, context)
        cache_file = self.cache_dir / cache_key
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                try:
                    data = json.load(f)
                    if self.config["ttl"] > 0:
                        age = time.time() - data.get("timestamp", 0)
                        if age > self.config["ttl"]:
                            # Cache entry has expired
                            self.delete(cache_key)
                            return None
                    return data
                except json.JSONDecodeError:
                    return None
        return None

    def set(self, prompt, response, context=None):
        # Set a cache entry
        cache_key = self._get_cache_key(prompt, context)
        cache_file = self.cache_dir / cache_key
        with open(cache_file, 'w') as f:
            json.dump({
                "prompt": prompt,
                "response": response,
                "context": context,
                "timestamp": time.time()
            }, f)
        
        # Prune cache by size if needed
        self.prune_by_size()

    def list(self, verbose=False):
        # List all cache entries
        entries = []
        for f in self.cache_dir.iterdir():
            if verbose:
                with open(f, 'r') as cache_file:
                    try:
                        data = json.load(cache_file)
                        entries.append({
                            "cache_key": f.name,
                            "prompt": data.get("prompt"),
                            "context": data.get("context")
                        })
                    except json.JSONDecodeError:
                        # Handle cases where the file is not a valid JSON
                        entries.append({
                            "cache_key": f.name,
                            "error": "Invalid JSON format"
                        })
            else:
                entries.append(f.name)
        return entries

    def clear(self):
        # Clear the cache
        for f in self.cache_dir.iterdir():
            f.unlink()

    def inspect(self, cache_key):
        # Inspect a cache entry
        cache_file = self.cache_dir / cache_key
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)
        return None

    def delete(self, cache_key):
        # Delete a specific cache entry
        cache_file = self.cache_dir / cache_key
        if cache_file.exists():
            cache_file.unlink()
            return True
        return False

    def prune(self):
        # Remove expired cache entries
        if self.config["ttl"] <= 0:
            return 0  # TTL is not enabled

        pruned_count = 0
        for f in self.cache_dir.iterdir():
            with open(f, 'r') as cache_file:
                try:
                    data = json.load(cache_file)
                    age = time.time() - data.get("timestamp", 0)
                    if age > self.config["ttl"]:
                        f.unlink()
                        pruned_count += 1
                except (json.JSONDecodeError, IsADirectoryError):
                    # Ignore invalid JSON files or directories
                    pass
        return pruned_count

    def get_cache_size(self):
        # Get the total size of the cache directory
        return sum(f.stat().st_size for f in self.cache_dir.glob('**/*') if f.is_file())

    def prune_by_size(self):
        # Prune the cache by size, removing the oldest entries first
        if self.config["cache_size_limit"] <= 0:
            return

        cache_size = self.get_cache_size()
        if cache_size > self.config["cache_size_limit"]:
            # Get all cache entries with their timestamps
            entries = []
            for f in self.cache_dir.iterdir():
                try:
                    with open(f, 'r') as cache_file:
                        data = json.load(cache_file)
                        entries.append((f, data.get("timestamp", 0)))
                except (json.JSONDecodeError, IsADirectoryError):
                    pass
            
            # Sort entries by timestamp (oldest first)
            entries.sort(key=lambda x: x[1])

            # Prune oldest entries until the size is below the limit
            for f, _ in entries:
                if self.get_cache_size() <= self.config["cache_size_limit"]:
                    break
                f.unlink()

    def stats(self):
        # Get cache statistics
        num_entries = len(list(self.cache_dir.iterdir()))
        total_size = self.get_cache_size()
        
        num_expired = 0
        if self.config["ttl"] > 0:
            for f in self.cache_dir.iterdir():
                with open(f, 'r') as cache_file:
                    try:
                        data = json.load(cache_file)
                        age = time.time() - data.get("timestamp", 0)
                        if age > self.config["ttl"]:
                            num_expired += 1
                    except (json.JSONDecodeError, IsADirectoryError):
                        pass

        return {
            "num_entries": num_entries,
            "total_size": total_size,
            "num_expired": num_expired,
        }
