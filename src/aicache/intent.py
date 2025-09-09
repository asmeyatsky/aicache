"""
Intent-based caching system.
Understands the developer's intent and caches what they mean, not just what they type.
"""

import asyncio
import logging
import hashlib
import json
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict

from .llm_service import LLMService

logger = logging.getLogger(__name__)

@dataclass
class IntentCacheEntry:
    """Represents an intent-based cache entry."""
    intent_hash: str
    original_query: str
    intent_description: str
    canonical_query: str
    related_queries: List[str]
    context: Dict[str, Any]
    created_at: float
    access_count: int = 0

class IntentAnalyzer:
    """Analyzes developer intent from queries."""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.intent_cache: Dict[str, IntentCacheEntry] = {}
        
    async def analyze_intent(self, query: str, context: Dict[str, Any]) -> Optional[IntentCacheEntry]:
        """Analyze the intent behind a query."""
        # Generate intent description (even without LLM, we can do basic analysis)
        intent_description = self._generate_basic_intent_description(query, context)
        
        # Generate canonical query
        canonical_query = self._generate_basic_canonical_query(query, context)
        
        # Generate related queries
        related_queries = self._generate_basic_related_queries(query, context)
        
        # Create intent hash
        intent_hash = self._get_intent_hash(intent_description, context)
        
        # Create cache entry
        entry = IntentCacheEntry(
            intent_hash=intent_hash,
            original_query=query,
            intent_description=intent_description,
            canonical_query=canonical_query,
            related_queries=related_queries,
            context=context,
            created_at=asyncio.get_event_loop().time()
        )
        
        # Store in cache
        self.intent_cache[intent_hash] = entry
        return entry
        
    def _generate_basic_intent_description(self, query: str, context: Dict[str, Any]) -> str:
        """Generate a basic intent description without LLM."""
        # Simple heuristic-based intent analysis
        query_lower = query.lower()
        
        if 'function' in query_lower or 'method' in query_lower:
            return f"Request to create or understand a function in {context.get('language', 'code')}"
        elif 'class' in query_lower:
            return f"Request to create or understand a class in {context.get('language', 'code')}"
        elif 'error' in query_lower or 'exception' in query_lower:
            return f"Request to handle or debug an error in {context.get('language', 'code')}"
        elif 'import' in query_lower or 'library' in query_lower:
            return f"Request to use or understand a library in {context.get('language', 'code')}"
        else:
            return f"General {context.get('language', 'programming')} query about {query[:20]}..."
            
    def _generate_basic_canonical_query(self, original_query: str, context: Dict[str, Any]) -> str:
        """Generate a basic canonical query without LLM."""
        # Simple keyword extraction
        important_keywords = ['function', 'class', 'method', 'error', 'exception', 'import', 'library']
        query_lower = original_query.lower()
        
        # Extract keywords
        keywords = [word for word in important_keywords if word in query_lower]
        
        # Add language context
        language = context.get('language', '')
        if language and language not in original_query:
            return f"{original_query} {language}".strip()
            
        return original_query
        
    def _generate_basic_related_queries(self, original_query: str, context: Dict[str, Any]) -> List[str]:
        """Generate basic related queries without LLM."""
        query_lower = original_query.lower()
        language = context.get('language', '')
        
        related = []
        
        if 'function' in query_lower:
            related.extend([
                f"How to write a {language} function",
                f"{language} function best practices",
                f"{language} function examples"
            ])
        elif 'class' in query_lower:
            related.extend([
                f"How to write a {language} class",
                f"{language} class best practices",
                f"{language} class examples"
            ])
        elif 'error' in query_lower or 'exception' in query_lower:
            related.extend([
                f"How to handle {language} errors",
                f"{language} exception handling",
                f"Common {language} errors and solutions"
            ])
            
        # Add generic related queries
        if language:
            related.extend([
                f"{language} tutorial",
                f"{language} best practices",
                f"{language} cheat sheet"
            ])
            
        return related[:5]  # Limit to 5 queries
            
    def _get_intent_hash(self, intent_description: str, context: Dict[str, Any]) -> str:
        """Generate a hash for the intent."""
        hasher = hashlib.sha256()
        hasher.update(intent_description.encode('utf-8'))
        # Include key context elements
        key_context = {k: v for k, v in context.items() if k in ['language', 'framework', 'project_path']}
        if key_context:
            hasher.update(json.dumps(key_context, sort_keys=True).encode('utf-8'))
        return hasher.hexdigest()[:16]

class IntentBasedCache:
    """Cache system that works with developer intent."""
    
    def __init__(self, llm_service: LLMService):
        self.intent_analyzer = IntentAnalyzer(llm_service)
        self.intent_mappings: Dict[str, str] = {}  # intent_hash -> canonical_cache_key
        
    async def get_by_intent(self, query: str, context: Dict[str, Any]) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Get cache entry based on intent analysis."""
        # Analyze intent
        intent_entry = await self.intent_analyzer.analyze_intent(query, context)
        if not intent_entry:
            return None
            
        # Check if we have a mapping for this intent
        if intent_entry.intent_hash in self.intent_mappings:
            canonical_key = self.intent_mappings[intent_entry.intent_hash]
            return canonical_key, intent_entry.__dict__
            
        return None
        
    async def link_intent_to_cache(self, intent_hash: str, cache_key: str):
        """Link an intent to a specific cache entry."""
        self.intent_mappings[intent_hash] = cache_key