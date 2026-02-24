# Architecture Diagram: stop-machine

## Component Map

```
stop-machine/
|
|-- stop_machine.py              # Root primitive: 3-state stop controller
|   State: GREEN -> AMBER -> RED (terminal)
|   Classes: StopMachine, State, TerminalStateError, InvalidTransitionError
|
|-- primitives/
|   |-- envelope-gate/           # Conformance gate primitive
|   |   |-- envelope_parser.py   # Parses raw markdown -> Envelope dataclass
|   |   |-- rules.py             # 18 conformance rules + Exit enum + Violation
|   |   |-- gate.py              # evaluate() -> GateResult (ALLOW|HOLD|DENY|SILENCE)
|   |   |-- cli.py               # CLI entry point
|   |   |-- conftest.py          # pytest isolation for sibling imports
|   |   '-- test_envelope_gate.py
|   |
|   |-- authority-gate-v0/       # Stub (no runtime code)
|   |-- stop-machine-v0/         # Stub (no runtime code)
|   |-- ambiguity-detector/      # Stub
|   |-- consistency-tester/      # Stub
|   |-- invariant-lock/          # Stub
|   '-- no-optimisation-wrapper/ # Stub
|
|-- tests/                       # Cross-cutting invariant tests
|   |-- __init__.py
|   '-- test_invariant_enforcement.py
|
|-- docs/
|   |-- runtime-trace.md         # Gate decision flow documentation
|   |-- architecture-diagram.md  # This file
|   |-- geometry_export_spec_v0.1.md
|   '-- GEOMETRY_LAYER_V0_FIT_REPORT_dddc878.md
|
|-- test_stop_machine.py         # Root-level StopMachine tests
|-- CANONICAL.md                 # Canonical commit pins
|-- CHANGELOG.md
|-- SECURITY.md
|-- GATE_LOG_v0.1.md
|-- README.md
'-- LICENSE
```

## Data Flow

```
                    +-------------------+
  raw markdown ---->| envelope_parser   |----> Envelope
                    +-------------------+         |
                                                  v
                    +-------------------+   +------------+
                    |   rules.py        |<--| gate.py    |
                    | (18 rules,       |   | evaluate() |
                    |  Exit enum,      |   +------------+
                    |  Violation)       |         |
                    +-------------------+         v
                                            GateResult
                                          (exit: ALLOW|HOLD|DENY|SILENCE)
                                                  |
                                                  v
                                          [optional: Geometry Layer
                                           JSONL emission if
                                           GEOMETRY_LOG_PATH set]
```

## Key Invariants

1. **StopMachine**: RED is terminal. No method can transition out of RED.
2. **Exit enum**: Exactly `{ALLOW, HOLD, DENY, SILENCE}`. No other values.
3. **VALID_EXIT_VALUES**: Must equal `{e.value for e in Exit}`.
4. **_classify_exit**: Output is always a member of `VALID_EXIT_VALUES`.
5. **ALL_RULES**: 18 rules, ordered R0 -> enum -> blank-field -> policy.
6. **Determinism**: Same input -> same output. Always.
