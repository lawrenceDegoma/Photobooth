"""Data-driven photo strip templates.

Templates describe layout only (dimensions, spacing, footer text) so new
event styles can be added without touching PhotoStrip generation code.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class StripTemplate:
    name: str
    photo_width: int = 1000
    photo_height: int = 750
    padding: int = 30
    spacing: int = 20
    footer_height: int = 160
    background_color: tuple[int, int, int] = (255, 255, 255)
    text_color: tuple[int, int, int] = (30, 30, 30)


TEMPLATES: dict[str, StripTemplate] = {
    "classic": StripTemplate(name="classic"),
    "wedding": StripTemplate(
        name="wedding", background_color=(250, 245, 240), text_color=(80, 60, 50)
    ),
    "birthday": StripTemplate(
        name="birthday", background_color=(255, 250, 205), text_color=(120, 40, 100)
    ),
    "graduation": StripTemplate(
        name="graduation", background_color=(20, 20, 40), text_color=(255, 215, 0)
    ),
    "holiday": StripTemplate(
        name="holiday", background_color=(245, 250, 245), text_color=(20, 90, 40)
    ),
}


def get_template(name: str) -> StripTemplate:
    return TEMPLATES.get(name, TEMPLATES["classic"])
