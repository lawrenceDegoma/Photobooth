from pathlib import Path

from app.sharing.download_manager import DownloadManager, SharedSession


def test_token_registration_and_retrieval(tmp_path):
    manager = DownloadManager()
    shared = SharedSession(
        session_id="abc123",
        originals_dir=tmp_path / "originals",
        processed_dir=tmp_path / "processed",
        strip_path=tmp_path / "strip.jpg",
    )
    manager.register("token123", shared)

    retrieved = manager.get("token123")
    assert retrieved is not None
    assert retrieved.session_id == "abc123"


def test_invalid_token_returns_none():
    manager = DownloadManager()
    assert manager.get("nonexistent") is None


def test_unregister_removes_session(tmp_path):
    manager = DownloadManager()
    shared = SharedSession(
        session_id="abc123",
        originals_dir=tmp_path,
        processed_dir=tmp_path,
        strip_path=tmp_path / "strip.jpg",
    )
    manager.register("token123", shared)
    manager.unregister("token123")

    assert manager.get("token123") is None
