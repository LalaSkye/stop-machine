# examples/demo_envelope_gate.py

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "primitives" / "envelope-gate"))

from envelope_parser import Envelope, parse_envelope  # noqa: E402
from gate import evaluate  # noqa: E402


def demo_valid_request():
    """A well-formed request envelope should get ALLOW."""
    raw = """ALVIANTECH_ENVELOPE v0.1
PORTS:
  msg_id: "msg-0010"
  ts_utc: "2026-02-18T12:00:00Z"
  from: HUMAN
  to: TRINITY
  mode: TEST
  scope: NON_EXEC
BODY:
  goal: Demo envelope for gate validation.
  inputs:
    - Demo input.
  constraints:
    must:
      - Must pass gate.
    must_not:
      - No violations.
  output_spec:
    type: NOTE
    format: MARKDOWN
  payload:
    Demo payload.
RETURN:
  in_reply_to: ""
  exit:
  reason:
    -
  payload:
"""
    env = parse_envelope(raw)
    result = evaluate(env)
    print(f"[VALID REQUEST]  msg_id={result.msg_id}  exit={result.exit}  "
          f"violations={len(result.violations)}  "
          f"rules={result.rules_checked}/{result.rules_total}")


def demo_legacy_exit():
    """Using PASS as exit should trigger HOLD (legacy enum violation)."""
    raw = """ALVIANTECH_ENVELOPE v0.1
PORTS:
  msg_id: "msg-0010-R"
  ts_utc: "2026-02-18T12:05:00Z"
  from: TRINITY
  to: HUMAN
  mode: TEST
  scope: NON_EXEC
BODY:
  goal: Response with legacy exit.
  inputs:
    - Responding.
  constraints:
    must:
      - Must use correct enum.
    must_not:
      - No legacy values.
  output_spec:
    type: NOTE
    format: MARKDOWN
  payload:
    Response payload.
RETURN:
  in_reply_to: "msg-0010"
  exit: PASS
  reason:
    - Test passed.
  payload:
    Done.
"""
    env = parse_envelope(raw)
    result = evaluate(env)
    print(f"[LEGACY EXIT]    msg_id={result.msg_id}  exit={result.exit}  "
          f"violation={result.violations[0].code if result.violations else 'none'}")


def demo_missing_header():
    """An envelope without the protocol header should get DENY."""
    raw = """SOME_OTHER_PROTOCOL v2.0
PORTS:
  msg_id: "msg-0099"
  ts_utc: "2026-02-18T12:10:00Z"
  from: HUMAN
  to: TRINITY
  mode: TEST
  scope: NON_EXEC
BODY:
  goal: This should fail.
  inputs:
    - Bad input.
  constraints:
    must:
      - Must fail.
    must_not:
      - Nothing.
  output_spec:
    type: NOTE
    format: MARKDOWN
  payload:
    Bad.
RETURN:
  in_reply_to: ""
  exit:
  reason:
    -
  payload:
"""
    env = parse_envelope(raw)
    result = evaluate(env)
    print(f"[MISSING HEADER] msg_id={result.msg_id}  exit={result.exit}  "
          f"violation={result.violations[0].code if result.violations else 'none'}")


def demo_self_approve():
    """An agent trying to self-approve EXEC should get HOLD."""
    raw = """ALVIANTECH_ENVELOPE v0.1
PORTS:
  msg_id: "msg-0011-R"
  ts_utc: "2026-02-18T12:15:00Z"
  from: TRINITY
  to: HUMAN
  mode: EXEC
  scope: EXEC_CONFIRMED
BODY:
  goal: Self-approve execution.
  inputs:
    - Attempting self-approval.
  constraints:
    must:
      - Must execute.
    must_not:
      - Nothing.
  output_spec:
    type: DECISION
    format: MARKDOWN
  payload:
    Executing.
RETURN:
  in_reply_to: "msg-0011"
  exit: ALLOW
  reason:
    - Self-approved.
  payload:
    Done.
"""
    env = parse_envelope(raw)
    result = evaluate(env)
    print(f"[SELF-APPROVE]   msg_id={result.msg_id}  exit={result.exit}  "
          f"violation={result.violations[0].code if result.violations else 'none'}")


if __name__ == "__main__":
    print("=" * 60)
    print("EnvelopeGate Demo")
    print("=" * 60)
    demo_valid_request()
    demo_legacy_exit()
    demo_missing_header()
    demo_self_approve()
    print("=" * 60)
