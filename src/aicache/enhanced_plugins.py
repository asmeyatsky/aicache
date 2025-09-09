"""
Enhanced plugin system with advanced provider support and middleware.
"""

import os
import json
import time
import asyncio
import logging
import importlib
import subprocess
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, Tuple, Iterator
from pathlib import Path
from dataclasses import dataclass, asdict
import re
import shutil

logger = logging.getLogger(__name__)

@dataclass
class ProviderCapabilities:
    """Defines capabilities of an AI provider."""
    supports_streaming: bool = False
    supports_prompt_caching: bool = False
    supports_function_calling: bool = False
    supports_vision: bool = False
    supports_code_generation: bool = True
    max_context_length: int = 4096
    cost_per_1k_input: float = 0.001
    cost_per_1k_output: float = 0.002
    rate_limits: Dict[str, int] = None  # requests per time period
    
    def __post_init__(self):
        if self.rate_limits is None:
            self.rate_limits = {'requests_per_minute': 60}

@dataclass
class ProviderMetrics:
    """Tracks provider performance metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens_used: int = 0
    total_cost: float = 0.0
    avg_response_time: float = 0.0
    last_request_time: float = 0
    rate_limit_hits: int = 0
    
    @property
    def success_rate(self) -> float:
        return self.successful_requests / max(self.total_requests, 1)

class ProviderMiddleware(ABC):
    """Base class for provider middleware."""
    
    @abstractmethod
    async def before_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Called before sending request to provider."""
        pass
    
    @abstractmethod
    async def after_request(self, request_data: Dict[str, Any], 
                          response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Called after receiving response from provider."""
        pass
    
    @abstractmethod
    async def on_error(self, request_data: Dict[str, Any], 
                      error: Exception) -> Optional[Dict[str, Any]]:
        """Called when request fails. Can return alternative response."""
        pass

class RateLimitMiddleware(ProviderMiddleware):
    """Middleware for handling rate limits."""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.request_times = []
    
    async def before_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        current_time = time.time()
        
        # Clean old requests
        cutoff_time = current_time - 60  # 1 minute ago
        self.request_times = [t for t in self.request_times if t > cutoff_time]
        
        # Check rate limit
        if len(self.request_times) >= self.requests_per_minute:
            sleep_time = 60 - (current_time - self.request_times[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
        
        self.request_times.append(current_time)
        return request_data
    
    async def after_request(self, request_data: Dict[str, Any], 
                          response_data: Dict[str, Any]) -> Dict[str, Any]:
        return response_data
    
    async def on_error(self, request_data: Dict[str, Any], 
                      error: Exception) -> Optional[Dict[str, Any]]:
        return None

class CostTrackingMiddleware(ProviderMiddleware):
    """Middleware for tracking costs."""
    
    def __init__(self, cost_per_1k_input: float, cost_per_1k_output: float):
        self.cost_per_1k_input = cost_per_1k_input
        self.cost_per_1k_output = cost_per_1k_output
        self.total_cost = 0.0
    
    async def before_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        request_data['_cost_tracking_start'] = time.time()
        return request_data
    
    async def after_request(self, request_data: Dict[str, Any], 
                          response_data: Dict[str, Any]) -> Dict[str, Any]:
        # Estimate token usage and cost
        prompt = request_data.get('prompt', '')
        response = response_data.get('response', '')
        
        # Rough token estimation (4 chars per token)
        input_tokens = len(prompt) / 4
        output_tokens = len(response) / 4
        
        cost = (input_tokens / 1000 * self.cost_per_1k_input + 
                output_tokens / 1000 * self.cost_per_1k_output)
        
        self.total_cost += cost
        
        # Add cost info to response
        response_data['_cost_info'] = {
            'estimated_input_tokens': int(input_tokens),
            'estimated_output_tokens': int(output_tokens),
            'estimated_cost': cost,
            'total_session_cost': self.total_cost
        }
        
        return response_data
    
    async def on_error(self, request_data: Dict[str, Any], 
                      error: Exception) -> Optional[Dict[str, Any]]:
        return None

class RetryMiddleware(ProviderMiddleware):
    """Middleware for handling retries."""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 1.5):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    async def before_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        request_data['_retry_count'] = request_data.get('_retry_count', 0)
        return request_data
    
    async def after_request(self, request_data: Dict[str, Any], 
                          response_data: Dict[str, Any]) -> Dict[str, Any]:
        return response_data
    
    async def on_error(self, request_data: Dict[str, Any], 
                      error: Exception) -> Optional[Dict[str, Any]]:
        retry_count = request_data.get('_retry_count', 0)
        
        if retry_count < self.max_retries:
            sleep_time = (self.backoff_factor ** retry_count)
            logger.info(f"Retrying request (attempt {retry_count + 1}/{self.max_retries}) "
                       f"after {sleep_time:.2f}s delay")
            await asyncio.sleep(sleep_time)
            request_data['_retry_count'] = retry_count + 1
            return {'retry': True, 'request_data': request_data}
        
        return None

class EnhancedCLIWrapper(ABC):
    """Enhanced base class for CLI wrappers with middleware support."""
    
    def __init__(self):
        self.capabilities = self.get_capabilities()
        self.metrics = ProviderMetrics()
        self.middleware_stack: List[ProviderMiddleware] = []
        self._setup_default_middleware()
    
    def _setup_default_middleware(self):
        """Setup default middleware stack."""
        # Add rate limiting if supported
        if 'requests_per_minute' in self.capabilities.rate_limits:
            self.add_middleware(RateLimitMiddleware(
                self.capabilities.rate_limits['requests_per_minute']
            ))
        
        # Add cost tracking
        self.add_middleware(CostTrackingMiddleware(
            self.capabilities.cost_per_1k_input,
            self.capabilities.cost_per_1k_output
        ))
        
        # Add retry logic
        self.add_middleware(RetryMiddleware())
    
    def add_middleware(self, middleware: ProviderMiddleware):
        """Add middleware to the stack."""
        self.middleware_stack.append(middleware)
    
    async def execute_with_middleware(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute request through middleware stack."""
        # Apply before_request middleware
        for middleware in self.middleware_stack:
            request_data = await middleware.before_request(request_data)
        
        try:
            # Execute the actual request
            response_data = await self._execute_request(request_data)
            
            # Apply after_request middleware
            for middleware in reversed(self.middleware_stack):
                response_data = await middleware.after_request(request_data, response_data)
            
            # Update metrics
            self.metrics.successful_requests += 1
            
            return response_data
            
        except Exception as e:
            self.metrics.failed_requests += 1
            
            # Apply error middleware
            for middleware in reversed(self.middleware_stack):
                alternative_response = await middleware.on_error(request_data, e)
                if alternative_response:
                    if alternative_response.get('retry'):
                        # Retry the request
                        return await self.execute_with_middleware(
                            alternative_response['request_data']
                        )
                    else:
                        return alternative_response
            
            # Re-raise if no middleware handled the error
            raise
        finally:
            self.metrics.total_requests += 1
            self.metrics.last_request_time = time.time()
    
    @abstractmethod
    async def _execute_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the actual request (to be implemented by subclasses)."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> ProviderCapabilities:
        """Get provider capabilities (to be implemented by subclasses)."""
        pass
    
    @abstractmethod
    def get_cli_name(self) -> str:
        """Get CLI name (to be implemented by subclasses)."""
        pass
    
    def get_metrics(self) -> ProviderMetrics:
        """Get provider metrics."""
        return self.metrics

class OpenAIEnhancedWrapper(EnhancedCLIWrapper):
    """Enhanced OpenAI CLI wrapper."""
    
    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_streaming=True,
            supports_prompt_caching=True,
            supports_function_calling=True,
            supports_vision=True,
            max_context_length=128000,
            cost_per_1k_input=0.0015,
            cost_per_1k_output=0.002,
            rate_limits={'requests_per_minute': 3500}
        )
    
    def get_cli_name(self) -> str:
        return "openai"
    
    async def _execute_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute OpenAI request."""
        args = request_data.get('args', [])
        
        # Check for streaming support
        if '--stream' in args and self.capabilities.supports_streaming:
            return await self._execute_streaming_request(args)
        else:
            return await self._execute_standard_request(args)
    
    async def _execute_standard_request(self, args: List[str]) -> Dict[str, Any]:
        """Execute standard (non-streaming) request."""
        try:
            process = await asyncio.create_subprocess_exec(
                'openai', *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                'response': stdout.decode('utf-8'),
                'error': stderr.decode('utf-8') if stderr else None,
                'return_code': process.returncode,
                'streaming': False
            }
        except FileNotFoundError:
            raise Exception("OpenAI CLI not found. Please install with: pip install openai")
    
    async def _execute_streaming_request(self, args: List[str]) -> Dict[str, Any]:
        """Execute streaming request."""
        try:
            process = await asyncio.create_subprocess_exec(
                'openai', *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            response_parts = []
            async for line in process.stdout:
                chunk = line.decode('utf-8')
                response_parts.append(chunk)
            
            await process.wait()
            
            return {
                'response': ''.join(response_parts),
                'response_parts': response_parts,
                'error': None,
                'return_code': process.returncode,
                'streaming': True
            }
        except FileNotFoundError:
            raise Exception("OpenAI CLI not found. Please install with: pip install openai")

class ClaudeEnhancedWrapper(EnhancedCLIWrapper):
    """Enhanced Claude CLI wrapper."""
    
    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_streaming=True,
            supports_prompt_caching=True,
            supports_function_calling=False,
            supports_vision=True,
            max_context_length=200000,
            cost_per_1k_input=0.015,
            cost_per_1k_output=0.075,
            rate_limits={'requests_per_minute': 1000}
        )
    
    def get_cli_name(self) -> str:
        return "claude"
    
    async def _execute_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Claude request."""
        args = request_data.get('args', [])
        
        try:
            process = await asyncio.create_subprocess_exec(
                'claude', *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                'response': stdout.decode('utf-8'),
                'error': stderr.decode('utf-8') if stderr else None,
                'return_code': process.returncode,
                'streaming': False  # Would need to detect streaming mode
            }
        except FileNotFoundError:
            raise Exception("Claude CLI not found")

class PluginManager:
    """Manages enhanced plugins and providers."""
    
    def __init__(self):
        self.registered_providers: Dict[str, EnhancedCLIWrapper] = {}
        self.middleware_registry: Dict[str, type] = {
            'rate_limit': RateLimitMiddleware,
            'cost_tracking': CostTrackingMiddleware,
            'retry': RetryMiddleware
        }
        self._register_builtin_providers()
    
    def _register_builtin_providers(self):
        """Register built-in providers."""
        self.register_provider(OpenAIEnhancedWrapper())
        self.register_provider(ClaudeEnhancedWrapper())
    
    def register_provider(self, provider: EnhancedCLIWrapper):
        """Register a provider."""
        self.registered_providers[provider.get_cli_name()] = provider
        logger.info(f"Registered provider: {provider.get_cli_name()}")
    
    def get_provider(self, name: str) -> Optional[EnhancedCLIWrapper]:
        """Get a registered provider."""
        return self.registered_providers.get(name)
    
    def list_providers(self) -> Dict[str, Dict[str, Any]]:
        """List all registered providers with their capabilities."""
        providers = {}
        for name, provider in self.registered_providers.items():
            providers[name] = {
                'capabilities': asdict(provider.get_capabilities()),
                'metrics': asdict(provider.get_metrics()),
                'middleware_count': len(provider.middleware_stack)
            }
        return providers
    
    def create_custom_provider(self, config: Dict[str, Any]) -> bool:
        """Create a custom provider from configuration."""
        try:
            name = config['name']
            executable = config['executable']
            capabilities_config = config.get('capabilities', {})
            
            # Create capabilities
            capabilities = ProviderCapabilities(**capabilities_config)
            
            # Create custom wrapper class
            class CustomWrapper(EnhancedCLIWrapper):
                def get_capabilities(self) -> ProviderCapabilities:
                    return capabilities
                
                def get_cli_name(self) -> str:
                    return name
                
                async def _execute_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
                    args = request_data.get('args', [])
                    
                    try:
                        process = await asyncio.create_subprocess_exec(
                            executable, *args,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )
                        
                        stdout, stderr = await process.communicate()
                        
                        return {
                            'response': stdout.decode('utf-8'),
                            'error': stderr.decode('utf-8') if stderr else None,
                            'return_code': process.returncode,
                            'streaming': False
                        }
                    except FileNotFoundError:
                        raise Exception(f"{executable} not found")
            
            # Register the custom provider
            custom_provider = CustomWrapper()
            self.register_provider(custom_provider)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create custom provider: {e}")
            return False
    
    def get_provider_recommendations(self, task_type: str = "general") -> List[Dict[str, Any]]:
        """Get provider recommendations based on task type."""
        recommendations = []
        
        for name, provider in self.registered_providers.items():
            capabilities = provider.get_capabilities()
            metrics = provider.get_metrics()
            
            score = 0
            reasoning = []
            
            # Score based on task type
            if task_type == "code" and capabilities.supports_code_generation:
                score += 20
                reasoning.append("Supports code generation")
            
            if task_type == "streaming" and capabilities.supports_streaming:
                score += 20
                reasoning.append("Supports streaming")
            
            if task_type == "vision" and capabilities.supports_vision:
                score += 20
                reasoning.append("Supports vision")
            
            # Score based on performance
            success_rate = metrics.success_rate
            score += success_rate * 30
            reasoning.append(f"Success rate: {success_rate:.1%}")
            
            # Score based on cost-effectiveness
            cost_score = max(0, 20 - capabilities.cost_per_1k_output * 10)
            score += cost_score
            reasoning.append(f"Cost per 1K output tokens: ${capabilities.cost_per_1k_output:.3f}")
            
            # Score based on context length
            context_score = min(20, capabilities.max_context_length / 10000)
            score += context_score
            reasoning.append(f"Max context: {capabilities.max_context_length:,} tokens")
            
            recommendations.append({
                'provider': name,
                'score': score,
                'reasoning': reasoning,
                'capabilities': asdict(capabilities),
                'metrics': asdict(metrics)
            })
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations

class ProviderLoadBalancer:
    """Load balancer for distributing requests across providers."""
    
    def __init__(self, plugin_manager: PluginManager):
        self.plugin_manager = plugin_manager
        self.provider_weights: Dict[str, float] = {}
    
    def set_provider_weights(self, weights: Dict[str, float]):
        """Set weights for load balancing."""
        total_weight = sum(weights.values())
        self.provider_weights = {k: v / total_weight for k, v in weights.items()}
    
    async def execute_with_fallback(self, provider_names: List[str], 
                                  request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute request with automatic fallback."""
        last_error = None
        
        for provider_name in provider_names:
            provider = self.plugin_manager.get_provider(provider_name)
            if not provider:
                continue
            
            try:
                logger.info(f"Trying provider: {provider_name}")
                result = await provider.execute_with_middleware(request_data)
                result['_provider_used'] = provider_name
                return result
                
            except Exception as e:
                logger.warning(f"Provider {provider_name} failed: {e}")
                last_error = e
                continue
        
        # All providers failed
        raise Exception(f"All providers failed. Last error: {last_error}")
    
    def get_optimal_provider(self, task_type: str = "general") -> Optional[str]:
        """Get the optimal provider for a task."""
        recommendations = self.plugin_manager.get_provider_recommendations(task_type)
        
        if not recommendations:
            return None
        
        # Apply weights if configured
        if self.provider_weights:
            for rec in recommendations:
                provider_name = rec['provider']
                if provider_name in self.provider_weights:
                    rec['score'] *= self.provider_weights[provider_name]
            
            # Re-sort after applying weights
            recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[0]['provider']

# Factory function
def create_enhanced_plugin_system() -> Tuple[PluginManager, ProviderLoadBalancer]:
    """Create enhanced plugin system with load balancer."""
    plugin_manager = PluginManager()
    load_balancer = ProviderLoadBalancer(plugin_manager)
    return plugin_manager, load_balancer