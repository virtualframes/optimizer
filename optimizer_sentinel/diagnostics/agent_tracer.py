import logging
import json

# Configure a specific logger for the Jules agent
logger = logging.getLogger("jules-agent")
logger.setLevel(logging.DEBUG)

# To prevent duplicate handlers if this module is imported multiple times
if not logger.handlers:
    # Create a handler and formatter
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def trace_event(event: str, context: dict):
    """Logs a structured event for agent tracing."""
    try:
        # Use json.dumps for safe and structured serialization of context
        log_message = f"[TRACE] {event} | Context: {json.dumps(context, indent=2)}"
        logger.debug(log_message)
    except TypeError as e:
        logger.error(f"Failed to serialize context for event '{event}': {e}")
        logger.debug(f"[TRACE] {event} | Context (raw): {context}")