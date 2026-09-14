import pytest

from app.core.state import BoothState, InvalidStateTransition, StateMachine


def test_valid_transition_succeeds():
    sm = StateMachine(initial=BoothState.IDLE)
    sm.transition(BoothState.PREVIEW)
    assert sm.state == BoothState.PREVIEW


def test_invalid_transition_raises():
    sm = StateMachine(initial=BoothState.IDLE)
    with pytest.raises(InvalidStateTransition):
        sm.transition(BoothState.CAPTURE)


def test_idle_to_capture_directly_is_invalid():
    sm = StateMachine(initial=BoothState.IDLE)
    assert not sm.can_transition(BoothState.CAPTURE)


def test_listeners_notified_on_change():
    sm = StateMachine(initial=BoothState.IDLE)
    seen = []
    sm.on_change(lambda prev, cur: seen.append((prev, cur)))
    sm.transition(BoothState.PREVIEW)
    assert seen == [(BoothState.IDLE, BoothState.PREVIEW)]
