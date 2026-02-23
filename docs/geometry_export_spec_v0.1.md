# Geometry Export Spec v0.1

> **Repo:** LalaSkye/stop-machine
> **Commit pin:** dddc878
> **Status:** DRAFT
> **Scope:** Analysis-only instrumentation (no runtime semantic change)
> **MCCS dependency:** None

---

## 1. Purpose

Define the log schema, artefact path conventions, and determinism rules
for Geometry Layer v0. This layer emits structured events from the
envelope-gate conformance checker to enable offline transition-graph
reconstruction and optionality analysis.

**This spec covers logging and observability only. It does not change
ALLOW / HOLD / DENY / SILENCE outcomes.**

---

## 2. Artefact Path Convention

```
artifacts/geometry/v0/stop-machine/dddc878/${RUN_ID}/
```

- In CI: `RUN_ID = ${{ github.run_id }}`
- Local runs: `RUN_ID = "local"`

All artefacts within a run are JSON Lines (`.jsonl`) files.

---

## 3. Log Format

- **Format:** JSON Lines (one JSON object per line)
- **Encoding:** UTF-8
- **Key ordering:** Canonical (sorted keys via `json.dumps(sort_keys=True)`)
- **Timestamps:** No wall-clock timestamps. Use monotonic integer counter
  or omit entirely. Analysis scripts may add external timestamps.

---

## 4. Event Schema (v0.1)

Each line in a `.jsonl` file MUST be a valid JSON object conforming to:

```json
{
  "schema_version": "0.1",
  "primitive": "envelope-gate",
  "event": "gate_evaluated",
  "envelope_id": "<string|null>",
  "exit": "ALLOW|HOLD|DENY|SILENCE",
  "violations": ["R0_MISSING_HEADER", "ENUM_INVALID_SENDER"],
  "input_hash": "<sha256 hex digest>",
  "result_hash": "<sha256 hex digest>"
}
```

### Field definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schema_version` | string | yes | Always `"0.1"` for this spec version |
| `primitive` | string | yes | Primitive that emitted the event |
| `event` | string | yes | Event type identifier |
| `envelope_id` | string or null | yes | `msg_id` from the envelope, or null |
| `exit` | string | yes | Gate exit decision (ALLOW/HOLD/DENY/SILENCE) |
| `violations` | array of strings | yes | Violation code identifiers (may be empty) |
| `input_hash` | string | yes | SHA-256 hex digest of canonical envelope raw text |
| `result_hash` | string | yes | SHA-256 hex digest of canonical result fields |

### Hashing rules

- `input_hash`: `sha256(envelope.raw.encode("utf-8")).hexdigest()`
- `result_hash`: `sha256(canonical_result_string.encode("utf-8")).hexdigest()`
  where `canonical_result_string = json.dumps({"exit": exit, "violations": sorted_violations}, sort_keys=True)`

---

## 5. Emission Rules

- Emission is **OFF by default**.
- Enabled only when the environment variable `GEOMETRY_LOG_PATH` is set
  to a writable file path.
- All writes are append-only.
- Emission is wrapped in `try/except Exception: pass`.
- If the path is invalid or the write fails: **do nothing**.
- Absence of logs MUST NOT change gate behaviour.

---

## 6. Determinism Requirements

- Same envelope raw text, same rules, same commit = identical JSONL output.
- No wall-clock time in emitted events.
- Key ordering is canonical (sorted).
- Violation lists are sorted.
- Hashes are computed from canonical representations.
- Replaying the same inputs twice MUST produce byte-identical JSONL.

---

## 7. Transition Graph Reconstruction (Analysis-Only)

Analysis scripts in `analysis/` may reconstruct a transition graph from
collected JSONL events:

- Each `gate_evaluated` event represents a node (state) and edge
  (transition from input to exit decision).
- `|Omega(t)|` (reachable state count) is a candidate measure computed
  offline from the collected graph.
- Interpretation of `|Omega(t)|` is **out of scope for v0**.

---

## 8. Runtime / Non-Runtime Boundary

| Path | Classification | May import from runtime? |
|------|---------------|-------------------------|
| `stop_machine.py` | Runtime | N/A |
| `primitives/**/*.py` | Runtime | N/A |
| `analysis/**` | Non-runtime | Yes (by file path only) |
| `docs/**` | Non-runtime | No |
| `artifacts/**` | Non-runtime | No |
| `examples/**` | Non-runtime | No |

**Runtime code MUST NOT import from analysis/, docs/, or artifacts/.**

If analysis code must load runtime modules, it MUST use file-path-based
loading with unique module names to avoid `sys.modules` collisions:
`module_name = "geom_" + sha256(path)[:12]`

---

## 9. CI Integration

- A `geometry-analysis` CI job runs after tests.
- It MUST use `continue-on-error: true` and `if: always()`.
- It uploads artefacts from `artifacts/geometry/**`.
- It does NOT gate merges.

---

## 10. What This Spec Does NOT Cover

- MCCS API hooks or certification handshake
- Metric branding or wrapper-vs-substrate equivalence
- FOI-specific reporting
- Any change to exit algebra or decision mapping

Those remain downstream and will reference this spec if needed.

---

**END — geometry_export_spec_v0.1**
