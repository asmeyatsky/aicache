"""
LLM Continuation Module: Vector-enhanced session context transfer between AI providers.

This module extends the existing Living Brain system to enable seamless continuation
of conversations and context between different LLMs (Claude, Gemini, Qwen, etc.)
using vector database storage for large context chunks.
"""

import os
import json
import time
import asyncio
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    import aiosqlite
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

from .living_brain import BrainStateManager, PersistentContext, CrossAIConcept
from .semantic import SemanticCache
from .config import get_config

logger = logging.getLogger(__name__)

@dataclass
class ContinuationPackage:
    """A package of context that can be transferred between LLMs."""
    package_id: str
    source_session_id: str
    source_llm: str
    target_llm: str
    timestamp: float
    project_context: Dict[str, Any]
    summary_concepts: List[str]
    recent_conversation: List[Dict[str, Any]]
    relevant_files: List[str]
    current_task: Optional[str]
    metadata: Dict[str, Any]
    vector_embeddings: Optional[List[float]] = None  # For semantic search

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ContinuationContext:
    """Context for continuation operations."""
    session_id: str
    llm_provider: str
    context_summary: str
    creation_time: float
    relevance_score: float = 0.0
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class ContinuationManager:
    """
    Manages the creation, storage, and retrieval of continuation packages
    using vector databases for semantic search and context matching.
    """

    def __init__(self, cache_dir: str = None):
        self.config = get_config()

        if cache_dir is None:
            cache_dir = os.path.expanduser("~/.cache/aicache/continuation")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = self.cache_dir / "continuation.db"
        
        # Initialize semantic cache for context matching
        self.semantic_config = self.config.get('semantic_cache', {})
        self.semantic_cache = None
        
        # Initialize brain state manager for context access
        self.brain_manager = None
        
        logger.info(f"Continuation Manager initialized at {self.cache_dir}")

    async def init_db(self):
        """Initialize the continuation database."""
        if not SQLITE_AVAILABLE:
            logger.error("aiosqlite not available, cannot initialize continuation DB")
            return

        async with aiosqlite.connect(self.db_path) as conn:
            # Create table for continuation packages
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS continuation_packages (
                    package_id TEXT PRIMARY KEY,
                    source_session_id TEXT,
                    source_llm TEXT,
                    target_llm TEXT,
                    timestamp REAL,
                    project_context TEXT,
                    summary_concepts TEXT,
                    recent_conversation TEXT,
                    relevant_files TEXT,
                    current_task TEXT,
                    metadata TEXT,
                    vector_embeddings BLOB
                )
            ''')

            # Create table for continuation contexts
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS continuation_contexts (
                    context_id TEXT PRIMARY KEY,
                    session_id TEXT,
                    llm_provider TEXT,
                    context_summary TEXT,
                    creation_time REAL,
                    relevance_score REAL,
                    tags TEXT
                )
            ''')

            # Create indexes for performance
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_source_session ON continuation_packages(source_session_id)
            ''')
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_target_llm ON continuation_packages(target_llm)
            ''')
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp ON continuation_packages(timestamp)
            ''')
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_session_id ON continuation_contexts(session_id)
            ''')

            await conn.commit()

        # Initialize semantic cache after db setup
        if self.semantic_config.get('enabled', True):
            try:
                self.semantic_cache = SemanticCache(self.semantic_config)
                logger.info("Semantic cache initialized for continuation")
            except Exception as e:
                logger.warning(f"Failed to initialize semantic cache: {e}")
                self.semantic_cache = None

    async def set_brain_manager(self, brain_manager: BrainStateManager):
        """Set the brain manager for context access."""
        self.brain_manager = brain_manager

    async def create_continuation_package(
        self, 
        session_id: str, 
        target_llm: str,
        max_conversation_length: int = 20,
        max_concepts: int = 50
    ) -> Optional[str]:
        """
        Create a continuation package from the current session for use in another LLM.
        
        Args:
            session_id: The source session ID
            target_llm: The target LLM provider (e.g., 'gemini', 'claude', 'qwen')
            max_conversation_length: Maximum number of conversation turns to include
            max_concepts: Maximum number of concepts to include
            
        Returns:
            Package ID if successful, None otherwise
        """
        if not self.brain_manager:
            logger.error("Brain manager not set, cannot create continuation package")
            return None

        # Load the session context
        context = await self.brain_manager.load_session_context(session_id)
        if not context:
            logger.error(f"Session context not found: {session_id}")
            return None

        # Get project context
        project = await self.brain_manager.get_project(context.project_id)
        project_context = asdict(project) if project else {}

        # Get relevant concepts
        concepts = await self.brain_manager.get_relevant_concepts("", limit=max_concepts)
        summary_concepts = [c.content for c in concepts]

        # Prepare recent conversation (limit to last N exchanges)
        recent_conversation = context.conversation_history[-max_conversation_length:]

        # Determine source LLM from conversation history
        source_llm = "unknown"
        if recent_conversation:
            source_llm = recent_conversation[-1].get('ai_provider', 'unknown')

        # Create package ID
        package_id = hashlib.sha256(f"{session_id}_{target_llm}_{time.time()}".encode()).hexdigest()[:16]

        # Create continuation package
        package = ContinuationPackage(
            package_id=package_id,
            source_session_id=session_id,
            source_llm=source_llm,
            target_llm=target_llm,
            timestamp=time.time(),
            project_context=project_context,
            summary_concepts=summary_concepts,
            recent_conversation=recent_conversation,
            relevant_files=context.relevant_files,
            current_task=context.current_task,
            metadata={
                "max_conversation_length": max_conversation_length,
                "max_concepts": max_concepts,
                "export_time": time.time()
            }
        )

        # Store in database
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute('''
                INSERT INTO continuation_packages
                (package_id, source_session_id, source_llm, target_llm, timestamp,
                 project_context, summary_concepts, recent_conversation, relevant_files,
                 current_task, metadata, vector_embeddings)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                package.package_id, package.source_session_id, package.source_llm,
                package.target_llm, package.timestamp,
                json.dumps(package.project_context),
                json.dumps(package.summary_concepts),
                json.dumps(package.recent_conversation),
                json.dumps(package.relevant_files),
                package.current_task,
                json.dumps(package.metadata),
                None  # vector_embeddings would be populated separately
            ))
            await conn.commit()

        # Add to semantic cache for later retrieval
        if self.semantic_cache and self.semantic_cache.enabled:
            try:
                # Create a summary for semantic search
                context_summary = self._create_context_summary(package)
                
                # Add to semantic cache
                await self.semantic_cache.add(
                    context_summary,
                    json.dumps(package.to_dict()),
                    {
                        "type": "continuation_package",
                        "target_llm": target_llm,
                        "source_session_id": session_id,
                        "package_id": package.package_id
                    }
                )
                
                # Also add individual conversation turns for fine-grained retrieval
                for turn in recent_conversation[-5:]:  # Last 5 turns
                    await self.semantic_cache.add(
                        f"{turn['role']}: {turn['content']}",
                        json.dumps(turn),
                        {
                            "type": "conversation_turn",
                            "session_id": session_id,
                            "package_id": package.package_id
                        }
                    )
            except Exception as e:
                logger.error(f"Failed to add continuation package to semantic cache: {e}")

        logger.info(f"Created continuation package {package_id} for {target_llm}")
        return package_id

    def _create_context_summary(self, package: ContinuationPackage) -> str:
        """Create a summary string for semantic search."""
        summary_parts = []
        
        if package.project_context:
            summary_parts.append(f"Project: {package.project_context.get('name', 'Unknown')}")
            summary_parts.append(f"Language: {package.project_context.get('language', 'Unknown')}")
            summary_parts.append(f"Framework: {package.project_context.get('framework', 'Unknown')}")
        
        if package.current_task:
            summary_parts.append(f"Current Task: {package.current_task}")
        
        if package.summary_concepts:
            summary_parts.append("Key Concepts: " + ", ".join(package.summary_concepts[:5]))  # First 5 concepts
        
        if package.recent_conversation:
            # Add last few conversation turns
            recent_turns = package.recent_conversation[-3:]  # Last 3 turns
            for turn in recent_turns:
                role = turn.get('role', 'unknown')
                content = turn.get('content', '')[:100]  # First 100 chars
                summary_parts.append(f"{role}: {content}...")
        
        return "\n".join(summary_parts)

    async def load_continuation_package(
        self, 
        package_id: str, 
        new_session_id: Optional[str] = None
    ) -> Optional[ContinuationPackage]:
        """
        Load a continuation package by ID.
        
        Args:
            package_id: The ID of the package to load
            new_session_id: Optional new session ID (if creating a new session)
            
        Returns:
            ContinuationPackage if found, None otherwise
        """
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute('''
                SELECT * FROM continuation_packages WHERE package_id = ?
            ''', (package_id,))
            row = await cursor.fetchone()

            if not row:
                logger.warning(f"Continuation package not found: {package_id}")
                return None

            # Reconstruct the package
            package = ContinuationPackage(
                package_id=row['package_id'],
                source_session_id=row['source_session_id'],
                source_llm=row['source_llm'],
                target_llm=row['target_llm'],
                timestamp=row['timestamp'],
                project_context=json.loads(row['project_context']) if row['project_context'] else {},
                summary_concepts=json.loads(row['summary_concepts']) if row['summary_concepts'] else [],
                recent_conversation=json.loads(row['recent_conversation']) if row['recent_conversation'] else [],
                relevant_files=json.loads(row['relevant_files']) if row['relevant_files'] else [],
                current_task=row['current_task'],
                metadata=json.loads(row['metadata']) if row['metadata'] else {},
                vector_embeddings=None  # Not currently stored
            )

        return package

    async def search_continuation_packages(
        self, 
        query: str, 
        target_llm: Optional[str] = None, 
        limit: int = 10
    ) -> List[Tuple[ContinuationPackage, float]]:
        """
        Search for relevant continuation packages using semantic search.
        
        Args:
            query: Natural language query to search for
            target_llm: Filter by target LLM (optional)
            limit: Maximum number of results to return
            
        Returns:
            List of tuples (package, similarity_score)
        """
        results = []

        if self.semantic_cache and self.semantic_cache.enabled:
            try:
                # Search for semantic matches
                semantic_result = await self.semantic_cache.get_similar(query)
                if semantic_result:
                    # Find the actual packages in the DB based on similarity
                    async with aiosqlite.connect(self.db_path) as conn:
                        conn.row_factory = aiosqlite.Row
                        
                        # Build query with optional target LLM filter
                        base_query = '''
                            SELECT * FROM continuation_packages
                            WHERE package_id IN (
                                SELECT value FROM json_each(?)
                            )
                        '''
                        params = [json.dumps([semantic_result.cache_key])]
                        
                        if target_llm:
                            base_query += " AND target_llm = ?"
                            params.append(target_llm)
                        
                        base_query += " ORDER BY timestamp DESC LIMIT ?"
                        params.append(limit)
                        
                        cursor = await conn.execute(base_query, params)
                        rows = await cursor.fetchall()
                        
                        for row in rows:
                            package = ContinuationPackage(
                                package_id=row['package_id'],
                                source_session_id=row['source_session_id'],
                                source_llm=row['source_llm'],
                                target_llm=row['target_llm'],
                                timestamp=row['timestamp'],
                                project_context=json.loads(row['project_context']) if row['project_context'] else {},
                                summary_concepts=json.loads(row['summary_concepts']) if row['summary_concepts'] else [],
                                recent_conversation=json.loads(row['recent_conversation']) if row['recent_conversation'] else [],
                                relevant_files=json.loads(row['relevant_files']) if row['relevant_files'] else [],
                                current_task=row['current_task'],
                                metadata=json.loads(row['metadata']) if row['metadata'] else {},
                                vector_embeddings=None
                            )
                            # Use semantic similarity as score (would need to be passed properly)
                            results.append((package, semantic_result.similarity_threshold))
            except Exception as e:
                logger.error(f"Semantic search failed: {e}")

        # If no semantic matches or semantic cache disabled, do text search
        if not results:
            async with aiosqlite.connect(self.db_path) as conn:
                conn.row_factory = aiosqlite.Row
                
                base_query = '''
                    SELECT * FROM continuation_packages
                    WHERE project_context LIKE ? OR current_task LIKE ? OR summary_concepts LIKE ?
                '''
                params = [f'%{query}%', f'%{query}%', f'%{query}%']
                
                if target_llm:
                    base_query += " AND target_llm = ?"
                    params.append(target_llm)
                
                base_query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor = await conn.execute(base_query, params)
                rows = await cursor.fetchall()
                
                for row in rows:
                    package = ContinuationPackage(
                        package_id=row['package_id'],
                        source_session_id=row['source_session_id'],
                        source_llm=row['source_llm'],
                        target_llm=row['target_llm'],
                        timestamp=row['timestamp'],
                        project_context=json.loads(row['project_context']) if row['project_context'] else {},
                        summary_concepts=json.loads(row['summary_concepts']) if row['summary_concepts'] else [],
                        recent_conversation=json.loads(row['recent_conversation']) if row['recent_conversation'] else [],
                        relevant_files=json.loads(row['relevant_files']) if row['relevant_files'] else [],
                        current_task=row['current_task'],
                        metadata=json.loads(row['metadata']) if row['metadata'] else {},
                        vector_embeddings=None
                    )
                    results.append((package, 0.5))  # Default score for text matches

        return results[:limit]

    async def apply_continuation_package(
        self, 
        package_id: str, 
        target_session_id: str
    ) -> bool:
        """
        Apply a continuation package to a target session.
        
        Args:
            package_id: The ID of the package to apply
            target_session_id: The target session ID to apply to
            
        Returns:
            True if successful, False otherwise
        """
        if not self.brain_manager:
            logger.error("Brain manager not set, cannot apply continuation package")
            return False

        package = await self.load_continuation_package(package_id)
        if not package:
            logger.error(f"Failed to load continuation package: {package_id}")
            return False

        # Load the target session context
        target_context = await self.brain_manager.load_session_context(target_session_id)
        if not target_context:
            logger.error(f"Target session context not found: {target_session_id}")
            return False

        # Update the target context with data from the package
        target_context.current_task = package.current_task or target_context.current_task
        
        # Add conversation history from the package
        for turn in package.recent_conversation:
            target_context.add_conversation_turn(
                turn['role'],
                turn['content'],
                package.target_llm,  # Use target LLM as provider
                turn.get('timestamp', time.time())
            )

        # Add relevant files
        target_context.relevant_files.extend([
            f for f in package.relevant_files 
            if f not in target_context.relevant_files
        ])

        # Update the session context
        await self.brain_manager.update_session_context(target_context)

        # Add concepts to the knowledge base
        for concept_content in package.summary_concepts:
            await self.brain_manager.add_concept(
                concept_content,
                package.target_llm,
                tags=['continuation', 'imported'],
                importance=0.8
            )

        logger.info(f"Applied continuation package {package_id} to session {target_session_id}")
        return True

    async def list_packages(
        self, 
        target_llm: Optional[str] = None, 
        source_session_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List continuation packages with optional filtering.
        
        Args:
            target_llm: Filter by target LLM (optional)
            source_session_id: Filter by source session (optional)
            limit: Maximum number of results to return
            
        Returns:
            List of package metadata dictionaries
        """
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            
            base_query = "SELECT package_id, source_session_id, source_llm, target_llm, timestamp, current_task FROM continuation_packages"
            params = []
            
            conditions = []
            if target_llm:
                conditions.append("target_llm = ?")
                params.append(target_llm)
            if source_session_id:
                conditions.append("source_session_id = ?")
                params.append(source_session_id)
            
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)
            
            base_query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor = await conn.execute(base_query, params)
            rows = await cursor.fetchall()
            
            packages = []
            for row in rows:
                packages.append({
                    'package_id': row['package_id'],
                    'source_session_id': row['source_session_id'],
                    'source_llm': row['source_llm'],
                    'target_llm': row['target_llm'],
                    'timestamp': row['timestamp'],
                    'current_task': row['current_task'],
                    'timestamp_readable': datetime.fromtimestamp(row['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        return packages

    async def delete_package(self, package_id: str) -> bool:
        """
        Delete a continuation package.
        
        Args:
            package_id: The ID of the package to delete
            
        Returns:
            True if successful, False otherwise
        """
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute(
                "DELETE FROM continuation_packages WHERE package_id = ?",
                (package_id,)
            )
            await conn.commit()
            deleted = cursor.rowcount > 0

        # Remove from semantic cache if available
        if self.semantic_cache and self.semantic_cache.enabled:
            try:
                await self.semantic_cache.delete(package_id)
            except Exception as e:
                logger.error(f"Failed to delete from semantic cache: {e}")

        if deleted:
            logger.info(f"Deleted continuation package: {package_id}")
        else:
            logger.warning(f"Package not found for deletion: {package_id}")

        return deleted


# Global continuation manager instance
_continuation_manager = None


def get_continuation_manager() -> ContinuationManager:
    """Get the global continuation manager instance."""
    global _continuation_manager
    if _continuation_manager is None:
        _continuation_manager = ContinuationManager()
    return _continuation_manager


def set_continuation_manager(manager: ContinuationManager):
    """Set the global continuation manager instance."""
    global _continuation_manager
    _continuation_manager = manager