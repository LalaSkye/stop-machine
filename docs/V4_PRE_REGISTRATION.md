# V4_PRE_REGISTRATION

**Project:** runtime-commit-gate-demo  
**Status:** PRE-REGISTRATION DRAFT  
**Classification:** PUBLIC-SAFE  
**Date:** 2026-04-25  

---

## 1. Objective

Make the runtime commit gate safer across real platforms without weakening the core invariant.

This document registers the V4 development intent, first target, and falsification criteria before implementation begins. It is not an implementation specification. It does not disclose private keys, internal infrastructure, exploit steps, or bypass-enabling detail.

---

## 2. Core Invariant

> **No valid DecisionRecord → no state mutation.**

This invariant is the governing constraint of the commit gate. All V4 work must preserve it. No V4 change may weaken, loosen, or create exceptions to this rule.

---

## 3. V4 Targets

The following improvement areas have been identified. Each is a proposed extension. None are proven production-ready at time of registration.

| Target | Description | Status |
|--------|-------------|--------|
| External anchor resilience | Graceful behaviour when canonical hash source is unavailable | **First target** |
| Windows file-locking | Correct locking behaviour on Windows platforms | Proposed |
| Recursion depth | Safe handling of deep or cyclic call stacks | Proposed |
| Heuristic specificity | Reduce false positives in gate decision logic | Proposed |

All items marked **Proposed** are design intentions only and are not yet implemented or validated.

---

## 4. First Target

**External anchor resilience.**

The commit gate currently depends on a canonical hash source to validate DecisionRecords before permitting state mutation. V4 addresses what the gate must do when that source is temporarily or permanently unavailable.

---

## 5. Default Decision

If the canonical hash source is unavailable, the system enters **READ-ONLY mode**.

No state mutation is permitted while the anchor status is unknown, corrupted, or unverifiable. This is the only safe default. Silent continuation is not acceptable.

---

## 6. Reason

READ-ONLY is the correct default because:

- It is **safe** — no mutation can corrupt state during degraded operation.
- It is **understandable** — operators know immediately that the system is constrained.
- It is **operator-visible** — a clear degraded-state signal is required and testable.
- It **preserves auditability** — an audit record is created even when mutation is blocked.

Alternatives such as cached fallback or best-effort continuation are not approved for V4 and would require separate falsification criteria before consideration.

---

## 7. First Falsification Test

**Claim under test:**  
If the canonical hash source is unavailable, mutation must be blocked and the operator must receive a clear degraded-state message.

**Test intent (high-level):**  
Simulate anchor unavailability. Attempt a state mutation through the gate. Observe gate response.

No exploit recipe, internal path, credential, or bypass detail is included here. Implementation detail is held in the private test file and must not be reproduced in public-facing documents.

---

## 8. Pass Condition

All four conditions must hold simultaneously:

- No silent continuation
- No state mutation
- Clear operator signal (degraded-state message visible)
- Audit record created

If any condition fails, the test does not pass. Partial credit is not valid.

---

## 9. Fail Condition

> **Any state mutation occurs while anchor status is unavailable, corrupted, or unverifiable.**

A single observed mutation under degraded anchor conditions constitutes a critical failure. The gate must be treated as broken until root cause is identified and all four pass conditions are re-verified.

---

## 10. IP / Disclosure Boundary

This document describes:

- ✅ Governance behaviour
- ✅ Test intent at high level
- ✅ Structural invariants (public-safe)
- ✅ Proposed improvement targets

This document does **not** disclose:

- ❌ Private keys, tokens, credentials, or hashes
- ❌ Internal URLs or machine-specific paths
- ❌ Unpublished business strategy or client names
- ❌ Proprietary implementation detail beyond approved project terms
- ❌ Exploit recipes or bypass-enabling steps
- ❌ Private infrastructure topology

Any item uncertain at review time must be marked `[REDACTED / NEEDS REVIEW]` before publication.

---

*End of V4 pre-registration document.*
