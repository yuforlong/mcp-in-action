import os
import sys
from loguru import logger

# Configure loguru logger
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Remove default logger
logger.remove()

# Add new logger with custom format
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=LOG_LEVEL,
    colorize=True
)

# Add file logger if LOG_FILE is set
LOG_FILE = os.getenv("LOG_FILE")
if LOG_FILE:
    logger.add(
        LOG_FILE,
        rotation="10 MB",
        retention="1 week",
        level=LOG_LEVEL
    )


def get_logger():
    """Get the configured logger.
    
    Returns:
        The logger instance
    """
    return logger 