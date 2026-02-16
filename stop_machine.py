"""A deterministic three-state stop controller.

States: GREEN -> AMBER -> RED
RED is terminal. No implicit transitions.
"""

from enum import Enum, unique


@unique
class State(Enum):
    """The three possible states of the stop machine."""
    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"


# Explicit transition table. Maps (current_state) -> allowed next state.
# RED has no entry because it is terminal.
_TRANSITIONS = {
    State.GREEN: State.AMBER,
    State.AMBER: State.RED,
}


class TerminalStateError(Exception):
    """Raised when a transition is attempted from a terminal state."""


class InvalidTransitionError(Exception):
    """Raised when a transition targets a state not permitted."""


class StopMachine:
    """A three-state stop controller.

    Starts at a given state (default GREEN).
    Transitions are explicit and deterministic.
    RED is terminal: no further transitions are allowed.
    """

    def __init__(self, initial: State = State.GREEN) -> None:
        self._state = initial

    @property
    def state(self) -> State:
        """Return the current state."""
        return self._state

    @property
    def is_terminal(self) -> bool:
        """Return True if the machine is in a terminal state."""
        return self._state == State.RED

    def advance(self) -> State:
        """Move to the next state in the sequence.

        Raises TerminalStateError if already RED.
        Returns the new state.
        """
        if self.is_terminal:
            raise TerminalStateError(
                f"Cannot advance: {self._state.value} is terminal."
            )
        self._state = _TRANSITIONS[self._state]
        return self._state

    def transition_to(self, target: State) -> State:
        """Transition to a specific target state.

        Only the immediate next state in the sequence is allowed.
        Raises TerminalStateError if already RED.
        Raises InvalidTransitionError if target is not the next state.
        Returns the new state.
        """
        if self.is_terminal:
            raise TerminalStateError(
                f"Cannot transition: {self._state.value} is terminal."
            )
        expected = _TRANSITIONS[self._state]
        if target != expected:
            raise InvalidTransitionError(
                f"Cannot transition from {self._state.value} to "
                f"{target.value}. Expected {expected.value}."
            )
        self._state = target
        return self._state

    def reset(self) -> State:
        """Reset the machine to GREEN.

        Returns the new state (always GREEN).
        """
        self._state = State.GREEN
        return self._state

    def __repr__(self) -> str:
        return f"StopMachine(state={self._state.value})"
