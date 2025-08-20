import os
import hashlib
import json
from pathlib import Path

class Cache:
    def __init__(self, project_path=None):
        self.project_path = self._find_project_root() if project_path is None else Path(project_path)
        self.cache_dir = self.project_path / ".aicache"
        self.cache_dir.mkdir(exist_ok=True)

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
                return json.load(f)
        return None

    def set(self, prompt, response, context=None):
        # Set a cache entry
        cache_key = self._get_cache_key(prompt, context)
        cache_file = self.cache_dir / cache_key
        with open(cache_file, 'w') as f:
            json.dump({
                "prompt": prompt,
                "response": response,
                "context": context
            }, f)

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
