"""Mock camera for development on non-Pi hardware.

Generates synthetic preview frames and "captures" using Pillow so the
entire application can be developed and tested without a Raspberry Pi or
camera module attached.
"""
from __future__ import annotations

import logging
import random
import time
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw

from app.camera.camera_interface import CameraInterface
from app.core.config import CameraConfig
from app.processing.fonts import load_font

logger = logging.getLogger(__name__)

_PALETTE = [
    (240, 128, 128),
    (135, 206, 235),
    (144, 238, 144),
    (255, 218, 185),
    (221, 160, 221),
]


class MockCamera(CameraInterface):
    """A fake camera that draws a colored frame with a timestamp."""

    def __init__(self, config: CameraConfig) -> None:
        self._config = config
        self._running = False
        self._initialized = False

    def initialize(self) -> None:
        self._initialized = True
        logger.info("Mock camera initialized")

    def start_preview(self) -> None:
        self._running = True

    def get_preview_frame(self):
        if not self._running:
            return None
        return self._render_frame(self._config.preview_width, self._config.preview_height)

    def autofocus(self) -> None:
        time.sleep(0.05)

    def capture(self, output_path: str) -> str:
        image = self._render_frame(
            self._config.resolution_width, self._config.resolution_height
        )
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, quality=95)
        logger.info("Mock camera captured photo to %s", output_path)
        return output_path

    def stop_preview(self) -> None:
        self._running = False

    def shutdown(self) -> None:
        self._initialized = False
        self._running = False

    def is_available(self) -> bool:
        return self._initialized

    def _render_frame(self, width: int, height: int) -> Image.Image:
        color = random.choice(_PALETTE)
        image = Image.new("RGB", (width, height), color)
        draw = ImageDraw.Draw(image)
        text = f"MOCK CAMERA\n{datetime.now().strftime('%H:%M:%S')}"
        font = load_font(max(20, width // 20))
        bbox = draw.multiline_textbbox((0, 0), text, font=font, align="center")
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.multiline_text(
            ((width - text_w) / 2, (height - text_h) / 2),
            text,
            fill=(0, 0, 0),
            font=font,
            align="center",
        )
        return image
