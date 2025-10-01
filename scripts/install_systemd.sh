#!/bin/bash

# This script installs the psi-daemon as a systemd service.
# It should be run with sudo privileges.

set -e

# --- Configuration ---
SERVICE_NAME="psi-daemon"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
PROJECT_DIR=$(cd "$(dirname "$0")/.." && pwd)
VENV_PYTHON="${PROJECT_DIR}/.venv/bin/python"
DAEMON_SCRIPT="${PROJECT_DIR}/psi_agent/daemon/vm_daemon.py"
CONFIG_FILE="${PROJECT_DIR}/configs/config.yaml"
USER=$(whoami)

# --- Check for root privileges ---
if [ "$EUID" -ne 0 ]; then
  echo "Please run this script with sudo."
  exit 1
fi

# --- Check for virtual environment ---
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Python virtual environment not found at ${VENV_PYTHON}."
    echo "Please run 'python -m venv .venv' in the project root first."
    exit 1
fi

# --- Create systemd service file ---
echo "Creating systemd service file at ${SERVICE_FILE}..."

cat > "${SERVICE_FILE}" << EOL
[Unit]
Description=PSI Agent Daemon
After=network.target

[Service]
User=${USER}
Group=$(id -gn ${USER})
WorkingDirectory=${PROJECT_DIR}
ExecStart=${VENV_PYTHON} ${DAEMON_SCRIPT} --config ${CONFIG_FILE}
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

echo "Service file created."

# --- Reload systemd and provide instructions ---
systemctl daemon-reload
echo "Systemd daemon reloaded."

echo -e "\n--- Installation Complete ---"
echo "To enable the service to start on boot, run:"
echo "  sudo systemctl enable ${SERVICE_NAME}"
echo ""
echo "To start the service now, run:"
echo "  sudo systemctl start ${SERVICE_NAME}"
echo ""
echo "To check the status of the service, run:"
echo "  sudo systemctl status ${SERVICE_NAME}"
echo ""
echo "To view the logs, run:"
echo "  sudo journalctl -u ${SERVICE_NAME} -f"