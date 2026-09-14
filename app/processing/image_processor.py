"""Image processing pipeline applied after capture.

Pipeline: orientation correction -> crop -> resize -> color adjust ->
optional filter -> template/overlay. Original captures are never modified.
"""
from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image, ImageOps

from app.processing.filters import apply_filter

logger = logging.getLogger(__name__)


class ImageProcessor:
    def __init__(self, target_size: tuple[int, int] = (1200, 1600)) -> None:
        self._target_size = target_size

    def process(
        self,
        source_path: str,
        output_path: str,
        filter_name: str | None = None,
    ) -> str:
        with Image.open(source_path) as img:
            img = ImageOps.exif_transpose(img)  # orientation correction
            img = ImageOps.fit(img, self._target_size, method=Image.LANCZOS)  # crop + resize
            img = ImageOps.autocontrast(img, cutoff=1)  # basic color adjustment

            if filter_name:
                img = apply_filter(img, filter_name)

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            img.convert("RGB").save(output_path, quality=92)

        logger.info("Processed %s -> %s", source_path, output_path)
        return output_path
