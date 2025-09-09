"""
Collaborative caching system for aicache.
Enables real-time collaboration and shared cache entries.
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from collections import defaultdict
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class CollaborativeCacheEntry:
    """Represents a collaborative cache entry."""
    cache_key: str
    prompt: str
    response: str
    context: Dict[str, Any]
    owner_id: str
    team_id: str
    created_at: float
    last_accessed: float
    access_count: int
    tags: List[str]
    shared_with: List[str]  # User IDs this entry is shared with
    permissions: Dict[str, str]  # Permission levels for shared users

@dataclass
class TeamPresence:
    """Represents team member presence information."""
    user_id: str
    username: str
    status: str  # 'online', 'away', 'offline'
    current_project: str
    current_task: str
    last_active: float
    capabilities: List[str]

@dataclass
class CollaborativeSession:
    """Represents a collaborative session."""
    session_id: str
    team_id: str
    participants: List[str]
    shared_context: Dict[str, Any]
    created_at: float
    last_activity: float
    active: bool

class CollaborativeCache:
    """Collaborative caching system for team-based development."""
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.cache_entries = {}  # cache_key -> CollaborativeCacheEntry
        self.team_presence = {}  # user_id -> TeamPresence
        self.collaborative_sessions = {}  # session_id -> CollaborativeSession
        self.user_subscriptions = defaultdict(set)  # user_id -> set of cache_keys
        self.tag_index = defaultdict(set)  # tag -> set of cache_keys
        
    async def initialize(self):
        """Initialize the collaborative cache."""
        logger.info(f"Collaborative cache initialized for team {self.team_id}")
        
    async def set_cache_entry(self, prompt: str, response: str, context: Dict[str, Any], 
                            owner_id: str, tags: List[str] = None) -> str:
        """Set a collaborative cache entry."""
        import time
        
        # Generate cache key
        cache_key = self._generate_cache_key(prompt, context)
        
        # Create cache entry
        entry = CollaborativeCacheEntry(
            cache_key=cache_key,
            prompt=prompt,
            response=response,
            context=context,
            owner_id=owner_id,
            team_id=self.team_id,
            created_at=time.time(),
            last_accessed=time.time(),
            access_count=0,
            tags=tags or [],
            shared_with=[],
            permissions={}
        )
        
        # Store entry
        self.cache_entries[cache_key] = entry
        
        # Update tag index
        for tag in entry.tags:
            self.tag_index[tag].add(cache_key)
            
        # Notify subscribers
        await self._notify_subscribers(cache_key, 'created')
        
        logger.info(f"Cache entry set: {cache_key[:8]}...")
        return cache_key
        
    async def get_cache_entry(self, prompt: str, context: Dict[str, Any], 
                            user_id: str) -> Optional[Dict[str, Any]]:
        """Get a collaborative cache entry."""
        cache_key = self._generate_cache_key(prompt, context)
        
        if cache_key not in self.cache_entries:
            return None
            
        # Check permissions
        entry = self.cache_entries[cache_key]
        if not self._has_permission(user_id, entry):
            logger.warning(f"User {user_id} lacks permission for cache entry {cache_key[:8]}...")
            return None
            
        # Update access stats
        entry.last_accessed = asyncio.get_event_loop().time()
        entry.access_count += 1
        
        # Subscribe user to this entry for updates
        self.user_subscriptions[user_id].add(cache_key)
        
        # Notify subscribers
        await self._notify_subscribers(cache_key, 'accessed')
        
        return {
            'prompt': entry.prompt,
            'response': entry.response,
            'context': entry.context,
            'owner_id': entry.owner_id,
            'created_at': entry.created_at,
            'access_count': entry.access_count,
            'tags': entry.tags
        }
        
    def _generate_cache_key(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate cache key from prompt and context."""
        import hashlib
        hasher = hashlib.sha256()
        hasher.update(prompt.encode('utf-8'))
        # Include key context elements
        key_context = {k: v for k, v in context.items() if k in ['language', 'framework', 'project']}
        if key_context:
            hasher.update(json.dumps(key_context, sort_keys=True).encode('utf-8'))
        return hasher.hexdigest()
        
    def _has_permission(self, user_id: str, entry: CollaborativeCacheEntry) -> bool:
        """Check if user has permission to access entry."""
        # Owner always has access
        if user_id == entry.owner_id:
            return True
            
        # Check shared permissions
        if user_id in entry.shared_with:
            return True
            
        # Team members have read access by default
        if user_id in self.team_presence:
            permission = entry.permissions.get(user_id, 'read')
            return permission in ['read', 'write', 'admin']
            
        return False
        
    async def share_cache_entry(self, cache_key: str, user_id: str, 
                              target_user_ids: List[str], permission: str = 'read'):
        """Share a cache entry with other users."""
        if cache_key not in self.cache_entries:
            raise ValueError(f"Cache entry {cache_key} not found")
            
        entry = self.cache_entries[cache_key]
        
        # Check if user has permission to share
        if not self._can_share(user_id, entry):
            raise PermissionError(f"User {user_id} cannot share this entry")
            
        # Share with target users
        for target_user in target_user_ids:
            entry.shared_with.append(target_user)
            entry.permissions[target_user] = permission
            
        # Notify subscribers
        await self._notify_subscribers(cache_key, 'shared')
        
        logger.info(f"Cache entry {cache_key[:8]}... shared with {len(target_user_ids)} users")
        
    def _can_share(self, user_id: str, entry: CollaborativeCacheEntry) -> bool:
        """Check if user can share an entry."""
        # Owner and admins can share
        if user_id == entry.owner_id:
            return True
            
        permission = entry.permissions.get(user_id, 'read')
        return permission == 'admin'
        
    async def update_team_presence(self, user_id: str, username: str, 
                                 status: str, current_project: str = None, 
                                 current_task: str = None, capabilities: List[str] = None):
        """Update team member presence information."""
        import time
        
        presence = TeamPresence(
            user_id=user_id,
            username=username,
            status=status,
            current_project=current_project or '',
            current_task=current_task or '',
            last_active=time.time(),
            capabilities=capabilities or []
        )
        
        self.team_presence[user_id] = presence
        
        # Notify about presence update
        await self._notify_presence_update(user_id, presence)
        
        logger.debug(f"Presence updated for user {username}")
        
    async def get_team_presence(self) -> Dict[str, Dict[str, Any]]:
        """Get presence information for all team members."""
        return {user_id: asdict(presence) for user_id, presence in self.team_presence.items()}
        
    async def create_collaborative_session(self, session_id: str, participants: List[str], 
                                         shared_context: Dict[str, Any]) -> str:
        """Create a collaborative session."""
        import time
        
        session = CollaborativeSession(
            session_id=session_id,
            team_id=self.team_id,
            participants=participants,
            shared_context=shared_context,
            created_at=time.time(),
            last_activity=time.time(),
            active=True
        )
        
        self.collaborative_sessions[session_id] = session
        
        # Notify participants
        await self._notify_session_created(session)
        
        logger.info(f"Collaborative session created: {session_id}")
        return session_id
        
    async def join_collaborative_session(self, session_id: str, user_id: str) -> bool:
        """Join a collaborative session."""
        if session_id not in self.collaborative_sessions:
            return False
            
        session = self.collaborative_sessions[session_id]
        if user_id not in session.participants:
            session.participants.append(user_id)
            
        session.last_activity = asyncio.get_event_loop().time()
        
        # Notify about new participant
        await self._notify_session_updated(session, 'joined', user_id)
        
        logger.info(f"User {user_id} joined session {session_id}")
        return True
        
    async def leave_collaborative_session(self, session_id: str, user_id: str) -> bool:
        """Leave a collaborative session."""
        if session_id not in self.collaborative_sessions:
            return False
            
        session = self.collaborative_sessions[session_id]
        if user_id in session.participants:
            session.participants.remove(user_id)
            
        session.last_activity = asyncio.get_event_loop().time()
        
        # Notify about participant leaving
        await self._notify_session_updated(session, 'left', user_id)
        
        logger.info(f"User {user_id} left session {session_id}")
        return True
        
    async def search_cache_entries(self, query: str, tags: List[str] = None, 
                                 user_id: str = None) -> List[Dict[str, Any]]:
        """Search cache entries by query and tags."""
        results = []
        
        # Get candidate entries
        candidate_keys = set(self.cache_entries.keys())
        
        # Filter by tags
        if tags:
            tag_filtered = set()
            for tag in tags:
                tag_filtered.update(self.tag_index.get(tag, set()))
            candidate_keys = candidate_keys.intersection(tag_filtered)
            
        # Search through candidates
        for cache_key in candidate_keys:
            entry = self.cache_entries[cache_key]
            
            # Check permissions
            if user_id and not self._has_permission(user_id, entry):
                continue
                
            # Check if query matches prompt or context
            if (query.lower() in entry.prompt.lower() or 
                any(query.lower() in str(v).lower() for v in entry.context.values())):
                results.append({
                    'cache_key': cache_key,
                    'prompt': entry.prompt,
                    'owner_id': entry.owner_id,
                    'created_at': entry.created_at,
                    'access_count': entry.access_count,
                    'tags': entry.tags,
                    'relevance_score': self._calculate_relevance(entry, query)
                })
                
        # Sort by relevance
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:20]  # Limit to 20 results
        
    def _calculate_relevance(self, entry: CollaborativeCacheEntry, query: str) -> float:
        """Calculate relevance score for search."""
        score = 0.0
        
        # Prompt match
        if query.lower() in entry.prompt.lower():
            score += 1.0
            
        # Context match
        for value in entry.context.values():
            if query.lower() in str(value).lower():
                score += 0.5
                
        # Tag match
        for tag in entry.tags:
            if query.lower() in tag.lower():
                score += 0.8
                
        # Recency boost
        import time
        recency = time.time() - entry.last_accessed
        if recency < 3600:  # Last hour
            score *= 1.2
        elif recency < 86400:  # Last day
            score *= 1.1
            
        return score
        
    async def _notify_subscribers(self, cache_key: str, event_type: str):
        """Notify subscribers about cache entry events."""
        # In a real implementation, this would send real-time notifications
        # For now, we'll just log the event
        logger.debug(f"Cache event: {event_type} for {cache_key[:8]}...")
        
    async def _notify_presence_update(self, user_id: str, presence: TeamPresence):
        """Notify about presence updates."""
        # In a real implementation, this would send real-time notifications
        logger.debug(f"Presence update for user {user_id}")
        
    async def _notify_session_created(self, session: CollaborativeSession):
        """Notify about session creation."""
        # In a real implementation, this would send real-time notifications
        logger.debug(f"Session created: {session.session_id}")
        
    async def _notify_session_updated(self, session: CollaborativeSession, action: str, user_id: str):
        """Notify about session updates."""
        # In a real implementation, this would send real-time notifications
        logger.debug(f"Session {session.session_id} updated: {user_id} {action}")
        
    async def get_collaborative_stats(self) -> Dict[str, Any]:
        """Get collaborative caching statistics."""
        import time
        
        # Calculate active users (active in last 15 minutes)
        active_users = 0
        current_time = time.time()
        for presence in self.team_presence.values():
            if current_time - presence.last_active < 900:  # 15 minutes
                active_users += 1
                
        # Calculate active sessions
        active_sessions = sum(1 for s in self.collaborative_sessions.values() if s.active)
        
        return {
            'team_id': self.team_id,
            'total_entries': len(self.cache_entries),
            'total_users': len(self.team_presence),
            'active_users': active_users,
            'total_sessions': len(self.collaborative_sessions),
            'active_sessions': active_sessions,
            'total_tags': len(self.tag_index),
            'subscriptions': sum(len(subs) for subs in self.user_subscriptions.values())
        }