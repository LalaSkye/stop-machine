# Security Policy for stop-machine

## Scope

**stop-machine** is a deterministic three-state stop controller (`GREEN -> AMBER -> RED`).
RED is terminal. No network I/O, no external dependencies in core primitives.

This repo also contains the **envelope-gate** conformance primitive
(`primitives/envelope-gate/`), which evaluates structured envelopes against
frozen protocol rules. It is equally deterministic and side-effect-free.

## Threat Model

This project is a **governance primitive**, not a networked service.
The primary risks are:

| Risk | Category |
|------|----------|
| Misconfiguration of EXIT_ENUM or gate mappings | Governance |
| Drift between docs, EXIT_ENUM, and VALID_EXIT_VALUES | Integrity |
| Unauthorised mutation of terminal state (RED) | Safety |
| Truncated or malformed test files passing CI | Build |

This repo does **not** handle authentication, transport security, rate limiting,
or logging. Integrators must add those layers.

## Invariants That Security Depends On

1. **EXIT_ENUM frozen set**: `{ALLOW, HOLD, DENY, SILENCE}` (per EXIT_ENUM_ERRATA v0.1)
2. **VALID_EXIT_VALUES** must be identical to the set of `Exit` enum values
3. **`_classify_exit`** must never emit a value outside that frozen set
4. **RED is terminal**: `advance()`, `transition_to()`, and `reset()` all raise
   `TerminalStateError` when the machine is in RED
5. **18 conformance rules** in `ALL_RULES` are ordered: R0 structural first,
   then enum validation, then policy

## Canonical Pin

Per `CANONICAL.md`:
- `stop_machine@3780882`
- `authority_gate@70ed2c9`

Any commit that changes runtime semantics must update the canonical pin.

## Reporting Vulnerabilities

- **Non-sensitive bugs**: Open a GitHub Issue
- **Security-sensitive issues**: Use the GitHub Security tab
  (Security > Advisories > New draft advisory) or email the maintainer directly

Please include:
- Description of the issue
- Steps to reproduce
- Expected vs actual behaviour
- Which invariant (if any) is violated

## Supported Versions

| Version | Supported |
|---------|----------|
| main (HEAD) | Yes |
| Tagged releases | Yes |
| Forks | No |

## Non-Goals

- No guarantees for external services, LLM integrations, or downstream repos
- No promise of uptime or availability (this is a library, not a service)
- No security review of third-party code that imports this primitive
