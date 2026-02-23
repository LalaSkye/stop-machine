"""EnvelopeGate -- deterministic conformance gate for ALVIANTECH_ENVELOPE v0.1.

Evaluates parsed envelopes against the frozen protocol rules.
Supports two evaluation policies:
    - FIRST_FAIL: halt on first violation (default, frozen at msg-0003).
    - ACCUMULATE_ALL: collect all violations (available for diagnostics).

    Decision mapping:
    - No violations      -> ALLOW
    - Structural violation  -> DENY
    - Policy violation     -> HOLD
    - Not addressed to gate -> SILENCE

Deterministic. No side effects. No network calls.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


# ---------------------------------------------------------------------------
# Robust local imports via importlib (avoids sibling gate.py collision)
# ---------------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent


def _load_local(module_name: str):
    """Load a module from this directory by file path."""
    path = _HERE / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


_ep = _load_local("envelope_parser")
Envelope = _ep.Envelope

_ru = _load_local("rules")
ALL_RULES = _ru.ALL_RULES
Exit = _ru.Exit
Violation = _ru.Violation


@dataclass(frozen=True)
class GateResult:
    """Outcome of running an envelope through the conformance gate."""

    msg_id: str
    exit: str  # ALLOW | HOLD | DENY | SILENCE
    violations: List[Violation] = field(default_factory=list)
    rules_checked: int = 0
    rules_total: int = 0

    @property
    def passed(self) -> bool:
        return self.exit == Exit.ALLOW.value


def _classify_exit(violations: List[Violation]) -> str:
    """Map a list of violations to a gate exit decision."""
    if not violations:
        return Exit.ALLOW.value

    # Any R0 structural failure -> DENY (envelope is malformed)
    for v in violations:
        if v.code.startswith("R0_"):
            return Exit.DENY.value

    # Everything else -> HOLD (policy or enum issue, fixable)
    return Exit.HOLD.value


# ---------------------------------------------------------------------------
# Geometry Layer v0 -- optional JSONL emission (best-effort, off by default)
# ---------------------------------------------------------------------------


def _sha256_bytes(b: bytes) -> str:
    """Return hex SHA-256 digest of *b*."""
    return hashlib.sha256(b).hexdigest()


def _canonical_json(obj: dict) -> str:
    """Canonical JSON: sorted keys, compact separators, no ASCII escaping."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _emit_geometry_event(event: dict) -> None:
    """Append one JSONL line to GEOMETRY_LOG_PATH if set; silently no-op otherwise."""
    path = os.environ.get("GEOMETRY_LOG_PATH")
    if not path:
        return
    try:
        line = _canonical_json(event) + "\n"
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(line)
    except Exception:
        return


def evaluate(
    envelope: Envelope,
    policy: str = "FIRST_FAIL",
) -> GateResult:
    """Run all conformance rules against an envelope.

    Args:
        envelope: A parsed Envelope object.
        policy:   "FIRST_FAIL" (default) or "ACCUMULATE_ALL".

    Returns:
        GateResult with exit decision and any violations found.
    """
    violations: List[Violation] = []
    rules_checked = 0

    for rule_fn in ALL_RULES:
        rules_checked += 1
        result = rule_fn(envelope)
        if result is not None:
            violations.append(result)
            if policy == "FIRST_FAIL":
                break

    exit_decision = _classify_exit(violations)
    violation_codes = sorted([v.code for v in violations])

    # -- Geometry Layer v0: optional emission (never throws, never blocks) --
    _emit_geometry_event({
        "schema_version": "0.1",
        "primitive": "envelope-gate",
        "event": "gate_evaluated",
        "envelope_id": envelope.msg_id or None,
        "exit": exit_decision,
        "violations": violation_codes,
        "input_hash": _sha256_bytes(envelope.raw.encode("utf-8")),
        "result_hash": _sha256_bytes(
            _canonical_json({"exit": exit_decision, "violations": violation_codes}).encode("utf-8")
        ),
    })

    return GateResult(
        msg_id=envelope.msg_id or "(unknown)",
        exit=exit_decision,
        violations=violations,
        rules_checked=rules_checked,
        rules_total=len(ALL_RULES),
    )


def evaluate_all(
    envelopes: List[Envelope],
    policy: str = "FIRST_FAIL",
) -> List[GateResult]:
    """Run conformance gate on a list of envelopes."""
    return [evaluate(env, policy=policy) for env in envelopes]
