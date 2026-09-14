#!/usr/bin/env bash
# (Re)install and enable the systemd service, then restart it.
set -euo pipefail

cd "$(dirname "$0")/.."

sudo cp systemd/photobooth.service /etc/systemd/system/photobooth.service
sudo systemctl daemon-reload
sudo systemctl enable photobooth.service
sudo systemctl restart photobooth.service
sudo systemctl status photobooth.service --no-pager
