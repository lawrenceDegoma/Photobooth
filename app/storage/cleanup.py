"""Cleanup utilities for old sessions to reclaim disk space over time."""
from __future__ import annotations

import logging
import shutil
import time
from pathlib import Path

logger = logging.getLogger(__name__)


def remove_sessions_older_than(root: Path, max_age_days: int) -> int:
    """Remove date-directories under root older than max_age_days.

    Returns the number of session directories removed.
    """
    if not root.exists():
        return 0

    cutoff = time.time() - max_age_days * 86400
    removed = 0

    for date_dir in root.iterdir():
        if not date_dir.is_dir():
            continue
        if date_dir.stat().st_mtime < cutoff:
            try:
                shutil.rmtree(date_dir)
                removed += 1
                logger.info("Removed old session directory: %s", date_dir)
            except Exception:
                logger.exception("Failed to remove %s", date_dir)

    return removed
