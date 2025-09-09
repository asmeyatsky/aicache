"""
Semantic caching engine with vector embeddings and similarity search.
"""

import os
import asyncio
import numpy as np
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import time

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except (ImportError, Exception):
    CHROMADB_AVAILABLE = False

SENTENCE_TRANSFORMERS_AVAILABLE = False
try:
    # Test import without actually importing
    import importlib.util
    spec = importlib.util.find_spec("sentence_transformers")
    if spec is not None:
        SENTENCE_TRANSFORMERS_AVAILABLE = True
except:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except (ImportError, Exception):
    FAISS_AVAILABLE = False

try:
    from rank_bm25 import BM25Okapi
    RANK_BM25_AVAILABLE = True
except (ImportError, Exception):
    RANK_BM25_AVAILABLE = False

try:
    import nltk
    from nltk.corpus import wordnet
    NLTK_AVAILABLE = True
except (ImportError, Exception):
    NLTK_AVAILABLE = False

from .config import get_config

logger = logging.getLogger(__name__)

if NLTK_AVAILABLE:
    try:
        wordnet.synsets('computer')
    except:
        nltk.download('wordnet')

def get_synonyms(word):
    """
    Gets synonyms for a word using NLTK's WordNet.
    """
    if not NLTK_AVAILABLE:
        return []
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return list(synonyms)

@dataclass
class SemanticCacheEntry:
    """Enhanced cache entry with semantic information."""
    cache_key: str
    prompt: str
    response: str
    context: Dict[str, Any]
    embedding: Optional[np.ndarray]
    timestamp: float
    access_count: int = 0
    last_accessed: float = 0
    semantic_tags: List[str] = None
    similarity_threshold: float = 0.85
    
    def __post_init__(self):
        if self.semantic_tags is None:
            self.semantic_tags = []
        if self.last_accessed == 0:
            self.last_accessed = self.timestamp

class EmbeddingModel:
    """Manages embedding models for semantic similarity."""
    
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.model_name = model_name
        self._model = None
        self._load_model()
    
    def _load_model(self):
        """Lazy load the sentence transformer model."""
        global SENTENCE_TRANSFORMERS_AVAILABLE
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.warning("sentence-transformers not available, semantic caching disabled")
            return
        
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model {self.model_name}: {e}")
            SENTENCE_TRANSFORMERS_AVAILABLE = False
    
    async def encode(self, texts: List[str]) -> Optional[np.ndarray]:
        """Encode texts to embeddings."""
        if self._model is None:
            return None
        
        try:
            return await asyncio.to_thread(self._model.encode, texts)
        except Exception as e:
            logger.error(f"Failed to encode texts: {e}")
            return None
    
    async def encode_single(self, text: str) -> Optional[np.ndarray]:
        """Encode a single text to embedding."""
        result = await self.encode([text])
        return result[0] if result is not None else None

class VectorStore:
    """Abstract base class for vector storage backends."""
    
    async def add(self, id: str, embedding: np.ndarray, metadata: Dict[str, Any]):
        raise NotImplementedError
    
    async def search(self, query_embedding: np.ndarray, k: int = 5, 
               threshold: float = 0.85) -> List[Tuple[str, float]]:
        raise NotImplementedError
    
    async def delete(self, id: str):
        raise NotImplementedError
    
    async def update(self, id: str, embedding: np.ndarray, metadata: Dict[str, Any]):
        raise NotImplementedError

    async def get_all_prompts(self) -> List[str]:
        raise NotImplementedError

class ChromaDBStore(VectorStore):
    """ChromaDB-based vector storage."""
    
    def __init__(self, collection_name: str = "aicache_embeddings", 
                 persist_directory: str = None):
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB not available. Install with: pip install chromadb")
        
        self.collection_name = collection_name
        self.persist_directory = persist_directory or os.path.expanduser("~/.cache/aicache/chroma")
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        
        logger.info(f"ChromaDB collection '{collection_name}' initialized")
    
    async def add(self, id: str, embedding: np.ndarray, metadata: Dict[str, Any]):
        """Add embedding to ChromaDB."""
        try:
            await asyncio.to_thread(self.collection.add, ids=[id], embeddings=[embedding.tolist()], metadatas=[metadata])
        except Exception as e:
            logger.error(f"Failed to add embedding to ChromaDB: {e}")
    
    async def search(self, query_embedding: np.ndarray, k: int = 5, 
               threshold: float = 0.85) -> List[Tuple[str, float]]:
        """Search for similar embeddings."""
        try:
            results = await asyncio.to_thread(self.collection.query, query_embeddings=[query_embedding.tolist()], n_results=k, include=['distances', 'metadatas'])
            
            # ChromaDB returns distances, we need to convert to similarity
            # For cosine distance: similarity = 1 - distance
            matches = []
            for i, distance in enumerate(results['distances'][0]):
                similarity = 1.0 - distance
                if similarity >= threshold:
                    matches.append((results['ids'][0][i], similarity))
            
            return matches
        except Exception as e:
            logger.error(f"Failed to search ChromaDB: {e}")
            return []
    
    async def delete(self, id: str):
        """Delete embedding from ChromaDB."""
        try:
            await asyncio.to_thread(self.collection.delete, ids=[id])
        except Exception as e:
            logger.error(f"Failed to delete from ChromaDB: {e}")
    
    async def update(self, id: str, embedding: np.ndarray, metadata: Dict[str, Any]):
        """Update embedding in ChromaDB."""
        try:
            await asyncio.to_thread(self.collection.update, ids=[id], embeddings=[embedding.tolist()], metadatas=[metadata])
        except Exception as e:
            logger.error(f"Failed to update ChromaDB: {e}")

    async def get_all_prompts(self) -> List[str]:
        """Gets all prompts from the collection."""
        try:
            results = await asyncio.to_thread(self.collection.get, include=["metadatas"])
            return [metadata["prompt"] for metadata in results["metadatas"]]
        except Exception as e:
            logger.error(f"Failed to get all prompts from ChromaDB: {e}")
            return []

class FAISSStore(VectorStore):
    """FAISS-based vector storage for high performance."""
    
    def __init__(self, dimension: int = 384, persist_directory: str = None):
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS not available. Install with: pip install faiss-cpu")
        
        self.dimension = dimension
        self.persist_directory = persist_directory or os.path.expanduser("~/.cache/aicache/faiss")
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        self.index_file = Path(self.persist_directory) / "index.faiss"
        self.metadata_file = Path(self.persist_directory) / "metadata.json"
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        self.id_to_idx = {}
        self.idx_to_id = {}
        self.metadata = {}
        
        # Load existing index if available
        self._load_index()
        
        logger.info(f"FAISS index initialized with dimension {dimension}")
    
    def _load_index(self):
        """Load existing FAISS index and metadata."""
        if self.index_file.exists():
            try:
                self.index = faiss.read_index(str(self.index_file))
                
                if self.metadata_file.exists():
                    with open(self.metadata_file, 'r') as f:
                        data = json.load(f)
                        self.id_to_idx = data.get('id_to_idx', {})
                        self.idx_to_id = data.get('idx_to_id', {})
                        self.metadata = data.get('metadata', {})
                
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            except Exception as e:
                logger.error(f"Failed to load FAISS index: {e}")
    
    def _save_index(self):
        """Save FAISS index and metadata."""
        try:
            faiss.write_index(self.index, str(self.index_file))
            
            with open(self.metadata_file, 'w') as f:
                json.dump({
                    'id_to_idx': self.id_to_idx,
                    'idx_to_id': self.idx_to_id,
                    'metadata': self.metadata
                }, f)
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")
    
    async def add(self, id: str, embedding: np.ndarray, metadata: Dict[str, Any]):
        """Add embedding to FAISS index."""
        try:
            # Normalize embedding for cosine similarity
            embedding = embedding / np.linalg.norm(embedding)
            embedding = embedding.reshape(1, -1).astype(np.float32)
            
            idx = self.index.ntotal
            await asyncio.to_thread(self.index.add, embedding)
            
            self.id_to_idx[id] = idx
            self.idx_to_id[str(idx)] = id
            self.metadata[id] = metadata
            
            await asyncio.to_thread(self._save_index)
        except Exception as e:
            logger.error(f"Failed to add embedding to FAISS: {e}")
    
    async def search(self, query_embedding: np.ndarray, k: int = 5, 
               threshold: float = 0.85) -> List[Tuple[str, float]]:
        """Search for similar embeddings."""
        try:
            # Normalize query embedding
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
            
            scores, indices = await asyncio.to_thread(self.index.search, query_embedding, k)
            
            matches = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx >= 0 and score >= threshold:  # Valid index and above threshold
                    id = self.idx_to_id.get(str(idx))
                    if id:
                        matches.append((id, float(score)))
            
            return matches
        except Exception as e:
            logger.error(f"Failed to search FAISS: {e}")
            return []
    
    async def delete(self, id: str):
        """Delete embedding from FAISS (marks as deleted)."""
        # FAISS doesn't support efficient deletion, so we mark as deleted
        if id in self.metadata:
            self.metadata[id]['deleted'] = True
            await asyncio.to_thread(self._save_index)
    
    async def update(self, id: str, embedding: np.ndarray, metadata: Dict[str, Any]):
        """Update embedding (delete and re-add)."""
        await self.delete(id)
        await self.add(id, embedding, metadata)

    async def get_all_prompts(self) -> List[str]:
        """Gets all prompts from the metadata."""
        return [meta["prompt"] for meta in self.metadata.values()]

class HybridSearch:
    """Combines sparse and dense retrieval for improved accuracy."""

    def __init__(self, dense_retriever, sparse_retriever, all_prompts):
        self.dense_retriever = dense_retriever
        self.sparse_retriever = sparse_retriever
        self.all_prompts = all_prompts

    async def search(self, query: str, k: int = 5, threshold: float = 0.85, alpha: float = 0.5, expand_query: bool = True) -> List[Tuple[str, float]]:
        """Performs a hybrid search and combines the results."""
        # Expand query with synonyms
        if expand_query:
            expanded_query = query.split(" ")
            for word in query.split(" "):
                synonyms = get_synonyms(word)
                if synonyms:
                    expanded_query.extend(synonyms)
            tokenized_query = expanded_query
        else:
            tokenized_query = query.split(" ")

        # Dense search
        query_embedding = await self.dense_retriever.embedding_model.encode_single(query)
        dense_results = await self.dense_retriever.vector_store.search(query_embedding, k=k, threshold=threshold)

        # Sparse search
        sparse_scores = self.sparse_retriever.get_scores(tokenized_query)

        # Combine results
        combined_results = {}
        for doc_id, score in dense_results:
            combined_results[doc_id] = combined_results.get(doc_id, 0) + alpha * score
        
        for i, score in enumerate(sparse_scores):
            # Get the prompt from the corpus using the index
            prompt = self.all_prompts[i]
            # Generate the cache key from the prompt to use as a unique identifier
            doc_id = hashlib.sha256(prompt.encode()).hexdigest()
            if doc_id in combined_results:
                combined_results[doc_id] += (1 - alpha) * score

        sorted_results = sorted(combined_results.items(), key=lambda item: item[1], reverse=True)
        return sorted_results[:k]

class SemanticCache:
    """Advanced semantic caching with vector similarity search."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or get_config().get('semantic_cache', {})
        
        # Initialize embedding model
        model_name = self.config.get('embedding_model', 'paraphrase-multilingual-MiniLM-L12-v2')
        self.embedding_model = EmbeddingModel(model_name)
        
        # Initialize vector store
        backend = self.config.get('backend', 'chromadb')
        self.similarity_threshold = self.config.get('similarity_threshold', 0.85)
        
        try:
            if backend == 'chromadb' and CHROMADB_AVAILABLE:
                self.vector_store = ChromaDBStore()
            elif backend == 'faiss' and FAISS_AVAILABLE:
                dimension = self.config.get('embedding_dimension', 384)
                self.vector_store = FAISSStore(dimension=dimension)
            else:
                logger.warning(f"Vector backend '{backend}' not available, semantic caching disabled")
                self.vector_store = None
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            self.vector_store = None
        
        self.enabled = self.vector_store is not None and self.embedding_model._model is not None
        
        # Initialize sparse retriever for hybrid search
        if self.enabled and RANK_BM25_AVAILABLE:
            self.all_prompts = asyncio.run(self.vector_store.get_all_prompts())
            tokenized_corpus = [doc.split(" ") for doc in self.all_prompts]
            self.sparse_retriever = BM25Okapi(tokenized_corpus)
            self.hybrid_search = HybridSearch(self, self.sparse_retriever, self.all_prompts)
        else:
            self.hybrid_search = None

        logger.info(f"Semantic cache initialized (enabled: {self.enabled}, hybrid_search: {self.hybrid_search is not None})")
    
    def _generate_cache_key(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate a unique cache key."""
        hasher = hashlib.sha256()
        hasher.update(prompt.encode('utf-8'))
        if context:
            sorted_context = json.dumps(context, sort_keys=True)
            hasher.update(sorted_context.encode('utf-8'))
        return hasher.hexdigest()
    
    def _extract_semantic_tags(self, prompt: str, context: Dict[str, Any] = None) -> List[str]:
        """Extract semantic tags from prompt and context."""
        tags = []
        
        # Extract from context
        if context:
            if 'model' in context:
                tags.append(f"model:{context['model']}")
            if 'cli' in context:
                tags.append(f"cli:{context['cli']}")
            if 'language' in context:
                tags.append(f"lang:{context['language']}")
        
        # Simple keyword-based tagging for prompt content
        prompt_lower = prompt.lower()
        if 'code' in prompt_lower or 'function' in prompt_lower:
            tags.append('category:code')
        elif 'explain' in prompt_lower or 'what' in prompt_lower:
            tags.append('category:explanation')
        elif 'debug' in prompt_lower or 'error' in prompt_lower:
            tags.append('category:debugging')
        elif 'write' in prompt_lower or 'create' in prompt_lower:
            tags.append('category:generation')
        
        return tags
    
    async def get_similar(self, prompt: str, context: Dict[str, Any] = None,
                   threshold: Optional[float] = None) -> Optional[SemanticCacheEntry]:
        """Get semantically similar cache entry."""
        if not self.enabled:
            return None
        
        threshold = threshold or self.similarity_threshold
        
        if self.hybrid_search:
            matches = await self.hybrid_search.search(prompt, threshold=threshold)
        else:
            try:
                # Generate embedding for query
                query_embedding = await self.embedding_model.encode_single(prompt)
                if query_embedding is None:
                    return None
                
                # Search for similar embeddings
                matches = await self.vector_store.search(query_embedding, k=5, threshold=threshold)
            except Exception as e:
                logger.error(f"Error in semantic search: {e}")
                return None

        if not matches:
            return None
        
        # Return the most similar match
        best_match_id, similarity = matches[0]
        
        # Load the full cache entry
        # This would typically come from your main cache storage
        # For now, we'll return a placeholder indicating a match was found
        logger.info(f"Found semantic match with similarity {similarity:.3f}")
        
        return SemanticCacheEntry(
            cache_key=best_match_id,
            prompt=prompt,
            response="",  # Would be loaded from main cache
            context=context or {},
            embedding=await self.embedding_model.encode_single(prompt),
            timestamp=time.time(),
            similarity_threshold=threshold
        )
            
    async def add(self, prompt: str, response: str, context: Dict[str, Any] = None) -> str:
        """Add new entry to semantic cache."""
        if not self.enabled:
            return ""
        
        try:
            cache_key = self._generate_cache_key(prompt, context)
            
            # Generate embedding
            embedding = await self.embedding_model.encode_single(prompt)
            if embedding is None:
                return cache_key
            
            # Prepare metadata
            metadata = {
                'prompt': prompt,
                'context': context or {},
                'timestamp': time.time(),
                'semantic_tags': self._extract_semantic_tags(prompt, context)
            }
            
            # Add to vector store
            await self.vector_store.add(cache_key, embedding, metadata)
            
            # Update sparse retriever
            if self.hybrid_search:
                self.all_prompts.append(prompt)
                tokenized_corpus = [doc.split(" ") for doc in self.all_prompts]
                self.sparse_retriever = BM25Okapi(tokenized_corpus)
                self.hybrid_search.sparse_retriever = self.sparse_retriever


            logger.info(f"Added semantic cache entry: {cache_key[:8]}...")
            return cache_key
            
        except Exception as e:
            logger.error(f"Error adding to semantic cache: {e}")
            return ""
    
    async def delete(self, cache_key: str):
        """Delete entry from semantic cache."""
        if not self.enabled:
            return
        
        try:
            await self.vector_store.delete(cache_key)
            logger.info(f"Deleted semantic cache entry: {cache_key[:8]}...")
        except Exception as e:
            logger.error(f"Error deleting from semantic cache: {e}")
    
    async def update_access(self, cache_key: str):
        """Update access statistics for cache entry."""
        # This would update access count and last_accessed time
        # Implementation depends on your storage backend
        pass
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get semantic cache statistics."""
        stats = {
            'enabled': self.enabled,
            'backend': type(self.vector_store).__name__ if self.vector_store else None,
            'model': self.embedding_model.model_name,
            'threshold': self.similarity_threshold,
            'hybrid_search': self.hybrid_search is not None
        }
        
        # Add backend-specific stats if available
        if isinstance(self.vector_store, ChromaDBStore):
            try:
                count = self.vector_store.collection.count()
                stats['total_vectors'] = count
            except:
                pass
        elif isinstance(self.vector_store, FAISSStore):
            stats['total_vectors'] = self.vector_store.index.ntotal
        
        return stats

# Convenience function for backward compatibility
def create_semantic_cache(config: Dict[str, Any] = None) -> SemanticCache:
    """Create and return a SemanticCache instance."""
    return SemanticCache(config)