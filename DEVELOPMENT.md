# Development Guide

Quickstart for developing the Portable Raspberry Pi Photo Booth application
on a regular computer (no Pi hardware required).

## Prerequisites

- Python 3.9+
- [`uv`](https://docs.astral.sh/uv/) for dependency management

## Setup

```bash
uv sync
```

This creates a `.venv` and installs all cross-platform dependencies
(PyQt6, Pillow, qrcode, Flask, PyYAML, pytest) as defined in `pyproject.toml`.

Raspberry Pi-only packages (`picamera2`, `gpiozero`) are **not** included in
`pyproject.toml` because they only build on Linux. They live in
`requirements-pi.txt` and are installed separately on the Pi itself via
`scripts/install.sh`.

## Running the app

```bash
uv run python -m app.main
```

or use the VS Code task **"Run Photo Booth (dev)"**.

On a non-Linux machine, `CameraService` automatically falls back to
`MockCamera`, which renders synthetic preview frames and captures so the
full booth flow (welcome → preview → countdown → capture → processing →
review → share) can be exercised without a Pi or camera attached.

The default `config/config.yaml` runs the UI windowed (not fullscreen) and
binds the sharing server to `0.0.0.0:8080` for local testing.

## Running tests

```bash
uv run pytest -q
```

or use the VS Code task **"Run Tests"**.

## Project layout

See the root README (`Portable Raspberry Pi Photo Booth — README.md`) for
the full architecture and design rationale. Key source directories:

```text
app/
├── core/        # config, state machine, event bus, application bootstrap
├── camera/      # CameraInterface + PiCamera / MockCamera + CameraService
├── session/     # PhotoSession model + SessionManager (capture flow)
├── processing/  # image processing, filters, templates, photo strip
├── storage/     # on-disk session/photo layout, cleanup
├── sharing/     # QR generation, local Flask server, download manager
├── hardware/    # physical button, lighting, power (GPIO on Pi, no-op elsewhere)
└── ui/          # PyQt6 screens (welcome, camera, countdown, review, share, error)
```

## Threading note

`SessionManager` runs the countdown/capture sequence on a background
thread and publishes progress via the synchronous `EventBus`. Since Qt
widgets are not thread-safe, any event subscriber in `application.py` that
updates the UI in response to a background-thread-published event wraps
its handler with `app.core.qt_utils.run_on_main_thread(...)` to marshal
the call onto the Qt main thread.

## Deploying to a Raspberry Pi

```bash
./scripts/install.sh   # uv sync + installs Pi-only deps + systemd service
./scripts/start.sh      # run manually
sudo systemctl start photobooth   # or run as a service
```
