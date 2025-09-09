"""
Enhanced core caching system with semantic search and intelligent management.
"""

import os
import asyncio
import aiosqlite
import aiofiles
import hashlib
import json
import time
import zlib
import logging
import shutil
import msgpack
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
from collections import defaultdict

from .config import get_config
try:
    from .semantic import SemanticCache, SemanticCacheEntry
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False
    SemanticCache = None
    SemanticCacheEntry = None

try:
    from .llm_service import LLMService
    LLM_SERVICE_AVAILABLE = True
except ImportError:
    LLM_SERVICE_AVAILABLE = False
    LLMService = None

logger = logging.getLogger(__name__)

@dataclass
class AdvancedContext:
    """Enhanced context with multi-dimensional awareness."""
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    cli: Optional[str] = None
    
    # Project context
    project_path: Optional[str] = None
    git_repo: Optional[str] = None
    language: Optional[str] = None
    framework: Optional[str] = None
    
    # User context
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Time context
    time_of_day: Optional[str] = None
    day_of_week: Optional[str] = None
    development_phase: Optional[str] = None
    
    # Additional metadata
    tags: Optional[List[str]] = None
    priority: Optional[str] = None  # low, normal, high
    cost_tier: Optional[str] = None  # cheap, moderate, expensive
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AdvancedContext':
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

@dataclass
class CacheMetrics:
    """Cache performance and usage metrics."""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    semantic_hits: int = 0
    exact_hits: int = 0
    
    total_cost_saved: float = 0.0
    total_time_saved: float = 0.0  # in seconds
    
    storage_size: int = 0  # in bytes
    compression_ratio: float = 1.0
    
    last_reset: float = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0
    
    @property
    def semantic_hit_rate(self) -> float:
        """Calculate semantic hit rate."""
        return self.semantic_hits / self.cache_hits if self.cache_hits > 0 else 0.0

class ProjectDetector:
    """Detects project context from file system."""
    
    @staticmethod
    def detect_context(path: str = ".") -> Dict[str, str]:
        """Detect project language, framework, and other context."""
        context = {}
        path_obj = Path(path).resolve()
        
        # Language detection
        if (path_obj / "package.json").exists():
            context['language'] = 'javascript'
            context['framework'] = ProjectDetector._detect_js_framework(path_obj)
        elif (path_obj / "requirements.txt").exists() or (path_obj / "pyproject.toml").exists():
            context['language'] = 'python'
            context['framework'] = ProjectDetector._detect_python_framework(path_obj)
        elif (path_obj / "Cargo.toml").exists():
            context['language'] = 'rust'
        elif (path_obj / "go.mod").exists():
            context['language'] = 'go'
        elif (path_obj / "pom.xml").exists() or (path_obj / "build.gradle").exists():
            context['language'] = 'java'
        
        # Git detection
        git_dir = ProjectDetector._find_git_root(path_obj)
        if git_dir:
            context['git_repo'] = str(git_dir)
        
        return context
    
    @staticmethod
    def _detect_js_framework(path: Path) -> str:
        """Detect JavaScript framework."""
        package_json = path / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    
                    if 'react' in deps:
                        return 'react'
                    elif 'vue' in deps:
                        return 'vue'
                    elif 'angular' in deps or '@angular/core' in deps:
                        return 'angular'
                    elif 'next' in deps:
                        return 'nextjs'
                    elif 'nuxt' in deps:
                        return 'nuxtjs'
            except:
                pass
        return 'javascript'
    
    @staticmethod
    def _detect_python_framework(path: Path) -> str:
        """Detect Python framework."""
        # Check for common framework files/folders
        if (path / "manage.py").exists():
            return 'django'
        elif (path / "app.py").exists() or (path / "application.py").exists():
            return 'flask'
        elif (path / "main.py").exists():
            # Check for FastAPI imports
            try:
                with open(path / "main.py") as f:
                    content = f.read()
                    if 'fastapi' in content.lower():
                        return 'fastapi'
            except:
                pass
        return 'python'
    
    @staticmethod
    def _find_git_root(path: Path) -> Optional[Path]:
        """Find the git root directory."""
        current = path
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return None

class IntelligentCacheManager:
    """Manages cache eviction and optimization policies."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.access_counts = defaultdict(int)
        self.last_access = {}
        self.cost_estimates = defaultdict(float)
    
    def should_evict(self, cache_key: str, entry_data: Dict[str, Any]) -> bool:
        """Determine if an entry should be evicted."""
        # Get cache limits from config
        max_size = self.config.get('max_size_mb', 1000) * 1024 * 1024  # Convert MB to bytes
        max_age = self.config.get('max_age_days', 30) * 24 * 3600  # Convert days to seconds
        
        # Age-based eviction
        age = time.time() - entry_data.get('timestamp', 0)
        if age > max_age:
            return True
        
        # Size-based eviction would require checking total cache size
        # This is handled at a higher level
        
        return False
    
    def calculate_priority(self, cache_key: str, entry_data: Dict[str, Any]) -> float:
        """Calculate priority score for cache entry (higher = more important)."""
        priority = 0.0
        
        # Frequency score (0-10)
        access_count = self.access_counts.get(cache_key, 0)
        frequency_score = min(access_count / 10.0, 10.0)
        priority += frequency_score * 0.3
        
        # Recency score (0-10)
        last_access = self.last_access.get(cache_key, entry_data.get('timestamp', 0))
        recency = time.time() - last_access
        recency_score = max(0, 10 - (recency / 3600))  # Decay over hours
        priority += recency_score * 0.3
        
        # Cost score (0-10) - expensive queries are more valuable to cache
        cost = self.cost_estimates.get(cache_key, 1.0)
        cost_score = min(cost * 2, 10.0)  # Assume cost is 0-5 scale
        priority += cost_score * 0.4
        
        return priority
    
    def update_access(self, cache_key: str):
        """Update access statistics."""
        self.access_counts[cache_key] += 1
        self.last_access[cache_key] = time.time()
    
    def set_cost_estimate(self, cache_key: str, cost: float):
        """Set cost estimate for a cache entry."""
        self.cost_estimates[cache_key] = cost

class EnhancedCache:
    """Enhanced cache with semantic search and intelligent management."""
    
    def __init__(self, cache_name: str = "default"):
        self.config = get_config()
        self.cache_name = cache_name
        
        # Initialize cache directory
        self.cache_dir = Path(os.path.expanduser(f"~/.cache/aicache/{self.cache_name}"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir = self.cache_dir / "images"
        self.images_dir.mkdir(exist_ok=True)
        self.notebooks_dir = self.cache_dir / "notebooks"
        self.notebooks_dir.mkdir(exist_ok=True)
        self.audio_dir = self.cache_dir / "audio"
        self.audio_dir.mkdir(exist_ok=True)
        self.video_dir = self.cache_dir / "video"
        self.video_dir.mkdir(exist_ok=True)

        # Initialize database
        self.db_path = self.cache_dir / "cache.db"
        
        # Initialize semantic cache (disabled for now due to dependency issues)
        semantic_config = self.config.get('semantic_cache', {})
        if False and SEMANTIC_AVAILABLE and semantic_config.get('enabled', True):
            try:
                self.semantic_cache = SemanticCache(semantic_config)
            except Exception as e:
                logger.warning(f"Failed to initialize semantic cache: {e}")
                self.semantic_cache = None
        else:
            self.semantic_cache = None
            logger.info("Semantic cache disabled - enhanced cache running in basic mode")
        
        # Initialize intelligent cache manager
        self.cache_manager = IntelligentCacheManager(self.config.get('intelligent_management', {}))
        
        # Initialize metrics
        self.metrics = CacheMetrics()
        
        # Project detector
        self.project_detector = ProjectDetector()
        
        logger.info(f"Enhanced cache initialized at {self.cache_dir}")

    async def init_async(self):
        await self._init_database()
        await self._load_metrics()

    async def _init_database(self):
        """Initialize SQLite database for structured cache storage."""
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS cache_entries (
                    cache_key TEXT PRIMARY KEY,
                    prompt TEXT NOT NULL,
                    response BLOB NOT NULL,  -- Compressed response
                    context BLOB,  -- MessagePacked context
                    timestamp REAL NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed REAL,
                    response_size INTEGER,  -- Uncompressed size
                    compression_ratio REAL DEFAULT 1.0,
                    semantic_tags TEXT,  -- JSON array of tags
                    cost_estimate REAL DEFAULT 1.0,
                    priority_score REAL DEFAULT 0.0
                )
            ''')

            await conn.execute('''
                CREATE TABLE IF NOT EXISTS image_cache (
                    cache_key TEXT PRIMARY KEY,
                    path TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            ''')

            await conn.execute('''
                CREATE TABLE IF NOT EXISTS notebook_cache (
                    cache_key TEXT PRIMARY KEY,
                    path TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            ''')

            await conn.execute('''
                CREATE TABLE IF NOT EXISTS audio_cache (
                    cache_key TEXT PRIMARY KEY,
                    path TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            ''')

            await conn.execute('''
                CREATE TABLE IF NOT EXISTS video_cache (
                    cache_key TEXT PRIMARY KEY,
                    path TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            ''')

            await conn.execute('''
                CREATE TABLE IF NOT EXISTS user_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    metadata TEXT,
                    timestamp REAL NOT NULL
                )
            ''')
            
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp ON cache_entries(timestamp)
            ''')
            
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)
            ''')
            
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_priority ON cache_entries(priority_score DESC)
            ''')
            
            await conn.commit()
    
    async def _load_metrics(self):
        """Load metrics from persistent storage."""
        metrics_file = self.cache_dir / "metrics.json"
        if metrics_file.exists():
            try:
                async with aiofiles.open(metrics_file, mode='r') as f:
                    data = await f.read()
                    self.metrics = CacheMetrics(**json.loads(data))
            except Exception as e:
                logger.error(f"Failed to load metrics: {e}")
    
    async def _save_metrics(self):
        """Save metrics to persistent storage."""
        metrics_file = self.cache_dir / "metrics.json"
        try:
            async with aiofiles.open(metrics_file, mode='w') as f:
                await f.write(json.dumps(asdict(self.metrics), indent=2))
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    @asynccontextmanager
    async def _get_db_connection(self):
        """Get database connection with proper locking."""
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        try:
            yield conn
        finally:
            await conn.close()
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serialize data using MessagePack and compress it."""
        packed = msgpack.packb(data, use_bin_type=True)
        return zlib.compress(packed)

    def _deserialize_data(self, data: bytes) -> Any:
        """Decompress and deserialize data."""
        unpacked = zlib.decompress(data)
        return msgpack.unpackb(unpacked, raw=False)

    def _get_cache_key(self, prompt: str, context: Union[Dict[str, Any], AdvancedContext] = None) -> str:
        """Generate cache key from prompt and context."""
        hasher = hashlib.sha256()
        hasher.update(prompt.encode('utf-8'))
        
        if context:
            if isinstance(context, AdvancedContext):
                context_dict = context.to_dict()
            else:
                context_dict = context
            
            # Normalize context for consistent hashing
            normalized_context = self._normalize_context(context_dict)
            # Use msgpack for consistent hashing of context
            sorted_context = msgpack.packb(normalized_context, use_bin_type=True)
            hasher.update(sorted_context)
        
        return hasher.hexdigest()
    
    def _normalize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize context by removing irrelevant parameters."""
        # Parameters to ignore when creating cache keys
        ignore_params = {
            'verbose', 'debug', 'quiet', 'color', 'no-color', 
            'help', 'version', 'output-format', 'format'
        }
        
        normalized = {}
        for key, value in context.items():
            # Skip ignored parameters
            if key.lower() in ignore_params:
                continue
            
            # Normalize parameter names (handle -m vs --model)
            normalized_key = self._normalize_parameter_name(key)
            normalized[normalized_key] = value
        
        return normalized
    
    def _normalize_parameter_name(self, param: str) -> str:
        """Normalize parameter names for consistent caching."""
        # Common parameter mappings
        mappings = {
            'm': 'model',
            't': 'temperature',
            'max': 'max_tokens',
            'temp': 'temperature'
        }
        
        # Remove leading dashes
        param = param.lstrip('-')
        
        # Apply mappings
        return mappings.get(param, param)
    
    def _enhance_context(self, context: Dict[str, Any] = None) -> AdvancedContext:
        """Enhance context with project and environment information."""
        base_context = context or {}
        
        # Detect project context
        try:
            project_context = self.project_detector.detect_context()
            base_context.update(project_context)
        except Exception as e:
            logger.debug(f"Failed to detect project context: {e}")
        
        # Add time context
        current_time = time.time()
        base_context['time_of_day'] = self._get_time_of_day(current_time)
        base_context['day_of_week'] = self._get_day_of_week(current_time)
        
        return AdvancedContext.from_dict(base_context)
    
    def _get_time_of_day(self, timestamp: float) -> str:
        """Get time of day category."""
        import datetime
        dt = datetime.datetime.fromtimestamp(timestamp)
        hour = dt.hour
        
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        else:
            return 'night'
    
    def _get_day_of_week(self, timestamp: float) -> str:
        """Get day of week."""
        import datetime
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime('%A').lower()
    
    async def get(self, prompt: str, context: Union[Dict[str, Any], AdvancedContext] = None) -> Optional[Dict[str, Any]]:
        """Get cache entry with semantic search fallback."""
        enhanced_context = self._enhance_context(context if isinstance(context, dict) else (context.to_dict() if context else None))
        
        # Update metrics
        self.metrics.total_requests += 1
        
        # First, try exact match
        cache_key = self._get_cache_key(prompt, enhanced_context)
        
        async with self._get_db_connection() as conn:
            cursor = await conn.execute(
                'SELECT * FROM cache_entries WHERE cache_key = ?', 
                (cache_key,)
            )
            row = await cursor.fetchone()
            
            if row:
                # Exact match found
                await self._update_access_stats(cache_key, conn)
                self.metrics.cache_hits += 1
                self.metrics.exact_hits += 1
                
                response = self._deserialize_data(row['response'])
                return {
                    'prompt': row['prompt'],
                    'response': response,
                    'context': self._deserialize_data(row['context']),
                    'timestamp': row['timestamp'],
                    'cache_type': 'exact'
                }
        
        # If no exact match, try semantic search
        if self.semantic_cache and self.semantic_cache.enabled:
            semantic_result = await self.semantic_cache.get_similar(prompt, enhanced_context.to_dict())
            
            if semantic_result:
                # Found semantic match, get the actual cached response
                async with self._get_db_connection() as conn:
                    cursor = await conn.execute(
                        'SELECT * FROM cache_entries WHERE cache_key = ?',
                        (semantic_result.cache_key,)
                    )
                    row = await cursor.fetchone()
                    
                    if row:
                        await self._update_access_stats(semantic_result.cache_key, conn)
                        self.metrics.cache_hits += 1
                        self.metrics.semantic_hits += 1
                        
                        response = self._deserialize_data(row['response'])
                        return {
                            'prompt': row['prompt'],
                            'response': response,
                            'context': self._deserialize_data(row['context']),
                            'timestamp': row['timestamp'],
                            'cache_type': 'semantic',
                            'similarity_score': getattr(semantic_result, 'similarity_score', 0.0)
                        }
        
        # No match found
        self.metrics.cache_misses += 1
        return None
    
    async def set(self, prompt: str, response: str, context: Union[Dict[str, Any], AdvancedContext] = None, 
            cost_estimate: float = 1.0) -> str:
        """Set cache entry with enhanced metadata."""
        enhanced_context = self._enhance_context(context if isinstance(context, dict) else (context.to_dict() if context else None))
        
        cache_key = self._get_cache_key(prompt, enhanced_context)
        
        # Serialize and compress data
        serialized_response = self._serialize_data(response)
        serialized_context = self._serialize_data(enhanced_context.to_dict())
        
        # Calculate priority score
        priority_score = self.cache_manager.calculate_priority(cache_key, {'timestamp': time.time()})
        
        current_time = time.time()
        
        async with self._get_db_connection() as conn:
            await conn.execute('''
                INSERT OR REPLACE INTO cache_entries 
                (cache_key, prompt, response, context, timestamp, last_accessed, 
                 response_size, compression_ratio, cost_estimate, priority_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cache_key,
                prompt,
                serialized_response,
                serialized_context,
                current_time,
                current_time,
                len(response.encode('utf-8')),
                len(serialized_response) / len(msgpack.packb(response, use_bin_type=True)),
                cost_estimate,
                priority_score
            ))
            await conn.commit()
        
        # Add to semantic cache
        if self.semantic_cache and self.semantic_cache.enabled:
            await self.semantic_cache.add(prompt, response, enhanced_context.to_dict())
        
        # Update cache manager
        self.cache_manager.set_cost_estimate(cache_key, cost_estimate)
        
        logger.info(f"Cached entry {cache_key[:8]}...")
        return cache_key

    async def set_image(self, cache_key: str, image_path: str):
        """Caches an image."""
        image_cache_path = self.images_dir / f"{cache_key}.png"
        shutil.copyfile(image_path, image_cache_path) # shutil does not have an async version
        async with self._get_db_connection() as conn:
            await conn.execute(
                "INSERT OR REPLACE INTO image_cache (cache_key, path, timestamp) VALUES (?, ?, ?)",
                (cache_key, str(image_cache_path), time.time()),
            )
            await conn.commit()

    async def get_image(self, cache_key: str) -> Optional[str]:
        """Gets a cached image path."""
        async with self._get_db_connection() as conn:
            cursor = await conn.execute(
                "SELECT path FROM image_cache WHERE cache_key = ?", (cache_key,)
            )
            row = await cursor.fetchone()
            return row["path"] if row else None

    async def set_notebook(self, cache_key: str, notebook_path: str):
        """Caches a notebook."""
        notebook_cache_path = self.notebooks_dir / f"{cache_key}.ipynb"
        shutil.copyfile(notebook_path, notebook_cache_path)
        async with self._get_db_connection() as conn:
            await conn.execute(
                "INSERT OR REPLACE INTO notebook_cache (cache_key, path, timestamp) VALUES (?, ?, ?)",
                (cache_key, str(notebook_cache_path), time.time()),
            )
            await conn.commit()

    async def get_notebook(self, cache_key: str) -> Optional[str]:
        """Gets a cached notebook path."""
        async with self._get_db_connection() as conn:
            cursor = await conn.execute(
                "SELECT path FROM notebook_cache WHERE cache_key = ?", (cache_key,)
            )
            row = await cursor.fetchone()
            return row["path"] if row else None

    async def set_audio(self, cache_key: str, audio_path: str):
        """Caches an audio file."""
        audio_cache_path = self.audio_dir / f"{cache_key}.mp3"
        shutil.copyfile(audio_path, audio_cache_path)
        async with self._get_db_connection() as conn:
            await conn.execute(
                "INSERT OR REPLACE INTO audio_cache (cache_key, path, timestamp) VALUES (?, ?, ?)",
                (cache_key, str(audio_cache_path), time.time()),
            )
            await conn.commit()

    async def get_audio(self, cache_key: str) -> Optional[str]:
        """Gets a cached audio path."""
        async with self._get_db_connection() as conn:
            cursor = await conn.execute(
                "SELECT path FROM audio_cache WHERE cache_key = ?", (cache_key,)
            )
            row = await cursor.fetchone()
            return row["path"] if row else None

    async def set_video(self, cache_key: str, video_path: str):
        """Caches a video file."""
        video_cache_path = self.video_dir / f"{cache_key}.mp4"
        shutil.copyfile(video_path, video_cache_path)
        async with self._get_db_connection() as conn:
            await conn.execute(
                "INSERT OR REPLACE INTO video_cache (cache_key, path, timestamp) VALUES (?, ?, ?)",
                (cache_key, str(video_cache_path), time.time()),
            )
            await conn.commit()

    async def get_video(self, cache_key: str) -> Optional[str]:
        """Gets a cached video path."""
        async with self._get_db_connection() as conn:
            cursor = await conn.execute(
                "SELECT path FROM video_cache WHERE cache_key = ?", (cache_key,)
            )
            row = await cursor.fetchone()
            return row["path"] if row else None

    async def log_action(self, action: str, metadata: dict):
        """Logs a user action to the database."""
        async with self._get_db_connection() as conn:
            await conn.execute(
                "INSERT INTO user_actions (action, metadata, timestamp) VALUES (?, ?, ?)",
                (action, json.dumps(metadata), time.time()),
            )
            await conn.commit()

    async def prefetch_data(self, context: AdvancedContext):
        """Prefetches data based on the current context."""
        if isinstance(context, dict):
            context_dict = context
        else:
            context_dict = context.to_dict() if hasattr(context, 'to_dict') else {}
            
        language = context_dict.get('language')
        if language == 'python':
            logger.info("Prefetching documentation for python libraries...")
            # In a real implementation, we would parse requirements.txt and prefetch docs.
        elif language == 'javascript':
            logger.info("Prefetching documentation for javascript libraries...")
            # In a real implementation, we would parse package.json and prefetch docs.

    async def _update_access_stats(self, cache_key: str, conn: aiosqlite.Connection):
        """Update access statistics for cache entry."""
        current_time = time.time()
        
        await conn.execute('''
            UPDATE cache_entries 
            SET access_count = access_count + 1, last_accessed = ?
            WHERE cache_key = ?
        ''', (current_time, cache_key))
        
        # Update cache manager
        self.cache_manager.update_access(cache_key)
    
    async def list(self, verbose: bool = False, limit: int = None) -> List[Dict[str, Any]]:
        """List cache entries with enhanced information."""
        async with self._get_db_connection() as conn:
            query = '''
                SELECT cache_key, prompt, context, timestamp, access_count, 
                       last_accessed, response_size, compression_ratio,
                       cost_estimate, priority_score
                FROM cache_entries 
                ORDER BY priority_score DESC, last_accessed DESC
            '''
            
            if limit:
                query += f' LIMIT {limit}'
            
            cursor = await conn.execute(query)
            rows = await cursor.fetchall()
            entries = []
            
            for row in rows:
                if verbose:
                    entry = dict(row)
                    entry['context'] = self._deserialize_data(entry['context'])
                    entries.append(entry)
                else:
                    entries.append(row['cache_key'])
            
            return entries
    
    async def inspect(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Inspect detailed cache entry information."""
        async with self._get_db_connection() as conn:
            cursor = await conn.execute(
                'SELECT * FROM cache_entries WHERE cache_key = ?',
                (cache_key,)
            )
            row = await cursor.fetchone()
            
            if not row:
                return None
            
            response = self._deserialize_data(row['response'])
            
            return {
                'cache_key': row['cache_key'],
                'prompt': row['prompt'],
                'response': response,
                'context': self._deserialize_data(row['context']),
                'timestamp': row['timestamp'],
                'access_count': row['access_count'],
                'last_accessed': row['last_accessed'],
                'response_size': row['response_size'],
                'compression_ratio': row['compression_ratio'],
                'cost_estimate': row['cost_estimate'],
                'priority_score': row['priority_score']
            }
    
    async def delete(self, cache_key: str) -> bool:
        """Delete specific cache entry."""
        async with self._get_db_connection() as conn:
            cursor = await conn.execute(
                'DELETE FROM cache_entries WHERE cache_key = ?',
                (cache_key,)
            )
            await conn.commit()
            deleted = cursor.rowcount > 0
        
        # Remove from semantic cache
        if self.semantic_cache and self.semantic_cache.enabled:
            await self.semantic_cache.delete(cache_key)
        
        return deleted
    
    async def clear(self):
        """Clear all cache entries."""
        async with self._get_db_connection() as conn:
            await conn.execute('DELETE FROM cache_entries')
            await conn.commit()
        
        # Clear semantic cache
        if self.semantic_cache and self.semantic_cache.enabled:
            # This would require a clear method in SemanticCache
            pass
    
    async def prune(self, max_age_days: int = None, max_size_mb: int = None) -> int:
        """Intelligent cache pruning based on multiple criteria."""
        config = self.config.get('intelligent_management', {})
        max_age = max_age_days or config.get('max_age_days', 30)
        max_size = (max_size_mb or config.get('max_size_mb', 1000)) * 1024 * 1024
        
        pruned_count = 0
        current_time = time.time()
        cutoff_time = current_time - (max_age * 24 * 3600)
        
        async with self._get_db_connection() as conn:
            # First, remove entries based on age
            cursor = await conn.execute(
                'DELETE FROM cache_entries WHERE timestamp < ?',
                (cutoff_time,)
            )
            pruned_count += cursor.rowcount
            await conn.commit()
            
            # Check total size and remove lowest priority entries if needed
            cursor = await conn.execute(
                'SELECT SUM(response_size) FROM cache_entries'
            )
            total_size = (await cursor.fetchone())[0] or 0
            
            if total_size > max_size:
                # Calculate how much to remove
                target_size = max_size * 0.8  # Remove to 80% of limit
                size_to_remove = total_size - target_size
                
                # Remove lowest priority entries until we reach target
                cursor = await conn.execute('''
                    SELECT cache_key, response_size FROM cache_entries 
                    ORDER BY priority_score ASC
                ''')
                rows = await cursor.fetchall()
                
                removed_size = 0
                for row in rows:
                    if removed_size >= size_to_remove:
                        break
                    
                    await conn.execute(
                        'DELETE FROM cache_entries WHERE cache_key = ?',
                        (row['cache_key'],)
                    )
                    removed_size += row['response_size']
                    pruned_count += 1
                await conn.commit()
        
        await self._save_metrics()
        return pruned_count
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        async with self._get_db_connection() as conn:
            # Basic stats
            cursor = await conn.execute('''
                SELECT 
                    COUNT(*) as total_entries,
                    SUM(response_size) as total_size,
                    AVG(compression_ratio) as avg_compression,
                    SUM(access_count) as total_accesses,
                    MAX(last_accessed) as last_activity
                FROM cache_entries
            ''')
            
            db_stats = dict(await cursor.fetchone())
            
            # Expired entries count
            current_time = time.time()
            max_age = self.config.get('intelligent_management', {}).get('max_age_days', 30)
            cutoff_time = current_time - (max_age * 24 * 3600)
            
            cursor = await conn.execute(
                'SELECT COUNT(*) as expired_count FROM cache_entries WHERE timestamp < ?',
                (cutoff_time,)
            )
            db_stats['expired_entries'] = (await cursor.fetchone())[0]
        
        # Combine with metrics
        stats = {
            'cache_performance': asdict(self.metrics),
            'storage': db_stats,
            'semantic_cache': await self.semantic_cache.get_stats() if self.semantic_cache else {'enabled': False}
        }
        
        return stats

# Backward compatibility
Cache = EnhancedCache