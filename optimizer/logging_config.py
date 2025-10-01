import logging
import sys
from optimizer.core.settings import JulesSettings

# Instantiate the settings
settings = JulesSettings()

def setup_logging():
    """
    Set up logging for the application.
    """
    log_level = getattr(logging, settings.jules_log_level.upper(), logging.INFO)

    handlers = [logging.StreamHandler(sys.stdout)]
    if settings.jules_log_file:
        handlers.append(logging.FileHandler(settings.jules_log_file))

    logging.basicConfig(
        level=log_level, format=settings.jules_log_format, handlers=handlers
    )


def get_logger(name: str):
    """
    Get a logger instance.
    """
    return logging.getLogger(name)