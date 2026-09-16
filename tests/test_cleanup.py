"""Tests for app.storage.cleanup, used by PhotoBoothApp.run() to purge old
session directories on startup."""
import os
import time
from pathlib import Path

from app.storage.cleanup import remove_sessions_older_than


def _make_session_dir(root: Path, name: str, age_days: float) -> Path:
    session_dir = root / name
    session_dir.mkdir(parents=True)
    (session_dir / "strip.jpg").write_bytes(b"fake")

    old_time = time.time() - age_days * 86400
    os.utime(session_dir, (old_time, old_time))
    return session_dir


def test_removes_only_directories_older_than_cutoff(tmp_path):
    old_dir = _make_session_dir(tmp_path, "2020-01-01", age_days=60)
    recent_dir = _make_session_dir(tmp_path, "2020-06-01", age_days=1)

    removed = remove_sessions_older_than(tmp_path, max_age_days=30)

    assert removed == 1
    assert not old_dir.exists()
    assert recent_dir.exists()


def test_no_op_when_root_does_not_exist(tmp_path):
    missing_root = tmp_path / "nope"

    removed = remove_sessions_older_than(missing_root, max_age_days=30)

    assert removed == 0


def test_no_op_when_nothing_is_old_enough(tmp_path):
    _make_session_dir(tmp_path, "today", age_days=0)

    removed = remove_sessions_older_than(tmp_path, max_age_days=30)

    assert removed == 0


def test_ignores_non_directory_entries(tmp_path):
    (tmp_path / "stray_file.txt").write_text("not a session dir")

    removed = remove_sessions_older_than(tmp_path, max_age_days=0)

    assert removed == 0
    assert (tmp_path / "stray_file.txt").exists()
