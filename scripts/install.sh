#!/usr/bin/env bash
# Install the photo booth application and its dependencies on a Raspberry Pi.
set -euo pipefail

cd "$(dirname "$0")/.."

if ! command -v uv >/dev/null 2>&1; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "Syncing Python dependencies..."
uv sync

echo "Installing Raspberry Pi-only dependencies (picamera2, gpiozero)..."
uv pip install -r requirements-pi.txt

mkdir -p photos logs

echo "Installing systemd service..."
sudo cp systemd/photobooth.service /etc/systemd/system/photobooth.service
sudo systemctl daemon-reload
sudo systemctl enable photobooth.service

echo "Install complete. Start with: sudo systemctl start photobooth"
