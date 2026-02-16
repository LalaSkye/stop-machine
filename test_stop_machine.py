"""Tests for stop_machine.py. Covers every transition."""

import pytest

from stop_machine import (
    InvalidTransitionError,
    State,
    StopMachine,
    TerminalStateError,
)


# --- Initial state ---

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


# --- advance() transitions ---

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


# --- transition_to() valid ---

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


# --- transition_to() invalid ---

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


# --- reset() ---

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
    result = m.reset()
    assert result == State.GREEN
    assert m.state == State.GREEN
    assert not m.is_terminal


def test_reset_then_advance():
    m = StopMachine()
    m.advance()
    m.advance()
    assert m.is_terminal
    m.reset()
    assert m.state == State.GREEN
    m.advance()
    assert m.state == State.AMBER


# --- repr ---

def test_repr_green():
    assert repr(StopMachine(State.GREEN)) == "StopMachine(state=GREEN)"


def test_repr_amber():
    assert repr(StopMachine(State.AMBER)) == "StopMachine(state=AMBER)"


def test_repr_red():
    assert repr(StopMachine(State.RED)) == "StopMachine(state=RED)"


# --- State enum ---

def test_state_values():
    assert State.GREEN.value == "GREEN"
    assert State.AMBER.value == "AMBER"
    assert State.RED.value == "RED"


def test_exactly_three_states():
    assert len(State) == 3


# --- No instance leakage ---

def test_two_machines_are_independent():
    m1 = StopMachine()
    m2 = StopMachine()
    m1.advance()
    assert m1.state == State.AMBER
    assert m2.state == State.GREEN
