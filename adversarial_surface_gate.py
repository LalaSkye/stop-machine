"""Adversarial Surface Gate v0.1.

A deterministic pre-admissibility gate for hostile or unstable input surfaces.

The gate blocks four demonstrated pressure classes:

1. Negation override
2. Interpretation drift
3. Paradox injection
4. Rotation geometry pressure

This module does not claim semantic completeness, prompt-injection immunity, or
production safety. It demonstrates a bounded fail-closed primitive: when the
input surface tries to invert, over-interpret, contradict, or rotate the frame
without authority, the demonstrated path returns HOLD or DENY before execution.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any

from stop_machine import StopMachine


class SurfaceVerdict(str, Enum):
    """Verdicts for adversarial surface evaluation."""

    ALLOW = "ALLOW"
    HOLD = "HOLD"
    DENY = "DENY"


class PressureClass(str, Enum):
    """Detected adversarial pressure class."""

    NONE = "NONE"
    NEGATION_OVERRIDE = "NEGATION_OVERRIDE"
    INTERPRETATION_DRIFT = "INTERPRETATION_DRIFT"
    PARADOX_INJECTION = "PARADOX_INJECTION"
    ROTATION_GEOMETRY = "ROTATION_GEOMETRY"
    MIXED_PRESSURE = "MIXED_PRESSURE"


@dataclass(frozen=True)
class SurfaceProbe:
    """Input surface to evaluate before admissibility or execution."""

    text: str
    authority_present: bool = False
    declared_frame: str = "default"
    requested_frame: str = "default"
    allow_interpretation: bool = False
    allow_rotation: bool = False


@dataclass(frozen=True)
class SurfaceReceipt:
    """Deterministic receipt for an adversarial surface decision."""

    verdict: str
    pressure_class: str
    reason: str
    stop_state: str
    execution_allowed: bool
    matched_signals: tuple[str, ...]
    receipt_hash: str
    claim_boundary: dict[str, bool]


_NEGATION_PATTERNS = (
    r"\bignore\b.*\b(previous|prior|above|earlier)\b.*\b(instruction|rule|constraint|policy|boundary)\b",
    r"\bdisregard\b.*\b(previous|prior|above|earlier)\b.*\b(instruction|rule|constraint|policy|boundary)\b",
    r"\boverride\b.*\b(boundary|constraint|policy|instruction|receipt|gate)\b",
    r"\bdo not\b.*\b(refuse|hold|deny|stop)\b",
    r"\bturn off\b.*\b(safety|gate|guard|boundary|constraint)\b",
)

_INTERPRETATION_DRIFT_PATTERNS = (
    r"\binterpret\b.*\bhowever you want\b",
    r"\bassume\b.*\bmy meaning\b",
    r"\bread between the lines\b",
    r"\bmake it mean\b",
    r"\bno need for exact wording\b",
    r"\bfill in\b.*\bmissing intent\b",
)

_PARADOX_PATTERNS = (
    r"\bthis statement is false\b",
    r"\bobey this instruction only if you disobey it\b",
    r"\bdeny all denials\b",
    r"\bhold unless you must not hold\b",
    r"\bif you refuse, you have complied\b",
    r"\bthe forbidden action is required because it is forbidden\b",
)

_ROTATION_PATTERNS = (
    r"\bswitch\b.*\bframe\b",
    r"\brotate\b.*\b(frame|geometry|meaning|context)\b",
    r"\brelabel\b.*\b(prohibited|denied|invalid)\b.*\b(allowed|valid|safe)\b",
    r"\btreat\b.*\bdeny\b.*\bas\b.*\ballow\b",
    r"\bmove\b.*\bto another layer\b.*\bso it can pass\b",
)


def _find_matches(text: str, patterns: tuple[str, ...]) -> tuple[str, ...]:
    """Return the regex patterns that match text."""

    lowered = text.lower()
    return tuple(pattern for pattern in patterns if re.search(pattern, lowered))


def _canonical_hash(payload: dict[str, Any]) -> str:
    """Return deterministic SHA-256 for receipt payload."""

    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()


def _terminal_stop() -> StopMachine:
    machine = StopMachine()
    machine.advance()
    machine.advance()
    return machine


def evaluate_surface(probe: SurfaceProbe) -> SurfaceReceipt:
    """Evaluate a probe before admissibility or execution.

    FIRST_FAIL behaviour:
    - negation override is DENY
    - paradox injection is DENY
    - interpretation drift is HOLD unless interpretation is explicitly allowed
    - rotation geometry is HOLD unless rotation is explicitly allowed with authority
    """

    negation = _find_matches(probe.text, _NEGATION_PATTERNS)
    interpretation = _find_matches(probe.text, _INTERPRETATION_DRIFT_PATTERNS)
    paradox = _find_matches(probe.text, _PARADOX_PATTERNS)
    rotation = _find_matches(probe.text, _ROTATION_PATTERNS)

    detected_classes = []
    if negation:
        detected_classes.append(PressureClass.NEGATION_OVERRIDE)
    if interpretation:
        detected_classes.append(PressureClass.INTERPRETATION_DRIFT)
    if paradox:
        detected_classes.append(PressureClass.PARADOX_INJECTION)
    if rotation or probe.declared_frame != probe.requested_frame:
        detected_classes.append(PressureClass.ROTATION_GEOMETRY)

    verdict = SurfaceVerdict.ALLOW
    pressure_class = PressureClass.NONE
    reason = "surface.admissible"
    matched_signals = negation + interpretation + paradox + rotation

    if len(detected_classes) > 1:
        verdict = SurfaceVerdict.DENY
        pressure_class = PressureClass.MIXED_PRESSURE
        reason = "surface.mixed_adversarial_pressure"
    elif negation:
        verdict = SurfaceVerdict.DENY
        pressure_class = PressureClass.NEGATION_OVERRIDE
        reason = "surface.negation_override"
    elif paradox:
        verdict = SurfaceVerdict.DENY
        pressure_class = PressureClass.PARADOX_INJECTION
        reason = "surface.paradox_injection"
    elif interpretation and not probe.allow_interpretation:
        verdict = SurfaceVerdict.HOLD
        pressure_class = PressureClass.INTERPRETATION_DRIFT
        reason = "surface.interpretation_blocked"
    elif (rotation or probe.declared_frame != probe.requested_frame) and not (
        probe.allow_rotation and probe.authority_present
    ):
        verdict = SurfaceVerdict.HOLD
        pressure_class = PressureClass.ROTATION_GEOMETRY
        reason = "surface.rotation_requires_authority"

    execution_allowed = verdict == SurfaceVerdict.ALLOW
    machine = StopMachine() if execution_allowed else _terminal_stop()

    payload = {
        "verdict": verdict.value,
        "pressure_class": pressure_class.value,
        "reason": reason,
        "stop_state": machine.state.value,
        "execution_allowed": execution_allowed,
        "matched_signals": matched_signals,
        "claim_boundary": {
            "does_not_prove_prompt_injection_immunity": True,
            "does_not_prove_semantic_completeness": True,
            "does_not_prove_production_readiness": True,
        },
    }

    return SurfaceReceipt(**payload, receipt_hash=_canonical_hash(payload))


def receipt_to_dict(receipt: SurfaceReceipt) -> dict[str, Any]:
    """Return JSON-compatible receipt dictionary."""

    return asdict(receipt)
