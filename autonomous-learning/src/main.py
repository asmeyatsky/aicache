"""
Main application module for aicache autonomous learning system
"""

import asyncio
from contextlib import asynccontextmanager
import logging

from .utils.config import get_config
from .utils.logger import get_logger
from .core.meta_learning_orchestrator import MetaLearningOrchestrator
from .nas.neural_architecture_search import NeuralArchitectureSearch
from .prompt_engineering.automated_prompt_engineering import AutomatedPromptEngineering
from .self_modification.self_modifying_code_system import SelfModifyingCodeSystem

config = get_config()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan():
    """Application lifespan manager"""
    logger.info("Initializing aicache autonomous learning system")
    
    # Initialize components
    # TODO: Initialize all autonomous learning components
    
    logger.info("aicache autonomous learning system initialized")
    
    yield
    
    # Cleanup
    logger.info("Shutting down aicache autonomous learning system")

async def main():
    """Main application entry point"""
    logger.info("Starting aicache autonomous learning system")
    
    # Initialize configuration
    app_config = get_config()
    
    # Initialize core components
    meta_learning_orchestrator = MetaLearningOrchestrator(app_config)
    nas = NeuralArchitectureSearch(app_config)
    prompt_engineering = AutomatedPromptEngineering(app_config)
    self_modification = SelfModifyingCodeSystem(app_config)
    
    # Initialize components
    await meta_learning_orchestrator.initialize()
    await nas.initialize()
    await prompt_engineering.initialize()
    await self_modification.initialize()
    
    # Start autonomous learning cycle
    logger.info("Starting autonomous learning cycle")
    
    # Run learning cycle
    await meta_learning_orchestrator.start_learning_cycle()
    
    # Run neural architecture search
    nas_results = await nas.search(max_evaluations=50)
    logger.info(f"Neural architecture search completed with best score: {nas_results['best_score']:.4f}")
    
    # Run prompt engineering optimization
    sample_prompt = "Explain the following {language} code:\n{code}"
    sample_context = {"language": "python", "code": "def hello():\n    print('Hello, World!')"}
    optimized_prompt = await prompt_engineering.optimize_prompt(sample_prompt, sample_context)
    logger.info(f"Prompt optimization completed. Optimized prompt: {optimized_prompt}")
    
    # Analyze code for modification opportunities
    sample_module = "cache_optimizer"
    performance_data = {"cache_hit_rate": 0.85, "response_time": 0.12}
    modification_opportunities = await self_modification.analyze_code_for_modification(
        sample_module, 
        performance_data
    )
    
    if modification_opportunities:
        # Generate and apply code modification
        opportunity = modification_opportunities[0]
        modification = await self_modification.generate_code_modification(opportunity, sample_context)
        applied = await self_modification.apply_code_modification(modification)
        logger.info(f"Code modification {'applied' if applied else 'failed'}")
    
    logger.info("Autonomous learning cycle completed")
    
    # Keep the system running for continuous learning
    while True:
        try:
            # Periodic learning cycle (every hour)
            await asyncio.sleep(3600)  # 1 hour
            
            # Run another learning cycle
            await meta_learning_orchestrator.start_learning_cycle()
            
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down")
            break
        except Exception as e:
            logger.error(f"Error in autonomous learning cycle: {e}")
            # Continue running despite errors
            await asyncio.sleep(60)  # Wait before retrying

if __name__ == "__main__":
    # Run the autonomous learning system
    asyncio.run(main())