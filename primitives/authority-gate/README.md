# AuthorityGate

A tiny, deterministic wrapper that makes **execution require explicit authority**.

## Invariants (all tested)

| Invariant | Meaning | Tested |
|---|---|:--:|
| Determinism | Same inputs => same allow/deny + same history | Yes |
| Monotonicity | Higher authority never loses permissions | Yes |
| Auditability | Every call records {required, provided, allowed} | Yes |

## Authority levels

Ordered (weak to strong):

- `NONE`
- `USER_CONFIRMED`
- `OWNER_CONFIRMED`
- `ADMIN_APPROVED`

## Why this matters

Most "governance" documents talk about approval, but runtime systems still execute on vibes.
This primitive forces the missing mechanical step: **no explicit authority, no execution**.

## Quickstart

```bash
python -m pytest primitives/authority-gate -v
```

## Scope

- No policy engine.
- No orchestration logic.
- No opinions.
