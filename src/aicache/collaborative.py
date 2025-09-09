"""
Collaborative and distributed caching system for team sharing.
"""

import os
import json
import time
import hashlib
import logging
import threading
import asyncio
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

logger = logging.getLogger(__name__)

@dataclass
class TeamMember:
    """Represents a team member in collaborative caching."""
    user_id: str
    username: str
    role: str  # 'admin', 'developer', 'viewer'
    public_key: Optional[str] = None
    last_seen: float = 0
    cache_contributions: int = 0
    
@dataclass
class ShareableEntry:
    """Cache entry that can be shared across team members."""
    cache_key: str
    prompt: str
    response: str
    context: Dict[str, Any]
    timestamp: float
    
    # Sharing metadata
    owner_id: str
    share_level: str  # 'private', 'team', 'public'
    encrypted: bool = False
    access_count: int = 0
    
    # Privacy and security
    sensitive: bool = False
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class CacheSync:
    """Synchronization record for distributed caching."""
    sync_id: str
    source_user: str
    target_users: List[str]
    operation: str  # 'add', 'update', 'delete'
    cache_key: str
    timestamp: float
    status: str  # 'pending', 'synced', 'failed'
    retry_count: int = 0

class EncryptionManager:
    """Manages encryption for sensitive cache entries."""
    
    def __init__(self, team_secret: str = None):
        self.team_secret = team_secret or self._generate_team_secret()
        self.cipher = self._create_cipher()
    
    def _generate_team_secret(self) -> str:
        """Generate a team secret key."""
        return Fernet.generate_key().decode()
    
    def _create_cipher(self) -> Fernet:
        """Create cipher from team secret."""
        key = self.team_secret.encode()
        if len(key) != 44:  # Fernet key should be 44 bytes
            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'aicache_salt',  # In production, use random salt
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(key))
        
        return Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data."""
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return data  # Fallback to unencrypted
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return encrypted_data  # Return as-is if decryption fails

class TeamCache:
    """Team-wide cache with sharing and collaboration features."""
    
    def __init__(self, team_id: str, user_id: str, config: Dict[str, Any] = None):
        self.team_id = team_id
        self.user_id = user_id
        self.config = config or {}
        
        # Initialize storage
        self.cache_dir = Path.home() / ".cache" / "aicache" / "team" / team_id
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Team management
        self.team_file = self.cache_dir / "team.json"
        self.team_members: Dict[str, TeamMember] = {}
        self._load_team_data()
        
        # Encryption
        self.encryption = EncryptionManager(self.config.get('team_secret'))
        
        # Sync management
        self.sync_queue: List[CacheSync] = []
        self.sync_lock = threading.RLock()
        
        # Shared entries storage
        self.shared_cache_file = self.cache_dir / "shared_cache.json"
        self.shared_entries: Dict[str, ShareableEntry] = {}
        self._load_shared_cache()
        
        logger.info(f"Team cache initialized for team {team_id}, user {user_id}")
    
    def _load_team_data(self):
        """Load team member data."""
        if self.team_file.exists():
            try:
                with open(self.team_file) as f:
                    data = json.load(f)
                    for member_data in data.get('members', []):
                        member = TeamMember(**member_data)
                        self.team_members[member.user_id] = member
            except Exception as e:
                logger.error(f"Failed to load team data: {e}")
    
    def _save_team_data(self):
        """Save team member data."""
        try:
            data = {
                'team_id': self.team_id,
                'members': [asdict(member) for member in self.team_members.values()],
                'last_updated': time.time()
            }
            with open(self.team_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save team data: {e}")
    
    def _load_shared_cache(self):
        """Load shared cache entries."""
        if self.shared_cache_file.exists():
            try:
                with open(self.shared_cache_file) as f:
                    data = json.load(f)
                    for entry_data in data.get('entries', []):
                        entry = ShareableEntry(**entry_data)
                        self.shared_entries[entry.cache_key] = entry
            except Exception as e:
                logger.error(f"Failed to load shared cache: {e}")
    
    def _save_shared_cache(self):
        """Save shared cache entries."""
        try:
            data = {
                'team_id': self.team_id,
                'entries': [asdict(entry) for entry in self.shared_entries.values()],
                'last_updated': time.time()
            }
            with open(self.shared_cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save shared cache: {e}")
    
    def add_team_member(self, user_id: str, username: str, role: str = 'developer') -> bool:
        """Add a new team member."""
        if self.get_user_role(self.user_id) != 'admin':
            logger.warning(f"User {self.user_id} not authorized to add team members")
            return False
        
        member = TeamMember(
            user_id=user_id,
            username=username,
            role=role,
            last_seen=time.time()
        )
        
        self.team_members[user_id] = member
        self._save_team_data()
        
        logger.info(f"Added team member {username} ({user_id}) with role {role}")
        return True
    
    def get_user_role(self, user_id: str) -> Optional[str]:
        """Get user role in the team."""
        member = self.team_members.get(user_id)
        return member.role if member else None
    
    def can_access_entry(self, entry: ShareableEntry, user_id: str) -> bool:
        """Check if user can access a specific entry."""
        # Owner can always access
        if entry.owner_id == user_id:
            return True
        
        # Check share level
        if entry.share_level == 'private':
            return False
        elif entry.share_level == 'team':
            return user_id in self.team_members
        elif entry.share_level == 'public':
            return True
        
        return False
    
    def share_entry(self, cache_key: str, prompt: str, response: str, 
                   context: Dict[str, Any], share_level: str = 'team',
                   sensitive: bool = False, tags: List[str] = None) -> str:
        """Share a cache entry with the team."""
        
        # Encrypt if sensitive
        actual_response = response
        encrypted = False
        if sensitive:
            actual_response = self.encryption.encrypt(response)
            encrypted = True
        
        entry = ShareableEntry(
            cache_key=cache_key,
            prompt=prompt,
            response=actual_response,
            context=context,
            timestamp=time.time(),
            owner_id=self.user_id,
            share_level=share_level,
            encrypted=encrypted,
            sensitive=sensitive,
            tags=tags or []
        )
        
        self.shared_entries[cache_key] = entry
        self._save_shared_cache()
        
        # Queue for sync
        self._queue_sync('add', cache_key)
        
        logger.info(f"Shared cache entry {cache_key[:8]}... at level {share_level}")
        return cache_key
    
    def get_shared_entry(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get a shared cache entry if accessible."""
        entry = self.shared_entries.get(cache_key)
        if not entry or not self.can_access_entry(entry, self.user_id):
            return None
        
        # Decrypt if necessary
        response = entry.response
        if entry.encrypted:
            response = self.encryption.decrypt(response)
        
        # Update access count
        entry.access_count += 1
        self._save_shared_cache()
        
        return {
            'prompt': entry.prompt,
            'response': response,
            'context': entry.context,
            'timestamp': entry.timestamp,
            'owner': entry.owner_id,
            'share_level': entry.share_level,
            'tags': entry.tags,
            'cache_type': 'team_shared'
        }
    
    def search_team_cache(self, query: str, context: Dict[str, Any] = None,
                         tags: List[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search team cache for relevant entries."""
        results = []
        
        for entry in self.shared_entries.values():
            if not self.can_access_entry(entry, self.user_id):
                continue
            
            # Simple text matching (could be enhanced with semantic search)
            if query.lower() in entry.prompt.lower():
                score = 1.0
                
                # Boost score for tag matches
                if tags and entry.tags:
                    matching_tags = set(tags) & set(entry.tags)
                    score += len(matching_tags) * 0.2
                
                # Decrypt if necessary for display
                response = entry.response
                if entry.encrypted:
                    response = self.encryption.decrypt(response)
                
                results.append({
                    'cache_key': entry.cache_key,
                    'prompt': entry.prompt,
                    'response': response[:200] + '...' if len(response) > 200 else response,
                    'context': entry.context,
                    'timestamp': entry.timestamp,
                    'owner': entry.owner_id,
                    'tags': entry.tags,
                    'score': score
                })
        
        # Sort by score and recency
        results.sort(key=lambda x: (x['score'], x['timestamp']), reverse=True)
        return results[:limit]
    
    def _queue_sync(self, operation: str, cache_key: str):
        """Queue a sync operation."""
        sync = CacheSync(
            sync_id=hashlib.md5(f"{operation}:{cache_key}:{time.time()}".encode()).hexdigest(),
            source_user=self.user_id,
            target_users=list(self.team_members.keys()),
            operation=operation,
            cache_key=cache_key,
            timestamp=time.time(),
            status='pending'
        )
        
        with self.sync_lock:
            self.sync_queue.append(sync)
    
    def get_team_stats(self) -> Dict[str, Any]:
        """Get team cache statistics."""
        total_entries = len(self.shared_entries)
        entries_by_level = {'private': 0, 'team': 0, 'public': 0}
        entries_by_user = {}
        total_accesses = 0
        
        for entry in self.shared_entries.values():
            entries_by_level[entry.share_level] += 1
            entries_by_user[entry.owner_id] = entries_by_user.get(entry.owner_id, 0) + 1
            total_accesses += entry.access_count
        
        return {
            'team_id': self.team_id,
            'total_members': len(self.team_members),
            'total_entries': total_entries,
            'entries_by_level': entries_by_level,
            'entries_by_user': entries_by_user,
            'total_accesses': total_accesses,
            'my_contributions': entries_by_user.get(self.user_id, 0),
            'pending_syncs': len([s for s in self.sync_queue if s.status == 'pending'])
        }

class DistributedCache:
    """Distributed cache system with P2P synchronization."""
    
    def __init__(self, local_cache, team_cache: TeamCache = None):
        self.local_cache = local_cache
        self.team_cache = team_cache
        self.sync_enabled = team_cache is not None
        
        # Hierarchical storage: Local → Team → Organization → Public
        self.cache_hierarchy = ['local', 'team', 'organization', 'public']
        
    async def get_distributed(self, prompt: str, context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Get cache entry from distributed hierarchy."""
        
        # Try local cache first
        result = self.local_cache.get(prompt, context)
        if result:
            result['source'] = 'local'
            return result
        
        # Try team cache
        if self.team_cache:
            cache_key = self.local_cache._get_cache_key(prompt, context)
            result = self.team_cache.get_shared_entry(cache_key)
            if result:
                result['source'] = 'team'
                # Optionally cache locally for faster access
                self._cache_locally_from_team(prompt, result['response'], context)
                return result
        
        # Could extend to organization and public caches
        return None
    
    def _cache_locally_from_team(self, prompt: str, response: str, context: Dict[str, Any] = None):
        """Cache a team entry locally for faster access."""
        try:
            self.local_cache.set(prompt, response, context)
        except Exception as e:
            logger.error(f"Failed to cache team entry locally: {e}")
    
    async def set_distributed(self, prompt: str, response: str, context: Dict[str, Any] = None,
                            share_level: str = 'private', sensitive: bool = False,
                            tags: List[str] = None) -> str:
        """Set cache entry in distributed system."""
        
        # Always cache locally
        cache_key = self.local_cache.set(prompt, response, context)
        
        # Share with team if requested and team cache available
        if share_level != 'private' and self.team_cache:
            try:
                self.team_cache.share_entry(
                    cache_key, prompt, response, context or {},
                    share_level, sensitive, tags
                )
            except Exception as e:
                logger.error(f"Failed to share with team: {e}")
        
        return cache_key
    
    def sync_status(self) -> Dict[str, Any]:
        """Get synchronization status."""
        if not self.team_cache:
            return {'enabled': False}
        
        return {
            'enabled': True,
            'team_stats': self.team_cache.get_team_stats(),
            'last_sync': getattr(self, '_last_sync_time', 0)
        }

class KnowledgeGraph:
    """Build knowledge graph of related queries and responses."""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.graph_file = cache_dir / "knowledge_graph.json"
        self.graph: Dict[str, Dict[str, Any]] = {}
        self._load_graph()
    
    def _load_graph(self):
        """Load knowledge graph from storage."""
        if self.graph_file.exists():
            try:
                with open(self.graph_file) as f:
                    self.graph = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load knowledge graph: {e}")
    
    def _save_graph(self):
        """Save knowledge graph to storage."""
        try:
            with open(self.graph_file, 'w') as f:
                json.dump(self.graph, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save knowledge graph: {e}")
    
    def add_relationship(self, source_key: str, target_key: str, relationship_type: str,
                        strength: float = 1.0):
        """Add relationship between cache entries."""
        if source_key not in self.graph:
            self.graph[source_key] = {'relationships': {}}
        
        self.graph[source_key]['relationships'][target_key] = {
            'type': relationship_type,
            'strength': strength,
            'created': time.time()
        }
        
        self._save_graph()
    
    def get_related_entries(self, cache_key: str, relationship_types: List[str] = None,
                           min_strength: float = 0.5) -> List[Tuple[str, Dict[str, Any]]]:
        """Get related cache entries."""
        if cache_key not in self.graph:
            return []
        
        relationships = self.graph[cache_key].get('relationships', {})
        results = []
        
        for target_key, rel_data in relationships.items():
            if relationship_types and rel_data['type'] not in relationship_types:
                continue
            if rel_data['strength'] < min_strength:
                continue
            
            results.append((target_key, rel_data))
        
        # Sort by strength
        results.sort(key=lambda x: x[1]['strength'], reverse=True)
        return results
    
    def suggest_similar_queries(self, prompt: str, limit: int = 5) -> List[str]:
        """Suggest similar queries based on knowledge graph."""
        # Simple implementation - could be enhanced with semantic analysis
        suggestions = []
        
        for cache_key, node_data in self.graph.items():
            # This would benefit from actual prompt storage in the graph
            # For now, just return some related cache keys
            if len(suggestions) < limit:
                suggestions.append(cache_key)
        
        return suggestions

# Factory functions
def create_team_cache(team_id: str, user_id: str, config: Dict[str, Any] = None) -> TeamCache:
    """Create a team cache instance."""
    return TeamCache(team_id, user_id, config)

def create_distributed_cache(local_cache, team_id: str = None, user_id: str = None) -> DistributedCache:
    """Create a distributed cache system."""
    team_cache = None
    if team_id and user_id:
        team_cache = TeamCache(team_id, user_id)
    
    return DistributedCache(local_cache, team_cache)