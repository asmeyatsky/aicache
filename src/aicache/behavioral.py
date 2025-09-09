"""
Behavioral learning system for predictive caching.
Analyzes user patterns to predict future queries and cache needs.
"""

import os
import asyncio
import time
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
from pathlib import Path
import hashlib
import sqlite3
import aiosqlite

logger = logging.getLogger(__name__)

@dataclass
class QueryPattern:
    """Represents a learned query pattern."""
    sequence: List[str]  # Sequence of query hashes
    frequency: int
    last_seen: float
    context_features: Dict[str, Any]
    success_rate: float  # How often this pattern leads to cache hits
    next_queries: Dict[str, float]  # Probable next queries with confidence

@dataclass
class UserBehavior:
    """User behavior profile."""
    user_id: str
    common_patterns: List[QueryPattern]
    preferred_contexts: Dict[str, int]  # Context types and frequency
    time_patterns: Dict[str, List[int]]  # Hour-based activity patterns
    session_length_avg: float
    query_frequency: float  # Queries per session
    
@dataclass  
class ContextualTrigger:
    """Context-based cache prefetch trigger."""
    trigger_context: Dict[str, Any]
    predicted_queries: List[Tuple[str, float]]  # Query and confidence
    prefetch_priority: float
    created_at: float
    success_count: int = 0
    total_triggers: int = 0

class BehavioralAnalyzer:
    """Analyzes user behavior patterns for predictive caching."""
    
    def __init__(self, cache_dir: str):
        self.cache_dir = Path(cache_dir)
        self.db_path = self.cache_dir / "behavioral.db"
        self.patterns = {}
        self.user_profiles = {}
        self.context_triggers = {}
        
        # Pattern detection parameters
        self.min_pattern_length = 2
        self.max_pattern_length = 5
        self.min_frequency = 3
        self.pattern_decay_hours = 24 * 7  # 1 week
        
        logger.info(f"Behavioral analyzer initialized at {self.cache_dir}")
    
    async def init_db(self):
        """Initialize behavioral analysis database."""
        await self._create_tables()
        await self._load_patterns()
    
    async def _create_tables(self):
        """Create database tables for behavioral data."""
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS query_sequences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    session_id TEXT,
                    query_hash TEXT,
                    query_text TEXT,
                    context TEXT,  -- JSON
                    timestamp REAL,
                    cache_hit BOOLEAN,
                    response_time REAL
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS learned_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_hash TEXT UNIQUE,
                    sequence TEXT,  -- JSON array of query hashes
                    frequency INTEGER,
                    last_seen REAL,
                    context_features TEXT,  -- JSON
                    success_rate REAL,
                    next_queries TEXT  -- JSON dict of next queries
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    profile_data TEXT,  -- JSON serialized UserBehavior
                    last_updated REAL
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS contextual_triggers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trigger_hash TEXT UNIQUE,
                    trigger_context TEXT,  -- JSON
                    predicted_queries TEXT,  -- JSON
                    priority REAL,
                    created_at REAL,
                    success_count INTEGER DEFAULT 0,
                    total_triggers INTEGER DEFAULT 0
                )
            ''')
            
            # Create indexes
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_query_user_time ON query_sequences(user_id, timestamp)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_query_session ON query_sequences(session_id, timestamp)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_pattern_frequency ON learned_patterns(frequency DESC)')
            
            await conn.commit()
    
    async def _load_patterns(self):
        """Load existing patterns from database."""
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row  # Enable row access by name
            # Load patterns
            cursor = await conn.execute('SELECT * FROM learned_patterns WHERE last_seen > ?', 
                                      (time.time() - self.pattern_decay_hours * 3600,))
            patterns = await cursor.fetchall()
            
            for pattern in patterns:
                pattern_hash = pattern['pattern_hash']
                self.patterns[pattern_hash] = QueryPattern(
                    sequence=json.loads(pattern['sequence']),
                    frequency=pattern['frequency'],
                    last_seen=pattern['last_seen'],
                    context_features=json.loads(pattern['context_features']),
                    success_rate=pattern['success_rate'],
                    next_queries=json.loads(pattern['next_queries'])
                )
            
            # Load contextual triggers
            cursor = await conn.execute('SELECT * FROM contextual_triggers')
            triggers = await cursor.fetchall()
            
            for trigger in triggers:
                trigger_hash = trigger['trigger_hash']
                self.context_triggers[trigger_hash] = ContextualTrigger(
                    trigger_context=json.loads(trigger['trigger_context']),
                    predicted_queries=json.loads(trigger['predicted_queries']),
                    prefetch_priority=trigger['priority'],
                    created_at=trigger['created_at'],
                    success_count=trigger['success_count'],
                    total_triggers=trigger['total_triggers']
                )
        
        logger.info(f"Loaded {len(self.patterns)} patterns and {len(self.context_triggers)} triggers")
    
    def _get_query_hash(self, query: str, context: Dict[str, Any] = None) -> str:
        """Generate hash for query+context combination."""
        hasher = hashlib.sha256()
        hasher.update(query.encode('utf-8'))
        if context:
            sorted_context = json.dumps(context, sort_keys=True)
            hasher.update(sorted_context.encode('utf-8'))
        return hasher.hexdigest()[:16]  # Shorter hash for patterns
    
    async def log_query(self, user_id: str, session_id: str, query: str, 
                       context: Dict[str, Any], cache_hit: bool, response_time: float):
        """Log a query for pattern analysis."""
        query_hash = self._get_query_hash(query, context)
        
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute('''
                INSERT INTO query_sequences 
                (user_id, session_id, query_hash, query_text, context, timestamp, cache_hit, response_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, session_id, query_hash, query, json.dumps(context), 
                 time.time(), cache_hit, response_time))
            await conn.commit()
        
        # Trigger pattern analysis for this session
        await self._analyze_session_patterns(session_id)
    
    async def _analyze_session_patterns(self, session_id: str):
        """Analyze patterns within a session."""
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row  # Enable row access by name
            # Get recent queries from this session (last 10)
            cursor = await conn.execute('''
                SELECT query_hash, context, timestamp, cache_hit
                FROM query_sequences 
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT 10
            ''', (session_id,))
            
            queries = await cursor.fetchall()
            
            if len(queries) < self.min_pattern_length:
                return
            
            # Reverse to get chronological order
            queries = list(reversed(queries))
            
            # Extract patterns of different lengths
            for pattern_length in range(self.min_pattern_length, 
                                      min(len(queries) + 1, self.max_pattern_length + 1)):
                for i in range(len(queries) - pattern_length + 1):
                    pattern_sequence = [q['query_hash'] for q in queries[i:i+pattern_length]]
                    
                    # Calculate pattern features
                    context_features = self._extract_context_features(queries[i:i+pattern_length])
                    success_rate = sum(q['cache_hit'] for q in queries[i:i+pattern_length]) / pattern_length
                    
                    # Update or create pattern
                    await self._update_pattern(pattern_sequence, context_features, success_rate)
    
    def _extract_context_features(self, queries: List[Dict]) -> Dict[str, Any]:
        """Extract common context features from a sequence of queries."""
        features = {}
        
        # Aggregate context data
        all_contexts = []
        for query in queries:
            try:
                context = json.loads(query['context']) if query['context'] else {}
                all_contexts.append(context)
            except:
                all_contexts.append({})
        
        if not all_contexts:
            return features
        
        # Find common context keys and their most frequent values
        all_keys = set()
        for ctx in all_contexts:
            all_keys.update(ctx.keys())
        
        for key in all_keys:
            values = [ctx.get(key) for ctx in all_contexts if key in ctx]
            if values:
                # Get most common value
                value_counts = Counter(values)
                most_common_value, count = value_counts.most_common(1)[0]
                if count >= len(all_contexts) * 0.5:  # At least 50% of queries
                    features[key] = most_common_value
        
        # Add temporal features
        timestamps = [q['timestamp'] for q in queries]
        if timestamps:
            features['time_span'] = max(timestamps) - min(timestamps)
            features['query_frequency'] = len(timestamps) / (features['time_span'] + 1)
        
        return features
    
    async def _update_pattern(self, sequence: List[str], context_features: Dict[str, Any], 
                            success_rate: float):
        """Update or create a learned pattern."""
        pattern_hash = hashlib.sha256(json.dumps(sequence).encode()).hexdigest()
        current_time = time.time()
        
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row  # Enable row access by name
            # Check if pattern exists
            cursor = await conn.execute(
                'SELECT * FROM learned_patterns WHERE pattern_hash = ?',
                (pattern_hash,)
            )
            existing = await cursor.fetchone()
            
            if existing:
                # Update existing pattern
                new_frequency = existing['frequency'] + 1
                new_success_rate = (existing['success_rate'] * existing['frequency'] + success_rate) / new_frequency
                
                # Update next queries prediction (if this is not the last pattern)
                next_queries = json.loads(existing['next_queries'])
                
                await conn.execute('''
                    UPDATE learned_patterns 
                    SET frequency = ?, last_seen = ?, success_rate = ?, next_queries = ?
                    WHERE pattern_hash = ?
                ''', (new_frequency, current_time, new_success_rate, 
                     json.dumps(next_queries), pattern_hash))
            else:
                # Create new pattern
                await conn.execute('''
                    INSERT INTO learned_patterns 
                    (pattern_hash, sequence, frequency, last_seen, context_features, success_rate, next_queries)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (pattern_hash, json.dumps(sequence), 1, current_time,
                     json.dumps(context_features), success_rate, json.dumps({})))
            
            await conn.commit()
        
        # Update in-memory cache
        if pattern_hash in self.patterns:
            self.patterns[pattern_hash].frequency += 1
            self.patterns[pattern_hash].last_seen = current_time
        else:
            self.patterns[pattern_hash] = QueryPattern(
                sequence=sequence,
                frequency=1,
                last_seen=current_time,
                context_features=context_features,
                success_rate=success_rate,
                next_queries={}
            )
    
    async def predict_next_queries(self, user_id: str, session_id: str, 
                                 recent_queries: List[str], context: Dict[str, Any]) -> List[Tuple[str, float]]:
        """Predict likely next queries based on current pattern."""
        if len(recent_queries) < self.min_pattern_length:
            return []
        
        predictions = []
        
        # Check for matching patterns
        for pattern_length in range(self.min_pattern_length, len(recent_queries) + 1):
            pattern_sequence = recent_queries[-pattern_length:]
            
            for pattern_hash, pattern in self.patterns.items():
                if (len(pattern.sequence) >= pattern_length and 
                    pattern.sequence[:pattern_length] == pattern_sequence):
                    
                    # Calculate confidence based on frequency and context match
                    frequency_confidence = min(pattern.frequency / 10.0, 1.0)
                    context_confidence = self._calculate_context_similarity(context, pattern.context_features)
                    overall_confidence = (frequency_confidence + context_confidence) / 2
                    
                    # Add predictions for next queries
                    for next_query, next_confidence in pattern.next_queries.items():
                        combined_confidence = overall_confidence * next_confidence
                        predictions.append((next_query, combined_confidence))
        
        # Sort by confidence and remove duplicates
        predictions = sorted(set(predictions), key=lambda x: x[1], reverse=True)
        return predictions[:5]  # Top 5 predictions
    
    def _calculate_context_similarity(self, context1: Dict[str, Any], 
                                    context2: Dict[str, Any]) -> float:
        """Calculate similarity between two contexts."""
        if not context1 or not context2:
            return 0.0
        
        common_keys = set(context1.keys()) & set(context2.keys())
        if not common_keys:
            return 0.0
        
        matches = 0
        for key in common_keys:
            if context1[key] == context2[key]:
                matches += 1
        
        return matches / len(common_keys)
    
    async def identify_prefetch_triggers(self, context: Dict[str, Any]) -> List[Tuple[str, float]]:
        """Identify queries that should be prefetched based on context."""
        prefetch_candidates = []
        
        # Check contextual triggers
        for trigger_hash, trigger in self.context_triggers.items():
            similarity = self._calculate_context_similarity(context, trigger.trigger_context)
            
            if similarity > 0.7:  # High context similarity
                for query, confidence in trigger.predicted_queries:
                    adjusted_confidence = confidence * similarity * trigger.prefetch_priority
                    prefetch_candidates.append((query, adjusted_confidence))
        
        # Check time-based patterns
        current_hour = int(time.time() % (24 * 3600) // 3600)
        # TODO: Add time-based pattern matching
        
        return sorted(prefetch_candidates, key=lambda x: x[1], reverse=True)[:3]
    
    async def create_contextual_trigger(self, trigger_context: Dict[str, Any], 
                                      predicted_queries: List[Tuple[str, float]], priority: float):
        """Create a new contextual prefetch trigger."""
        trigger_hash = hashlib.sha256(json.dumps(trigger_context, sort_keys=True).encode()).hexdigest()
        
        trigger = ContextualTrigger(
            trigger_context=trigger_context,
            predicted_queries=predicted_queries,
            prefetch_priority=priority,
            created_at=time.time()
        )
        
        self.context_triggers[trigger_hash] = trigger
        
        # Persist to database
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute('''
                INSERT OR REPLACE INTO contextual_triggers
                (trigger_hash, trigger_context, predicted_queries, priority, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (trigger_hash, json.dumps(trigger_context), json.dumps(predicted_queries),
                 priority, time.time()))
            await conn.commit()
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Get behavioral analytics summary."""
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row  # Enable row access by name
            # Query statistics
            cursor = await conn.execute('SELECT COUNT(*) as total FROM query_sequences')
            total_queries = (await cursor.fetchone())['total']
            
            cursor = await conn.execute('SELECT COUNT(*) as hits FROM query_sequences WHERE cache_hit = 1')
            cache_hits = (await cursor.fetchone())['hits']
            
            cursor = await conn.execute('SELECT COUNT(DISTINCT user_id) as users FROM query_sequences')
            unique_users = (await cursor.fetchone())['users']
            
            cursor = await conn.execute('SELECT COUNT(DISTINCT session_id) as sessions FROM query_sequences')
            unique_sessions = (await cursor.fetchone())['sessions']
            
            # Pattern statistics  
            active_patterns = len([p for p in self.patterns.values() 
                                 if p.last_seen > time.time() - self.pattern_decay_hours * 3600])
            
            return {
                'total_queries': total_queries,
                'cache_hit_rate': cache_hits / total_queries if total_queries > 0 else 0,
                'unique_users': unique_users,
                'unique_sessions': unique_sessions,
                'active_patterns': active_patterns,
                'total_patterns': len(self.patterns),
                'contextual_triggers': len(self.context_triggers),
                'queries_per_session': total_queries / unique_sessions if unique_sessions > 0 else 0
            }