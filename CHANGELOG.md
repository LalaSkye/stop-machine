# Changelog

All notable changes to **stop-machine** will be documented in this file.

---

## [meta-hardening] — 2026-02-24

### Added
- **SECURITY.md**: Security policy documenting threat model, invariants, and reporting
- **docs/runtime-trace.md**: Gate decision flow documentation (incl. SILENCE rephrase)
- **docs/architecture-diagram.md**: Component map and data flow diagram
- **tests/__init__.py**: Test package marker
- **tests/test_invariant_enforcement.py**: Cross-cutting invariant enforcement tests
  - EXIT_ENUM invariants (exact members, VALID_EXIT_VALUES consistency, _classify_exit)
  - StopMachine terminal invariant (GREEN->AMBER->RED, advance/transition_to/reset from RED)
  - Gate boundary invariants (valid->ALLOW, invalid->DENY, legacy PASS->HOLD)

### Changed
- `.github/workflows/ci.yml` — added `python -m pytest tests/ -v` step
- `CHANGELOG.md` — this entry

### Notes
- **No runtime semantic change**. Only docs/tests/security policy/CI wiring.
- No edits to `stop_machine.py`, `gate.py`, `rules.py`, `envelope_parser.py`, or `primitives/*`


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
