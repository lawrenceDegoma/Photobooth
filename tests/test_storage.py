from app.core.config import StorageConfig
from app.session.session import PhotoSession
from app.storage.storage_service import InsufficientStorageError, StorageService


def test_session_dir_creates_expected_layout(tmp_path):
    config = StorageConfig(path=str(tmp_path), minimum_free_space_mb=0)
    service = StorageService(config)
    session = PhotoSession()

    session_dir = service.session_dir(session)
    assert session_dir.exists()
    assert session.id in str(session_dir)


def test_originals_and_processed_dirs_do_not_collide(tmp_path):
    config = StorageConfig(path=str(tmp_path), minimum_free_space_mb=0)
    service = StorageService(config)

    session_a = PhotoSession()
    session_b = PhotoSession()

    dir_a = service.originals_dir(session_a)
    dir_b = service.originals_dir(session_b)

    assert dir_a != dir_b


def test_low_disk_space_detection(tmp_path):
    config = StorageConfig(path=str(tmp_path), minimum_free_space_mb=10**9)
    service = StorageService(config)

    try:
        service.check_free_space()
        assert False, "Expected InsufficientStorageError"
    except InsufficientStorageError:
        pass
