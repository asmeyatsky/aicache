
import asyncio
import logging
import json
from typing import Dict, Any, Optional

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

logger = logging.getLogger(__name__)

class LLMService:
    """
    Service for interacting with Large Language Models (LLMs) for tasks like
    code generation and query understanding.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ollama_model = self.config.get("ollama_model", "llama2")
        self.ollama_host = self.config.get("ollama_host", "http://localhost:11434")
        
        if not OLLAMA_AVAILABLE:
            logger.warning("Ollama library not found. LLMService will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
            # Basic check if Ollama server is reachable
            try:
                # This is a synchronous call, ideally ollama client would have async ping
                ollama.list(host=self.ollama_host) 
                logger.info(f"LLMService initialized with Ollama model '{self.ollama_model}' at {self.ollama_host}")
            except Exception as e:
                logger.error(f"Could not connect to Ollama server at {self.ollama_host}: {e}")
                self.enabled = False

    async def generate_code(self, prompt: str, context: Dict[str, Any]) -> Optional[str]:
        """
        Generates code based on the given prompt and context using Ollama.
        """
        if not self.enabled:
            logger.warning("LLMService is disabled, cannot generate code.")
            return None
        
        full_prompt = f"Generate code based on the following request and context:\n\nRequest: {prompt}\nContext: {json.dumps(context, indent=2)}\n\nCode:"
        
        try:
            # Ollama client might not be fully async, using to_thread for non-blocking
            response = await asyncio.to_thread(
                ollama.generate,
                model=self.ollama_model,
                prompt=full_prompt,
                host=self.ollama_host
            )
            return response.get("response")
        except Exception as e:
            logger.error(f"Error generating code with Ollama: {e}")
            return None

    async def understand_query(self, query: str) -> Optional[str]:
        """
        Uses Ollama to understand and potentially rewrite a natural language query
        into a more precise form for caching.
        """
        if not self.enabled:
            logger.warning("LLMService is disabled, cannot understand query.")
            return query # Return original query if service is disabled
        
        prompt = f"Rewrite the following natural language query into a concise, precise, and keyword-rich query suitable for a code cache search. Focus on key terms, programming concepts, and relevant technologies. Only return the rewritten query, no other text.\n\nOriginal Query: {query}\nRewritten Query:"
        
        try:
            response = await asyncio.to_thread(
                ollama.generate,
                model=self.ollama_model,
                prompt=prompt,
                host=self.ollama_host,
                options={"num_predict": 128} # Limit response length for query rewriting
            )
            rewritten_query = response.get("response", "").strip()
            # Basic post-processing to clean up potential LLM chatter
            if rewritten_query.lower().startswith("rewritten query:"):
                rewritten_query = rewritten_query[len("rewritten query:"):].strip()
            return rewritten_query
        except Exception as e:
            logger.error(f"Error understanding query with Ollama: {e}")
            return query # Fallback to original query on error

