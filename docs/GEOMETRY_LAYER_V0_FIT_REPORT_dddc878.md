# Geometry Layer v0 — Build Fit Report

> **Repo:** LalaSkye/stop-machine
> **Commit pin:** dddc878
> **Date:** 2026-02-23
> **Status:** OK TO PROCEED
> **Scope:** NON_EXEC (design + integration check only)

---

## 1. Repo Layout (Actual @ dddc878)

```
stop-machine/
├── .github/workflows/ci.yml
├── examples/                          (5 demo scripts)
├── primitives/
│   ├── ambiguity-detector/            (detector.py, test_detector.py)
│   ├── authority-gate-v0/             (STUB — raises RuntimeError)
│   ├── consistency-tester/            (tester.py, test_tester.py)
│   ├── envelope-gate/                 (gate.py, rules.py, envelope_parser.py, cli.py, tests, conftest)
│   ├── invariant-lock/                (invariant_lock.py, test_invariant_lock.py)
│   ├── no-optimisation-wrapper/       (wrapper.py, test_wrapper.py)
│   └── stop-machine-v0/              (STUB — raises RuntimeError)
├── ALVIANTECH_COMMS_CENTER_v0.1.md
├── CANONICAL.md
├── GATE_LOG_v0.1.md
├── LICENSE (MIT)
├── README.md
├── stop_machine.py
└── test_stop_machine.py
```

**Key facts:**
- Pure Python, no packaging (no pyproject.toml, setup.cfg, requirements.txt)
- Only dependency: pytest (pip install pytest)
- No `__init__.py` anywhere; imports use `importlib.util.spec_from_file_location`
- No existing `docs/`, `analysis/`, or `scripts/` directories
- Two v0 stub folders raise RuntimeError on import; CI drift alarms enforce this

---

## 2. CI Structure (Actual)

Single workflow: `.github/workflows/ci.yml`
- Trigger: push/PR to main
- Matrix: Python 3.10, 3.11, 3.12 on ubuntu-latest
- Steps: checkout, setup-python, pip install pytest, 2 drift alarms (grep), run primitive tests, run root tests
- No artefact uploads; no continue-on-error jobs; everything gating
- CI status: GREEN on main (54 runs, latest passing in 12s)

---

## 3. Runtime Architecture

- `stop_machine.py`: 3-state FSM (GREEN/AMBER/RED), ~80 LOC, zero imports beyond enum
- `envelope-gate`: Most complex primitive (4 source files, 18 rules, ALLOW/HOLD/DENY/SILENCE exit algebra)
- All primitives: pure functions, frozen dataclasses, deterministic, no side effects
- Import pattern: `_load_local()` via importlib; sys.modules collision risk documented in conftest.py

---

## 4. Proposed Slot-In Paths

| Addition | Path | Rationale |
|----------|------|-----------|
| Analysis code | `analysis/` (new top-level) | No collision; not importable by runtime |
| Geometry spec | `docs/geometry_export_spec_v0.1.md` | Establishes docs/ pattern |
| Fit report | `docs/GEOMETRY_LAYER_V0_FIT_REPORT_dddc878.md` | This file |
| Adversarial tests | `primitives/envelope-gate/test_envelope_gate_adversarial.py` | Discovered by existing `pytest primitives -v` |
| Log schema | Defined in docs spec; emitted as JSONL | Separate from existing Markdown gate log |
| CI job | `geometry-analysis` in ci.yml | First non-gating job; first artefact upload |

---

## 5. Conflicts and Resolutions

| Conflict | Resolution |
|----------|------------|
| No docs/ folder exists | Creating it establishes the pattern cleanly |
| Existing Markdown gate log vs JSONL | Geometry logs are entirely separate path + format |
| sys.modules collision risk | Analysis operates on emitted logs only; if must load runtime, use unique module names |
| No continue-on-error precedent | geometry-analysis job will be documented as first non-gating job |
| No artefact upload precedent | Define canonical path in spec before first use |

---

## 6. Risk List

1. **Import collision via _load_local**: Analysis must not use bare module names like "gate" or "rules"
2. **Logging failures changing behaviour**: Emission wrapped in try/except; failure = no log, not altered gate result
3. **CI brittleness**: Missing logs treated as "no data"; geometry job uses continue-on-error
4. **Packaging leak**: No packaging exists currently; if added later, exclude analysis/
5. **Markdown log contamination**: Geometry JSONL uses completely separate path from GATE_LOG_v0.1.md

---

## 7. Absolute Invariants (Must Hold)

- No change to ALLOW/HOLD/DENY/SILENCE exit algebra
- Runtime code never imports from analysis/, docs/, or artifacts/
- Logging is side-effect free; absence of logs changes nothing
- CI geometry job is non-gating (continue-on-error: true)
- Deterministic output: same input = byte-identical JSONL

---

## 8. Verdict

**OK TO PROCEED.** No HOLD conditions triggered.

---

**END — GEOMETRY_LAYER_V0_FIT_REPORT_dddc878**
