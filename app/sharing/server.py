"""Lightweight local Flask server for offline QR-based photo sharing.

Serves only registered session tokens (see DownloadManager). No directory
listing, no predictable sequential URLs, no remote administrative endpoints.
"""
from __future__ import annotations

import logging
import threading
from pathlib import Path

from flask import Flask, abort, render_template_string, send_file

from app.sharing.download_manager import DownloadManager

logger = logging.getLogger(__name__)

_PAGE_TEMPLATE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Your Photos</title>
  <style>
    body { font-family: sans-serif; background: #111; color: #fff; text-align: center; padding: 20px; }
    h1 { font-size: 1.6em; }
    img { max-width: 90%; border-radius: 8px; margin: 12px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.5); }
    a.button { display: inline-block; background: #4a90d9; color: #fff; padding: 14px 28px;
               border-radius: 8px; text-decoration: none; font-size: 1.1em; margin-top: 20px; }
  </style>
</head>
<body>
  <h1>YOUR PHOTOS</h1>
  {% for i in range(photo_count) %}
    <div><img src="{{ url_for('photo', token=token, index=i) }}" alt="Photo {{ i + 1 }}"></div>
  {% endfor %}
  <div><img src="{{ url_for('strip', token=token) }}" alt="Photo Strip"></div>
  <div><a class="button" href="{{ url_for('download_all', token=token) }}">DOWNLOAD ALL</a></div>
</body>
</html>
"""


def create_app(download_manager: DownloadManager) -> Flask:
    app = Flask(__name__)

    @app.get("/s/<token>")
    def session_page(token: str):
        shared = download_manager.get(token)
        if shared is None:
            abort(404)
        photo_count = len(list(shared.processed_dir.glob("*.jpg")))
        return render_template_string(_PAGE_TEMPLATE, token=token, photo_count=photo_count)

    @app.get("/s/<token>/photo/<int:index>")
    def photo(token: str, index: int):
        shared = download_manager.get(token)
        if shared is None:
            abort(404)
        path = shared.processed_dir / f"{index + 1:02d}.jpg"
        if not path.exists():
            abort(404)
        return send_file(path)

    @app.get("/s/<token>/strip")
    def strip(token: str):
        shared = download_manager.get(token)
        if shared is None or not shared.strip_path.exists():
            abort(404)
        return send_file(shared.strip_path)

    @app.get("/s/<token>/download")
    def download_all(token: str):
        shared = download_manager.get(token)
        if shared is None:
            abort(404)
        # Simple MVP: send the strip as the primary downloadable artifact.
        if shared.strip_path.exists():
            return send_file(shared.strip_path, as_attachment=True)
        abort(404)

    return app


class SharingServer:
    """Runs the Flask app in a background thread."""

    def __init__(self, download_manager: DownloadManager, host: str, port: int) -> None:
        self._app = create_app(download_manager)
        self._host = host
        self._port = port
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._thread = threading.Thread(
            target=self._app.run,
            kwargs={"host": self._host, "port": self._port, "debug": False, "use_reloader": False},
            daemon=True,
        )
        self._thread.start()
        logger.info("Sharing server started on %s:%s", self._host, self._port)

    def url_for_token(self, token: str, hostname: str) -> str:
        resolved_host = hostname
        if hostname in ("0.0.0.0", "", None):
            resolved_host = get_local_ip()
        return f"http://{resolved_host}:{self._port}/s/{token}"


def get_local_ip() -> str:
    """Best-effort detection of this machine's LAN IP address.

    Falls back to 127.0.0.1 if no network route is available (e.g. no
    Wi-Fi hotspot configured yet — see README Milestone 7).
    """
    import socket

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(0.5)
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
