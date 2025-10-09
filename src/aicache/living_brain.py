"""
Living Brain: Persistent context management across AI sessions.
This module creates a unified brain-like system that maintains context
across different AI providers (Claude, Gemini, Qwen) and persistently
throughout the lifetime of working on an application.
"""
import os
import json
import time
import hashlib
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict, field
from collections import defaultdict, deque

try:
    import aiosqlite
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

from .config import get_config
from .semantic import SemanticCache, SemanticCacheEntry

logger = logging.getLogger(__name__)

@dataclass
class BrainSession:
    """Represents a continuous working session on a project."""
    session_id: str
    project_id: str
    start_time: float
    end_time: Optional[float] = None
    ai_providers_used: Set[str] = field(default_factory=set)
    total_interactions: int = 0
    active: bool = True
    
    def complete_session(self):
        """Mark session as complete."""
        self.end_time = time.time()
        self.active = False

@dataclass
class ProjectContext:
    """Persistent project-specific context and knowledge."""
    project_id: str
    name: str
    path: str
    language: str
    framework: str
    created_at: float
    last_accessed: float
    metadata: Dict[str, Any] = field(default_factory=dict)  # Framework-specific config, dependencies, etc.
    tags: List[str] = field(default_factory=list)
    
    def update_access_time(self):
        """Update last accessed time."""
        self.last_accessed = time.time()

@dataclass
class CrossAIConcept:
    """A concept or piece of knowledge that spans multiple AI interactions."""
    concept_id: str
    content: str
    embeddings: Optional[List[float]] = None
    ai_providers: Set[str] = field(default_factory=set)  # Providers that contributed to this concept
    created_at: float = 0
    last_accessed: float = 0
    importance_score: float = 0.0
    tags: List[str] = field(default_factory=list)
    related_concepts: List[str] = field(default_factory=list)  # Related concept IDs
    
    def add_provider(self, provider: str):
        """Add an AI provider to this concept."""
        self.ai_providers.add(provider)
        self.last_accessed = time.time()

@dataclass
class PersistentContext:
    """Context that persists across AI switches and sessions."""
    session_id: str
    project_id: str
    current_task: Optional[str] = None
    active_ai_provider: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    current_working_directory: Optional[str] = None
    relevant_files: List[str] = field(default_factory=list)
    temporary_context: Dict[str, Any] = field(default_factory=dict)
    
    def add_conversation_turn(self, role: str, content: str, ai_provider: str, timestamp: float = None):
        """Add a turn to the conversation history."""
        if timestamp is None:
            timestamp = time.time()
        
        self.conversation_history.append({
            'role': role,
            'content': content,
            'ai_provider': ai_provider,
            'timestamp': timestamp
        })
        
        # Keep only recent history to prevent infinite growth
        if len(self.conversation_history) > 100:  # Keep last 100 exchanges
            self.conversation_history = self.conversation_history[-50:]  # Keep last 50

class BrainStateManager:
    """
    Manages the persistent state of the living brain across sessions and AI providers.
    """
    
    def __init__(self, cache_dir: str = None):
        self.config = get_config()
        
        if cache_dir is None:
            cache_dir = os.path.expanduser("~/.cache/aicache/brain")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.cache_dir / "brain.db"
        self.current_session: Optional[BrainSession] = None
        self.current_context: Optional[PersistentContext] = None
        self.current_project: Optional[ProjectContext] = None
        
        # Semantic cache for concept relationships
        semantic_config = self.config.get('semantic_cache', {})
        if semantic_config.get('enabled', True):
            try:
                self.semantic_cache = SemanticCache(semantic_config)
            except Exception as e:
                logger.warning(f"Failed to initialize semantic cache: {e}")
                self.semantic_cache = None
        else:
            self.semantic_cache = None
        
        logger.info(f"Brain State Manager initialized at {self.cache_dir}")
    
    async def init_db(self):
        """Initialize the brain database."""
        if not SQLITE_AVAILABLE:
            logger.error("aiosqlite not available, cannot initialize brain DB")
            return
        
        async with aiosqlite.connect(self.db_path) as conn:
            # Create tables for brain data
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS brain_sessions (
                    session_id TEXT PRIMARY KEY,
                    project_id TEXT,
                    start_time REAL,
                    end_time REAL,
                    ai_providers_used TEXT,
                    total_interactions INTEGER,
                    active BOOLEAN
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    name TEXT,
                    path TEXT,
                    language TEXT,
                    framework TEXT,
                    created_at REAL,
                    last_accessed REAL,
                    metadata TEXT,
                    tags TEXT
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS cross_ai_concepts (
                    concept_id TEXT PRIMARY KEY,
                    content TEXT,
                    embeddings BLOB,
                    ai_providers TEXT,
                    created_at REAL,
                    last_accessed REAL,
                    importance_score REAL,
                    tags TEXT,
                    related_concepts TEXT
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS persistent_contexts (
                    session_id TEXT PRIMARY KEY,
                    project_id TEXT,
                    current_task TEXT,
                    active_ai_provider TEXT,
                    conversation_history TEXT,
                    current_working_directory TEXT,
                    relevant_files TEXT,
                    temporary_context TEXT
                )
            ''')
            
            # Create indexes for performance
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_sessions_project ON brain_sessions(project_id)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_sessions_active ON brain_sessions(active)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_concepts_project_importance ON cross_ai_concepts(last_accessed, importance_score)')
            
            await conn.commit()
    
    async def create_new_session(self, project_id: str, project_name: str = None) -> BrainSession:
        """Create a new brain session for a project."""
        import uuid
        session_id = str(uuid.uuid4())
        
        # Get or create project context
        if project_name is None:
            project_name = f"Project-{project_id[:8]}"
        
        project = await self.get_project(project_id)
        if project is None:
            project = ProjectContext(
                project_id=project_id,
                name=project_name,
                path=os.getcwd(),  # Current working directory
                language="unknown",
                framework="unknown",
                created_at=time.time()
            )
            await self.save_project(project)
        
        session = BrainSession(
            session_id=session_id,
            project_id=project_id,
            start_time=time.time(),
            total_interactions=0
        )
        
        self.current_session = session
        self.current_project = project
        
        # Initialize persistent context for this session
        self.current_context = PersistentContext(
            session_id=session_id,
            project_id=project_id
        )
        
        # Save to database
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute('''
                INSERT INTO brain_sessions
                (session_id, project_id, start_time, end_time, ai_providers_used, total_interactions, active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.session_id, project_id, session.start_time, session.end_time,
                json.dumps(list(session.ai_providers_used)), session.total_interactions, session.active
            ))
            
            await conn.execute('''
                INSERT INTO persistent_contexts
                (session_id, project_id, current_task, active_ai_provider, conversation_history,
                 current_working_directory, relevant_files, temporary_context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id, project_id, self.current_context.current_task,
                self.current_context.active_ai_provider, json.dumps(self.current_context.conversation_history),
                self.current_context.current_working_directory, json.dumps(self.current_context.relevant_files),
                json.dumps(self.current_context.temporary_context)
            ))
            
            await conn.commit()
        
        logger.info(f"Created new brain session {session_id} for project {project_id}")
        return session
    
    async def switch_ai_provider(self, provider: str) -> bool:
        """Switch to a different AI provider within the current session."""
        if self.current_session is None:
            logger.warning("No active session, creating a temporary one")
            # We might want to detect the project automatically here
            project_id = f"temp-{provider}-{int(time.time())}"
            await self.create_new_session(project_id, f"Temporary-{provider}")
        
        self.current_session.ai_providers_used.add(provider)
        if self.current_context:
            self.current_context.active_ai_provider = provider
            
            # Add to conversation history
            self.current_context.add_conversation_turn(
                "system", 
                f"Switching to AI provider: {provider}", 
                provider
            )
        
        # Update database
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute('''
                UPDATE brain_sessions
                SET ai_providers_used = ?, total_interactions = total_interactions + 1
                WHERE session_id = ?
            ''', (json.dumps(list(self.current_session.ai_providers_used)), self.current_session.session_id))
            
            if self.current_context:
                await conn.execute('''
                    UPDATE persistent_contexts
                    SET active_ai_provider = ?, conversation_history = ?
                    WHERE session_id = ?
                ''', (
                    self.current_context.active_ai_provider,
                    json.dumps(self.current_context.conversation_history),
                    self.current_session.session_id
                ))
            
            await conn.commit()
        
        logger.info(f"Switched to AI provider: {provider} in session {self.current_session.session_id}")
        return True
    
    async def add_concept(self, content: str, ai_provider: str, tags: List[str] = None, importance: float = 1.0) -> str:
        """Add a new concept to the cross-AI knowledge base."""
        import uuid
        concept_id = str(uuid.uuid4())
        
        concept = CrossAIConcept(
            concept_id=concept_id,
            content=content,
            ai_providers={ai_provider},
            created_at=time.time(),
            last_accessed=time.time(),
            importance_score=importance,
            tags=tags or []
        )
        
        # Add to semantic cache if available
        if self.semantic_cache and self.semantic_cache.enabled:
            try:
                await self.semantic_cache.add(content, content, {"concept_id": concept_id, "tags": tags})
            except Exception as e:
                logger.error(f"Failed to add concept to semantic cache: {e}")
        
        # Save to database
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute('''
                INSERT INTO cross_ai_concepts
                (concept_id, content, embeddings, ai_providers, created_at, last_accessed, importance_score, tags, related_concepts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                concept_id, content, None,  # embeddings would be stored separately if using vector DB
                json.dumps(list(concept.ai_providers)), concept.created_at, concept.last_accessed,
                concept.importance_score, json.dumps(concept.tags), json.dumps(concept.related_concepts)
            ))
            await conn.commit()
        
        logger.info(f"Added concept {concept_id[:8]}... from {ai_provider}")
        return concept_id
    
    async def get_project(self, project_id: str) -> Optional[ProjectContext]:
        """Retrieve a project context."""
        if self.current_project and self.current_project.project_id == project_id:
            return self.current_project
        
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute('''
                SELECT * FROM projects WHERE project_id = ?
            ''', (project_id,))
            row = await cursor.fetchone()
            
            if row:
                project = ProjectContext(
                    project_id=row['project_id'],
                    name=row['name'],
                    path=row['path'],
                    language=row['language'],
                    framework=row['framework'],
                    created_at=row['created_at'],
                    last_accessed=row['last_accessed'],
                    metadata=json.loads(row['metadata']) if row['metadata'] else {},
                    tags=json.loads(row['tags']) if row['tags'] else []
                )
                
                # Update access time in DB
                await conn.execute('''
                    UPDATE projects SET last_accessed = ? WHERE project_id = ?
                ''', (time.time(), project_id))
                await conn.commit()
                
                return project
        
        return None
    
    async def save_project(self, project: ProjectContext):
        """Save a project context."""
        project.update_access_time()
        
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute('''
                INSERT OR REPLACE INTO projects
                (project_id, name, path, language, framework, created_at, last_accessed, metadata, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project.project_id, project.name, project.path, project.language,
                project.framework, project.created_at, project.last_accessed,
                json.dumps(project.metadata), json.dumps(project.tags)
            ))
            await conn.commit()
        
        if self.current_project and self.current_project.project_id == project.project_id:
            self.current_project = project
    
    async def get_relevant_concepts(self, query: str, limit: int = 5) -> List[CrossAIConcept]:
        """Find relevant concepts using semantic search."""
        results = []
        
        if self.semantic_cache and self.semantic_cache.enabled:
            try:
                # Search for semantic matches
                semantic_result = await self.semantic_cache.get_similar(query)
                if semantic_result:
                    # Find the actual concept in the DB based on similarity
                    async with aiosqlite.connect(self.db_path) as conn:
                        conn.row_factory = aiosqlite.Row
                        cursor = await conn.execute('''
                            SELECT * FROM cross_ai_concepts 
                            WHERE content LIKE ? 
                            ORDER BY importance_score DESC
                            LIMIT ?
                        ''', (f'%{query}%', limit))
                        
                        rows = await cursor.fetchall()
                        for row in rows:
                            results.append(CrossAIConcept(
                                concept_id=row['concept_id'],
                                content=row['content'],
                                ai_providers=set(json.loads(row['ai_providers'])),
                                created_at=row['created_at'],
                                last_accessed=row['last_accessed'],
                                importance_score=row['importance_score'],
                                tags=json.loads(row['tags']) if row['tags'] else [],
                                related_concepts=json.loads(row['related_concepts']) if row['related_concepts'] else []
                            ))
            except Exception as e:
                logger.error(f"Semantic search failed: {e}")
        
        # If no semantic matches or semantic cache disabled, do text search
        if not results:
            async with aiosqlite.connect(self.db_path) as conn:
                conn.row_factory = aiosqlite.Row
                cursor = await conn.execute('''
                    SELECT * FROM cross_ai_concepts 
                    WHERE content LIKE ? OR tags LIKE ?
                    ORDER BY importance_score DESC
                    LIMIT ?
                ''', (f'%{query}%', f'%{query}%', limit))
                
                rows = await cursor.fetchall()
                for row in rows:
                    results.append(CrossAIConcept(
                        concept_id=row['concept_id'],
                        content=row['content'],
                        ai_providers=set(json.loads(row['ai_providers'])),
                        created_at=row['created_at'],
                        last_accessed=row['last_accessed'],
                        importance_score=row['importance_score'],
                        tags=json.loads(row['tags']) if row['tags'] else [],
                        related_concepts=json.loads(row['related_concepts']) if row['related_concepts'] else []
                    ))
        
        return results[:limit]
    
    async def load_session_context(self, session_id: str) -> Optional[PersistentContext]:
        """Load the persistent context for a session."""
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute('''
                SELECT * FROM persistent_contexts WHERE session_id = ?
            ''', (session_id,))
            row = await cursor.fetchone()
            
            if row:
                context = PersistentContext(
                    session_id=row['session_id'],
                    project_id=row['project_id'],
                    current_task=row['current_task'],
                    active_ai_provider=row['active_ai_provider'],
                    conversation_history=json.loads(row['conversation_history']) if row['conversation_history'] else [],
                    current_working_directory=row['current_working_directory'],
                    relevant_files=json.loads(row['relevant_files']) if row['relevant_files'] else [],
                    temporary_context=json.loads(row['temporary_context']) if row['temporary_context'] else {}
                )
                return context
        
        return None
    
    async def update_session_context(self, context: PersistentContext):
        """Update the persistent context for the current session."""
        if not self.current_session or context.session_id != self.current_session.session_id:
            logger.warning("Context does not match current session")
            return
        
        # Update conversation history with access time
        if self.current_session:
            self.current_session.total_interactions += 1
        
        # Save to database
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute('''
                UPDATE persistent_contexts
                SET current_task = ?, active_ai_provider = ?, conversation_history = ?,
                    current_working_directory = ?, relevant_files = ?, temporary_context = ?
                WHERE session_id = ?
            ''', (
                context.current_task, context.active_ai_provider,
                json.dumps(context.conversation_history), context.current_working_directory,
                json.dumps(context.relevant_files), json.dumps(context.temporary_context),
                context.session_id
            ))
            
            # Update session info too
            await conn.execute('''
                UPDATE brain_sessions
                SET total_interactions = ?
                WHERE session_id = ?
            ''', (self.current_session.total_interactions, self.current_session.session_id))
            
            await conn.commit()
        
        self.current_context = context
    
    async def get_active_sessions(self) -> List[BrainSession]:
        """Get all active brain sessions."""
        sessions = []
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute('''
                SELECT * FROM brain_sessions WHERE active = 1
            ''')
            rows = await cursor.fetchall()
            
            for row in rows:
                session = BrainSession(
                    session_id=row['session_id'],
                    project_id=row['project_id'],
                    start_time=row['start_time'],
                    end_time=row['end_time'],
                    ai_providers_used=set(json.loads(row['ai_providers_used'])),
                    total_interactions=row['total_interactions'],
                    active=bool(row['active'])
                )
                sessions.append(session)
        
        return sessions
    
    async def get_project_stats(self, project_id: str) -> Dict[str, Any]:
        """Get statistics for a specific project."""
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            
            # Get session stats
            cursor = await conn.execute('''
                SELECT COUNT(*) as total_sessions, 
                       SUM(total_interactions) as total_interactions,
                       MIN(start_time) as first_session,
                       MAX(start_time) as last_session
                FROM brain_sessions WHERE project_id = ?
            ''', (project_id,))
            session_stats = await cursor.fetchone()
            
            # Get concept stats
            cursor = await conn.execute('''
                SELECT COUNT(*) as total_concepts,
                       AVG(importance_score) as avg_importance,
                       COUNT(DISTINCT ai_providers) as unique_providers
                FROM cross_ai_concepts
            ''')
            concept_stats = await cursor.fetchone()
            
            return {
                'project_id': project_id,
                'total_sessions': session_stats['total_sessions'],
                'total_interactions': session_stats['total_interactions'],
                'first_session': session_stats['first_session'],
                'last_session': session_stats['last_session'],
                'total_concepts': concept_stats['total_concepts'],
                'avg_concept_importance': concept_stats['avg_importance'],
                'unique_ai_providers': concept_stats['unique_providers']
            }
    
    async def cleanup_inactive_sessions(self, max_age_days: int = 30):
        """Clean up sessions that have been inactive for more than max_age_days."""
        cutoff_time = time.time() - (max_age_days * 24 * 3600)
        
        async with aiosqlite.connect(self.db_path) as conn:
            # Find and deactivate old sessions
            await conn.execute('''
                UPDATE brain_sessions 
                SET active = 0 
                WHERE active = 1 AND end_time < ?
            ''', (cutoff_time,))
            
            await conn.commit()
        
        logger.info(f"Cleaned up sessions older than {max_age_days} days")

# Global brain state manager instance
_brain_manager = None

def get_brain_manager() -> BrainStateManager:
    """Get the global brain state manager instance."""
    global _brain_manager
    if _brain_manager is None:
        _brain_manager = BrainStateManager()
    return _brain_manager

def set_brain_manager(manager: BrainStateManager):
    """Set the global brain state manager instance."""
    global _brain_manager
    _brain_manager = manager