# StopMachine

Deterministic finite-state stop controller.

```
Inputs (events) ──▶ [ StopMachine ] ──▶ Output state

                       GREEN
                        │
                        ▼
                       AMBER
                        │
                        ▼
                       RED   (terminal, absorbing)
```

- **RED is terminal** (cannot be bypassed)
- **Transition table is explicit** (no hidden behaviour)
- **Determinism is tested** (replay stable)

## Invariants (all tested)

| Invariant | Meaning | Tested |
|---|---|:--:|
| Determinism | Same state + same event => same next state; replay is stable | ✅ |
| Absorption | RED is terminal: (RED, *) -> RED | ✅ |
| Completeness | Every (State, Event) pair exists in the table | ✅ |
| Monotonicity | WARN and STOP never decrease severity (GREEN < AMBER < RED) | ✅ |

## Full transition table

| Current | TICK | WARN | STOP | RESET |
|---|---|---|---|---|
| GREEN | GREEN | AMBER | RED | GREEN |
| AMBER | AMBER | AMBER | RED | GREEN |
| RED | RED | RED | RED | RED |

**The table is the implementation. There is no branching logic.**

## Why this matters

In real systems, "optimisation" often means adding behaviour without tightening failure modes. This primitive does the opposite: it makes **stop-rights** explicit, deterministic, and testable.

- You can replay decisions and get identical results.
- You can prove terminal behaviour (absorption) rather than hoping it holds.
- You can inspect the entire behavioural surface area in one table.

## Quickstart

```bash
cd primitives/stop-machine
pip install pytest
pytest test_stop_machine.py -v
```

## Scope

- No orchestration logic.
- No selection logic.
- No opinions.
