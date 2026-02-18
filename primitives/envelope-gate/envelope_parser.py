"""Envelope parser for ALVIANTECH_ENVELOPE v0.1 protocol.

Extracts structured envelope data from raw Markdown text.
Deterministic. No network calls. No side effects.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


_ENVELOPE_HEADER = "ALVIANTECH_ENVELOPE v0.1"

# Regex to split a comms-center markdown file into individual envelopes.
_ENVELOPE_BLOCK_RE = re.compile(
    r"```\s*\n(ALVIANTECH_ENVELOPE v0\.1.*?)```",
    re.DOTALL,
)


@dataclass(frozen=True)
class Envelope:
    """Parsed representation of a single ALVIANTECH_ENVELOPE."""

    raw: str
    msg_id: str = ""
    ts_utc: str = ""
    sender: str = ""
    recipient: str = ""
    mode: str = ""
    scope: str = ""
    goal: str = ""
    inputs: List[str] = field(default_factory=list)
    must: List[str] = field(default_factory=list)
    must_not: List[str] = field(default_factory=list)
    output_type: str = ""
    output_format: str = ""
    body_payload: str = ""
    in_reply_to: str = ""
    exit_code: str = ""
    return_reasons: List[str] = field(default_factory=list)
    return_payload: str = ""

    @property
    def is_response(self) -> bool:
        """True if this envelope is a reply (msg_id ends with -R)."""
        return self.msg_id.endswith("-R")


def _strip_quotes(value: str) -> str:
    """Remove surrounding quotes from a parsed value."""
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1]
    return value


def _extract_field(text: str, field_name: str) -> str:
    """Extract a single key: value field from envelope text."""
    pattern = re.compile(
        rf"^\s*{re.escape(field_name)}\s*:\s*(.+)$",
        re.MULTILINE,
    )
    match = pattern.search(text)
    if match:
        raw_val = match.group(1).strip()
        # Strip inline comments (# ...)
        if "#" in raw_val:
            raw_val = raw_val[:raw_val.index("#")].strip()
        return _strip_quotes(raw_val)
    return ""


def _extract_bullet_list(text: str, section_start: str) -> List[str]:
    """Extract a bullet list (lines starting with - ) under a section header."""
    pattern = re.compile(
        rf"^\s*{re.escape(section_start)}\s*:\s*$",
        re.MULTILINE,
    )
    match = pattern.search(text)
    if not match:
        return []
    items: List[str] = []
    rest = text[match.end():]
    for line in rest.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
        elif stripped and not stripped.startswith("-"):
            break
    return items


def _extract_section(text: str, header: str) -> str:
    """Extract everything between a section header and the next section."""
    pattern = re.compile(
        rf"^{re.escape(header)}\s*:\s*$",
        re.MULTILINE,
    )
    match = pattern.search(text)
    if not match:
        return ""
    rest = text[match.end():]
    # Find next top-level section (PORTS:, BODY:, RETURN:)
    next_section = re.search(r"^(?:PORTS|BODY|RETURN)\s*:", rest, re.MULTILINE)
    if next_section:
        return rest[:next_section.start()]
    return rest


def _extract_payload(section_text: str) -> str:
    """Extract the payload sub-field from a section."""
    pattern = re.compile(
        r"^\s*payload\s*:\s*(.*)$",
        re.MULTILINE,
    )
    match = pattern.search(section_text)
    if not match:
        return ""
    first_line = match.group(1).strip()
    rest = section_text[match.end():]
    # Collect continuation lines (indented, non-empty, not a new field)
    lines = [first_line] if first_line else []
    for line in rest.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # Stop at next recognised field or section
        if re.match(r"^\s*\w+\s*:", line) and not line.startswith(" " * 6):
            break
        lines.append(stripped)
    return "\n".join(lines)


def parse_envelope(raw: str) -> Envelope:
    """Parse a single raw envelope text block into an Envelope."""
    ports_section = _extract_section(raw, "PORTS")
    body_section = _extract_section(raw, "BODY")
    return_section = _extract_section(raw, "RETURN")

    # Extract constraints sub-sections from body
    constraints_text = _extract_section(body_section, "  constraints") or \
        _extract_section(body_section, "constraints")

    return Envelope(
        raw=raw,
        msg_id=_extract_field(ports_section, "msg_id"),
        ts_utc=_extract_field(ports_section, "ts_utc"),
        sender=_extract_field(ports_section, "from"),
        recipient=_extract_field(ports_section, "to"),
        mode=_extract_field(ports_section, "mode"),
        scope=_extract_field(ports_section, "scope"),
        goal=_extract_field(body_section, "goal"),
        inputs=_extract_bullet_list(body_section, "  inputs") or
               _extract_bullet_list(body_section, "inputs"),
        must=_extract_bullet_list(constraints_text, "  must") or
             _extract_bullet_list(constraints_text, "must"),
        must_not=_extract_bullet_list(constraints_text, "  must_not") or
                 _extract_bullet_list(constraints_text, "must_not"),
        output_type=_extract_field(body_section, "type"),
        output_format=_extract_field(body_section, "format"),
        body_payload=_extract_payload(body_section),
        in_reply_to=_extract_field(return_section, "in_reply_to"),
        exit_code=_extract_field(return_section, "exit"),
        return_reasons=_extract_bullet_list(return_section, "  reason") or
                       _extract_bullet_list(return_section, "reason"),
        return_payload=_extract_payload(return_section),
    )


def extract_envelopes(markdown_text: str) -> List[Envelope]:
    """Extract all envelopes from a Markdown comms-center file."""
    blocks = _ENVELOPE_BLOCK_RE.findall(markdown_text)
    return [parse_envelope(block) for block in blocks]
