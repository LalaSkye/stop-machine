#!/usr/bin/env python3
"""Verify adversarial surface gate fixtures and write a deterministic receipt.

Usage:
    python scripts/verify_adversarial_surface_gate.py

Writes:
    tests/adversarial/latest_surface_gate_verification_receipt.json

Claim boundary:
- Does not claim prompt-injection immunity.
- Does not claim semantic completeness.
- Does not claim production readiness.
- Does not claim universal adversarial coverage.

Allowed claim:
On the demonstrated path, adversarial input surfaces are refused or held
before execution, and the fixture corpus can be replayed into a verification
receipt.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Make repo root importable when run from scripts/
sys.path.insert(0, str(Path(__file__).parent.parent))

from adversarial_surface_gate import SurfaceProbe, evaluate_surface, receipt_to_dict

FIXTURE_DIR = Path("tests/fixtures/adversarial_surface_gate")
OUTPUT_PATH = Path("tests/adversarial/latest_surface_gate_verification_receipt.json")


def _load_fixtures() -> list[dict]:
    if not FIXTURE_DIR.exists():
        print(f"ERROR: fixture directory not found: {FIXTURE_DIR}", file=sys.stderr)
        sys.exit(1)
    fixtures = []
    for path in sorted(FIXTURE_DIR.glob("*.json")):
        with path.open(encoding="utf-8") as fh:
            fixtures.append((path.name, json.load(fh)))
    return fixtures


def _build_probe(probe_dict: dict) -> SurfaceProbe:
    return SurfaceProbe(
        text=probe_dict["text"],
        authority_present=probe_dict.get("authority_present", False),
        declared_frame=probe_dict.get("declared_frame", "default"),
        requested_frame=probe_dict.get("requested_frame", "default"),
        allow_interpretation=probe_dict.get("allow_interpretation", False),
        allow_rotation=probe_dict.get("allow_rotation", False),
    )


def main() -> None:
    fixtures = _load_fixtures()
    results = []
    failures = []

    for filename, fixture in fixtures:
        fixture_id = fixture.get("fixture_id", filename)
        expected = fixture["expected"]
        probe = _build_probe(fixture["probe"])
        receipt = evaluate_surface(probe)
        rd = receipt_to_dict(receipt)

        checks = {
            "verdict": rd["verdict"] == expected["verdict"],
            "pressure_class": rd["pressure_class"] == expected["pressure_class"],
            "stop_state": rd["stop_state"] == expected["stop_state"],
            "execution_allowed": rd["execution_allowed"] == expected["execution_allowed"],
        }
        passed = all(checks.values())

        entry = {
            "fixture_id": fixture_id,
            "filename": filename,
            "passed": passed,
            "checks": checks,
            "receipt": rd,
            "expected": expected,
        }
        results.append(entry)
        if not passed:
            failures.append(fixture_id)

    corpus_blob = json.dumps(
        [r["receipt"]["receipt_hash"] for r in results],
        sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    corpus_hash = hashlib.sha256(corpus_blob).hexdigest()

    verification_receipt = {
        "schema_version": "0.2",
        "generator": "scripts/verify_adversarial_surface_gate.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "fixture_dir": str(FIXTURE_DIR),
        "total": len(results),
        "passed": len(results) - len(failures),
        "failed": len(failures),
        "corpus_hash": corpus_hash,
        "claim_boundary": {
            "does_not_claim_prompt_injection_immunity": True,
            "does_not_claim_semantic_completeness": True,
            "does_not_claim_production_readiness": True,
            "does_not_claim_universal_adversarial_coverage": True,
            "allowed_claim": (
                "On the demonstrated path, adversarial input surfaces are refused or held "
                "before execution, and the fixture corpus can be replayed into a verification receipt."
            ),
        },
        "results": results,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as fh:
        json.dump(verification_receipt, fh, indent=2)

    print(f"Receipt written: {OUTPUT_PATH}")
    print(f"Total: {len(results)}  Passed: {len(results) - len(failures)}  Failed: {len(failures)}")
    print(f"Corpus hash: {corpus_hash}")

    if failures:
        print("FAILED fixtures:", failures, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
