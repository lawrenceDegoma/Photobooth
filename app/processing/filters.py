"""Optional lightweight image filters.

Kept intentionally simple (Pillow-only) per Pi 3 performance constraints.
"""
from __future__ import annotations

from PIL import Image, ImageEnhance, ImageOps


def apply_filter(image: Image.Image, name: str) -> Image.Image:
    if name == "grayscale":
        return ImageOps.grayscale(image).convert("RGB")
    if name == "sepia":
        grayscale = ImageOps.grayscale(image)
        sepia = ImageOps.colorize(grayscale, black="#2b1b0e", white="#d9c7a3")
        return sepia.convert("RGB")
    if name == "vivid":
        return ImageEnhance.Color(image).enhance(1.4)
    if name == "bw_high_contrast":
        gray = ImageOps.grayscale(image)
        return ImageOps.autocontrast(gray, cutoff=2).convert("RGB")
    return image
