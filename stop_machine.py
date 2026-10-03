"""Halt primitive. Polite callers cannot leave RED.

Ceiling: same-process poke via object.__setattr__ still works.
This is not a vault. It is a brake on the public methods.
"""

from enum import Enum, unique
from threading import RLock


@unique
class State(Enum):
    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"


_TRANSITIONS = {
    State.GREEN: State.AMBER,
    State.AMBER: State.RED,
}


class TerminalStateError(Exception):
    pass


class InvalidTransitionError(Exception):
    pass


class StopMachine:
    __slots__ = ("_state", "_lock")

    def __init__(self, initial: State = State.GREEN) -> None:
        object.__setattr__(self, "_state", initial)
        object.__setattr__(self, "_lock", RLock())

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("state only moves through advance, transition_to, reset")

    @property
    def state(self) -> State:
        lock = object.__getattribute__(self, "_lock")
        with lock:
            return object.__getattribute__(self, "_state")

    @property
    def is_terminal(self) -> bool:
        return self.state == State.RED

    def _set(self, nxt: State) -> State:
        object.__setattr__(self, "_state", nxt)
        return nxt

    def advance(self) -> State:
        lock = object.__getattribute__(self, "_lock")
        with lock:
            if self.is_terminal:
                raise TerminalStateError("RED is terminal")
            return self._set(_TRANSITIONS[self.state])

    def transition_to(self, target: State) -> State:
        lock = object.__getattribute__(self, "_lock")
        with lock:
            if self.is_terminal:
                raise TerminalStateError("RED is terminal")
            expected = _TRANSITIONS[self.state]
            if target != expected:
                raise InvalidTransitionError(
                    f"{self.state.value} -> {target.value} not allowed"
                )
            return self._set(target)

    def reset(self) -> State:
        lock = object.__getattribute__(self, "_lock")
        with lock:
            if self.is_terminal:
                raise TerminalStateError("cannot reset RED")
            return self._set(State.GREEN)

    def __repr__(self) -> str:
        return f"StopMachine(state={self.state.value})"
