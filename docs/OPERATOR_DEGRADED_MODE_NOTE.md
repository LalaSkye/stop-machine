# OPERATOR_DEGRADED_MODE_NOTE

## 1. Purpose

Explain what operators should understand when the system enters READ-ONLY / degraded mode because the canonical validation source is unavailable or unverifiable.

## 2. What Degraded Mode Means

Degraded mode means the system cannot verify the required decision basis for mutation.

When this condition exists, the system must enter **READ-ONLY mode** and block state mutation.

## 3. Invariant Reminder

> **No valid DecisionRecord → no state mutation.**

This invariant remains in force during normal operation and degraded operation.

## 4. Default Behaviour

If anchor status is unavailable, corrupted, or unverifiable:

- Mutation is blocked
- The system enters **READ-ONLY mode**
- A visible audit signal is created
- Silent continuation is not allowed

## 5. What Operators Can Still Do

Operators may:

- Observe current system state
- Review visible status information
- Review the audit signal
- Escalate for review using approved governance process

## 6. What Operators Must Not Do

Operators must not:

- Assume mutation has occurred
- Treat degraded mode as normal operation
- Override governance behaviour without explicit authority
- Record degraded-state events as successful mutation events

## 7. What the Audit Signal Means

The audit signal indicates that a mutation attempt was blocked because the required validation condition was not met.

It exists to preserve visibility, traceability, and reviewability.

## 8. Escalation Note

If degraded mode persists or appears unexpectedly, operators should escalate through the approved review path.

Any uncertain detail for public release should be marked `[REDACTED / NEEDS REVIEW]`.

## 9. IP / Disclosure Boundary

This document may describe governance behaviour and operator-facing meaning at a high level only.

This document must not include:

- Secrets or credentials
- Infrastructure details
- Internal URLs or machine-specific paths
- Implementation guidance
- Exploit steps
- Bypass-enabling detail
