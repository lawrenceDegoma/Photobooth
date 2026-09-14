"""Cross-platform font loading helper.

Avoids hardcoding a single font name (e.g. "Arial.ttf") that only exists on
one OS. Tries a list of common font paths/names across macOS, Linux
(including Raspberry Pi OS), and falls back to Pillow's built-in bitmap
font if none are found.
"""
from __future__ import annotations

from PIL import ImageFont

_CANDIDATE_FONTS = [
    "Arial.ttf",
    "DejaVuSans-Bold.ttf",
    "DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for candidate in _CANDIDATE_FONTS:
        try:
            return ImageFont.truetype(candidate, size=size)
        except Exception:
            continue
    return ImageFont.load_default()
