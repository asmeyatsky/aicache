"""
Proactive code generation system.
Generates code snippets and function skeletons in the background, ready to be inserted.
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from .llm_service import LLMService
from .behavioral import BehavioralAnalyzer

logger = logging.getLogger(__name__)

@dataclass
class ProactiveCodeGeneration:
    """Represents a proactive code generation task."""
    task_id: str
    query: str
    context: Dict[str, Any]
    generated_code: Optional[str] = None
    confidence: float = 0.0
    created_at: float = 0.0
    completed_at: Optional[float] = None
    success: bool = False
    error: Optional[str] = None

class ProactiveCodeGenerator:
    """Generates code proactively based on developer behavior and context."""
    
    def __init__(self, llm_service: LLMService, behavioral_analyzer: BehavioralAnalyzer):
        self.llm_service = llm_service
        self.behavioral_analyzer = behavioral_analyzer
        self.generation_queue = asyncio.Queue()
        self.generated_code_cache: Dict[str, ProactiveCodeGeneration] = {}
        self._running = False
        self._worker_task = None
        
    async def start(self):
        """Start the proactive code generation worker."""
        if self._running:
            return
            
        self._running = True
        self._worker_task = asyncio.create_task(self._generation_worker())
        logger.info("Proactive code generator started")
        
    async def stop(self):
        """Stop the proactive code generation worker."""
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("Proactive code generator stopped")
        
    async def _generation_worker(self):
        """Background worker that processes code generation requests."""
        logger.info("Proactive code generation worker started")
        
        while self._running:
            try:
                # Get next generation request (with timeout)
                try:
                    task = await asyncio.wait_for(self.generation_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                    
                # Process the generation task
                await self._process_generation_task(task)
                
            except Exception as e:
                logger.error(f"Error in proactive code generation worker: {e}")
                await asyncio.sleep(1.0)
                
        logger.info("Proactive code generation worker stopped")
        
    async def _process_generation_task(self, task: ProactiveCodeGeneration):
        """Process a single code generation task."""
        try:
            logger.info(f"Generating code for: {task.query[:50]}...")
            
            # Generate code using LLM service if available
            if self.llm_service and self.llm_service.enabled:
                generated_code = await self.llm_service.generate_code(task.query, task.context)
            else:
                # Fallback to template-based generation
                generated_code = self._generate_template_code(task.query, task.context)
            
            if generated_code:
                task.generated_code = generated_code
                task.confidence = 0.8 if (self.llm_service and self.llm_service.enabled) else 0.5
                task.completed_at = time.time()
                task.success = True
                logger.info(f"Successfully generated code for: {task.query[:50]}...")
            else:
                task.error = "Failed to generate code"
                task.completed_at = time.time()
                task.success = False
                logger.warning(f"Failed to generate code for: {task.query[:50]}...")
                
        except Exception as e:
            task.error = str(e)
            task.completed_at = time.time()
            task.success = False
            logger.error(f"Error generating code for '{task.query[:50]}...': {e}")
            
        finally:
            # Store the result
            self.generated_code_cache[task.task_id] = task
            
    async def schedule_generation(self, query: str, context: Dict[str, Any], 
                                confidence: float = 0.5) -> str:
        """Schedule a code generation task."""
        import uuid
        task_id = str(uuid.uuid4())
        
        task = ProactiveCodeGeneration(
            task_id=task_id,
            query=query,
            context=context,
            confidence=confidence,
            created_at=time.time()
        )
        
        await self.generation_queue.put(task)
        logger.info(f"Scheduled code generation: {query[:50]}... (confidence: {confidence:.2f})")
        
        return task_id
        
    async def get_generated_code(self, task_id: str) -> Optional[ProactiveCodeGeneration]:
        """Get generated code for a task."""
        return self.generated_code_cache.get(task_id)
        
    async def analyze_and_generate(self, user_id: str, session_id: str, 
                                 query: str, context: Dict[str, Any], cache_hit: bool):
        """Analyze current query and proactively generate relevant code."""
        # Check if we should generate code based on confidence and context
        should_generate = await self._should_generate_code(query, context, cache_hit)
        
        if should_generate:
            # Schedule code generation
            await self.schedule_generation(query, context, confidence=0.7)
            
            # Also generate for related queries if available
            related_queries = await self._get_related_queries(query, context)
            for related_query in related_queries:
                await self.schedule_generation(related_query, context, confidence=0.5)
                
    def _generate_template_code(self, query: str, context: Dict[str, Any]) -> Optional[str]:
        """Generate template-based code when LLM is not available."""
        query_lower = query.lower()
        language = context.get('language', 'python')
        
        # Simple template-based code generation
        if 'factorial' in query_lower:
            if language == 'python':
                return '''def factorial(n):
    """Calculate factorial of n."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Example usage
result = factorial(5)
print(f"Factorial of 5 is {result}")'''
            elif language == 'javascript':
                return '''function factorial(n) {
    // Calculate factorial of n
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

// Example usage
const result = factorial(5);
console.log(`Factorial of 5 is ${result}`);'''
                
        elif 'sort' in query_lower and 'list' in query_lower:
            if language == 'python':
                return '''def sort_list(arr):
    """Sort a list in ascending order."""
    return sorted(arr)

# Example usage
numbers = [3, 1, 4, 1, 5, 9, 2, 6]
sorted_numbers = sort_list(numbers)
print(f"Sorted list: {sorted_numbers}")'''
            elif language == 'javascript':
                return '''function sortList(arr) {
    // Sort an array in ascending order
    return [...arr].sort((a, b) => a - b);
}

// Example usage
const numbers = [3, 1, 4, 1, 5, 9, 2, 6];
const sortedNumbers = sortList(numbers);
console.log(`Sorted array: ${sortedNumbers}`);'''
                
        elif 'function' in query_lower:
            if language == 'python':
                return '''def example_function(param1, param2=None):
    """
    Example function with parameters.
    
    Args:
        param1: Required parameter
        param2: Optional parameter
    
    Returns:
        Description of return value
    """
    # Implementation here
    result = f"Processing {param1}"
    if param2:
        result += f" with {param2}"
    return result

# Example usage
output = example_function("test", "option")
print(output)'''
            elif language == 'javascript':
                return '''function exampleFunction(param1, param2 = null) {
    /**
     * Example function with parameters.
     * 
     * @param {any} param1 - Required parameter
     * @param {any} [param2=null] - Optional parameter
     * @returns {string} Description of return value
     */
    // Implementation here
    let result = `Processing ${param1}`;
    if (param2) {
        result += ` with ${param2}`;
    }
    return result;
}

// Example usage
const output = exampleFunction("test", "option");
console.log(output);'''
        
        # Default template
        return f"# Template code for: {query}\n# This is a placeholder. In a real implementation with LLM, this would be actual code.\n\nprint('Hello from aicache!')"

    async def _should_generate_code(self, query: str, context: Dict[str, Any], 
                                  cache_hit: bool) -> bool:
        """Determine if we should generate code for this query."""
        # Don't generate if it was a cache hit (code already exists)
        if cache_hit:
            return False
            
        # Check if query is code-related
        code_indicators = ['function', 'class', 'method', 'code', 'implement', 'create', 
                          'write', 'generate', 'build', 'develop', 'program', 'factorial', 'sort']
                          
        query_lower = query.lower()
        if any(indicator in query_lower for indicator in code_indicators):
            return True
            
        # Check context for code-related indicators
        context_indicators = context.get('language', '') or context.get('framework', '')
        if context_indicators:
            return True
            
        return False
        
    async def _get_related_queries(self, query: str, context: Dict[str, Any]) -> List[str]:
        """Get related queries that might benefit from code generation."""
        # Simple heuristic: if asking about a specific function, generate related functions
        if 'function' in query.lower() or 'method' in query.lower():
            base_query = query.replace('function', '').replace('method', '').strip()
            return [
                f"How to test {base_query}",
                f"Example usage of {base_query}",
                f"Best practices for {base_query}"
            ]
            
        return []
        
    async def get_generation_stats(self) -> Dict[str, Any]:
        """Get statistics about code generation."""
        total_tasks = len(self.generated_code_cache)
        successful_tasks = sum(1 for task in self.generated_code_cache.values() if task.success)
        failed_tasks = total_tasks - successful_tasks
        
        # Calculate average generation time
        completed_tasks = [task for task in self.generated_code_cache.values() 
                          if task.completed_at is not None]
        avg_generation_time = 0.0
        if completed_tasks:
            total_time = sum(task.completed_at - task.created_at for task in completed_tasks)
            avg_generation_time = total_time / len(completed_tasks)
            
        return {
            'total_tasks': total_tasks,
            'successful_tasks': successful_tasks,
            'failed_tasks': failed_tasks,
            'success_rate': successful_tasks / total_tasks if total_tasks > 0 else 0,
            'avg_generation_time': avg_generation_time,
            'queue_size': self.generation_queue.qsize(),
            'running': self._running
        }