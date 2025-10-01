import logging
import sys
from pathlib import Path

def setup_logging(log_file_path="logs/psi_daemon.log"):
    """
    Sets up a standardized logger for the application.

    Args:
        log_file_path (str): The path to the log file, relative to the project root.
    """
    project_root = Path(__file__).resolve().parents[2]
    log_file = project_root / log_file_path

    log_file.parent.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info("Logging configured.")