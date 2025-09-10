"""
Logger utility for aicache decentralized identity system
"""

import logging
import os
import sys
from typing import Optional
import json
from datetime import datetime

# Global logger instance
_logger: Optional[logging.Logger] = None

def get_logger(name: str = __name__) -> logging.Logger:
    """Get logger instance with proper configuration"""
    global _logger
    
    if _logger is None:
        _logger = setup_logger(name)
        
    return _logger

def setup_logger(name: str = __name__) -> logging.Logger:
    """Setup logger with configuration"""
    # Create logger
    logger = logging.getLogger(name)
    
    # Prevent adding multiple handlers
    if logger.handlers:
        return logger
        
    # Set level
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Create formatter
    log_format = os.environ.get('LOG_FORMAT', 'json')
    if log_format.lower() == 'json':
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    return logger

class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        # Add extra fields if present
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                              'filename', 'module', 'lineno', 'funcName', 'created', 
                              'msecs', 'relativeCreated', 'thread', 'threadName', 
                              'processName', 'process', 'getMessage', 'exc_info', 
                              'exc_text', 'stack_info']:
                    log_entry[key] = value
                    
        return json.dumps(log_entry)

def log_debug(message: str, **kwargs):
    """Log debug message"""
    logger = get_logger()
    logger.debug(message, extra=kwargs)

def log_info(message: str, **kwargs):
    """Log info message"""
    logger = get_logger()
    logger.info(message, extra=kwargs)

def log_warning(message: str, **kwargs):
    """Log warning message"""
    logger = get_logger()
    logger.warning(message, extra=kwargs)

def log_error(message: str, **kwargs):
    """Log error message"""
    logger = get_logger()
    logger.error(message, extra=kwargs)

def log_critical(message: str, **kwargs):
    """Log critical message"""
    logger = get_logger()
    logger.critical(message, extra=kwargs)