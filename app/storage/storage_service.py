"""StorageService manages the on-disk layout for sessions and photos.

Layout:

    photos/
    └── 2026-09-14/
        └── <session_uuid>/
            ├── originals/
            │   ├── 01.jpg ...
            ├── processed/
            │   ├── 01.jpg ...
            └── strip.jpg

Never overwrites another session's files and monitors free disk space.
"""
from __future__ import annotations

import logging
import shutil
from datetime import datetime
from pathlib import Path

from app.core.config import StorageConfig
from app.session.session import PhotoSession

logger = logging.getLogger(__name__)


class InsufficientStorageError(Exception):
    pass


class StorageService:
    def __init__(self, config: StorageConfig) -> None:
        self._config = config
        self._root = Path(config.path)
        self._root.mkdir(parents=True, exist_ok=True)

    def session_dir(self, session: PhotoSession) -> Path:
        date_str = session.created_at.strftime("%Y-%m-%d")
        path = self._root / date_str / session.id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def originals_dir(self, session: PhotoSession) -> Path:
        path = self.session_dir(session) / "originals"
        path.mkdir(parents=True, exist_ok=True)
        self.check_free_space()
        return path

    def processed_dir(self, session: PhotoSession) -> Path:
        path = self.session_dir(session) / "processed"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def strip_path(self, session: PhotoSession) -> Path:
        return self.session_dir(session) / "strip.jpg"

    def check_free_space(self) -> None:
        usage = shutil.disk_usage(self._root)
        free_mb = usage.free / (1024 * 1024)
        if free_mb < self._config.minimum_free_space_mb:
            logger.error("Low disk space: %.1f MB free", free_mb)
            raise InsufficientStorageError(
                f"Only {free_mb:.1f} MB free, minimum required is "
                f"{self._config.minimum_free_space_mb} MB"
            )

    def free_space_mb(self) -> float:
        usage = shutil.disk_usage(self._root)
        return usage.free / (1024 * 1024)
