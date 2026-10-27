"""Image processing pipeline applied after capture.

Pipeline: orientation correction -> crop -> resize -> auto brightness ->
autocontrast -> saturation -> sharpening -> optional filter. Original
captures are never modified.
"""
from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps, ImageStat

from app.processing.filters import apply_filter

logger = logging.getLogger(__name__)


class ImageProcessor:
    def __init__(
        self,
        target_size: tuple[int, int] = (1200, 1600),
        auto_brightness: bool = False,
        target_brightness: int = 118,
        max_brightness_gain: float = 1.5,
        saturation: float = 1.0,
        sharpness: float = 1.0,
    ) -> None:
        self._target_size = target_size
        self._auto_brightness = auto_brightness
        self._target_brightness = target_brightness
        self._max_gain = max(1.0, max_brightness_gain)
        self._saturation = saturation
        self._sharpness = sharpness

    def _adjust_brightness(self, img: Image.Image) -> Image.Image:
        mean = ImageStat.Stat(img.convert("L")).mean[0]
        if mean <= 0:
            return img
        gain = self._target_brightness / mean
        gain = min(self._max_gain, max(1.0 / self._max_gain, gain))
        if abs(gain - 1.0) < 0.02:
            return img
        return ImageEnhance.Brightness(img).enhance(gain)

    def process(
        self,
        source_path: str,
        output_path: str,
        filter_name: str | None = None,
    ) -> str:
        with Image.open(source_path) as img:
            img = ImageOps.exif_transpose(img)  # orientation correction
            img = img.convert("RGB")
            img = ImageOps.fit(img, self._target_size, method=Image.LANCZOS)  # crop + resize

            if self._auto_brightness:
                img = self._adjust_brightness(img)
            img = ImageOps.autocontrast(img, cutoff=1)
            if self._saturation != 1.0:
                img = ImageEnhance.Color(img).enhance(self._saturation)
            if self._sharpness != 1.0:
                img = ImageEnhance.Sharpness(img).enhance(self._sharpness)

            if filter_name:
                img = apply_filter(img, filter_name)

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            img.convert("RGB").save(output_path, quality=92)

        logger.info("Processed %s -> %s", source_path, output_path)
        return output_path
