import asyncio
import logging
from typing import Dict, Any, Optional

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

logger = logging.getLogger(__name__)

class CodeGenerator:
    """
    Generates code snippets and function skeletons using Ollama.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ollama_model = self.config.get("ollama_code_model", "codellama")
        self.ollama_host = self.config.get("ollama_host", "http://localhost:11434")
        self.enabled = OLLAMA_AVAILABLE

        if not self.enabled:
            logger.warning("Ollama library not found. CodeGenerator will be disabled.")
            return
        
        try:
            # Verify Ollama server and model availability
            # This is a synchronous call, ideally ollama client would have async ping
            models = ollama.list(host=self.ollama_host)
            if not any(m['name'].startswith(self.ollama_model) for m in models['models']):
                logger.warning(f"Ollama model '{self.ollama_model}' not found. CodeGenerator disabled.")
                self.enabled = False
            else:
                logger.info(f"CodeGenerator initialized with Ollama model '{self.ollama_model}' at {self.ollama_host}")
        except Exception as e:
            logger.error(f"Could not connect to Ollama server at {self.ollama_host} or list models: {e}")
            self.enabled = False

    async def generate_code(self, prompt: str, context: Dict[str, Any]) -> Optional[str]:
        """
        Generates code based on the given prompt and context using Ollama.
        """
        if not self.enabled:
            logger.warning("CodeGenerator is disabled, cannot generate code.")
            return None
        
        full_prompt = f"Generate code based on the following request and context:\n\nRequest: {prompt}\nContext: {json.dumps(context, indent=2)}\n\nCode:"
        
        try:
            response = await asyncio.to_thread(
                ollama.generate,
                model=self.ollama_model,
                prompt=full_prompt,
                host=self.ollama_host,
                options={"temperature": self.config.get("temperature", 0.7), "num_predict": self.config.get("max_tokens", 512)}
            )
            return response.get("response")
        except Exception as e:
            logger.error(f"Error generating code with Ollama: {e}")
            return None

class QueryUnderstanding:
    """
    Uses Ollama to understand and potentially rewrite natural language queries.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ollama_model = self.config.get("ollama_nlu_model", "llama2") # General purpose LLM for NLU
        self.ollama_host = self.config.get("ollama_host", "http://localhost:11434")
        self.enabled = OLLAMA_AVAILABLE

        if not self.enabled:
            logger.warning("Ollama library not found. QueryUnderstanding will be disabled.")
            return
        
        try:
            models = ollama.list(host=self.ollama_host)
            if not any(m['name'].startswith(self.ollama_model) for m in models['models']):
                logger.warning(f"Ollama model '{self.ollama_model}' not found. QueryUnderstanding disabled.")
                self.enabled = False
            else:
                logger.info(f"QueryUnderstanding initialized with Ollama model '{self.ollama_model}' at {self.ollama_host}")
        except Exception as e:
            logger.error(f"Could not connect to Ollama server at {self.ollama_host} or list models: {e}")
            self.enabled = False

    async def understand_query(self, query: str) -> str:
        """
        Uses Ollama to understand and potentially rewrite a natural language query
        into a more precise form for caching.
        """
        if not self.enabled:
            logger.warning("QueryUnderstanding is disabled, returning original query.")
            return query # Return original query if service is disabled
        
        prompt = f"Rewrite the following natural language query into a concise, precise, and keyword-rich query suitable for a code cache search. Focus on key terms, programming concepts, and relevant technologies. Only return the rewritten query, no other text.\n\nOriginal Query: {query}\nRewritten Query:"
        
        try:
            response = await asyncio.to_thread(
                ollama.generate,
                model=self.ollama_model,
                prompt=prompt,
                host=self.ollama_host,
                options={"num_predict": 128, "temperature": self.config.get("temperature", 0.3)} # Limit response length for query rewriting
            )
            rewritten_query = response.get("response", "").strip()
            # Basic post-processing to clean up potential LLM chatter
            if rewritten_query.lower().startswith("rewritten query:"):
                rewritten_query = rewritten_query[len("rewritten query:"):].strip()
            return rewritten_query
        except Exception as e:
            logger.error(f"Error understanding query with Ollama: {e}")
            return query # Fallback to original query on error
