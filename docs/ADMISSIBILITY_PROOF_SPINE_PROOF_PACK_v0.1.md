# Admissibility Proof Spine — Proof Pack v0.1

## Status

`DRAFT / INSPECTION SURFACE`

This pack records the bounded claim, the files involved, the run commands, the expected outputs, the adversarial cases covered, the non-goals, and the claim boundary for v0.1 of the Admissibility Proof Spine.

---

## Bounded claim

A complete evidence record must not convert an inadmissible transition into an admissible one.

On the demonstrated path:

- if any required admissibility surface fails, the verdict is `HOLD` or `DENY`
- the `stop-machine` reaches or remains at `RED`
- `consequence_bound` is `false`
- a refusal receipt is produced
- the next decision can read the prior refusal

A clean log of an invalid transition is not control. It is a well-formatted incident.

---

## Files added

- `admissibility_proof_spine.py` — admissibility evaluator and refusal receipt object
- `examples/admissibility_proof_spine_demo.py` — runnable demonstration
- `test_admissibility_proof_spine.py` — unit tests for the spine
- `docs/admissibility_proof_spine_v0.1.md` — architecture note
- `docs/ADMISSIBILITY_PROOF_SPINE_PROOF_PACK_v0.1.md` — this file
- `tests/fixtures/clean_evidence_invalid_action_v0_1.json` — adversarial fixture

---

## Run commands

```bash
python -m examples.admissibility_proof_spine_demo
pytest test_admissibility_proof_spine.py -v
pytest test_stop_machine.py test_admissibility_proof_spine.py -v
```

---

## Expected outputs

For the demonstrated `Clean Evidence / Invalid Action` scenario:

```
verdict           = HOLD
stop_state        = RED
consequence_bound = false
receipt           = produced
chain_head        = advanced
```

All tests pass under `pytest -v`.

---

## Adversarial cases covered

The v0.1 spine demonstrates that a structurally complete evidence record does not upgrade an inadmissible transition when one of the following holds:

1. Authority has expired.
2. Authority scope does not cover the action.
3. Current state changed before execution.
4. Reference surface is not structurally eligible.
5. Prior receipt requires `REBIND_REQUIRED`.
6. Prior refusal remains unresolved.
7. Receipt chain head cannot be verified.

In each case:

- `verdict` is `HOLD` or `DENY`
- `consequence_bound` is `false`
- `stop_state` is `RED` for the demonstrated path
- a refusal receipt is appended

---

## Non-goals

This proof pack does not claim:

- production readiness
- enterprise deployment
- compliance or certification
- standardisation
- legal sufficiency
- complete path coverage
- physical side-effect prevention
- universal AI governance
- model alignment
- safety of all agentic systems
- field adoption

---

## Claim boundary

The Admissibility Proof Spine v0.1 may claim only:

> On the demonstrated path, clean evidence does not make an inadmissible transition admissible.

It must not claim that all real-world paths are covered, that all bypasses are impossible, or that the architecture is legally sufficient.
