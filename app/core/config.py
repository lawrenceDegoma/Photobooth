"""Configuration loading for the photo booth application.

Loads settings from config/config.yaml (or a path supplied via the
PHOTOBOOTH_CONFIG environment variable) into a simple dataclass-backed
structure so the rest of the app never touches raw dicts.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "config.yaml"


@dataclass
class BoothConfig:
    name: str = "Photo Booth"


@dataclass
class SessionConfig:
    photos_per_session: int = 4
    countdown_seconds: int = 3
    delay_between_photos_ms: int = 1000


@dataclass
class CameraConfig:
    resolution_width: int = 4608
    resolution_height: int = 2592
    preview_width: int = 1280
    preview_height: int = 720
    autofocus: bool = True


@dataclass
class DisplayConfig:
    fullscreen: bool = False
    orientation: str = "portrait"
    width: int = 720
    height: int = 1280


@dataclass
class StorageConfig:
    path: str = "photos"
    minimum_free_space_mb: int = 1000


@dataclass
class SharingConfig:
    enabled: bool = True
    hostname: str = "0.0.0.0"
    port: int = 8080


@dataclass
class HardwareConfig:
    physical_button: bool = False
    button_gpio: int = 17


@dataclass
class LoggingConfig:
    path: str = "logs/photobooth.log"
    level: str = "INFO"
    max_bytes: int = 1_000_000
    backup_count: int = 3


@dataclass
class Config:
    booth: BoothConfig = field(default_factory=BoothConfig)
    session: SessionConfig = field(default_factory=SessionConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    sharing: SharingConfig = field(default_factory=SharingConfig)
    hardware: HardwareConfig = field(default_factory=HardwareConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @classmethod
    def load(cls, path: str | Path | None = None) -> "Config":
        config_path = Path(path or os.environ.get("PHOTOBOOTH_CONFIG", DEFAULT_CONFIG_PATH))
        data: dict[str, Any] = {}
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

        return cls(
            booth=BoothConfig(**data.get("booth", {})),
            session=SessionConfig(**data.get("session", {})),
            camera=CameraConfig(**data.get("camera", {})),
            display=DisplayConfig(**data.get("display", {})),
            storage=StorageConfig(**data.get("storage", {})),
            sharing=SharingConfig(**data.get("sharing", {})),
            hardware=HardwareConfig(**data.get("hardware", {})),
            logging=LoggingConfig(**data.get("logging", {})),
        )
