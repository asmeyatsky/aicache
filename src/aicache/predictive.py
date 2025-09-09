"""
Predictive caching system with proactive prefetching.
Uses behavioral patterns to predict and cache likely future queries.
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from collections import deque
import json

from .behavioral import BehavioralAnalyzer

logger = logging.getLogger(__name__)

@dataclass
class PrefetchRequest:
    """Represents a request to prefetch data."""
    query: str
    context: Dict[str, Any]
    confidence: float
    trigger_reason: str
    created_at: float
    priority: int = 1  # 1=low, 2=medium, 3=high
    estimated_cost: float = 1.0
    
    def __post_init__(self):
        if self.created_at == 0:
            self.created_at = time.time()

@dataclass
class PrefetchResult:
    """Result of a prefetch operation."""
    request: PrefetchRequest
    success: bool
    cache_key: str = ""
    execution_time: float = 0.0
    error: Optional[str] = None

class PredictivePrefetcher:
    """Manages predictive prefetching operations."""
    
    def __init__(self, enhanced_cache, behavioral_analyzer: BehavioralAnalyzer):
        self.cache = enhanced_cache
        self.behavioral = behavioral_analyzer
        
        # Prefetch management
        self.prefetch_queue = asyncio.PriorityQueue()
        self.active_prefetches: Set[str] = set()
        self.prefetch_history = deque(maxlen=1000)
        
        # Configuration
        self.max_concurrent_prefetches = 3
        self.prefetch_confidence_threshold = 0.6
        self.max_prefetch_cost_per_hour = 10.0
        self.current_hour_cost = 0.0
        self.last_cost_reset = time.time()
        
        # Background task
        self._prefetch_task = None
        self._running = False
        
        logger.info("Predictive prefetcher initialized")
    
    async def start(self):
        """Start the predictive prefetching background task."""
        if self._running:
            return
        
        self._running = True
        self._prefetch_task = asyncio.create_task(self._prefetch_worker())
        logger.info("Predictive prefetcher started")
    
    async def stop(self):
        """Stop the predictive prefetching."""
        self._running = False
        if self._prefetch_task:
            self._prefetch_task.cancel()
            try:
                await self._prefetch_task
            except asyncio.CancelledError:
                pass
        logger.info("Predictive prefetcher stopped")
    
    async def analyze_and_predict(self, user_id: str, session_id: str, 
                                query: str, context: Dict[str, Any], cache_hit: bool):
        """Analyze current query and predict future needs."""
        start_time = time.time()
        
        # Log the query for behavioral analysis
        await self.behavioral.log_query(user_id, session_id, query, context, 
                                       cache_hit, time.time() - start_time)
        
        # Get recent queries from this session (simplified - in real implementation, 
        # would query from behavioral analyzer's database)
        recent_queries = [self.behavioral._get_query_hash(query, context)]
        
        # Predict next queries
        predictions = await self.behavioral.predict_next_queries(
            user_id, session_id, recent_queries, context
        )
        
        # Create prefetch requests for high-confidence predictions
        for predicted_query, confidence in predictions:
            if confidence >= self.prefetch_confidence_threshold:
                await self.schedule_prefetch(
                    query=predicted_query,
                    context=context,
                    confidence=confidence,
                    trigger_reason=f"pattern_prediction_from_{query[:20]}..."
                )
        
        # Check for contextual triggers
        contextual_prefetches = await self.behavioral.identify_prefetch_triggers(context)
        for query_hash, confidence in contextual_prefetches:
            if confidence >= self.prefetch_confidence_threshold:
                await self.schedule_prefetch(
                    query=query_hash,
                    context=context,
                    confidence=confidence,
                    trigger_reason="contextual_trigger"
                )
    
    async def schedule_prefetch(self, query: str, context: Dict[str, Any], 
                              confidence: float, trigger_reason: str, priority: int = None):
        """Schedule a query for prefetching."""
        # Reset cost tracking if needed
        current_time = time.time()
        if current_time - self.last_cost_reset > 3600:  # 1 hour
            self.current_hour_cost = 0.0
            self.last_cost_reset = current_time
        
        # Check cost limits
        estimated_cost = self._estimate_query_cost(query, context)
        if self.current_hour_cost + estimated_cost > self.max_prefetch_cost_per_hour:
            logger.info(f"Skipping prefetch due to cost limit: {query[:30]}...")
            return
        
        # Determine priority based on confidence and context
        if priority is None:
            if confidence > 0.9:
                priority = 3  # High
            elif confidence > 0.7:
                priority = 2  # Medium
            else:
                priority = 1  # Low
        
        request = PrefetchRequest(
            query=query,
            context=context,
            confidence=confidence,
            trigger_reason=trigger_reason,
            created_at=current_time,
            priority=priority,
            estimated_cost=estimated_cost
        )
        
        # Add to queue (negative priority for correct ordering in PriorityQueue)
        queue_priority = (
            -priority,  # Higher priority first
            -confidence,  # Higher confidence first
            current_time  # Older requests first for ties
        )
        
        await self.prefetch_queue.put((queue_priority, request))
        logger.info(f"Scheduled prefetch: {query[:30]}... (confidence: {confidence:.2f})")
    
    def _estimate_query_cost(self, query: str, context: Dict[str, Any]) -> float:
        """Estimate the cost of executing a query."""
        # Simple cost estimation - in practice, this would be more sophisticated
        base_cost = 1.0
        
        # Adjust based on context
        if context.get('model') in ['gpt-4', 'claude-3-opus']:
            base_cost *= 5.0
        elif context.get('model') in ['gpt-3.5-turbo', 'claude-3-sonnet']:
            base_cost *= 2.0
        
        # Adjust based on query complexity (rough heuristic)
        if len(query) > 100:
            base_cost *= 1.5
        
        return base_cost
    
    async def _prefetch_worker(self):
        """Background worker that processes prefetch requests."""
        logger.info("Prefetch worker started")
        
        while self._running:
            try:
                # Get next prefetch request (with timeout)
                try:
                    queue_priority, request = await asyncio.wait_for(
                        self.prefetch_queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Check if we're not exceeding concurrent limit
                if len(self.active_prefetches) >= self.max_concurrent_prefetches:
                    # Put request back and wait
                    await self.prefetch_queue.put((queue_priority, request))
                    await asyncio.sleep(0.1)
                    continue
                
                # Check if request is still relevant (not too old)
                if time.time() - request.created_at > 300:  # 5 minutes
                    logger.debug(f"Skipping stale prefetch request: {request.query[:30]}...")
                    continue
                
                # Execute prefetch
                await self._execute_prefetch(request)
                
            except Exception as e:
                logger.error(f"Error in prefetch worker: {e}")
                await asyncio.sleep(1.0)
        
        logger.info("Prefetch worker stopped")
    
    async def _execute_prefetch(self, request: PrefetchRequest):
        """Execute a single prefetch request."""
        query_key = self.cache._get_cache_key(request.query, request.context)
        
        # Check if already cached
        existing = await self.cache.get(request.query, request.context)
        if existing:
            logger.debug(f"Query already cached: {request.query[:30]}...")
            return
        
        # Check if already being prefetched
        if query_key in self.active_prefetches:
            return
        
        self.active_prefetches.add(query_key)
        start_time = time.time()
        
        try:
            # In a real implementation, this would call the actual LLM service
            # For now, we'll simulate a response
            await self._simulate_query_execution(request)
            
            result = PrefetchResult(
                request=request,
                success=True,
                cache_key=query_key,
                execution_time=time.time() - start_time
            )
            
            # Update cost tracking
            self.current_hour_cost += request.estimated_cost
            
            logger.info(f"Prefetch successful: {request.query[:30]}... "
                       f"(took {result.execution_time:.2f}s)")
            
        except Exception as e:
            result = PrefetchResult(
                request=request,
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )
            
            logger.error(f"Prefetch failed: {request.query[:30]}... - {e}")
        
        finally:
            self.active_prefetches.discard(query_key)
            self.prefetch_history.append(result)
    
    async def _simulate_query_execution(self, request: PrefetchRequest):
        """Simulate executing a query (placeholder for real LLM integration)."""
        # Simulate processing time
        await asyncio.sleep(min(request.estimated_cost * 0.5, 2.0))
        
        # Generate a simulated response
        simulated_response = f"Prefetched response for: {request.query[:50]}..."
        
        # Cache the result
        enhanced_context = self.cache._enhance_context(request.context)
        await self.cache.set(
            prompt=request.query,
            response=simulated_response,
            context=enhanced_context,
            cost_estimate=request.estimated_cost
        )
    
    async def get_prefetch_stats(self) -> Dict[str, Any]:
        """Get prefetching statistics."""
        recent_results = list(self.prefetch_history)
        
        total_prefetches = len(recent_results)
        successful_prefetches = sum(1 for r in recent_results if r.success)
        
        # Calculate average metrics
        avg_execution_time = 0.0
        total_cost = 0.0
        
        if recent_results:
            avg_execution_time = sum(r.execution_time for r in recent_results) / len(recent_results)
            total_cost = sum(r.request.estimated_cost for r in recent_results)
        
        # Group by trigger reason
        trigger_stats = {}
        for result in recent_results:
            reason = result.request.trigger_reason
            if reason not in trigger_stats:
                trigger_stats[reason] = {'total': 0, 'successful': 0}
            trigger_stats[reason]['total'] += 1
            if result.success:
                trigger_stats[reason]['successful'] += 1
        
        return {
            'total_prefetches': total_prefetches,
            'successful_prefetches': successful_prefetches,
            'success_rate': successful_prefetches / total_prefetches if total_prefetches > 0 else 0,
            'avg_execution_time': avg_execution_time,
            'total_estimated_cost': total_cost,
            'current_hour_cost': self.current_hour_cost,
            'active_prefetches': len(self.active_prefetches),
            'queue_size': self.prefetch_queue.qsize(),
            'trigger_stats': trigger_stats,
            'running': self._running
        }
    
    async def force_prefetch(self, query: str, context: Dict[str, Any], priority: int = 3):
        """Force an immediate high-priority prefetch."""
        await self.schedule_prefetch(
            query=query,
            context=context,
            confidence=1.0,
            trigger_reason="manual_force",
            priority=priority
        )

class ContextualLearner:
    """Learns context patterns and creates smart triggers."""
    
    def __init__(self, behavioral_analyzer: BehavioralAnalyzer):
        self.behavioral = behavioral_analyzer
        self.learning_threshold = 0.8  # Confidence threshold for creating new triggers
    
    async def analyze_context_patterns(self):
        """Analyze patterns and create contextual triggers."""
        # This would analyze the behavioral data to find strong context->query correlations
        # and create contextual triggers automatically
        
        # Get behavioral analytics
        analytics = await self.behavioral.get_analytics()
        
        logger.info(f"Context learner analyzing {analytics['total_queries']} queries "
                   f"across {analytics['unique_sessions']} sessions")
        
        # In a full implementation, this would:
        # 1. Query the behavioral database for strong context->query correlations
        # 2. Create contextual triggers for patterns above threshold
        # 3. Remove outdated or ineffective triggers
        
        # For now, create some example contextual triggers
        await self._create_example_triggers()
    
    async def _create_example_triggers(self):
        """Create example contextual triggers for demonstration."""
        # Python development context
        python_context = {
            "language": "python",
            "time_of_day": "morning"
        }
        python_queries = [
            ("How to write Python functions?", 0.8),
            ("Python error handling best practices", 0.7),
            ("Python async/await tutorial", 0.6)
        ]
        
        await self.behavioral.create_contextual_trigger(
            trigger_context=python_context,
            predicted_queries=python_queries,
            priority=0.8
        )
        
        # JavaScript development context
        js_context = {
            "language": "javascript",
            "framework": "react"
        }
        js_queries = [
            ("React hooks best practices", 0.9),
            ("JavaScript async patterns", 0.7),
            ("React state management", 0.8)
        ]
        
        await self.behavioral.create_contextual_trigger(
            trigger_context=js_context,
            predicted_queries=js_queries,
            priority=0.9
        )
        
        logger.info("Created example contextual triggers")