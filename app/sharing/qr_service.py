"""QR code generation for session share links."""
from __future__ import annotations

import logging
from pathlib import Path

import qrcode

logger = logging.getLogger(__name__)


class QRService:
    def generate(self, url: str, output_path: str) -> str:
        img = qrcode.make(url)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path)
        logger.info("Generated QR code for %s -> %s", url, output_path)
        return output_path
