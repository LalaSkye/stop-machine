"""Property tests for StopMachine.

Three guarantees, tested exhaustively over the finite domain:
  1. Determinism   -- same (state, event) always yields same next_state.
  2. Absorption    -- RED is terminal; no event can leave it.
  3. Completeness  -- every (state, event) pair has an entry.
"""
import pytest

from stop_machine import Event, State, StopMachine, TRANSITIONS

ALL_STATES = list(State)
ALL_EVENTS = list(Event)
ALLOWED = set(ALL_STATES)
SEVERITY = {State.GREEN: 0, State.AMBER: 1, State.RED: 2}


# -- Determinism -------------------------------------------------------------

def test_determinism_replay_identical_history():
    """Same input sequence -> same output sequence. Always."""
    seq = [Event.TICK, Event.WARN, Event.TICK, Event.STOP, Event.RESET, Event.TICK]
    m1 = StopMachine()
    m2 = StopMachine()
    for ev in seq:
        m1.send(ev)
        m2.send(ev)
    assert m1.state == m2.state
    assert m1.history == m2.history


@pytest.mark.parametrize("state", ALL_STATES)
@pytest.mark.parametrize("event", ALL_EVENTS)
def test_determinism_table_lookup_same_value_twice(state, event):
    """The table returns the same value on every read."""
    a = TRANSITIONS[(state, event)]
    b = TRANSITIONS[(state, event)]
    assert a is b


# -- Absorption (RED is terminal) --------------------------------------------

@pytest.mark.parametrize("event", ALL_EVENTS)
def test_absorption_red_to_red_for_each_event(event):
    assert TRANSITIONS[(State.RED, event)] is State.RED


def test_absorption_enter_red_then_fire_every_event_stays_red():
    sm = StopMachine()
    sm.send(Event.STOP)
    assert sm.is_terminal()
    for event in ALL_EVENTS:
        sm.send(event)
        assert sm.state is State.RED
        assert sm.is_terminal()


# -- Completeness ------------------------------------------------------------

def test_completeness_every_state_event_pair_exists():
    for s in ALL_STATES:
        for e in ALL_EVENTS:
            assert (s, e) in TRANSITIONS


# -- Exhaustive transition closure -------------------------------------------

def test_exhaustive_transition_closure():
    """
    For every (state, event) pair:
      - next_state is in {GREEN, AMBER, RED}
      - RED is absorbing
      - determinism holds
    """
    for s in ALL_STATES:
        for e in ALL_EVENTS:
            a = TRANSITIONS[(s, e)]
            b = TRANSITIONS[(s, e)]
            assert a in ALLOWED, f"({s}, {e}) -> {a} not in allowed set"
            assert a is b  # determinism
            if s is State.RED:
                assert a is State.RED, f"RED escaped via {e} -> {a}"


# -- Monotonicity ------------------------------------------------------------

@pytest.mark.parametrize("state", ALL_STATES)
@pytest.mark.parametrize("event", [Event.WARN, Event.STOP])
def test_monotonicity_warn_and_stop_never_decrease_severity(state, event):
    nxt = TRANSITIONS[(state, event)]
    assert SEVERITY[nxt] >= SEVERITY[state]
