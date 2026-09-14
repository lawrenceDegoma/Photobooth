import time

import pytest

from app.camera.camera_service import CameraService
from app.camera.mock_camera import MockCamera
from app.core.config import CameraConfig, SessionConfig
from app.core.events import EventBus
from app.core.state import BoothState, StateMachine
from app.session.session_manager import SessionManager


@pytest.fixture
def camera_service():
    config = CameraConfig()
    service = CameraService(config, camera=MockCamera(config))
    service.initialize()
    return service


@pytest.fixture
def state_machine():
    sm = StateMachine(initial=BoothState.PREVIEW)
    return sm


def make_session_manager(tmp_path, camera_service, state_machine, photos_per_session=2, countdown=0):
    events = EventBus()
    config = SessionConfig(
        photos_per_session=photos_per_session,
        countdown_seconds=countdown,
        delay_between_photos_ms=0,
    )
    return SessionManager(
        config=config,
        camera_service=camera_service,
        state_machine=state_machine,
        event_bus=events,
        photo_output_dir_factory=lambda session: tmp_path / session.id,
    ), events


def test_session_creation_has_unique_id(tmp_path, camera_service, state_machine):
    manager, events = make_session_manager(tmp_path, camera_service, state_machine)
    manager.start_session()
    session1 = manager.current_session
    assert session1 is not None
    time.sleep(0.3)

    # session completed -> PROCESSING; walk back through valid states to PREVIEW
    state_machine.transition(BoothState.REVIEW)
    state_machine.transition(BoothState.PREVIEW)
    manager.start_session()
    session2 = manager.current_session
    time.sleep(0.3)

    assert session1.id != session2.id


def test_session_completes_with_correct_photo_count(tmp_path, camera_service, state_machine):
    manager, events = make_session_manager(tmp_path, camera_service, state_machine, photos_per_session=2)
    completed = []
    events.subscribe("session_complete", lambda s: completed.append(s))

    manager.start_session()
    time.sleep(0.5)

    assert len(completed) == 1
    assert len(completed[0].photos) == 2
