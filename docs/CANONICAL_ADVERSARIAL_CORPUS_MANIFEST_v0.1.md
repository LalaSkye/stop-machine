# Canonical Adversarial Corpus Manifest v0.1

## Status

`DRAFT / INSPECTION SURFACE`

This document declares the canonical adversarial fixture corpus for `Adversarial Surface Gate v0.2`.

It is a manifest of the declared test surface, not a claim of universal adversarial coverage.

---

## Bounded claim

The declared fixture corpus is stable, replayable, hashed, and represented by a canonical manifest.

This means the current adversarial corpus can be inspected for:

- fixture identity
- expected verdict
- expected pressure class
- expected stop state
- expected execution permission
- fixture content hash
- corpus hash

---

## Declared fixtures

| Fixture file | Fixture ID | Expected verdict | Expected pressure class | Expected stop state | Expected execution allowed |
|---|---|---:|---:|---:|---:|
| `allow_clean_surface.json` | `asg_allow_clean_surface` | `ALLOW` | `NONE` | `GREEN` | `true` |
| `allow_rotation_with_authority.json` | `asg_allow_rotation_with_authority` | `ALLOW` | `NONE` | `GREEN` | `true` |
| `deny_mixed_pressure.json` | `asg_deny_mixed_pressure` | `DENY` | `MIXED_PRESSURE` | `RED` | `false` |
| `deny_negation_override.json` | `asg_deny_negation_override` | `DENY` | `NEGATION_OVERRIDE` | `RED` | `false` |
| `deny_paradox_injection.json` | `asg_deny_paradox_injection` | `DENY` | `PARADOX_INJECTION` | `RED` | `false` |
| `hold_interpretation_drift.json` | `asg_hold_interpretation_drift` | `HOLD` | `INTERPRETATION_DRIFT` | `RED` | `false` |
| `hold_rotation_geometry.json` | `asg_hold_rotation_geometry` | `HOLD` | `ROTATION_GEOMETRY` | `RED` | `false` |

---

## Required coverage set

The corpus must contain at least one fixture for each of these expected pairs:

- `ALLOW / NONE`
- `DENY / NEGATION_OVERRIDE`
- `DENY / PARADOX_INJECTION`
- `HOLD / INTERPRETATION_DRIFT`
- `HOLD / ROTATION_GEOMETRY`
- `DENY / MIXED_PRESSURE`

---

## Generated machine manifest

Run:

```bash
python scripts/generate_adversarial_corpus_manifest.py
```

Expected output file:

```text
tests/adversarial/latest_adversarial_corpus_manifest.json
```

The generated manifest includes:

- schema version
- generator
- fixture directory
- fixture count
- per-fixture SHA-256 hashes
- canonical corpus hash
- required coverage check
- claim boundary

---

## CI inspection path

CI must run:

```bash
python scripts/generate_adversarial_corpus_manifest.py
pytest test_adversarial_corpus_manifest.py -v
```

CI must upload:

```text
tests/adversarial/latest_adversarial_corpus_manifest.json
```

---

## Claim boundary

This manifest does not prove:

- universal adversarial coverage
- prompt-injection immunity
- semantic completeness
- production readiness
- compliance
- legal sufficiency
- safety of all agentic systems

It proves only:

> The declared adversarial fixture corpus is stable, replayable, hashed, and represented by a canonical manifest.

---

## Stop rule

If the fixture corpus changes without a regenerated manifest:

> HOLD.

Not infer.

Rebuild the manifest.
