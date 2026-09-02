"""Tests for the bounded public guarantee made by stop-machine."""

import pytest

from stop_machine import (
    InvalidTransitionError,
    State,
    StopMachine,
    TerminalStateError,
)


def test_default_state_is_green():
    assert StopMachine().state is State.GREEN


def test_green_advances_to_amber_then_red():
    machine = StopMachine()
    assert machine.advance() is State.AMBER
    assert machine.advance() is State.RED
    assert machine.is_terminal


@pytest.mark.parametrize("operation", ["advance", "transition_to", "reset"])
def test_public_interface_cannot_leave_red(operation):
    machine = StopMachine(State.RED)
    with pytest.raises(TerminalStateError):
        if operation == "advance":
            machine.advance()
        elif operation == "transition_to":
            machine.transition_to(State.GREEN)
        else:
            machine.reset()
    assert machine.state is State.RED


def test_only_immediate_explicit_transition_is_allowed():
    machine = StopMachine(State.GREEN)
    with pytest.raises(InvalidTransitionError):
        machine.transition_to(State.RED)
    assert machine.state is State.GREEN


def test_reset_before_red_returns_to_green():
    machine = StopMachine(State.AMBER)
    assert machine.reset() is State.GREEN


def test_state_property_has_no_public_setter():
    machine = StopMachine()
    with pytest.raises(AttributeError):
        machine.state = State.RED
    assert machine.state is State.GREEN


def test_slots_reject_undeclared_instance_attributes():
    machine = StopMachine()
    with pytest.raises(AttributeError):
        machine.untracked_state = State.RED


def test_in_process_private_poke_still_works_and_is_out_of_scope():
    """In-process code can poke _state; out-of-process tampering is out of scope."""

    machine = StopMachine(State.RED)
    machine._state = State.GREEN
    assert machine.state is State.GREEN


def test_instances_do_not_share_state():
    first = StopMachine()
    second = StopMachine()
    first.advance()
    assert first.state is State.AMBER
    assert second.state is State.GREEN


def test_repr_reports_state():
    assert repr(StopMachine(State.RED)) == "StopMachine(state=RED)"
