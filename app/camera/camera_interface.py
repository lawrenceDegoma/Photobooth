"""Abstract camera interface.

All camera implementations (real Pi camera, mock camera for development)
must implement this interface. The UI and session manager depend only on
this interface, never on Picamera2 directly.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class CameraInterface(ABC):
    @abstractmethod
    def initialize(self) -> None:
        """Initialize and open the camera."""

    @abstractmethod
    def start_preview(self) -> None:
        """Begin streaming preview frames."""

    @abstractmethod
    def get_preview_frame(self):
        """Return the latest preview frame (e.g. as a PIL Image), or None."""

    @abstractmethod
    def autofocus(self) -> None:
        """Trigger an autofocus cycle, if supported."""

    @abstractmethod
    def capture(self, output_path: str) -> str:
        """Capture a full-resolution photo to output_path. Returns the path."""

    @abstractmethod
    def stop_preview(self) -> None:
        """Stop streaming preview frames."""

    @abstractmethod
    def shutdown(self) -> None:
        """Release all camera resources."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the camera is currently usable."""
