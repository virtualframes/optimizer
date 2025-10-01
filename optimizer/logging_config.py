import logging
import sys
from optimizer.config.settings import settings

def setup_logging():
    """
    Set up logging for the application.
    """
    log_level = getattr(logging, settings.logging.level.upper(), logging.INFO)

    handlers = [logging.StreamHandler(sys.stdout)]
    if settings.logging.file:
        handlers.append(logging.FileHandler(settings.logging.file))

    logging.basicConfig(
        level=log_level,
        format=settings.logging.format,
        handlers=handlers
    )

def get_logger(name: str):
    """
    Get a logger instance.
    """
    return logging.getLogger(name)