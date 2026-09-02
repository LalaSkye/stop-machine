"""A deterministic three-state stop controller.

The public interface exposes read-only state and explicit transitions.
RED is terminal through that interface. Direct in-process mutation of the
private ``_state`` attribute remains possible and is outside the guarantee.
"""

from enum import Enum, unique


@unique
class State(Enum):
    """The three possible stop states."""

    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"


_TRANSITIONS = {
    State.GREEN: State.AMBER,
    State.AMBER: State.RED,
}


class TerminalStateError(Exception):
    """Raised when a public transition is attempted from RED."""


class InvalidTransitionError(Exception):
    """Raised when a target is not the permitted next state."""


class StopMachine:
    """A small state controller whose public interface cannot leave RED."""

    __slots__ = ("_state",)

    def __init__(self, initial: State = State.GREEN) -> None:
        self._state = initial

    @property
    def state(self) -> State:
        """Return the current state; no public setter is provided."""

        return self._state

    @property
    def is_terminal(self) -> bool:
        """Return whether the current state is RED."""

        return self._state is State.RED

    def advance(self) -> State:
        """Advance GREEN to AMBER or AMBER to RED."""

        if self.is_terminal:
            raise TerminalStateError("Cannot advance: RED is terminal.")
        self._state = _TRANSITIONS[self._state]
        return self._state

    def transition_to(self, target: State) -> State:
        """Move to the permitted next state, or fail explicitly."""

        if self.is_terminal:
            raise TerminalStateError("Cannot transition: RED is terminal.")
        expected = _TRANSITIONS[self._state]
        if target is not expected:
            raise InvalidTransitionError(
                f"Cannot transition from {self._state.value} to "
                f"{target.value}. Expected {expected.value}."
            )
        self._state = target
        return self._state

    def reset(self) -> State:
        """Return GREEN or AMBER to GREEN; RED cannot be reset publicly."""

        if self.is_terminal:
            raise TerminalStateError("Cannot reset: RED is terminal.")
        self._state = State.GREEN
        return self._state

    def __repr__(self) -> str:
        return f"StopMachine(state={self._state.value})"
