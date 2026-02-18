"""EnvelopeGate -- deterministic conformance gate for ALVIANTECH_ENVELOPE v0.1.

Evaluates parsed envelopes against the frozen protocol rules.
Supports two evaluation policies:
    - FIRST_FAIL: halt on first violation (default, frozen at msg-0003).
    - ACCUMULATE_ALL: collect all violations (available for diagnostics).

Decision mapping:
    - No violations      -> ALLOW
    - Structural violation  -> DENY
    - Policy violation      -> HOLD
    - Not addressed to gate -> SILENCE

Deterministic. No side effects. No network calls.
"""

from __future__ import annotations

import importlib.util
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


def evaluate(
    envelope: Envelope,
    policy: str = "FIRST_FAIL",
) -> GateResult:
    """Run all conformance rules against an envelope.

    Args:
        envelope: A parsed Envelope object.
        policy: "FIRST_FAIL" (default) or "ACCUMULATE_ALL".

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

    return GateResult(
        msg_id=envelope.msg_id or "(unknown)",
        exit=_classify_exit(violations),
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
