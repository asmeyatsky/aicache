"""
Main application module for aicache self-healing system
"""

import asyncio
from contextlib import asynccontextmanager
import logging

from .utils.config import get_config
from .utils.logger import get_logger
from .health_monitor.continuous_monitor import ContinuousMonitor
from .diagnostics.diagnostic_engine import DiagnosticEngine
from .healing.repair_system import RepairSystem
from .audit.audit_logger import AuditLogger

config = get_config()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan():
    """Application lifespan manager"""
    logger.info("Initializing aicache self-healing system")
    
    # Initialize components
    # TODO: Initialize all self-healing components
    
    logger.info("aicache self-healing system initialized")
    
    yield
    
    # Cleanup
    logger.info("Shutting down aicache self-healing system")

async def main():
    """Main application entry point"""
    logger.info("Starting aicache self-healing system")
    
    # Initialize configuration
    app_config = get_config()
    
    # Initialize core components
    health_monitor = ContinuousMonitor(app_config)
    diagnostic_engine = DiagnosticEngine(app_config)
    repair_system = RepairSystem(app_config)
    audit_logger = AuditLogger(app_config)
    
    # Initialize components
    await health_monitor.initialize()
    await diagnostic_engine.initialize()
    await repair_system.initialize()
    await audit_logger.initialize()
    
    # Start continuous monitoring
    monitoring_task = asyncio.create_task(health_monitor.start_monitoring())
    
    try:
        # Main healing loop
        while True:
            # Check for health issues
            health_issues = await health_monitor.get_detected_issues()
            
            if health_issues:
                # Log detected issues
                for issue in health_issues:
                    await audit_logger.log_issue_detection(issue)
                
                # Diagnose issues
                diagnoses = await diagnostic_engine.diagnose_issues(health_issues)
                
                # Log diagnoses
                for diagnosis in diagnoses:
                    await audit_logger.log_diagnosis(diagnosis)
                
                # Apply healing
                healing_results = await repair_system.apply_healing(diagnoses)
                
                # Log healing results
                for result in healing_results:
                    await audit_logger.log_healing_result(result)
                
                # Clear handled issues
                await health_monitor.clear_handled_issues()
            
            # Perform preventive maintenance periodically
            await repair_system.perform_preventive_maintenance()
            
            # Wait before next iteration
            await asyncio.sleep(config.get('healing_cycle_interval', 60))
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down")
    except Exception as e:
        logger.error(f"Error in self-healing system: {e}")
        raise
    finally:
        # Cancel monitoring task
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass
            
        logger.info("aicache self-healing system shutdown complete")

if __name__ == "__main__":
    # Run the self-healing system
    asyncio.run(main())