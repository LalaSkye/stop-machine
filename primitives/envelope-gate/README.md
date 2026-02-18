# EnvelopeGate

A deterministic conformance gate for **ALVIANTECH_ENVELOPE v0.1** protocol messages.

Parses envelopes from the comms-center postbox, validates them against frozen protocol rules, and emits a structured decision: `ALLOW | HOLD | DENY | SILENCE`.

## Invariants (all tested)

| Invariant | Meaning | Tested |
|---|---|---|
| Determinism | Same envelope => same decision, always | Yes |
| FIRST_FAIL | Halts on first violation (frozen msg-0003) | Yes |
| EXIT_ENUM_ERRATA | Enforces {ALLOW, HOLD, DENY, SILENCE} only | Yes |
| Blank-field rule | Response envelopes must set exit (msg-0007) | Yes |
| No self-approve | Agents cannot ALLOW their own EXEC_CONFIRMED | Yes |
| Auditability | Every decision records violations + rule count | Yes |

## Decision mapping

| Condition | Gate exit |
|---|---|
| All rules pass | `ALLOW` |
| R0 structural failure (missing fields) | `DENY` |
| Enum or policy violation | `HOLD` |
| Not addressed to gate | `SILENCE` |

## Files

| File | Purpose |
|---|---|
| `envelope_parser.py` | Parse raw envelope text into structured `Envelope` dataclass |
| `rules.py` | Pure-function conformance rules (R0, enum, policy) |
| `gate.py` | Evaluator: runs rules, classifies exit, returns `GateResult` |
| `test_envelope_gate.py` | Full test suite (30+ tests) |
| `cli.py` | CLI tool: `check` and `log` commands for batch scanning |

## Protocol references

- **EXIT_ENUM_ERRATA v0.1** (frozen msg-0007-R): Canonical exit enum is `{ALLOW, HOLD, DENY, SILENCE}`. Legacy values `PASS/FAIL/DEFER/ESCALATE` are prohibited.
- **evaluation_policy = FIRST_FAIL** (frozen msg-0003): Gate halts on first violation.
- **Blank-field clarification** (msg-0007): Response envelopes (`-R`) must set `RETURN.exit`. Request envelopes may leave it blank.
- **Section 2.5** (frozen): No agent may self-approve `EXEC_CONFIRMED` scope.

## Usage

```python
from envelope_parser import parse_envelope
from gate import evaluate

raw = """ALVIANTECH_ENVELOPE v0.1
PORTS:
  msg_id: "msg-0010"
  ts_utc: "2026-02-18T12:00:00Z"
  from: HUMAN
  to: TRINITY
  mode: TEST
  scope: NON_EXEC
BODY:
  goal: Validate this envelope.
  ...
RETURN:
  in_reply_to: ""
  exit:
  ...
"""

env = parse_envelope(raw)
result = evaluate(env)
print(result.exit)        # ALLOW | HOLD | DENY | SILENCE
print(result.violations)  # [] if ALLOW
```

## CLI

Scan a comms-center file and print a conformance table:

```bash
python primitives/envelope-gate/cli.py check ALVIANTECH_COMMS_CENTER_v0.1.md
```

Scan and append results to the gate log:

```bash
python primitives/envelope-gate/cli.py log ALVIANTECH_COMMS_CENTER_v0.1.md GATE_LOG_v0.1.md
```

Output columns: `msg_id | from | to | exit | violations`

