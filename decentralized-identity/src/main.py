"""
Main application module for aicache decentralized identity system
"""

import asyncio
from contextlib import asynccontextmanager
import logging

from .utils.config import get_config
from .utils.logger import get_logger
from .identity.identity_manager import IdentityManager
from .crypto.key_manager import KeyManager
from .verification.trust_registry import TrustRegistry
from .integration.did_resolver import DIDResolver
from .integration.identity_bridge import IdentityBridge

config = get_config()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan():
    """Application lifespan manager"""
    logger.info("Initializing aicache decentralized identity system")
    
    # Initialize components
    # TODO: Initialize all decentralized identity components
    
    logger.info("aicache decentralized identity system initialized")
    
    yield
    
    # Cleanup
    logger.info("Shutting down aicache decentralized identity system")

async def main():
    """Main application entry point"""
    logger.info("Starting aicache decentralized identity system")
    
    # Initialize configuration
    app_config = get_config()
    
    # Initialize core components
    identity_manager = IdentityManager(app_config)
    key_manager = KeyManager(app_config)
    trust_registry = TrustRegistry(app_config)
    did_resolver = DIDResolver(app_config)
    identity_bridge = IdentityBridge(app_config)
    
    # Initialize components
    await identity_manager.initialize()
    await key_manager.initialize()
    await trust_registry.initialize()
    await did_resolver.initialize()
    await identity_bridge.initialize()
    
    # Start identity management
    logger.info("Decentralized identity system started")
    
    try:
        # Main identity management loop
        while True:
            # Check for identity operations
            pending_operations = await identity_manager.get_pending_operations()
            
            if pending_operations:
                # Process identity operations
                for operation in pending_operations:
                    await identity_manager.process_operation(operation)
                    
            # Wait before next iteration
            await asyncio.sleep(config.get('identity_cycle_interval', 60))
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down")
    except Exception as e:
        logger.error(f"Error in decentralized identity system: {e}")
        raise
    finally:
        logger.info("aicache decentralized identity system shutdown complete")

if __name__ == "__main__":
    # Run the decentralized identity system
    asyncio.run(main())