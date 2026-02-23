# Changelog

All notable changes to **stop-machine** will be documented in this file.

---

## [geometry-layer-v0] — 2026-02-23

### Added
- **Geometry Layer v0** (log-only, analysis-only instrumentation)
  - Optional JSONL emission from `primitives/envelope-gate/gate.py` via `GEOMETRY_LOG_PATH` env var
  - Emission is OFF by default, best-effort (swallows errors), and cannot alter gate exit decisions
  - Deterministic JSON serialisation (sorted keys, canonical hashing, no wall-clock timestamps)
- **Spec**: `docs/geometry_export_spec_v0.1.md` — defines log schema, artefact paths, and determinism rules (status: FROZEN)
- **Fit report**: `docs/GEOMETRY_LAYER_V0_FIT_REPORT_dddc878.md`
- **CI**: Non-gating `geometry-analysis` job (continue-on-error) with `upload-artifact` wiring
- **CI**: Drift alarm preventing runtime code from importing `analysis/`, `docs/`, `artifacts/`, or `examples/`
- **README**: Geometry Layer v0 FROZEN badge

### Changed
- `primitives/envelope-gate/gate.py` — added emission hook (no change to exit semantics)
- `.github/workflows/ci.yml` — added geometry-analysis job and drift-alarm step

### Fixed
- Nothing

### Notes
- Runtime exit semantics (ALLOW / HOLD / DENY / SILENCE) are unchanged
- No new runtime dependencies introduced
- Geometry artefacts are not yet produced in CI (emission is off by default); this is expected

---

## [v0.1.0] — 2026-02-16

- Initial release: deterministic three-state stop controller
