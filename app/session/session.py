"""PhotoSession data model.

Every group of photos taken in one visit to the booth belongs to a
PhotoSession. Session IDs are collision-resistant UUIDs and must never be
sequential, since they may be used in externally accessible share URLs.
"""
from __future__ import annotations

import secrets
import uuid
from dataclasses import dataclass, field
from datetime import datetime


def _generate_share_token() -> str:
    """Generate a random, non-sequential token safe for use in URLs."""
    return secrets.token_urlsafe(8)


@dataclass
class PhotoSession:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: datetime = field(default_factory=datetime.now)
    photos: list[str] = field(default_factory=list)
    processed_photos: list[str] = field(default_factory=list)
    strip_path: str | None = None
    share_token: str = field(default_factory=_generate_share_token)

    def add_photo(self, path: str) -> None:
        self.photos.append(path)

    def add_processed_photo(self, path: str) -> None:
        self.processed_photos.append(path)

    def is_complete(self, photos_per_session: int) -> bool:
        return len(self.photos) >= photos_per_session
