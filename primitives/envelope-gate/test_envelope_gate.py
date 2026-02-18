"""Tests for envelope-gate conformance checker.

Covers:
- R0 structural pre-check (green + red paths)
- EXIT_ENUM_ERRATA v0.1 enforcement
- Blank-field clarification (msg-0007)
- FIRST_FAIL evaluation policy
- Policy: no self-approve execution
"""

import importlib.util
import sys
from pathlib import Path

import pytest

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
parse_envelope = _ep.parse_envelope

_ru = _load_local("rules")
Exit = _ru.Exit
Violation = _ru.Violation
rule_has_header = _ru.rule_has_header
rule_has_msg_id = _ru.rule_has_msg_id
rule_has_sender = _ru.rule_has_sender
rule_has_recipient = _ru.rule_has_recipient
rule_has_mode = _ru.rule_has_mode
rule_has_scope = _ru.rule_has_scope
rule_has_goal = _ru.rule_has_goal
rule_valid_sender = _ru.rule_valid_sender
rule_valid_exit = _ru.rule_valid_exit
rule_response_must_have_exit = _ru.rule_response_must_have_exit
rule_no_self_approve_exec = _ru.rule_no_self_approve_exec

_ga = _load_local("gate")
evaluate = _ga.evaluate
GateResult = _ga.GateResult



# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

VALID_ENVELOPE_RAW = """ALVIANTECH_ENVELOPE v0.1
PORTS:
  msg_id: "msg-0008"
  ts_utc: "2026-02-18T11:00:00Z"
  from: HUMAN
  to: TRINITY
  mode: TEST
  scope: NON_EXEC
BODY:
  goal: Test envelope for gate validation.
  inputs:
    - Test input one.
  constraints:
    must:
      - Reply must use correct schema.
    must_not:
      - No external links.
  output_spec:
    type: NOTE
    format: MARKDOWN
  payload: This is a test payload.
RETURN:
  in_reply_to: ""
  exit:
  reason:
    -
  payload:
"""

VALID_RESPONSE_RAW = """ALVIANTECH_ENVELOPE v0.1
PORTS:
  msg_id: "msg-0008-R"
  ts_utc: "2026-02-18T11:05:00Z"
  from: TRINITY
  to: HUMAN
  mode: TEST
  scope: NON_EXEC
BODY:
  goal: Response to test envelope.
  inputs:
    - Responding to msg-0008.
  constraints:
    must:
      - Use correct exit enum.
    must_not:
      - No schema mutation.
  output_spec:
    type: NOTE
    format: MARKDOWN
  payload: Response payload here.
RETURN:
  in_reply_to: "msg-0008"
  exit: ALLOW
  reason:
    - All checks passed.
  payload: Conformance verified.
"""


def _make_envelope(**overrides) -> Envelope:
    """Build an Envelope with sensible defaults, overriding specified fields."""
    defaults = dict(
        raw="ALVIANTECH_ENVELOPE v0.1\nPORTS:\nBODY:\nRETURN:",
        msg_id="msg-0099",
        ts_utc="2026-02-18T12:00:00Z",
        sender="HUMAN",
        recipient="TRINITY",
        mode="TEST",
        scope="NON_EXEC",
        goal="Test goal.",
        inputs=["input"],
        must=["must"],
        must_not=["must_not"],
        output_type="NOTE",
        output_format="MARKDOWN",
        body_payload="payload",
        in_reply_to="",
        exit_code="",
        return_reasons=[],
        return_payload="",
    )
    defaults.update(overrides)
    return Envelope(**defaults)


# ---------------------------------------------------------------------------
# R0 structural pre-check tests
# ---------------------------------------------------------------------------


class TestR0Structural:
    def test_valid_envelope_passes_r0(self):
        env = parse_envelope(VALID_ENVELOPE_RAW)
        result = evaluate(env)
        assert result.exit != "DENY"

    def test_missing_header_is_deny(self):
        bad_raw = VALID_ENVELOPE_RAW.replace(
            "ALVIANTECH_ENVELOPE v0.1", "INVALID_HEADER"
        )
        env = parse_envelope(bad_raw)
        result = evaluate(env)
        assert result.exit == "DENY"
        assert result.violations[0].code == "R0_MISSING_HEADER"

    def test_missing_msg_id(self):
        env = _make_envelope(msg_id="")
        v = rule_has_msg_id(env)
        assert v is not None
        assert v.code == "R0_MISSING_MSG_ID"

    def test_missing_sender(self):
        env = _make_envelope(sender="")
        v = rule_has_sender(env)
        assert v is not None
        assert v.code == "R0_MISSING_SENDER"

    def test_missing_recipient(self):
        env = _make_envelope(recipient="")
        v = rule_has_recipient(env)
        assert v is not None
        assert v.code == "R0_MISSING_RECIPIENT"

    def test_missing_mode(self):
        env = _make_envelope(mode="")
        v = rule_has_mode(env)
        assert v is not None
        assert v.code == "R0_MISSING_MODE"

    def test_missing_scope(self):
        env = _make_envelope(scope="")
        v = rule_has_scope(env)
        assert v is not None
        assert v.code == "R0_MISSING_SCOPE"

    def test_missing_goal(self):
        env = _make_envelope(goal="")
        v = rule_has_goal(env)
        assert v is not None
        assert v.code == "R0_MISSING_GOAL"

    def test_present_fields_pass(self):
        env = _make_envelope()
        assert rule_has_msg_id(env) is None
        assert rule_has_sender(env) is None
        assert rule_has_recipient(env) is None
        assert rule_has_mode(env) is None
        assert rule_has_scope(env) is None
        assert rule_has_goal(env) is None


# ---------------------------------------------------------------------------
# EXIT_ENUM_ERRATA v0.1 tests
# ---------------------------------------------------------------------------


class TestExitEnum:
    def test_allow_is_valid(self):
        env = _make_envelope(exit_code="ALLOW")
        assert rule_valid_exit(env) is None

    def test_hold_is_valid(self):
        env = _make_envelope(exit_code="HOLD")
        assert rule_valid_exit(env) is None

    def test_deny_is_valid(self):
        env = _make_envelope(exit_code="DENY")
        assert rule_valid_exit(env) is None

    def test_silence_is_valid(self):
        env = _make_envelope(exit_code="SILENCE")
        assert rule_valid_exit(env) is None

    def test_pass_is_legacy_violation(self):
        env = _make_envelope(exit_code="PASS")
        v = rule_valid_exit(env)
        assert v is not None
        assert v.code == "EXIT_ENUM_LEGACY"

    def test_fail_is_legacy_violation(self):
        env = _make_envelope(exit_code="FAIL")
        v = rule_valid_exit(env)
        assert v is not None
        assert v.code == "EXIT_ENUM_LEGACY"

    def test_defer_is_legacy_violation(self):
        env = _make_envelope(exit_code="DEFER")
        v = rule_valid_exit(env)
        assert v is not None
        assert v.code == "EXIT_ENUM_LEGACY"

    def test_escalate_is_legacy_violation(self):
        env = _make_envelope(exit_code="ESCALATE")
        v = rule_valid_exit(env)
        assert v is not None
        assert v.code == "EXIT_ENUM_LEGACY"

    def test_random_value_is_invalid(self):
        env = _make_envelope(exit_code="BANANA")
        v = rule_valid_exit(env)
        assert v is not None
        assert v.code == "EXIT_ENUM_INVALID"

    def test_blank_exit_not_flagged_by_enum_rule(self):
        env = _make_envelope(exit_code="")
        assert rule_valid_exit(env) is None


# ---------------------------------------------------------------------------
# Blank-field clarification (msg-0007)
# ---------------------------------------------------------------------------


class TestBlankField:
    def test_blank_exit_in_request_is_ok(self):
        env = _make_envelope(msg_id="msg-0010", exit_code="")
        assert rule_response_must_have_exit(env) is None

    def test_blank_exit_in_response_is_violation(self):
        env = _make_envelope(msg_id="msg-0010-R", exit_code="")
        v = rule_response_must_have_exit(env)
        assert v is not None
        assert v.code == "EXIT_BLANK_IN_RESPONSE"

    def test_response_with_exit_is_ok(self):
        env = _make_envelope(msg_id="msg-0010-R", exit_code="ALLOW")
        assert rule_response_must_have_exit(env) is None


# ---------------------------------------------------------------------------
# FIRST_FAIL evaluation policy
# ---------------------------------------------------------------------------


class TestFirstFail:
    def test_first_fail_halts_on_first_violation(self):
        env = _make_envelope(msg_id="", sender="")
        result = evaluate(env, policy="FIRST_FAIL")
        assert len(result.violations) == 1
        assert result.rules_checked < result.rules_total

    def test_accumulate_all_collects_all(self):
        env = _make_envelope(msg_id="", sender="")
        result = evaluate(env, policy="ACCUMULATE_ALL")
        assert len(result.violations) >= 2
        assert result.rules_checked == result.rules_total


# ---------------------------------------------------------------------------
# Policy: no self-approve execution
# ---------------------------------------------------------------------------


class TestSelfApprove:
    def test_human_can_approve_exec(self):
        env = _make_envelope(
            sender="HUMAN",
            scope="EXEC_CONFIRMED",
            exit_code="ALLOW",
        )
        assert rule_no_self_approve_exec(env) is None

    def test_agent_cannot_self_approve_exec(self):
        env = _make_envelope(
            sender="TRINITY",
            scope="EXEC_CONFIRMED",
            exit_code="ALLOW",
        )
        v = rule_no_self_approve_exec(env)
        assert v is not None
        assert v.code == "POLICY_SELF_APPROVE"

    def test_agent_hold_on_exec_is_ok(self):
        env = _make_envelope(
            sender="TRINITY",
            scope="EXEC_CONFIRMED",
            exit_code="HOLD",
        )
        assert rule_no_self_approve_exec(env) is None


# ---------------------------------------------------------------------------
# Invalid agent tests
# ---------------------------------------------------------------------------


class TestAgentValidation:
    def test_valid_agents_pass(self):
        for agent in ["HUMAN", "TRINITY", "MORPHEUS"]:
            env = _make_envelope(sender=agent)
            assert rule_valid_sender(env) is None

    def test_unknown_agent_fails(self):
        env = _make_envelope(sender="ZIGGY")
        v = rule_valid_sender(env)
        assert v is not None
        assert v.code == "ENUM_INVALID_SENDER"


# ---------------------------------------------------------------------------
# Gate-level integration tests
# ---------------------------------------------------------------------------


class TestGateIntegration:
    def test_valid_request_gets_allow(self):
        env = _make_envelope()
        result = evaluate(env)
        assert result.exit == "ALLOW"
        assert result.passed is True
        assert len(result.violations) == 0

    def test_valid_response_gets_allow(self):
        env = parse_envelope(VALID_RESPONSE_RAW)
        result = evaluate(env)
        assert result.exit == "ALLOW"

    def test_structural_failure_gets_deny(self):
        env = _make_envelope(msg_id="")
        result = evaluate(env)
        assert result.exit == "DENY"

    def test_legacy_exit_gets_hold(self):
        env = _make_envelope(exit_code="PASS")
        result = evaluate(env)
        assert result.exit == "HOLD"

    def test_blank_response_exit_gets_hold(self):
        env = _make_envelope(msg_id="msg-0099-R", exit_code="")
        result = evaluate(env)
        assert result.exit == "HOLD"
