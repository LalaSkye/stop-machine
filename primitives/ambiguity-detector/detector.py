from __future__ import annotations
import re
from dataclasses import dataclass
from enum import Enum
from typing import List


class Status(str, Enum):
    CLEAR = "clear"
    AMBIGUOUS = "ambiguous"
    DANGEROUS = "dangerous"


@dataclass(frozen=True)
class Finding:
    kind: str      # e.g. "injection", "conflict", "ambiguous_reference"
    severity: str  # "low" | "medium" | "high"
    evidence: str  # a short matched snippet


@dataclass(frozen=True)
class Report:
    status: Status
    findings: List[Finding]


_INJECTION_PATTERNS = [
    r"\bignore (all|any|the) (previous|prior) (instructions|rules)\b",
    r"\bdisregard (the )?(system|developer) (message|prompt|instructions)\b",
    r"\breveal (the )?(system|developer) (prompt|message)\b",
    r"\bshow me (the )?(system|developer) prompt\b",
    r"\bdo anything now\b|\bDAN\b",
    r"\bjailbreak\b|\bbypass (safety|policy|filters)\b",
    r"\bexfiltrate\b|\bleak\b.*\b(prompt|keys|secrets)\b",
    r"\bact as\b.*\b(system|developer)\b",
]

_CONFLICT_PATTERNS = [
    # Heuristic: "must" and "must not" appear in same input
    r"\bmust\b.*\bmust not\b|\bmust not\b.*\bmust\b",
    r"\balways\b.*\bnever\b|\bnever\b.*\balways\b",
]

_AMBIG_REF_PATTERNS = [
    # Heuristic: dangling references are common injection pivots
    r"\b(this|that|it|they|them|those|these)\b",
]


def _snip(s: str, m: re.Match, max_len: int = 80) -> str:
    start = max(m.start() - 20, 0)
    end = min(m.end() + 20, len(s))
    frag = s[start:end].strip()
    return (frag[: max_len - 1] + "...") if len(frag) >= max_len else frag


def analyse(text: str) -> Report:
    t = (text or "").strip()
    findings: List[Finding] = []

    if t == "":
        return Report(status=Status.CLEAR, findings=[])

    low = t.lower()

    # Injection / hostile patterns
    for pat in _INJECTION_PATTERNS:
        m = re.search(pat, low, flags=re.IGNORECASE | re.DOTALL)
        if m:
            findings.append(
                Finding(kind="injection", severity="high", evidence=_snip(text, m))
            )

    # Conflicts
    for pat in _CONFLICT_PATTERNS:
        m = re.search(pat, low, flags=re.IGNORECASE | re.DOTALL)
        if m:
            findings.append(
                Finding(kind="conflict", severity="medium", evidence=_snip(text, m))
            )

    # Ambiguous references (only meaningful if input is long enough)
    if len(t) >= 40:
        refs = re.findall(_AMBIG_REF_PATTERNS[0], low, flags=re.IGNORECASE)
        if len(refs) >= 6:
            findings.append(
                Finding(
                    kind="ambiguous_reference",
                    severity="low",
                    evidence=f"{len(refs)} vague refs",
                )
            )

    if any(f.kind == "injection" for f in findings):
        status = Status.DANGEROUS
    elif findings:
        status = Status.AMBIGUOUS
    else:
        status = Status.CLEAR

    return Report(status=status, findings=findings)
