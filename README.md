**Boundary:** In-process code can still poke `_state`; out-of-process tampering is out of scope. `__slots__` and a read-only `state` property reduce accidental mutation. They do not make this a vault.

# stop-machine

A deterministic three-state controller for one bounded claim:

> Through the public interface, once the machine reaches RED, it cannot leave RED.

It does not intercept arbitrary effects. The caller must place the check before the function it wants to protect.

## Run the tests

```bash
python -m pip install pytest
python -m pytest -q
```

CI runs the same tests on Python 3.10, 3.11 and 3.12.

## One example

The example wraps one function. When the machine is RED, that function is not called.

```bash
python -m examples.red_blocks_action
```

Expected output:

```text
RED: action not run
```

## Public interface

```python
from stop_machine import State, StopMachine

machine = StopMachine()
machine.advance()                 # GREEN -> AMBER
machine.transition_to(State.RED)  # AMBER -> RED
machine.advance()                 # raises TerminalStateError
```

- `state` is readable and has no public setter.
- `__slots__` prevents undeclared instance attributes.
- `advance()` permits GREEN → AMBER → RED.
- `transition_to()` permits only the immediate next state.
- `reset()` can return GREEN or AMBER to GREEN, but cannot leave RED.

## Claim ceiling

This repository demonstrates only the public-interface behaviour tested here. It does not claim tamper-proofing, process isolation, enforcement against hostile in-process code, production readiness, certification, or universal safety.

## Licence

MIT. See [LICENSE](LICENSE).
