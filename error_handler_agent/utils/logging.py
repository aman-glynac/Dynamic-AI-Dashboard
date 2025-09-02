"""
logging.py - Logging configuration utilities
"""
import logging
import sys
from typing import Optional
from ..config import LOG_LEVEL, LOG_FORMAT


def setup_logging(
    level: int = LOG_LEVEL,
    format_string: str = LOG_FORMAT,
    log_file: Optional[str] = None
):
    """
    Configure logging for the Error Handler Agent
    
    Args:
        level: Logging level
        format_string: Log message format
        log_file: Optional file path for logging
    """
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=handlers
    )
    
    # Set specific loggers
    logging.getLogger("error_handler").setLevel(level)
    
    # Reduce noise from external libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"error_handler.{name}")