#!/usr/bin/env python3
"""CLI for EnvelopeGate conformance checking.

Usage:
    python cli.py check <comms_file>          Print gate results table
    python cli.py log   <comms_file> <logfile> Print + append to gate log

Deterministic. No network calls. No side effects (except log append).
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List

# ---------------------------------------------------------------------------
# Robust local imports via importlib
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
extract_envelopes = _ep.extract_envelopes

_ga = _load_local("gate")
evaluate = _ga.evaluate
evaluate_all = _ga.evaluate_all
GateResult = _ga.GateResult


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _violations_str(result: GateResult) -> str:
    """Compact violations summary."""
    if not result.violations:
        return "--"
    return "; ".join(v.code for v in result.violations)


def _print_table(results: List[GateResult]) -> None:
    """Print a formatted results table to stdout."""
    hdr = f"{'msg_id':<16} {'from':<10} {'to':<10} {'exit':<8} {'violations'}"
    sep = "-" * len(hdr)
    print()
    print(sep)
    print(hdr)
    print(sep)
    for r in results:
        # Recover sender/recipient from violations context or raw
        env = None
        for e in _last_envelopes:
            if (e.msg_id or "(unknown)") == r.msg_id:
                env = e
                break
        sender = env.sender if env else "?"
        recipient = env.recipient if env else "?"
        print(f"{r.msg_id:<16} {sender:<10} {recipient:<10} {r.exit:<8} {_violations_str(r)}")
    print(sep)

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    print(f"\n  {passed}/{total} envelopes passed (exit=ALLOW)")
    print()


def _format_log_entry(results: List[GateResult]) -> str:
    """Format gate results as a Markdown log entry."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        f"## Gate Run: {ts}",
        "",
        f"Envelopes scanned: {len(results)}",
        f"Passed: {sum(1 for r in results if r.passed)}",
        f"Failed: {sum(1 for r in results if not r.passed)}",
        "",
        "| msg_id | exit | violations |",
        "|--------|------|------------|",
    ]
    for r in results:
        lines.append(f"| {r.msg_id} | {r.exit} | {_violations_str(r)} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

_last_envelopes: list = []


def cmd_check(comms_path: str) -> List[GateResult]:
    """Read comms file, evaluate all envelopes, print table."""
    global _last_envelopes
    text = Path(comms_path).read_text(encoding="utf-8")
    envelopes = extract_envelopes(text)
    _last_envelopes = envelopes

    if not envelopes:
        print("No envelopes found in file.")
        return []

    print(f"Found {len(envelopes)} envelopes in {comms_path}")
    results = evaluate_all(envelopes)
    _print_table(results)
    return results


def cmd_log(comms_path: str, log_path: str) -> None:
    """Run check and append results to gate log file."""
    results = cmd_check(comms_path)
    if not results:
        return

    entry = _format_log_entry(results)
    log_file = Path(log_path)

    if log_file.exists():
        existing = log_file.read_text(encoding="utf-8")
        log_file.write_text(existing + "\n" + entry, encoding="utf-8")
    else:
        log_file.write_text(entry, encoding="utf-8")

    print(f"Results appended to {log_path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "check":
        cmd_check(sys.argv[2])
    elif command == "log":
        if len(sys.argv) < 4:
            print("Usage: python cli.py log <comms_file> <logfile>")
            sys.exit(1)
        cmd_log(sys.argv[2], sys.argv[3])
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
