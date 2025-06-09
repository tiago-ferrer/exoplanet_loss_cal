import logging
import sys

# Configure the root logger
def configure_logging(level=logging.INFO):
    """
    Configure the root logger with the specified log level.
    
    Parameters:
        level (int): The logging level (e.g., logging.INFO, logging.DEBUG)
    """
    # Create a formatter that includes timestamp, level, and message
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create a console handler and set its formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove any existing handlers to avoid duplicate logs
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add the console handler to the root logger
    root_logger.addHandler(console_handler)

# Get a logger for a specific module
def get_logger(name):
    """
    Get a logger for a specific module.
    
    Parameters:
        name (str): The name of the module (typically __name__)
        
    Returns:
        logging.Logger: A configured logger
    """
    return logging.getLogger(name)