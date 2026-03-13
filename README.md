![CI](https://github.com/LalaSkye/stop-machine/actions/workflows/ci.yml/badge.svg)
![Geometry Layer v0](https://img.shields.io/badge/Geometry_Layer-v0_FROZEN-blue)

# stop-machine

A deterministic three-state stop controller.

**This is a halt primitive, not a framework.** It does not contain orchestration logic, agent wrappers, or alignment policy. It makes stopping a mechanical, fail-closed property of the system.

## Why this exists

Stop conditions in most systems are afterthoughts — flags checked late, states that can be bypassed, or halts that leave the system in an undefined state. This primitive makes stopping a first-class structural guarantee: three states, one direction, no reversal. Once the machine reaches RED, it stays there. No configuration can override it, no runtime condition can reset it. If your system needs a provably terminal stop, this is the brick.

## States

```
GREEN -> AMBER -> RED (terminal)
```

RED is terminal. No implicit transitions. No global state. Fail-closed: invalid transitions raise, they do not silently proceed.

## Quickstart

```python
from stop_machine import StopMachine, State

m = StopMachine()          # starts GREEN
m.advance()                # -> AMBER
m.advance()                # -> RED (terminal)
m.advance()                # raises TerminalStateError
```

## Explicit transitions

```python
m = StopMachine()
m.transition_to(State.AMBER)   # ok
m.transition_to(State.GREEN)   # raises InvalidTransitionError
```

## Reset

```python
m = StopMachine(State.RED)
m.reset()                      # -> GREEN
```

## Run tests

```bash
pip install pytest
pytest test_stop_machine.py -v
```

## Constraints

- Deterministic behaviour only
- No global state
- <200 LOC implementation
- All transitions explicit
- RED is terminal
- Fail-closed control: undefined transitions are errors, not silent passes

## Docs

- [Geometry Export Spec v0.1](docs/geometry_export_spec_v0.1.md) — log schema, artefact paths, and determinism rules for Geometry Layer v0 (experimental, analysis-only)


## License

MIT
