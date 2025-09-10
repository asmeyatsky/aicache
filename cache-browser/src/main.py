"""
Main application module for aicache public cache browser
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .utils.config import get_config
from .utils.logger import get_logger

config = get_config()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Initializing aicache public cache browser")
    
    # Initialize components
    # TODO: Initialize database connections
    # TODO: Initialize search engine
    # TODO: Initialize cache services
    # TODO: Initialize social services
    
    logger.info("aicache public cache browser initialized")
    
    yield
    
    # Cleanup
    logger.info("Shutting down aicache public cache browser")

app = FastAPI(
    title="aicache Public Cache Browser API",
    description="Public cache browser for aicache community",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get('ALLOWED_ORIGINS', ['*']),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": __import__('time').time(),
        "service": "aicache-public-cache-browser"
    }

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=config.get('HOST', '0.0.0.0'),
        port=config.get('PORT', 8000),
        reload=config.get('DEBUG', False)
    )