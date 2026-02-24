# Runtime Trace: Envelope Gate Decision Flow

This document describes the deterministic decision flow when an envelope
is evaluated by the conformance gate (`primitives/envelope-gate/gate.py`).

## Overview

```
Envelope (raw text)
  -> parse_envelope()       [envelope_parser.py]
  -> Envelope dataclass
  -> evaluate(envelope)     [gate.py]
     -> for rule in ALL_RULES:   [rules.py, 18 rules]
          rule(envelope) -> None | Violation
     -> _classify_exit(violations)
     -> GateResult
```

## Exit Decision Mapping

| Condition | Exit |
|-----------|------|
| No violations | ALLOW |
| Any `R0_*` structural violation | DENY |
| Non-structural violation (enum, policy) | HOLD |
| Envelope not addressed to gate | SILENCE |

**SILENCE** is emitted when the envelope is not relevant to this gate instance.
It is a valid, non-error exit that means the gate has no opinion on the message.
SILENCE does not indicate suppression or censorship; it indicates routing irrelevance.

## Rule Evaluation Order

Rules are evaluated in registry order (`ALL_RULES` list in `rules.py`):

1. **R0 structural pre-checks** (9 rules): header, msg_id, ts_utc, sender,
   recipient, mode, scope, goal, RETURN block
2. **Enum validation** (7 rules): valid sender/recipient agents, valid mode,
   valid scope, valid exit code, valid output type/format
3. **Blank-field clarification** (1 rule): response envelopes must set exit
4. **Policy rules** (1 rule): no self-approve execution

## Evaluation Policies

- **FIRST_FAIL** (default, frozen at msg-0003): halts on first violation
- **ACCUMULATE_ALL**: collects all violations (diagnostic use only)

## GateResult Fields

| Field | Type | Description |
|-------|------|-------------|
| `msg_id` | str | Envelope message ID |
| `exit` | str | ALLOW, HOLD, DENY, or SILENCE |
| `violations` | list | Violation objects found |
| `rules_checked` | int | How many rules were evaluated |
| `rules_total` | int | Total rules in registry |
| `passed` | bool | True if exit == ALLOW |

## Determinism Guarantee

Given the same envelope text, the gate will always produce the same
GateResult. No randomness, no wall-clock reads, no network calls.
The optional Geometry Layer emission hook is best-effort and cannot
alter the exit decision.
