# Admissibility Proof Spine v0.1

## Status

`DRAFT / INSPECTION SURFACE`

This document defines the robust build target for connecting the existing execution-boundary repositories into one proof spine.

It is not a production claim.
It is not a compliance claim.
It is not an adoption claim.

It is a bounded architecture note for inspection, build planning, and adversarial test design.

---

## Core line

A clean log of an invalid transition is not control.

It is a well-formatted incident.

---

## Purpose

The purpose of the Admissibility Proof Spine is to connect five proof surfaces:

1. Reference-surface validation
2. Authority / state admissibility
3. Execution-boundary refusal
4. Refusal receipt generation
5. Receipt-chain continuity

The target claim is narrow:

> A complete evidence record must not convert an inadmissible transition into an admissible one.

If a transition is inadmissible, the system must refuse before consequence binds.

The refusal must be recorded.

The next decision must be able to read the prior refusal.

---

## Existing repository roles

| Repository | Role |
|---|---|
| `reference-surface-validation` | Tests whether the upstream reference surface is structurally eligible for inspection |
| `commit-gate-core` | Demonstrates path-local execution-boundary refusal before mutation |
| `receipt-chain-core` | Demonstrates temporal receipt chaining and prior-state influence |
| `refusal-receipt-chain` | Demonstrates replayable local ALLOW / DENY / HOLD receipt objects |
| `stop-machine` | Deterministic terminal stop primitive: once RED, nothing runs |

---

## Why `stop-machine` belongs in the spine

`stop-machine` provides the hard stop primitive.

Its existing invariant is:

> GREEN -> AMBER -> RED, and RED is terminal.

This is useful because execution governance needs a state that cannot quietly become permission again.

In this spine:

- `GREEN` means the proposed path may continue to admissibility evaluation.
- `AMBER` means review, rebind, or caution is required.
- `RED` means terminal stop. No execution. No reset. No silent continuation.

RED is not advice.

RED is the mechanical refusal state.

---

## Spine invariant

A proposed transition is not admissible unless all required surfaces hold:

1. The reference surface is structurally eligible.
2. Authority is current, scoped, and unexpired.
3. Current state still supports the proposed transition.
4. Prior receipt-chain state does not require HOLD, DENY, or REBIND_REQUIRED.
5. The execution boundary can refuse before consequence binds.
6. The refusal or authorisation is receipted.
7. The next decision can verify the receipt-chain head.

If any required surface fails:

> verdict = HOLD or DENY

No consequence binds.

---

## Clean Evidence / Invalid Action scenario

This is the primary v0.1 adversarial scenario.

### Given

A proposed action carries clean evidence:

- timestamp
- actor
- declared authority
- scope
- replay data
- structured receipt fields
- complete local log

### But

One admissibility condition fails:

- authority expired
- authority scope does not cover the action
- current state changed before execution
- reference surface is not structurally eligible
- prior receipt requires `REBIND_REQUIRED`
- prior refusal remains unresolved
- chain head cannot be verified

### Expected

The system must not allow the transition to bind.

Expected behaviour:

- verdict is `HOLD` or `DENY`
- `stop-machine` reaches or remains at `RED` for the demonstrated path
- consequence does not bind
- refusal receipt is produced
- chain head changes
- next decision reads the prior refusal
- replay is deterministic
- tampering, removal, or reordering breaks verification

---

## Non-goals

This document does not claim:

- production readiness
- enterprise deployment
- compliance
- certification
- standardisation
- legal sufficiency
- complete path coverage
- physical side-effect prevention
- universal AI governance
- model alignment
- safety of all agentic systems

It defines one bounded build target.

---

## Claim boundary

The Admissibility Proof Spine may claim only:

> On the demonstrated path, clean evidence does not make an inadmissible transition admissible.

It may also claim:

- a structurally invalid reference surface blocks eligibility
- an expired or invalid authority blocks execution
- an unresolved prior refusal can affect the next decision
- a terminal stop state prevents demonstrated continuation
- receipt-chain tampering is detectable
- replay can reproduce the demonstrated verdict

It must not claim:

- that all real-world paths are covered
- that all bypasses are impossible
- that the system is production ready
- that the architecture is legally sufficient
- that the wider field has adopted the pattern

---

## Build plan

### Phase 1 — document the spine

Add this file to `stop-machine`:

```text
docs/admissibility_proof_spine_v0.1.md
```

Purpose:

- define the spine
- identify existing repo roles
- freeze the clean-evidence / invalid-action scenario

### Phase 2 — add stop-state evidence

Add a simple scenario showing:

```text
GREEN -> AMBER -> RED
```

Once RED is reached:

- no reset
- no execution
- no silent continuation

### Phase 3 — connect to receipt-chain-core

Add a scenario in `receipt-chain-core`:

```text
Clean Evidence / Invalid Action
```

Expected:

- evidence object is structurally complete
- admissibility fails
- verdict is HOLD or DENY
- refusal receipt is appended
- next decision reads prior refusal

### Phase 4 — connect to reference-surface-validation

Add a test where:

- reference surface looks complete
- but fails structural eligibility
- execution must not proceed
- receipt records the reason

### Phase 5 — publish proof pack

Create a reviewer-facing proof pack:

```text
docs/ADMISSIBILITY_PROOF_SPINE_PROOF_PACK_v0.1.md
```

It should include:

- bounded claim
- run commands
- expected verdicts
- receipt examples
- failure cases
- claim boundary

---

## Minimal test vector

```json
{
  "scenario_id": "clean_evidence_invalid_action_v0_1",
  "description": "A complete evidence record must not make an inadmissible transition admissible.",
  "input": {
    "actor": "agent.synthetic",
    "action": "send_external_email",
    "declared_authority": {
      "authority_id": "auth.expired.demo",
      "scope": "internal_draft_only",
      "expires_at": "2026-05-17T20:00:00Z"
    },
    "attempted_at": "2026-05-17T21:00:00Z",
    "evidence": {
      "timestamp_present": true,
      "actor_present": true,
      "scope_present": true,
      "replay_data_present": true,
      "receipt_fields_complete": true
    },
    "prior_chain_state": {
      "chain_head_verified": true,
      "prior_verdict": "REBIND_REQUIRED",
      "rebind_resolved": false
    }
  },
  "expected": {
    "verdict": "HOLD",
    "consequence_bound": false,
    "stop_state": "RED",
    "receipt_written": true,
    "next_decision_reads_prior_refusal": true
  },
  "claim_boundary": {
    "does_not_prove_production_readiness": true,
    "does_not_prove_compliance": true,
    "does_not_prove_universal_path_coverage": true
  }
}
```

---

## Reviewer question

The reviewer should be able to ask:

> Did the system merely record the action, or did it prove the action was refused before consequence attached?

If the answer is only “we have a log”, the spine fails.

If the answer is “the transition was refused, receipted, chained, and replayed”, the demonstrated path passes.

---

## Public language boundary

Allowed public wording:

> A clean log of an invalid transition is not control.

Allowed technical wording:

> Coherent evidence of an inadmissible action is still inadmissible.

Forbidden public wording:

- “This solves AI governance.”
- “This proves production safety.”
- “This is compliance-ready.”
- “This prevents all harmful actions.”
- “The field is converging on this architecture.”
- “This is the standard.”

---

## Stop rule

If the evidence is clean but admissibility fails:

> STOP.

Not describe.

Stop.
