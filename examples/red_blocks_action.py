"""One example: wrap one function and refuse to call it when state is RED."""

from collections.abc import Callable

from stop_machine import StopMachine


def run_unless_red(machine: StopMachine, action: Callable[[], None]) -> bool:
    """Call ``action`` unless ``machine`` is RED; report whether it ran."""

    if machine.is_terminal:
        return False
    action()
    return True


def main() -> None:
    machine = StopMachine()
    machine.advance()
    machine.advance()

    calls = []

    def one_action() -> None:
        calls.append("ran")

    ran = run_unless_red(machine, one_action)
    assert ran is False
    assert calls == []
    print("RED: action not run")


if __name__ == "__main__":
    main()
