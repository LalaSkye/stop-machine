"""StopMachine -- deterministic finite-state stop controller.

States:  GREEN -> AMBER -> RED
RED is terminal and absorbing: once entered, no event can leave it.
The transition table is the single source of truth.
There is no implicit behaviour.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple


class State(Enum):
    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"


class Event(Enum):
    TICK = "TICK"
    WARN = "WARN"
    STOP = "STOP"
    RESET = "RESET"


# -- Transition table --------------------------------------------------------
# Key:   (current_state, event)
# Value: next_state
# Every (State, Event) pair is listed. Nothing is implicit.

TRANSITIONS: Dict[Tuple[State, Event], State] = {
    # GREEN
    (State.GREEN, Event.TICK):  State.GREEN,
    (State.GREEN, Event.WARN):  State.AMBER,
    (State.GREEN, Event.STOP):  State.RED,
    (State.GREEN, Event.RESET): State.GREEN,
    # AMBER
    (State.AMBER, Event.TICK):  State.AMBER,
    (State.AMBER, Event.WARN):  State.AMBER,
    (State.AMBER, Event.STOP):  State.RED,
    (State.AMBER, Event.RESET): State.GREEN,
    # RED (absorbing)
    (State.RED, Event.TICK):    State.RED,
    (State.RED, Event.WARN):    State.RED,
    (State.RED, Event.STOP):    State.RED,
    (State.RED, Event.RESET):   State.RED,
}


@dataclass
class StopMachine:
    """Finite-state stop controller. Deterministic. No side-effects."""

    _state: State = State.GREEN
    _history: List[Tuple[State, Event, State]] = field(default_factory=list)

    def send(self, event: Event) -> State:
        """Apply *event*, return the new state. Pure lookup -- no branching."""
        prev = self._state
        nxt = TRANSITIONS[(prev, event)]
        self._state = nxt
        self._history.append((prev, event, nxt))
        return nxt

    @property
    def state(self) -> State:
        return self._state

    @property
    def history(self) -> List[Tuple[State, Event, State]]:
        """Immutable copy of transition log."""
        return list(self._history)

    def is_terminal(self) -> bool:
        return self._state is State.RED

    def __repr__(self) -> str:
        return f"StopMachine(state={self._state.value})"
