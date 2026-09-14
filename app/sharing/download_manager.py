"""Tracks share tokens -> session directories for the sharing server.

Tokens are random and non-sequential (see PhotoSession.share_token) so
guessing another guest's session is impractical. No directory listing is
ever exposed; only registered session files can be served.
"""
from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class SharedSession:
    session_id: str
    originals_dir: Path
    processed_dir: Path
    strip_path: Path


class DownloadManager:
    def __init__(self) -> None:
        self._sessions: dict[str, SharedSession] = {}
        self._lock = threading.Lock()

    def register(self, token: str, shared: SharedSession) -> None:
        with self._lock:
            self._sessions[token] = shared
        logger.info("Registered share token for session %s", shared.session_id)

    def get(self, token: str) -> SharedSession | None:
        with self._lock:
            return self._sessions.get(token)

    def unregister(self, token: str) -> None:
        with self._lock:
            self._sessions.pop(token, None)
