import logging
import sys

class StdoutFilter(logging.Filter):
    """Filter that allows records at INFO level and below"""
    def filter(self, record):
        return record.levelno <= logging.INFO

def setup_logging():
    """Initialize logging configuration for the entire application."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Base threshold
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')
    
    # Handler for INFO -> stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.addFilter(StdoutFilter())  # Only <= INFO passes
    
    # Handler for WARNING+ -> stderr
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(formatter)
    stderr_handler.setLevel(logging.WARNING)  # Only >= WARNING passes
    
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)
    
    return logger

def get_logger(name):
    """Get a logger instance for a specific module."""
    return logging.getLogger(name) 
