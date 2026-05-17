"""Tests for canonical adversarial corpus manifest generation."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.generate_adversarial_corpus_manifest import REQUIRED_COVERAGE

FIXTURE_DIR = Path("tests/fixtures/adversarial_surface_gate")
VALID_VERDICTS = {"ALLOW", "HOLD", "DENY"}
VALID_PRESSURE_CLASSES = {
    "NONE",
    "NEGATION_OVERRIDE",
    "INTERPRETATION_DRIFT",
    "PARADOX_INJECTION",
    "ROTATION_GEOMETRY",
    "MIXED_PRESSURE",
}
VALID_STOP_STATES = {"GREEN", "AMBER", "RED"}


def _load_fixtures() -> list[tuple[str, dict]]:
    fixtures = []
    for path in sorted(FIXTURE_DIR.glob("*.json")):
        fixtures.append((path.name, json.loads(path.read_text(encoding="utf-8"))))
    assert fixtures, f"No fixtures found in {FIXTURE_DIR}"
    return fixtures


def test_every_fixture_has_stable_fixture_id():
    for filename, fixture in _load_fixtures():
        fixture_id = fixture.get("fixture_id")
        assert isinstance(fixture_id, str) and fixture_id.strip(), (
            f"{filename}: fixture_id must be a non-empty string"
        )
        assert fixture_id.startswith("asg_"), (
            f"{filename}: fixture_id should use stable asg_ prefix"
        )


def test_no_duplicate_fixture_id():
    fixture_ids = [fixture["fixture_id"] for _, fixture in _load_fixtures()]
    assert len(fixture_ids) == len(set(fixture_ids))


def test_no_duplicate_filename():
    filenames = [filename for filename, _ in _load_fixtures()]
    assert len(filenames) == len(set(filenames))


def test_expected_verdict_pressure_pairs_are_valid():
    for filename, fixture in _load_fixtures():
        expected = fixture["expected"]
        assert expected["verdict"] in VALID_VERDICTS, filename
        assert expected["pressure_class"] in VALID_PRESSURE_CLASSES, filename
        assert expected["stop_state"] in VALID_STOP_STATES, filename
        assert isinstance(expected["execution_allowed"], bool), filename


def test_required_coverage_is_present():
    present = {
        (fixture["expected"]["verdict"], fixture["expected"]["pressure_class"])
        for _, fixture in _load_fixtures()
    }
    missing = REQUIRED_COVERAGE - present
    assert not missing, f"Missing required coverage: {sorted(missing)}"


def test_allowed_fixtures_do_not_stop():
    for filename, fixture in _load_fixtures():
        expected = fixture["expected"]
        if expected["verdict"] == "ALLOW":
            assert expected["stop_state"] == "GREEN", filename
            assert expected["execution_allowed"] is True, filename


def test_blocked_fixtures_stop_red():
    for filename, fixture in _load_fixtures():
        expected = fixture["expected"]
        if expected["verdict"] in {"HOLD", "DENY"}:
            assert expected["stop_state"] == "RED", filename
            assert expected["execution_allowed"] is False, filename
