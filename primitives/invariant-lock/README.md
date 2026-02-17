# InvariantLock

A minimal integrity primitive: **seal a file's hash, then verify it later**.

## Invariants (all tested)

| Invariant | Meaning | Tested |
|---|---|:--:|
| Determinism | Same bytes => same digest | Yes |
| Tamper detection | Any change flips verify() to False | Yes |
| Replay stability | verify() is stable across repeated calls | Yes |

## Why this matters

You can't govern what you can't *freeze*. This primitive makes "unchanged artefact" a mechanical claim: seal, verify, refuse drift.

## Quickstart

```bash
python -m pytest primitives/invariant-lock -v
```

## Scope

- Not a security system.
- Not a key manager.
- No orchestration logic.
