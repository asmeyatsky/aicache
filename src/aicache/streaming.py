"""
Streaming and real-time support for aicache.
"""

import asyncio
import json
import time
import hashlib
import logging
import threading
from typing import Dict, List, Any, Optional, AsyncIterator, Iterator, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import deque
import websockets
import zlib
from enum import Enum

logger = logging.getLogger(__name__)

class StreamChunkType(Enum):
    """Types of stream chunks."""
    TEXT = "text"
    CODE = "code"
    METADATA = "metadata"
    END = "end"
    ERROR = "error"

@dataclass
class StreamChunk:
    """Individual chunk in a streaming response."""
    chunk_id: int
    chunk_type: StreamChunkType
    content: str
    timestamp: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class StreamCache:
    """Cached streaming response."""
    cache_key: str
    prompt: str
    chunks: List[StreamChunk]
    context: Dict[str, Any]
    total_chunks: int
    complete: bool
    timestamp: float
    last_accessed: float
    
    # Stream metadata
    stream_id: str
    original_duration: float = 0.0  # How long original stream took
    compression_ratio: float = 1.0
    
    def get_full_response(self) -> str:
        """Reconstruct full response from chunks."""
        return ''.join(chunk.content for chunk in self.chunks if chunk.chunk_type == StreamChunkType.TEXT)
    
    def get_chunks_after(self, chunk_id: int) -> List[StreamChunk]:
        """Get chunks after specified ID (for resume functionality)."""
        return [chunk for chunk in self.chunks if chunk.chunk_id > chunk_id]

class ChunkBuffer:
    """Buffer for managing streaming chunks."""
    
    def __init__(self, max_size: int = 1000):
        self.chunks = deque(maxlen=max_size)
        self.lock = threading.RLock()
        self.chunk_counter = 0
    
    def add_chunk(self, chunk_type: StreamChunkType, content: str, metadata: Dict[str, Any] = None) -> StreamChunk:
        """Add a new chunk to the buffer."""
        with self.lock:
            chunk = StreamChunk(
                chunk_id=self.chunk_counter,
                chunk_type=chunk_type,
                content=content,
                timestamp=time.time(),
                metadata=metadata or {}
            )
            self.chunks.append(chunk)
            self.chunk_counter += 1
            return chunk
    
    def get_chunks(self, start_id: int = 0) -> List[StreamChunk]:
        """Get chunks starting from specified ID."""
        with self.lock:
            return [chunk for chunk in self.chunks if chunk.chunk_id >= start_id]
    
    def clear(self):
        """Clear the buffer."""
        with self.lock:
            self.chunks.clear()
            self.chunk_counter = 0

class StreamingCache:
    """Cache system optimized for streaming responses."""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache for active streams
        self.active_streams: Dict[str, ChunkBuffer] = {}
        self.stream_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Persistent storage for completed streams
        self.persistent_cache: Dict[str, StreamCache] = {}
        self._load_persistent_cache()
        
        # Real-time subscribers
        self.subscribers: Dict[str, List[Callable]] = {}
        
        self.lock = threading.RLock()
    
    def _load_persistent_cache(self):
        """Load persistent stream cache."""
        cache_file = self.cache_dir / "stream_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    data = json.load(f)
                    for cache_data in data.get('streams', []):
                        # Reconstruct StreamChunk objects
                        chunks = []
                        for chunk_data in cache_data['chunks']:
                            chunk = StreamChunk(
                                chunk_id=chunk_data['chunk_id'],
                                chunk_type=StreamChunkType(chunk_data['chunk_type']),
                                content=chunk_data['content'],
                                timestamp=chunk_data['timestamp'],
                                metadata=chunk_data.get('metadata', {})
                            )
                            chunks.append(chunk)
                        
                        stream_cache = StreamCache(
                            cache_key=cache_data['cache_key'],
                            prompt=cache_data['prompt'],
                            chunks=chunks,
                            context=cache_data['context'],
                            total_chunks=cache_data['total_chunks'],
                            complete=cache_data['complete'],
                            timestamp=cache_data['timestamp'],
                            last_accessed=cache_data.get('last_accessed', cache_data['timestamp']),
                            stream_id=cache_data.get('stream_id', ''),
                            original_duration=cache_data.get('original_duration', 0.0),
                            compression_ratio=cache_data.get('compression_ratio', 1.0)
                        )
                        
                        self.persistent_cache[cache_data['cache_key']] = stream_cache
                        
            except Exception as e:
                logger.error(f"Failed to load stream cache: {e}")
    
    def _save_persistent_cache(self):
        """Save persistent stream cache."""
        cache_file = self.cache_dir / "stream_cache.json"
        try:
            streams_data = []
            for stream_cache in self.persistent_cache.values():
                chunks_data = []
                for chunk in stream_cache.chunks:
                    chunks_data.append({
                        'chunk_id': chunk.chunk_id,
                        'chunk_type': chunk.chunk_type.value,
                        'content': chunk.content,
                        'timestamp': chunk.timestamp,
                        'metadata': chunk.metadata
                    })
                
                stream_data = {
                    'cache_key': stream_cache.cache_key,
                    'prompt': stream_cache.prompt,
                    'chunks': chunks_data,
                    'context': stream_cache.context,
                    'total_chunks': stream_cache.total_chunks,
                    'complete': stream_cache.complete,
                    'timestamp': stream_cache.timestamp,
                    'last_accessed': stream_cache.last_accessed,
                    'stream_id': stream_cache.stream_id,
                    'original_duration': stream_cache.original_duration,
                    'compression_ratio': stream_cache.compression_ratio
                }
                streams_data.append(stream_data)
            
            data = {
                'streams': streams_data,
                'last_updated': time.time()
            }
            
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save stream cache: {e}")
    
    def start_stream(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Start a new streaming session."""
        stream_id = hashlib.md5(f"{prompt}:{time.time()}".encode()).hexdigest()
        
        with self.lock:
            self.active_streams[stream_id] = ChunkBuffer()
            self.stream_metadata[stream_id] = {
                'prompt': prompt,
                'context': context or {},
                'start_time': time.time(),
                'complete': False
            }
            self.subscribers[stream_id] = []
        
        logger.info(f"Started stream {stream_id[:8]}...")
        return stream_id
    
    def add_chunk(self, stream_id: str, content: str, chunk_type: StreamChunkType = StreamChunkType.TEXT,
                  metadata: Dict[str, Any] = None) -> Optional[StreamChunk]:
        """Add a chunk to an active stream."""
        if stream_id not in self.active_streams:
            logger.warning(f"Stream {stream_id} not found")
            return None
        
        chunk = self.active_streams[stream_id].add_chunk(chunk_type, content, metadata)
        
        # Notify subscribers
        self._notify_subscribers(stream_id, chunk)
        
        return chunk
    
    def complete_stream(self, stream_id: str) -> str:
        """Mark stream as complete and cache it."""
        if stream_id not in self.active_streams:
            logger.warning(f"Stream {stream_id} not found")
            return ""
        
        with self.lock:
            buffer = self.active_streams[stream_id]
            metadata = self.stream_metadata[stream_id]
            
            # Create cache key
            cache_key = hashlib.sha256(
                f"{metadata['prompt']}:{json.dumps(metadata['context'], sort_keys=True)}".encode()
            ).hexdigest()
            
            # Create persistent cache entry
            chunks = buffer.get_chunks()
            duration = time.time() - metadata['start_time']
            
            stream_cache = StreamCache(
                cache_key=cache_key,
                prompt=metadata['prompt'],
                chunks=chunks,
                context=metadata['context'],
                total_chunks=len(chunks),
                complete=True,
                timestamp=metadata['start_time'],
                last_accessed=time.time(),
                stream_id=stream_id,
                original_duration=duration
            )
            
            self.persistent_cache[cache_key] = stream_cache
            
            # Clean up active stream
            del self.active_streams[stream_id]
            del self.stream_metadata[stream_id]
            del self.subscribers[stream_id]
        
        self._save_persistent_cache()
        logger.info(f"Completed and cached stream {stream_id[:8]}... as {cache_key[:8]}...")
        return cache_key
    
    def get_cached_stream(self, cache_key: str) -> Optional[StreamCache]:
        """Get a cached stream."""
        stream_cache = self.persistent_cache.get(cache_key)
        if stream_cache:
            stream_cache.last_accessed = time.time()
            return stream_cache
        return None
    
    def subscribe_to_stream(self, stream_id: str, callback: Callable[[StreamChunk], None]):
        """Subscribe to real-time stream updates."""
        if stream_id in self.subscribers:
            self.subscribers[stream_id].append(callback)
    
    def unsubscribe_from_stream(self, stream_id: str, callback: Callable[[StreamChunk], None]):
        """Unsubscribe from stream updates."""
        if stream_id in self.subscribers and callback in self.subscribers[stream_id]:
            self.subscribers[stream_id].remove(callback)
    
    def _notify_subscribers(self, stream_id: str, chunk: StreamChunk):
        """Notify all subscribers of new chunk."""
        if stream_id in self.subscribers:
            for callback in self.subscribers[stream_id]:
                try:
                    callback(chunk)
                except Exception as e:
                    logger.error(f"Error notifying subscriber: {e}")

class StreamingWrapper:
    """Wrapper for CLI tools that support streaming."""
    
    def __init__(self, streaming_cache: StreamingCache):
        self.streaming_cache = streaming_cache
    
    async def execute_streaming_command(self, command: List[str], prompt: str, 
                                      context: Dict[str, Any] = None) -> AsyncIterator[StreamChunk]:
        """Execute a streaming command and yield chunks."""
        
        # Check if we have a cached stream first
        cache_key = hashlib.sha256(
            f"{prompt}:{json.dumps(context or {}, sort_keys=True)}".encode()
        ).hexdigest()
        
        cached_stream = self.streaming_cache.get_cached_stream(cache_key)
        if cached_stream:
            logger.info(f"Serving cached stream {cache_key[:8]}...")
            for chunk in cached_stream.chunks:
                yield chunk
                # Add small delay to simulate original timing
                await asyncio.sleep(0.01)
            return
        
        # Start new stream
        stream_id = self.streaming_cache.start_stream(prompt, context)
        
        try:
            # Execute the actual command
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Read output line by line
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                
                content = line.decode('utf-8')
                chunk = self.streaming_cache.add_chunk(stream_id, content)
                if chunk:
                    yield chunk
            
            # Wait for process to complete
            await process.wait()
            
            # Handle any errors
            if process.returncode != 0:
                stderr = await process.stderr.read()
                error_chunk = self.streaming_cache.add_chunk(
                    stream_id, 
                    stderr.decode('utf-8'),
                    StreamChunkType.ERROR
                )
                if error_chunk:
                    yield error_chunk
        
        except Exception as e:
            logger.error(f"Error in streaming execution: {e}")
            error_chunk = self.streaming_cache.add_chunk(
                stream_id,
                f"Error: {str(e)}",
                StreamChunkType.ERROR
            )
            if error_chunk:
                yield error_chunk
        
        finally:
            # Complete the stream
            self.streaming_cache.complete_stream(stream_id)
    
    def resume_stream(self, cache_key: str, from_chunk_id: int = 0) -> Iterator[StreamChunk]:
        """Resume a stream from a specific chunk ID."""
        cached_stream = self.streaming_cache.get_cached_stream(cache_key)
        if not cached_stream:
            return
        
        chunks_to_serve = cached_stream.get_chunks_after(from_chunk_id)
        for chunk in chunks_to_serve:
            yield chunk

class WebSocketStreamer:
    """WebSocket server for real-time streaming."""
    
    def __init__(self, streaming_cache: StreamingCache, host: str = "localhost", port: int = 8765):
        self.streaming_cache = streaming_cache
        self.host = host
        self.port = port
        self.clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        
    async def register_client(self, websocket, path):
        """Register a new WebSocket client."""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}:{time.time()}"
        self.clients[client_id] = websocket
        
        try:
            await websocket.send(json.dumps({
                'type': 'connection',
                'client_id': client_id,
                'message': 'Connected to aicache streaming'
            }))
            
            async for message in websocket:
                await self.handle_message(client_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            if client_id in self.clients:
                del self.clients[client_id]
    
    async def handle_message(self, client_id: str, message: str):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'subscribe_stream':
                stream_id = data.get('stream_id')
                if stream_id:
                    await self.subscribe_client_to_stream(client_id, stream_id)
            
            elif message_type == 'get_cached_stream':
                cache_key = data.get('cache_key')
                if cache_key:
                    await self.send_cached_stream(client_id, cache_key)
            
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
    
    async def subscribe_client_to_stream(self, client_id: str, stream_id: str):
        """Subscribe client to stream updates."""
        def chunk_callback(chunk: StreamChunk):
            asyncio.create_task(self.send_chunk_to_client(client_id, chunk))
        
        self.streaming_cache.subscribe_to_stream(stream_id, chunk_callback)
    
    async def send_chunk_to_client(self, client_id: str, chunk: StreamChunk):
        """Send chunk to specific client."""
        if client_id in self.clients:
            try:
                message = {
                    'type': 'stream_chunk',
                    'chunk': {
                        'chunk_id': chunk.chunk_id,
                        'chunk_type': chunk.chunk_type.value,
                        'content': chunk.content,
                        'timestamp': chunk.timestamp,
                        'metadata': chunk.metadata
                    }
                }
                await self.clients[client_id].send(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending chunk to client {client_id}: {e}")
    
    async def send_cached_stream(self, client_id: str, cache_key: str):
        """Send entire cached stream to client."""
        cached_stream = self.streaming_cache.get_cached_stream(cache_key)
        if not cached_stream or client_id not in self.clients:
            return
        
        try:
            # Send stream metadata first
            metadata_message = {
                'type': 'stream_metadata',
                'cache_key': cache_key,
                'prompt': cached_stream.prompt,
                'total_chunks': cached_stream.total_chunks,
                'original_duration': cached_stream.original_duration
            }
            await self.clients[client_id].send(json.dumps(metadata_message))
            
            # Send all chunks
            for chunk in cached_stream.chunks:
                await self.send_chunk_to_client(client_id, chunk)
            
            # Send completion message
            completion_message = {
                'type': 'stream_complete',
                'cache_key': cache_key
            }
            await self.clients[client_id].send(json.dumps(completion_message))
            
        except Exception as e:
            logger.error(f"Error sending cached stream: {e}")
    
    async def start_server(self):
        """Start the WebSocket server."""
        server = await websockets.serve(
            self.register_client, 
            self.host, 
            self.port
        )
        logger.info(f"WebSocket streaming server started on {self.host}:{self.port}")
        return server

class DeltaCaching:
    """Implements delta caching for similar streaming responses."""
    
    def __init__(self, streaming_cache: StreamingCache):
        self.streaming_cache = streaming_cache
    
    def calculate_delta(self, original_chunks: List[StreamChunk], 
                       new_chunks: List[StreamChunk]) -> Dict[str, Any]:
        """Calculate delta between two chunk sequences."""
        
        # Simple delta calculation - could be enhanced with more sophisticated diff algorithms
        delta = {
            'operations': [],
            'compression_ratio': 0.0
        }
        
        original_content = [chunk.content for chunk in original_chunks]
        new_content = [chunk.content for chunk in new_chunks]
        
        # Find common subsequences and differences
        # This is a simplified implementation
        common_parts = []
        differences = []
        
        i = j = 0
        while i < len(original_content) and j < len(new_content):
            if original_content[i] == new_content[j]:
                common_parts.append(('match', i, j, original_content[i]))
                i += 1
                j += 1
            else:
                # Find next match
                found_match = False
                for k in range(j + 1, min(j + 10, len(new_content))):  # Look ahead max 10 chunks
                    if k < len(new_content) and original_content[i] == new_content[k]:
                        # Insert operation
                        for insert_idx in range(j, k):
                            differences.append(('insert', insert_idx, new_content[insert_idx]))
                        j = k
                        found_match = True
                        break
                
                if not found_match:
                    differences.append(('replace', i, j, original_content[i], new_content[j]))
                    i += 1
                    j += 1
        
        delta['operations'] = common_parts + differences
        
        # Calculate compression ratio
        original_size = sum(len(content) for content in original_content)
        delta_size = sum(len(str(op)) for op in delta['operations'])
        delta['compression_ratio'] = delta_size / original_size if original_size > 0 else 1.0
        
        return delta
    
    def apply_delta(self, base_chunks: List[StreamChunk], delta: Dict[str, Any]) -> List[StreamChunk]:
        """Apply delta to base chunks to reconstruct new chunks."""
        
        result_chunks = []
        operations = delta['operations']
        
        for operation in operations:
            if operation[0] == 'match':
                # Copy from base
                _, base_idx, _, content = operation
                if base_idx < len(base_chunks):
                    result_chunks.append(base_chunks[base_idx])
            
            elif operation[0] == 'insert':
                # Insert new chunk
                _, _, content = operation
                new_chunk = StreamChunk(
                    chunk_id=len(result_chunks),
                    chunk_type=StreamChunkType.TEXT,
                    content=content,
                    timestamp=time.time()
                )
                result_chunks.append(new_chunk)
            
            elif operation[0] == 'replace':
                # Replace with new content
                _, _, _, _, new_content = operation
                new_chunk = StreamChunk(
                    chunk_id=len(result_chunks),
                    chunk_type=StreamChunkType.TEXT,
                    content=new_content,
                    timestamp=time.time()
                )
                result_chunks.append(new_chunk)
        
        return result_chunks

# Factory functions
def create_streaming_cache(cache_dir: Path) -> StreamingCache:
    """Create a streaming cache instance."""
    return StreamingCache(cache_dir)

def create_websocket_streamer(streaming_cache: StreamingCache, 
                             host: str = "localhost", port: int = 8765) -> WebSocketStreamer:
    """Create a WebSocket streamer instance."""
    return WebSocketStreamer(streaming_cache, host, port)