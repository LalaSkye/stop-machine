[![CI](https://github.com/LalaSkye/stop-machine/actions/workflows/ci.yml/badge.svg)](https://github.com/LalaSkye/stop-machine/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![stdlib only](https://img.shields.io/badge/dependencies-stdlib%20only-brightgreen)](stop_machine.py)
[![Lines of code](https://img.shields.io/badge/%3C200%20LOC-implementation-lightgrey)](stop_machine.py)
[![Geometry Layer v0](https://img.shields.io/badge/Geometry_Layer-v0_FROZEN-blue)](docs/geometry_export_spec_v0.1.md)

# stop-machine

## Try in 30 seconds

```bash
git clone https://github.com/LalaSkye/stop-machine.git
cd stop-machine
python -m examples.basic_stop
```

**Expected output:** Machine refuses the unsafe action and logs a receipt.

**A deterministic three-state stop controller. Once RED, nothing runs.**

## Why This Exists

AI systems need a real stop button, not a suggestion. Stop conditions in most systems are afterthoughts — flags checked late, states that can be bypassed, or halts that leave the system in an undefined residual state.

This primitive makes stopping a mechanical, fail-closed property of the system. Three states. One direction. No reversal. No configuration can override a terminal RED. No runtime condition can reset it. If your system needs a provably terminal stop, this is the brick.

## States

```
  ┌───────┐   advance()   ┌───────┐   advance()   ┌─────────────┐
  │       │  ──────────►  │       │  ──────────►  │             │
  │ GREEN │               │ AMBER │               │  RED        │
  │       │               │       │               │  (terminal) │
  └───────┘               └───────┘               └─────────────┘
                                                         │
                                                  advance() raises
                                                  TerminalStateError
```

RED is terminal. No implicit transitions. No global state. Fail-closed: invalid transitions raise, they do not silently proceed.

## Quick Start

```bash
git clone https://github.com/LalaSkye/stop-machine.git
cd stop-machine
python -c "
from stop_machine import StopMachine, State

m = StopMachine()
print(m.state)        # State.GREEN
m.advance()
print(m.state)        # State.AMBER
m.advance()
print(m.state)        # State.RED
"
```

Expected output:

```
State.GREEN
State.AMBER
State.RED
```

## Usage

### Basic advancement

```python
from stop_machine import StopMachine, State

m = StopMachine()          # starts GREEN
m.advance()                # -> AMBER
m.advance()                # -> RED (terminal)
m.advance()                # raises TerminalStateError
```

### Explicit transitions

```python
m = StopMachine()
m.transition_to(State.AMBER)   # ok
m.transition_to(State.GREEN)   # raises InvalidTransitionError
```

### Reset

```python
m = StopMachine()
m.advance()                        # -> AMBER
m.reset()                          # -> GREEN

m = StopMachine(State.RED)
m.reset()                          # raises TerminalStateError
```

### Checking state before acting

```python
m = StopMachine()

if m.state == State.GREEN:
    # safe to proceed
    do_work()
    m.advance()            # move to AMBER after first signal

if m.state == State.AMBER:
    # proceed with caution
    do_cautious_work()
    m.advance()            # -> RED, terminal
```

## Run Tests

```bash
pytest test_stop_machine.py -v
```

Example output:

```
test_stop_machine.py::test_initial_state PASSED
test_stop_machine.py::test_advance_green_to_amber PASSED
test_stop_machine.py::test_advance_amber_to_red PASSED
test_stop_machine.py::test_terminal_raises PASSED
test_stop_machine.py::test_explicit_transition_ok PASSED
test_stop_machine.py::test_invalid_transition_raises PASSED
test_stop_machine.py::test_reset_from_red PASSED
...
```

## Constraints

- Deterministic behaviour only
- No global state
- < 200 LOC implementation
- All transitions explicit
- RED is terminal
- Fail-closed control: undefined transitions are errors, not silent passes

## Docs

- [Geometry Export Spec v0.1](docs/geometry_export_spec_v0.1.md) — log schema, artefact paths, and determinism rules for Geometry Layer v0 (experimental, analysis-only)

## Part of the Execution Boundary Series

| Repo | Layer | What It Does |
|---|---|---|
| [interpretation-boundary-lab](https://github.com/LalaSkye/interpretation-boundary-lab) | Upstream boundary | 10-rule admissibility gate for interpretations |
| [dual-boundary-admissibility-lab](https://github.com/LalaSkye/dual-boundary-admissibility-lab) | Full corridor | Dual-boundary model with pressure monitoring and C-sector rotation |
| [execution-boundary-lab](https://github.com/LalaSkye/execution-boundary-lab) | Execution boundary | Demonstrates cascading failures without upstream governance |
| [stop-machine](https://github.com/LalaSkye/stop-machine) | Control primitive | Deterministic three-state stop controller |
| [constraint-workshop](https://github.com/LalaSkye/constraint-workshop) | Control primitives | Execution gate, invariant litmus, stop machine |
| [csgr-lab](https://github.com/LalaSkye/csgr-lab) | Measurement | Contracted stability and drift measurement |
| [invariant-lock](https://github.com/LalaSkye/invariant-lock) | Drift prevention | Refuse execution unless version increments |
| [policy-lint](https://github.com/LalaSkye/policy-lint) | Policy validation | Deterministic linter for governance statements |
| [deterministic-lexicon](https://github.com/LalaSkye/deterministic-lexicon) | Vocabulary | Fixed terms, exact matches, no inference |

## License

MIT

---

## Authorship & Rights

All architecture, methods, and system designs in this repository are the original work of **Ricky Dean Jones** unless otherwise stated.
No rights to use, reproduce, or implement are granted without explicit permission beyond the terms of the repository licence.

**Author:** Ricky Dean Jones
**Repository owner:** [LalaSkye](https://github.com/LalaSkye)
**Status:** Active research / architecture work
**Part of:** [Execution Boundary Series](https://github.com/LalaSkye) — TrinityOS / AlvianTech

---

This repository demonstrates deterministic control using standard engineering techniques. No proprietary frameworks or external implementations are used.

