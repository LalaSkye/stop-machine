"""Conformance rules for ALVIANTECH_ENVELOPE v0.1 protocol.

Each rule is a pure function: Envelope -> Optional[Violation].
Deterministic. No side effects. No network calls.

Rules encode:
- EXIT_ENUM_ERRATA v0.1 (frozen msg-0007-R)
- evaluation_policy = FIRST_FAIL (frozen msg-0003)
- R0 structural pre-check
- Blank-field clarification (msg-0007)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, unique
from typing import Callable, List, Optional

from envelope_parser import Envelope


# ---------------------------------------------------------------------------
# Protocol constants (frozen)
# ---------------------------------------------------------------------------

@unique
class Exit(Enum):
    """Canonical RETURN.exit enum per EXIT_ENUM_ERRATA v0.1."""
    ALLOW = "ALLOW"
    HOLD = "HOLD"
    DENY = "DENY"
    SILENCE = "SILENCE"


VALID_AGENTS = frozenset({"HUMAN", "TRINITY", "MORPHEUS"})
VALID_MODES = frozenset({"DESIGN", "EVAL", "EXEC", "REFLECT", "TEST"})
VALID_SCOPES = frozenset({"NON_EXEC", "EXEC_CONFIRMED", "REVIEW_ONLY"})
VALID_EXIT_VALUES = frozenset({e.value for e in Exit})
VALID_OUTPUT_TYPES = frozenset({"ARTEFACT", "DECISION", "QUESTION", "LOG", "NOTE"})
VALID_OUTPUT_FORMATS = frozenset({"MARKDOWN", "PLAINTEXT", "JSON"})

# Legacy values that are conformance violations after msg-0005-R
LEGACY_EXIT_VALUES = frozenset({"PASS", "FAIL", "DEFER", "ESCALATE"})


# ---------------------------------------------------------------------------
# Violation dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Violation:
    """A single conformance violation found by a rule."""
    code: str
    message: str
    field: str = ""
    severity: str = "ERROR"  # ERROR | WARNING


# ---------------------------------------------------------------------------
# Rule type
# ---------------------------------------------------------------------------

RuleFunc = Callable[[Envelope], Optional[Violation]]


# ---------------------------------------------------------------------------
# R0 structural pre-check rules
# ---------------------------------------------------------------------------

def rule_has_header(env: Envelope) -> Optional[Violation]:
    """Envelope must start with ALVIANTECH_ENVELOPE v0.1."""
    if "ALVIANTECH_ENVELOPE v0.1" not in env.raw[:80]:
        return Violation(
            code="R0_MISSING_HEADER",
            message="Envelope does not begin with ALVIANTECH_ENVELOPE v0.1.",
            field="header",
        )
    return None


def rule_has_msg_id(env: Envelope) -> Optional[Violation]:
    """PORTS.msg_id must be present and non-empty."""
    if not env.msg_id:
        return Violation(
            code="R0_MISSING_MSG_ID",
            message="PORTS.msg_id is missing or empty.",
            field="PORTS.msg_id",
        )
    return None


def rule_has_ts_utc(env: Envelope) -> Optional[Violation]:
    """PORTS.ts_utc must be present."""
    if not env.ts_utc:
        return Violation(
            code="R0_MISSING_TS_UTC",
            message="PORTS.ts_utc is missing or empty.",
            field="PORTS.ts_utc",
        )
    return None


def rule_has_sender(env: Envelope) -> Optional[Violation]:
    """PORTS.from must be present."""
    if not env.sender:
        return Violation(
            code="R0_MISSING_SENDER",
            message="PORTS.from is missing or empty.",
            field="PORTS.from",
        )
    return None


def rule_has_recipient(env: Envelope) -> Optional[Violation]:
    """PORTS.to must be present."""
    if not env.recipient:
        return Violation(
            code="R0_MISSING_RECIPIENT",
            message="PORTS.to is missing or empty.",
            field="PORTS.to",
        )
    return None


def rule_has_mode(env: Envelope) -> Optional[Violation]:
    """PORTS.mode must be present."""
    if not env.mode:
        return Violation(
            code="R0_MISSING_MODE",
            message="PORTS.mode is missing or empty.",
            field="PORTS.mode",
        )
    return None


def rule_has_scope(env: Envelope) -> Optional[Violation]:
    """PORTS.scope must be present."""
    if not env.scope:
        return Violation(
            code="R0_MISSING_SCOPE",
            message="PORTS.scope is missing or empty.",
            field="PORTS.scope",
        )
    return None


def rule_has_goal(env: Envelope) -> Optional[Violation]:
    """BODY.goal must be present."""
    if not env.goal:
        return Violation(
            code="R0_MISSING_GOAL",
            message="BODY.goal is missing or empty.",
            field="BODY.goal",
        )
    return None


def rule_has_return_block(env: Envelope) -> Optional[Violation]:
    """RETURN block must exist (in_reply_to or exit or reasons)."""
    if not env.in_reply_to and not env.exit_code and not env.return_reasons:
        # Check raw text for RETURN: section
        if "RETURN:" not in env.raw:
            return Violation(
                code="R0_MISSING_RETURN",
                message="RETURN block is missing from envelope.",
                field="RETURN",
            )
    return None


# ---------------------------------------------------------------------------
# Enum validation rules
# ---------------------------------------------------------------------------

def rule_valid_sender(env: Envelope) -> Optional[Violation]:
    """PORTS.from must be a registered agent."""
    if env.sender and env.sender not in VALID_AGENTS:
        return Violation(
            code="ENUM_INVALID_SENDER",
            message=f"PORTS.from '{env.sender}' is not a registered agent. "
                    f"Valid: {sorted(VALID_AGENTS)}.",
            field="PORTS.from",
        )
    return None


def rule_valid_recipient(env: Envelope) -> Optional[Violation]:
    """PORTS.to must be a registered agent."""
    if env.recipient and env.recipient not in VALID_AGENTS:
        return Violation(
            code="ENUM_INVALID_RECIPIENT",
            message=f"PORTS.to '{env.recipient}' is not a registered agent. "
                    f"Valid: {sorted(VALID_AGENTS)}.",
            field="PORTS.to",
        )
    return None


def rule_valid_mode(env: Envelope) -> Optional[Violation]:
    """PORTS.mode must be in the allowed set."""
    if env.mode and env.mode not in VALID_MODES:
        return Violation(
            code="ENUM_INVALID_MODE",
            message=f"PORTS.mode '{env.mode}' is not valid. "
                    f"Valid: {sorted(VALID_MODES)}.",
            field="PORTS.mode",
        )
    return None


def rule_valid_scope(env: Envelope) -> Optional[Violation]:
    """PORTS.scope must be in the allowed set."""
    if env.scope and env.scope not in VALID_SCOPES:
        return Violation(
            code="ENUM_INVALID_SCOPE",
            message=f"PORTS.scope '{env.scope}' is not valid. "
                    f"Valid: {sorted(VALID_SCOPES)}.",
            field="PORTS.scope",
        )
    return None


def rule_valid_exit(env: Envelope) -> Optional[Violation]:
    """RETURN.exit must be in canonical enum {ALLOW|HOLD|DENY|SILENCE}.

    Per EXIT_ENUM_ERRATA v0.1: PASS/FAIL/DEFER/ESCALATE are prohibited
    in messages after msg-0005-R.
    """
    if not env.exit_code:
        return None  # Blank exit checked separately
    if env.exit_code in LEGACY_EXIT_VALUES:
        return Violation(
            code="EXIT_ENUM_LEGACY",
            message=f"RETURN.exit '{env.exit_code}' is a legacy value. "
                    f"Per EXIT_ENUM_ERRATA v0.1, use "
                    f"{sorted(VALID_EXIT_VALUES)} only.",
            field="RETURN.exit",
        )
    if env.exit_code not in VALID_EXIT_VALUES:
        return Violation(
            code="EXIT_ENUM_INVALID",
            message=f"RETURN.exit '{env.exit_code}' is not valid. "
                    f"Canonical enum: {sorted(VALID_EXIT_VALUES)}.",
            field="RETURN.exit",
        )
    return None


# ---------------------------------------------------------------------------
# Blank-field clarification (msg-0007)
# ---------------------------------------------------------------------------

def rule_response_must_have_exit(env: Envelope) -> Optional[Violation]:
    """Response envelopes (-R) MUST set RETURN.exit.

    Per msg-0007 blank-field clarification: blank exit is only valid
    in request envelopes, not in responses.
    """
    if env.is_response and not env.exit_code:
        return Violation(
            code="EXIT_BLANK_IN_RESPONSE",
            message="Response envelope has blank RETURN.exit. "
                    "Per msg-0007 clarification, responses MUST set "
                    "exit to one of {ALLOW, HOLD, DENY, SILENCE}.",
            field="RETURN.exit",
        )
    return None


def rule_valid_output_type(env: Envelope) -> Optional[Violation]:
    """output_spec.type must be in the allowed set."""
    if env.output_type and env.output_type not in VALID_OUTPUT_TYPES:
        return Violation(
            code="ENUM_INVALID_OUTPUT_TYPE",
            message=f"output_spec.type '{env.output_type}' is not valid. "
                    f"Valid: {sorted(VALID_OUTPUT_TYPES)}.",
            field="BODY.output_spec.type",
        )
    return None


def rule_valid_output_format(env: Envelope) -> Optional[Violation]:
    """output_spec.format must be in the allowed set."""
    if env.output_format and env.output_format not in VALID_OUTPUT_FORMATS:
        return Violation(
            code="ENUM_INVALID_OUTPUT_FORMAT",
            message=f"output_spec.format '{env.output_format}' is not valid. "
                    f"Valid: {sorted(VALID_OUTPUT_FORMATS)}.",
            field="BODY.output_spec.format",
        )
    return None


# ---------------------------------------------------------------------------
# Policy rules
# ---------------------------------------------------------------------------

def rule_no_self_approve_exec(env: Envelope) -> Optional[Violation]:
    """No agent may self-approve execution (Section 2.5)."""
    if (env.scope == "EXEC_CONFIRMED"
            and env.sender != "HUMAN"
            and env.exit_code == "ALLOW"):
        return Violation(
            code="POLICY_SELF_APPROVE",
            message=f"Agent '{env.sender}' cannot self-approve "
                    f"EXEC_CONFIRMED scope. Only HUMAN may approve.",
            field="PORTS.scope",
            severity="ERROR",
        )
    return None


# ---------------------------------------------------------------------------
# Rule registry
# ---------------------------------------------------------------------------

# Ordered: R0 structural checks first, then enum, then policy.
ALL_RULES: List[RuleFunc] = [
    # R0 structural pre-check
    rule_has_header,
    rule_has_msg_id,
    rule_has_ts_utc,
    rule_has_sender,
    rule_has_recipient,
    rule_has_mode,
    rule_has_scope,
    rule_has_goal,
    rule_has_return_block,
    # Enum validation
    rule_valid_sender,
    rule_valid_recipient,
    rule_valid_mode,
    rule_valid_scope,
    rule_valid_exit,
    rule_valid_output_type,
    rule_valid_output_format,
    # Blank-field / response rules
    rule_response_must_have_exit,
    # Policy rules
    rule_no_self_approve_exec,
]
