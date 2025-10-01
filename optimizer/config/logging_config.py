"""Semantic logging configuration using structlog."""

import logging
import sys
from typing import Optional
import structlog
from pythonjsonlogger import jsonlogger


def setup_logging(
    level: str = "INFO",
    format_type: str = "json",
    output_file: Optional[str] = None
) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Format type ("json" or "console")
        output_file: Optional file path for log output
    """
    # Configure standard logging
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Set up handlers
    handlers = []
    
    if format_type == "json":
        # JSON formatter for structured logs
        if output_file:
            file_handler = logging.FileHandler(output_file)
            file_handler.setFormatter(
                jsonlogger.JsonFormatter(
                    "%(asctime)s %(name)s %(levelname)s %(message)s"
                )
            )
            handlers.append(file_handler)
        
        # Console handler with JSON
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            jsonlogger.JsonFormatter(
                "%(asctime)s %(name)s %(levelname)s %(message)s"
            )
        )
        handlers.append(console_handler)
    else:
        # Console-friendly format
        if output_file:
            file_handler = logging.FileHandler(output_file)
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            handlers.append(file_handler)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
        handlers.append(console_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        force=True
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if format_type == "json"
            else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


# Initialize default logging
setup_logging()
