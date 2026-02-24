"""Cross-cutting invariant enforcement tests for stop-machine.

Verifies structural invariants that SECURITY.md depends on:
  1. EXIT_ENUM members and VALID_EXIT_VALUES consistency
  2. StopMachine terminal-state enforcement
  3. Gate boundary: valid envelope -> ALLOW, invalid -> DENY

Scope: read-only against runtime modules. ZERO runtime changes.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Robust imports via importlib (matches repo conventions)
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parent.parent
_GATE_DIR = _ROOT / "primitives" / "envelope-gate"

# Root-level module
from stop_machine import (
    InvalidTransitionError,
    State,
    StopMachine,
    TerminalStateError,
)


def _load_gate_module(module_name: str):
    """Load a module from primitives/envelope-gate by file path."""
    path = _GATE_DIR / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


_ep = _load_gate_module("envelope_parser")
Envelope = _ep.Envelope
parse_envelope = _ep.parse_envelope

_ru = _load_gate_module("rules")
Exit = _ru.Exit
VALID_EXIT_VALUES = _ru.VALID_EXIT_VALUES
ALL_RULES = _ru.ALL_RULES
Violation = _ru.Violation

_ga = _load_gate_module("gate")
evaluate = _ga.evaluate
GateResult = _ga.GateResult
_classify_exit = _ga._classify_exit

# ---------------------------------------------------------------------------
# Canonical frozen set for assertions
# ---------------------------------------------------------------------------
EXPECTED_EXIT_MEMBERS = frozenset({"ALLOW", "HOLD", "DENY", "SILENCE"})

# ===================================================================
# Section 1: EXIT_ENUM Invariants
# ===================================================================

class TestExitEnumInvariants:
    """Exit enum must be exactly {ALLOW, HOLD, DENY, SILENCE}."""

    def test_exit_enum_exact_members(self):
        """Exit enum has exactly four members."""
        actual = frozenset(e.value for e in Exit)
        assert actual == EXPECTED_EXIT_MEMBERS, (
            f"Exit enum drift: expected {EXPECTED_EXIT_MEMBERS}, got {actual}"
        )

    def test_valid_exit_values_matches_enum(self):
        """VALID_EXIT_VALUES must be identical to the set of Exit enum values."""
        enum_values = frozenset(e.value for e in Exit)
        assert VALID_EXIT_VALUES == enum_values, (
            f"VALID_EXIT_VALUES drift: {VALID_EXIT_VALUES} != {enum_values}"
        )

    def test_classify_exit_no_violations_returns_allow(self):
        """_classify_exit with empty violations returns ALLOW."""
        result = _classify_exit([])
        assert result in EXPECTED_EXIT_MEMBERS
        assert result == "ALLOW"

    def test_classify_exit_structural_violation_returns_deny(self):
        """_classify_exit with R0 violation returns DENY."""
        v = Violation(code="R0_MISSING_MSG_ID", message="test", field="test")
        result = _classify_exit([v])
        assert result in EXPECTED_EXIT_MEMBERS
        assert result == "DENY"

    def test_classify_exit_policy_violation_returns_hold(self):
        """_classify_exit with non-R0 violation returns HOLD."""
        v = Violation(code="EXIT_ENUM_LEGACY", message="test", field="test")
        result = _classify_exit([v])
        assert result in EXPECTED_EXIT_MEMBERS
        assert result == "HOLD"

    def test_classify_exit_output_always_in_frozen_set(self):
        """Every _classify_exit output is a member of EXPECTED_EXIT_MEMBERS."""
        test_cases = [
            [],
            [Violation(code="R0_MISSING_HEADER", message="x", field="x")],
            [Violation(code="ENUM_INVALID_MODE", message="x", field="x")],
            [Violation(code="POLICY_SELF_APPROVE", message="x", field="x")],
            [Violation(code="EXIT_ENUM_LEGACY", message="x", field="x")],
        ]
        for violations in test_cases:
            result = _classify_exit(violations)
            assert result in EXPECTED_EXIT_MEMBERS, (
                f"_classify_exit returned '{result}' which is outside "
                f"{EXPECTED_EXIT_MEMBERS} for violations={violations}"
            )

# ===================================================================
# Section 2: StopMachine Terminal Invariant
# ===================================================================

class TestStopMachineTerminalInvariant:
    """RED is terminal: no method can transition out of RED."""

    def test_green_to_amber_to_red_works(self):
        """Normal progression GREEN -> AMBER -> RED succeeds."""
        m = StopMachine(State.GREEN)
        assert m.state == State.GREEN

        m.advance()
        assert m.state == State.AMBER

        m.advance()
        assert m.state == State.RED
        assert m.is_terminal is True

    def test_advance_from_red_raises_terminal_error(self):
        """advance() in RED raises TerminalStateError."""
        m = StopMachine(State.RED)
        with pytest.raises(TerminalStateError):
            m.advance()

    def test_transition_to_from_red_raises_terminal_error(self):
        """transition_to() in RED raises TerminalStateError."""
        m = StopMachine(State.RED)
        with pytest.raises(TerminalStateError):
            m.transition_to(State.GREEN)

    def test_reset_from_red_raises_terminal_error(self):
        """reset() in RED raises TerminalStateError."""
        m = StopMachine(State.RED)
        with pytest.raises(TerminalStateError):
            m.reset()

    def test_red_stays_red_after_failed_advance(self):
        """After a failed advance from RED, state remains RED."""
        m = StopMachine(State.RED)
        with pytest.raises(TerminalStateError):
            m.advance()
        assert m.state == State.RED
        assert m.is_terminal is True

    def test_red_stays_red_after_failed_reset(self):
        """After a failed reset from RED, state remains RED."""
        m = StopMachine(State.RED)
        with pytest.raises(TerminalStateError):
            m.reset()
        assert m.state == State.RED

# ===================================================================
# Section 3: Gate Boundary Invariants
# ===================================================================

# Envelope fixture (i): fully-valid envelope that passes all 18 rules -> ALLOW
# Based on VALID_ENVELOPE_RAW from primitives/envelope-gate/test_envelope_gate.py
# with msg_id and ts changed.
VALID_ENVELOPE_RAW = """ALVIANTECH_ENVELOPE v0.1

PORTS:
  msg_id: "msg-9001"
  ts_utc: "2026-02-24T16:00:00Z"
  from: HUMAN
  to: TRINITY
  mode: TEST
  scope: NON_EXEC

BODY:
  goal: Invariant enforcement test envelope.
  inputs:
    - Test input for invariant verification.
  constraints:
    must:
      - Reply must use correct schema.
    must_not:
      - No external links.
  output_spec:
    type: NOTE
    format: MARKDOWN
  payload: This is a test payload for invariant tests.

RETURN:
  in_reply_to: ""
  exit:
  reason:
    -
  payload:
"""

# Envelope fixture (ii): structurally-invalid envelope (missing msg_id) -> DENY
INVALID_ENVELOPE_RAW = """ALVIANTECH_ENVELOPE v0.1

PORTS:
  msg_id: ""
  ts_utc: "2026-02-24T16:00:00Z"
  from: HUMAN
  to: TRINITY
  mode: TEST
  scope: NON_EXEC

BODY:
  goal: Invalid envelope for testing.
  inputs:
    - Test input.
  constraints:
    must:
      - Must test.
    must_not:
      - No test.
  output_spec:
    type: NOTE
    format: MARKDOWN
  payload: Test payload.

RETURN:
  in_reply_to: ""
  exit:
  reason:
    -
  payload:
"""

# Helper to build Envelope dataclass directly (matches existing test pattern)
def _make_envelope(**overrides) -> Envelope:
    """Build an Envelope with sensible defaults, overriding specified fields."""
    defaults = dict(
        raw="ALVIANTECH_ENVELOPE v0.1\nPORTS:\nBODY:\nRETURN:",
        msg_id="msg-9002",
        ts_utc="2026-02-24T16:00:00Z",
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


def _extract_exit(result: GateResult) -> str:
    """Extract exit deterministically from GateResult."""
    return result.exit


class TestGateBoundaryInvariants:
    """Gate must return correct exits for valid and invalid envelopes."""

    def test_valid_envelope_gets_allow(self):
        """A fully-valid envelope must produce exit == ALLOW."""
        env = _make_envelope()
        result = evaluate(env)
        exit_val = _extract_exit(result)
        assert exit_val in EXPECTED_EXIT_MEMBERS, (
            f"Gate exit '{exit_val}' not in {EXPECTED_EXIT_MEMBERS}"
        )
        assert exit_val == "ALLOW", (
            f"Expected ALLOW for valid envelope, got {exit_val}"
        )

    def test_invalid_envelope_gets_deny(self):
        """A structurally-invalid envelope (missing msg_id) must produce DENY."""
        env = _make_envelope(msg_id="")
        result = evaluate(env)
        exit_val = _extract_exit(result)
        assert exit_val in EXPECTED_EXIT_MEMBERS, (
            f"Gate exit '{exit_val}' not in {EXPECTED_EXIT_MEMBERS}"
        )
        assert exit_val == "DENY", (
            f"Expected DENY for invalid envelope, got {exit_val}"
        )

    def test_legacy_exit_pass_gets_hold(self):
        """Envelope with legacy RETURN.exit PASS produces HOLD."""
        env = _make_envelope(exit_code="PASS")
        result = evaluate(env)
        exit_val = _extract_exit(result)
        assert exit_val in EXPECTED_EXIT_MEMBERS, (
            f"Gate exit '{exit_val}' not in {EXPECTED_EXIT_MEMBERS}"
        )
        assert exit_val == "HOLD", (
            f"Expected HOLD for legacy PASS exit, got {exit_val}"
        )

    def test_parsed_valid_envelope_gets_allow(self):
        """Parsing VALID_ENVELOPE_RAW and evaluating produces ALLOW."""
        env = parse_envelope(VALID_ENVELOPE_RAW)
        result = evaluate(env)
        exit_val = _extract_exit(result)
        assert exit_val in EXPECTED_EXIT_MEMBERS
        assert exit_val == "ALLOW", (
            f"Expected ALLOW for parsed valid envelope, got {exit_val}. "
            f"Violations: {result.violations}"
        )

    def test_gate_result_exit_always_in_frozen_set(self):
        """Every GateResult.exit must be in EXPECTED_EXIT_MEMBERS."""
        envelopes = [
            _make_envelope(),
            _make_envelope(msg_id=""),
            _make_envelope(exit_code="PASS"),
            _make_envelope(sender="ZIGGY"),
        ]
        for env in envelopes:
            result = evaluate(env)
            exit_val = _extract_exit(result)
            assert exit_val in EXPECTED_EXIT_MEMBERS, (
                f"GateResult.exit '{exit_val}' not in frozen set "
                f"for envelope with msg_id={env.msg_id}"
            )
