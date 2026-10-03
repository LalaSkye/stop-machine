"""Tests for stop_machine.py. Covers every transition."""

import threading

import pytest

from stop_machine import (
    InvalidTransitionError,
    State,
    StopMachine,
    TerminalStateError,
)


def test_default_initial_state():
    m = StopMachine()
    assert m.state == State.GREEN


def test_custom_initial_state():
    for s in State:
        m = StopMachine(initial=s)
        assert m.state == s


def test_is_terminal_false_for_green():
    assert not StopMachine(State.GREEN).is_terminal


def test_is_terminal_false_for_amber():
    assert not StopMachine(State.AMBER).is_terminal


def test_is_terminal_true_for_red():
    assert StopMachine(State.RED).is_terminal


def test_advance_green_to_amber():
    m = StopMachine(State.GREEN)
    result = m.advance()
    assert result == State.AMBER
    assert m.state == State.AMBER


def test_advance_amber_to_red():
    m = StopMachine(State.AMBER)
    result = m.advance()
    assert result == State.RED
    assert m.state == State.RED


def test_advance_from_red_raises():
    m = StopMachine(State.RED)
    with pytest.raises(TerminalStateError):
        m.advance()


def test_advance_full_sequence():
    m = StopMachine()
    assert m.state == State.GREEN
    m.advance()
    assert m.state == State.AMBER
    m.advance()
    assert m.state == State.RED
    with pytest.raises(TerminalStateError):
        m.advance()


def test_transition_to_green_to_amber():
    m = StopMachine(State.GREEN)
    result = m.transition_to(State.AMBER)
    assert result == State.AMBER
    assert m.state == State.AMBER


def test_transition_to_amber_to_red():
    m = StopMachine(State.AMBER)
    result = m.transition_to(State.RED)
    assert result == State.RED
    assert m.state == State.RED


def test_transition_to_from_red_raises():
    m = StopMachine(State.RED)
    with pytest.raises(TerminalStateError):
        m.transition_to(State.GREEN)


def test_transition_to_green_to_red_raises():
    m = StopMachine(State.GREEN)
    with pytest.raises(InvalidTransitionError):
        m.transition_to(State.RED)


def test_transition_to_green_to_green_raises():
    m = StopMachine(State.GREEN)
    with pytest.raises(InvalidTransitionError):
        m.transition_to(State.GREEN)


def test_transition_to_amber_to_green_raises():
    m = StopMachine(State.AMBER)
    with pytest.raises(InvalidTransitionError):
        m.transition_to(State.GREEN)


def test_transition_to_amber_to_amber_raises():
    m = StopMachine(State.AMBER)
    with pytest.raises(InvalidTransitionError):
        m.transition_to(State.AMBER)


def test_reset_from_green():
    m = StopMachine(State.GREEN)
    result = m.reset()
    assert result == State.GREEN
    assert m.state == State.GREEN


def test_reset_from_amber():
    m = StopMachine(State.AMBER)
    result = m.reset()
    assert result == State.GREEN
    assert m.state == State.GREEN


def test_reset_from_red():
    m = StopMachine(State.RED)
    with pytest.raises(TerminalStateError):
        m.reset()


def test_reset_then_advance():
    m = StopMachine()
    m.advance()
    m.advance()
    assert m.is_terminal
    with pytest.raises(TerminalStateError):
        m.reset()


def test_repr_green():
    assert repr(StopMachine(State.GREEN)) == "StopMachine(state=GREEN)"


def test_repr_amber():
    assert repr(StopMachine(State.AMBER)) == "StopMachine(state=AMBER)"


def test_repr_red():
    assert repr(StopMachine(State.RED)) == "StopMachine(state=RED)"


def test_state_values():
    assert State.GREEN.value == "GREEN"
    assert State.AMBER.value == "AMBER"
    assert State.RED.value == "RED"


def test_exactly_three_states():
    assert len(State) == 3


def test_two_machines_are_independent():
    m1 = StopMachine()
    m2 = StopMachine()
    m1.advance()
    assert m1.state == State.AMBER
    assert m2.state == State.GREEN


def test_advance_reset_race_cannot_leave_red_as_green():
    """Force the historical check/write interleaving without timing statistics."""

    class CoordinatedStopMachine(StopMachine):
        __slots__ = ("red_entered", "green_entered", "red_written")

        def __init__(self) -> None:
            super().__init__(State.AMBER)
            object.__setattr__(self, "red_entered", threading.Event())
            object.__setattr__(self, "green_entered", threading.Event())
            object.__setattr__(self, "red_written", threading.Event())

        def _set(self, nxt: State) -> State:
            if nxt is State.RED:
                self.red_entered.set()
                self.green_entered.wait(timeout=0.5)
                result = super()._set(nxt)
                self.red_written.set()
                return result
            if nxt is State.GREEN:
                self.green_entered.set()
                if self.red_entered.wait(timeout=0.5):
                    self.red_written.wait(timeout=0.5)
                return super()._set(nxt)
            return super()._set(nxt)

    m = CoordinatedStopMachine()
    start = threading.Barrier(3)
    unexpected = []

    def run_advance():
        start.wait()
        try:
            m.advance()
        except Exception as exc:
            unexpected.append(exc)

    def run_reset():
        start.wait()
        try:
            m.reset()
        except TerminalStateError:
            pass
        except Exception as exc:
            unexpected.append(exc)

    advance_thread = threading.Thread(target=run_advance)
    reset_thread = threading.Thread(target=run_reset)
    advance_thread.start()
    reset_thread.start()
    start.wait()

    advance_thread.join(timeout=2)
    reset_thread.join(timeout=2)

    assert not advance_thread.is_alive()
    assert not reset_thread.is_alive()
    assert unexpected == []
    assert m.state in {State.RED, State.AMBER}
    assert m.state is not State.GREEN


def test_polite_state_write_blocked():
    m = StopMachine()
    m.advance()
    m.advance()
    with pytest.raises(AttributeError):
        m._state = State.GREEN
    assert m.state == State.RED


def test_documented_poke_still_works():
    m = StopMachine()
    m.advance()
    m.advance()
    object.__setattr__(m, "_state", State.GREEN)
    assert m.state == State.GREEN
