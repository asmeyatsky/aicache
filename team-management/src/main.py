"""
Main application module for aicache team management
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
    logger.info("Initializing aicache team management")
    
    # Initialize components
    # TODO: Initialize database connections
    # TODO: Initialize real-time services
    # TODO: Initialize notification services
    
    logger.info("aicache team management initialized")
    
    yield
    
    # Cleanup
    logger.info("Shutting down aicache team management")

app = FastAPI(
    title="aicache Team Management API",
    description="Team collaboration and management for aicache",
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
        "service": "aicache-team-management"
    }

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=config.get('HOST', '0.0.0.0'),
        port=config.get('PORT', 8000),
        reload=config.get('DEBUG', False)
    )