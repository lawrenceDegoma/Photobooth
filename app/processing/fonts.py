"""Cross-platform font loading helper.

Avoids hardcoding a single font name (e.g. "Arial.ttf") that only exists on
one OS. Prefers a font bundled in assets/fonts/ (so an event can be
customized without touching code), then tries a list of common font
paths/names across macOS, Linux (including Raspberry Pi OS), and finally
falls back to Pillow's built-in bitmap font if none are found.
"""
from __future__ import annotations

from pathlib import Path

from PIL import ImageFont

_ASSETS_FONTS_DIR = Path(__file__).resolve().parents[2] / "assets" / "fonts"

_CANDIDATE_FONTS = [
    "Arial.ttf",
    "DejaVuSans-Bold.ttf",
    "DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def _bundled_font_candidates() -> list[str]:
    if not _ASSETS_FONTS_DIR.is_dir():
        return []
    return [
        str(p)
        for p in sorted(_ASSETS_FONTS_DIR.glob("*.ttf")) + sorted(_ASSETS_FONTS_DIR.glob("*.ttc"))
    ]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for candidate in _bundled_font_candidates() + _CANDIDATE_FONTS:
        try:
            return ImageFont.truetype(candidate, size=size)
        except Exception:
            continue
    return ImageFont.load_default()
