#!/usr/bin/env bash
# Run the photo booth application directly (development or manual start).
set -euo pipefail

cd "$(dirname "$0")/.."

uv run python -m app.main
