"""Generates a traditional vertical photo strip from processed photos."""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw

from app.processing.fonts import load_font
from app.processing.templates import StripTemplate, get_template

logger = logging.getLogger(__name__)


class PhotoStrip:
    def __init__(self, template_name: str = "classic") -> None:
        self._template = get_template(template_name)

    def generate(
        self,
        photo_paths: list[str],
        output_path: str,
        event_name: str = "",
        event_date: datetime | None = None,
    ) -> str:
        t: StripTemplate = self._template
        width = t.photo_width + t.padding * 2
        height = (
            t.padding
            + len(photo_paths) * t.photo_height
            + (len(photo_paths) - 1) * t.spacing
            + t.footer_height
            + t.padding
        )

        strip = Image.new("RGB", (width, height), t.background_color)
        y = t.padding
        for path in photo_paths:
            with Image.open(path) as photo:
                photo = photo.convert("RGB").resize(
                    (t.photo_width, t.photo_height), Image.LANCZOS
                )
                strip.paste(photo, (t.padding, y))
            y += t.photo_height + t.spacing

        draw = ImageDraw.Draw(strip)
        date_str = (event_date or datetime.now()).strftime("%m.%d.%Y")
        footer_text = f"{event_name}\n{date_str}" if event_name else date_str
        font = load_font(36)

        bbox = draw.multiline_textbbox((0, 0), footer_text, font=font, align="center")
        text_w = bbox[2] - bbox[0]
        text_x = (width - text_w) / 2
        text_y = height - t.footer_height - t.padding + (t.footer_height - (bbox[3] - bbox[1])) / 2
        draw.multiline_text(
            (text_x, text_y), footer_text, fill=t.text_color, font=font, align="center"
        )

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        strip.save(output_path, quality=95)
        logger.info("Generated photo strip: %s", output_path)
        return output_path
