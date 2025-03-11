import logging

def setup_logging():
    """Initialize logging configuration for the entire application."""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

def get_logger(name):
    """Get a logger instance for a specific module."""
    return logging.getLogger(name) 
