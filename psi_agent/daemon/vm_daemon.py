import argparse
import logging
import os
import sys
import time
from pathlib import Path

# Add project root to sys.path to allow imports from other modules
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

import yaml

# Import utilities
from psi_agent.utils.logging import setup_logging

# Placeholder imports for agent capabilities
# from psi_agent.agents.knowledge_expander import KnowledgeExpander
# from psi_agent.agents.repo_rewriter import RepoRewriter
# from psi_agent.agents.db_evolver import DbEvolver

# --- Configuration ---
LOCK_FILE = project_root / "psi_daemon.lock"
HEARTBEAT_FILE = project_root / "logs/heartbeat.txt"
HEARTBEAT_INTERVAL = 60  # seconds

# --- Config Loading ---
def load_config(config_path):
    """Loads the YAML configuration file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logging.info(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        logging.error(f"Configuration file not found at {config_path}. Aborting.")
        return None
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML file: {e}. Aborting.")
        return None

# --- Lock File Management ---
def create_lock():
    if LOCK_FILE.exists():
        logging.warning("Lock file exists. Another instance may be running.")
        return False
    try:
        with open(LOCK_FILE, 'w') as f:
            f.write(str(os.getpid()))
        logging.info(f"Lock file created at {LOCK_FILE}")
        return True
    except IOError as e:
        logging.error(f"Failed to create lock file: {e}")
        return False

def release_lock():
    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
            logging.info("Lock file released.")
    except IOError as e:
        logging.error(f"Failed to release lock file: {e}")

# --- Heartbeat Management ---
def update_heartbeat():
    try:
        HEARTBEAT_FILE.parent.mkdir(exist_ok=True)
        with open(HEARTBEAT_FILE, 'w') as f:
            f.write(str(int(time.time())))
        logging.info("Heartbeat updated.")
    except IOError as e:
        logging.error(f"Failed to update heartbeat: {e}")

# --- Main Daemon Loop ---
def main_loop(config):
    """The main operational loop for the agent."""
    logging.info("--- Starting new agent cycle ---")

    # 1. Expand Knowledge (e.g., crawl APIs, read docs)
    logging.info("Running knowledge expansion...")
    # expander = KnowledgeExpander(config)
    # expander.run()

    # 2. Rewrite Repository (e.g., apply patches, refactor)
    logging.info("Running repository rewriter...")
    # rewriter = RepoRewriter(config)
    # rewriter.run()

    # 3. Evolve Database (e.g., apply schema changes)
    logging.info("Running database evolver...")
    # evolver = DbEvolver(config)
    # evolver.run()

    logging.info("--- Agent cycle complete ---")


def main():
    parser = argparse.ArgumentParser(description="PSI Agent Daemon")
    parser.add_argument("--config", type=str, default="configs/config.yaml", help="Path to the configuration file.")
    parser.add_argument("--once", action="store_true", help="Run the main loop once and exit.")
    args = parser.parse_args()

    setup_logging()

    # Construct absolute path for config file
    config_path = project_root / args.config
    config = load_config(config_path)
    if config is None:
        sys.exit(1)

    if not create_lock():
        sys.exit(1)

    try:
        if args.once:
            update_heartbeat()
            main_loop(config)
            return

        # Continuous loop
        while True:
            update_heartbeat()
            main_loop(config)
            interval = config.get('interval_seconds', 3600)
            logging.info(f"Sleeping for {interval} seconds...")
            time.sleep(interval)

    except KeyboardInterrupt:
        logging.info("Daemon stopped by user.")
    finally:
        release_lock()
        logging.info("Daemon shut down gracefully.")

if __name__ == "__main__":
    main()