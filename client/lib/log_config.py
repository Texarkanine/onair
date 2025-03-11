import logging
import sys

class StdoutFilter(logging.Filter):
    """Filter that allows records at INFO level and below"""
    def filter(self, record):
        return record.levelno <= logging.INFO

def setup_logging():
    """Initialize logging configuration for the entire application."""
    # Create the base logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Format for both handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')
    
    # Handler for INFO and below -> stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.addFilter(StdoutFilter())  # INFO and below
    stdout_handler.setLevel(logging.INFO)
    
    # Handler for WARNING and above -> stderr
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(formatter)
    stderr_handler.setLevel(logging.WARNING)  # WARNING and above
    
    # Add both handlers
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)
    
    return logger

def get_logger(name):
    """Get a logger instance for a specific module."""
    return logging.getLogger(name) 
