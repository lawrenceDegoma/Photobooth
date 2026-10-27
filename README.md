# Photobooth

A portable photo booth application for Raspberry Pi. It captures a multi-photo session on a touchscreen, builds a photo strip, and shares results with guests over a local web server via QR code. Designed to run offline on its own Wi-Fi hotspot.

On non-Linux machines the camera is replaced by a mock, so the full flow can be developed and tested without Pi hardware.

The original design specification is in `Portable Raspberry Pi Photo Booth — README.md`.

## Features

- Touchscreen UI (PyQt6), 720x1280 portrait
- Session flow: welcome, preview, countdown, capture, processing, review, share
- Photo strip generation with selectable templates and optional filters
- Local Flask server with tokenized download URLs and QR codes
- Explicit state machine preventing invalid transitions
- Hidden admin screen (long-press the logo) showing status, with restart and shutdown
- Automatic cleanup of old sessions on startup
- Rotating log files
- Optional physical button, lighting, and power control (GPIO on Pi, no-op elsewhere)

## Requirements

- Python 3.9+
- [uv](https://docs.astral.sh/uv/)
- Raspberry Pi with a camera module (for deployment only)

## Development

```bash
uv sync
uv run python -m app.main
uv run pytest -q
```

`picamera2` and `gpiozero` are Linux-only and are listed in `requirements-pi.txt` rather than `pyproject.toml`.

## Deployment on a Raspberry Pi

```bash
git clone https://github.com/lawrenceDegoma/Photobooth.git ~/photobooth
cd ~/photobooth
./scripts/install.sh
```

`install.sh` syncs dependencies, installs the Pi-only packages, creates the `photos/` and `logs/` directories, and installs the systemd service.

Other scripts:

| Script | Purpose |
| --- | --- |
| `scripts/start.sh` | Run the app manually |
| `scripts/setup_service.sh` | Install, enable, and restart the systemd service |
| `scripts/setup_hotspot.sh` | Configure the Pi as a Wi-Fi access point (run with sudo) |

The systemd unit assumes the project lives at `/home/pi/photobooth` and runs as user `pi`. Edit `systemd/photobooth.service` if your path or user differs.

The admin shutdown action runs `sudo shutdown -h now`, so the service user needs passwordless sudo for that command.

### Offline hotspot

`scripts/setup_hotspot.sh` installs `hostapd` and `dnsmasq` using the files in `config/hotspot/`. The default SSID is `PhotoBooth` and the Pi address is `192.168.4.1`. Change `wpa_passphrase` in `config/hotspot/hostapd.conf` before use, and set `sharing.hostname` in `config/config.yaml` to the Pi address so QR codes resolve for connected guests.

The hotspot setup has not yet been verified on hardware.

## Configuration

Settings are read from `config/config.yaml`. Set `PHOTOBOOTH_CONFIG` to use a different file.

| Section | Controls |
| --- | --- |
| `booth` | Display name |
| `session` | Photos per session, countdown, delay between photos |
| `camera` | Capture and preview resolution, autofocus |
| `display` | Fullscreen, orientation, window size |
| `storage` | Photo directory, minimum free space |
| `sharing` | Enable server, hostname, port |
| `hardware` | Physical button and GPIO pin |
| `logging` | Log path, level, rotation size and backup count |
| `processing` | Strip template (`classic`, `wedding`, `birthday`, `graduation`, `holiday`) and filter (`grayscale`, `sepia`, `vivid`, `bw_high_contrast`, or none) |
| `cleanup` | Enable, maximum session age in days, run on startup |
| `admin` | Enable, long-press duration in seconds |

## Project layout

```text
app/
  core/         config, state machine, event bus, application bootstrap
  camera/       camera interface, Pi camera, mock camera
  session/      session model and capture flow
  processing/   image processing, filters, templates, photo strip
  storage/      session directory layout and cleanup
  sharing/      QR codes, Flask server, download manager
  hardware/     button, lighting, power
  ui/           PyQt6 screens
assets/         icons, fonts, templates, branding (optional)
config/         config.yaml and hotspot configuration
scripts/        install and setup scripts
systemd/        service unit
tests/          pytest suite
```

Assets are optional. A font placed in `assets/fonts/` is preferred over system fonts for strip text.

## Architecture notes

- Components communicate through a synchronous `EventBus`. Handlers for events published from background threads must use `app.core.qt_utils.run_on_main_thread` before touching Qt widgets.
- `app/core/application.py` is the composition root; it is the only place that constructs and connects services.
- State transitions are defined in `app/core/state.py`.

See `DEVELOPMENT.md` for more detail.
