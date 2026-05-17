#!/usr/bin/env python3
"""Generate the canonical adversarial corpus manifest.

Usage:
    python scripts/generate_adversarial_corpus_manifest.py

Writes:
    tests/adversarial/latest_adversarial_corpus_manifest.json

Claim boundary:
This does not prove universal adversarial coverage. It proves only that the
declared fixture corpus is stable, replayable, hashed, and represented by a
canonical manifest.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

FIXTURE_DIR = Path("tests/fixtures/adversarial_surface_gate")
OUTPUT_PATH = Path("tests/adversarial/latest_adversarial_corpus_manifest.json")

REQUIRED_COVERAGE = {
    ("ALLOW", "NONE"),
    ("DENY", "NEGATION_OVERRIDE"),
    ("DENY", "PARADOX_INJECTION"),
    ("HOLD", "INTERPRETATION_DRIFT"),
    ("HOLD", "ROTATION_GEOMETRY"),
    ("DENY", "MIXED_PRESSURE"),
}


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _load_fixture(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    return json.loads(raw.decode("utf-8")), _sha256_bytes(raw)


def main() -> None:
    if not FIXTURE_DIR.exists():
        raise SystemExit(f"Fixture directory not found: {FIXTURE_DIR}")

    fixtures = []
    seen_ids = set()
    seen_files = set()

    for path in sorted(FIXTURE_DIR.glob("*.json")):
        fixture, fixture_hash = _load_fixture(path)
        fixture_id = fixture["fixture_id"]
        expected = fixture["expected"]

        if fixture_id in seen_ids:
            raise SystemExit(f"Duplicate fixture_id: {fixture_id}")
        if path.name in seen_files:
            raise SystemExit(f"Duplicate filename: {path.name}")

        seen_ids.add(fixture_id)
        seen_files.add(path.name)

        fixtures.append(
            {
                "filename": path.name,
                "fixture_id": fixture_id,
                "description": fixture["description"],
                "sha256": fixture_hash,
                "expected": {
                    "verdict": expected["verdict"],
                    "pressure_class": expected["pressure_class"],
                    "stop_state": expected["stop_state"],
                    "execution_allowed": expected["execution_allowed"],
                },
            }
        )

    present_coverage = {
        (item["expected"]["verdict"], item["expected"]["pressure_class"])
        for item in fixtures
    }
    missing_coverage = sorted(
        f"{verdict}/{pressure}" for verdict, pressure in REQUIRED_COVERAGE - present_coverage
    )

    canonical_blob = json.dumps(
        [(item["filename"], item["fixture_id"], item["sha256"]) for item in fixtures],
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    corpus_hash = hashlib.sha256(canonical_blob).hexdigest()

    manifest = {
        "schema_version": "0.1",
        "generator": "scripts/generate_adversarial_corpus_manifest.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "fixture_dir": str(FIXTURE_DIR),
        "fixture_count": len(fixtures),
        "corpus_hash": corpus_hash,
        "required_coverage": sorted(f"{v}/{p}" for v, p in REQUIRED_COVERAGE),
        "missing_coverage": missing_coverage,
        "fixtures": fixtures,
        "claim_boundary": {
            "does_not_prove_universal_adversarial_coverage": True,
            "does_not_prove_prompt_injection_immunity": True,
            "does_not_prove_semantic_completeness": True,
            "does_not_prove_production_readiness": True,
            "allowed_claim": (
                "The declared adversarial fixture corpus is stable, replayable, "
                "hashed, and represented by a canonical manifest."
            ),
        },
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Manifest written: {OUTPUT_PATH}")
    print(f"Fixture count: {len(fixtures)}")
    print(f"Corpus hash: {corpus_hash}")
    if missing_coverage:
        print(f"Missing coverage: {missing_coverage}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
