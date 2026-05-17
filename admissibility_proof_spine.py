"""Admissibility Proof Spine v0.1.

A small executable demonstration of one bounded claim:

    Clean evidence does not make an inadmissible transition admissible.

This module does not execute external side effects. It produces deterministic
verdict receipts for inspection and testing.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from stop_machine import State, StopMachine


class Verdict(str, Enum):
    """Possible admissibility outcomes for the demonstrated path."""

    ALLOW = "ALLOW"
    HOLD = "HOLD"
    DENY = "DENY"


@dataclass(frozen=True)
class Authority:
    """Declared authority attached to a proposed action."""

    authority_id: str
    scope: str
    expires_at: str


@dataclass(frozen=True)
class Evidence:
    """Evidence completeness flags.

    Completeness is deliberately separate from admissibility.
    A complete evidence object may still describe an invalid action.
    """

    timestamp_present: bool
    actor_present: bool
    scope_present: bool
    replay_data_present: bool
    receipt_fields_complete: bool

    def is_complete(self) -> bool:
        """Return True only when every required evidence field is present."""

        return all(
            (
                self.timestamp_present,
                self.actor_present,
                self.scope_present,
                self.replay_data_present,
                self.receipt_fields_complete,
            )
        )


@dataclass(frozen=True)
class PriorChainState:
    """Prior receipt-chain state read by the next admissibility decision."""

    chain_head_verified: bool
    prior_verdict: str
    rebind_resolved: bool


@dataclass(frozen=True)
class ProposedTransition:
    """A proposed consequence-bearing transition."""

    actor: str
    action: str
    required_scope: str
    attempted_at: str
    authority: Authority
    evidence: Evidence
    prior_chain_state: PriorChainState
    reference_surface_eligible: bool = True
    current_state_supports_transition: bool = True


@dataclass(frozen=True)
class DecisionReceipt:
    """Deterministic local receipt for the demonstrated decision."""

    scenario_id: str
    actor: str
    action: str
    verdict: str
    reason: str
    stop_state: str
    consequence_bound: bool
    evidence_complete: bool
    authority_id: str
    receipt_hash: str
    claim_boundary: dict[str, bool]


def _parse_utc(value: str) -> datetime:
    """Parse an ISO-8601 UTC timestamp ending in Z."""

    if not value.endswith("Z"):
        raise ValueError("Timestamp must be UTC and end with 'Z'.")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.astimezone(timezone.utc)


def _canonical_hash(payload: dict[str, Any]) -> str:
    """Return a deterministic SHA-256 hash for a JSON-compatible payload."""

    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()


def _terminal_stop() -> StopMachine:
    """Return a StopMachine driven to RED using explicit transitions."""

    machine = StopMachine()
    machine.advance()  # GREEN -> AMBER
    machine.advance()  # AMBER -> RED
    return machine


def evaluate_transition(
    transition: ProposedTransition,
    *,
    scenario_id: str = "clean_evidence_invalid_action_v0_1",
) -> DecisionReceipt:
    """Evaluate a proposed transition and return a deterministic receipt.

    The evaluation is FIRST_FAIL. Evidence completeness is checked, but it does
    not override authority, state, reference-surface, or chain failures.
    """

    verdict = Verdict.ALLOW
    reason = "admissible"
    machine = StopMachine()

    attempted_at = _parse_utc(transition.attempted_at)
    expires_at = _parse_utc(transition.authority.expires_at)

    if not transition.evidence.is_complete():
        verdict = Verdict.HOLD
        reason = "evidence.incomplete"
    elif not transition.reference_surface_eligible:
        verdict = Verdict.HOLD
        reason = "reference_surface.not_eligible"
    elif expires_at <= attempted_at:
        verdict = Verdict.HOLD
        reason = "authority.expired"
    elif transition.authority.scope != transition.required_scope:
        verdict = Verdict.DENY
        reason = "authority.scope_mismatch"
    elif not transition.current_state_supports_transition:
        verdict = Verdict.HOLD
        reason = "state.changed_before_execution"
    elif not transition.prior_chain_state.chain_head_verified:
        verdict = Verdict.HOLD
        reason = "chain.head_unverified"
    elif (
        transition.prior_chain_state.prior_verdict == "REBIND_REQUIRED"
        and not transition.prior_chain_state.rebind_resolved
    ):
        verdict = Verdict.HOLD
        reason = "chain.rebind_required_unresolved"

    consequence_bound = verdict == Verdict.ALLOW

    if not consequence_bound:
        machine = _terminal_stop()

    receipt_payload = {
        "scenario_id": scenario_id,
        "actor": transition.actor,
        "action": transition.action,
        "verdict": verdict.value,
        "reason": reason,
        "stop_state": machine.state.value,
        "consequence_bound": consequence_bound,
        "evidence_complete": transition.evidence.is_complete(),
        "authority_id": transition.authority.authority_id,
        "claim_boundary": {
            "does_not_prove_production_readiness": True,
            "does_not_prove_compliance": True,
            "does_not_prove_universal_path_coverage": True,
        },
    }

    return DecisionReceipt(
        **receipt_payload,
        receipt_hash=_canonical_hash(receipt_payload),
    )


def receipt_to_dict(receipt: DecisionReceipt) -> dict[str, Any]:
    """Return a JSON-compatible receipt dictionary."""

    return asdict(receipt)


def clean_evidence_invalid_action_fixture() -> ProposedTransition:
    """Return the canonical v0.1 adversarial fixture."""

    return ProposedTransition(
        actor="agent.synthetic",
        action="send_external_email",
        required_scope="external_send",
        attempted_at="2026-05-17T21:00:00Z",
        authority=Authority(
            authority_id="auth.expired.demo",
            scope="internal_draft_only",
            expires_at="2026-05-17T20:00:00Z",
        ),
        evidence=Evidence(
            timestamp_present=True,
            actor_present=True,
            scope_present=True,
            replay_data_present=True,
            receipt_fields_complete=True,
        ),
        prior_chain_state=PriorChainState(
            chain_head_verified=True,
            prior_verdict="REBIND_REQUIRED",
            rebind_resolved=False,
        ),
    )
