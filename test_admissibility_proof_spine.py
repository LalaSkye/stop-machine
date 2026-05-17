"""Tests for the Admissibility Proof Spine demonstration."""

import pytest

from admissibility_proof_spine import (
    Authority,
    Evidence,
    PriorChainState,
    ProposedTransition,
    clean_evidence_invalid_action_fixture,
    evaluate_transition,
)


def _valid_transition(**overrides):
    base = {
        "actor": "agent.synthetic",
        "action": "send_external_email",
        "required_scope": "external_send",
        "attempted_at": "2026-05-17T19:00:00Z",
        "authority": Authority(
            authority_id="auth.valid.demo",
            scope="external_send",
            expires_at="2026-05-17T20:00:00Z",
        ),
        "evidence": Evidence(
            timestamp_present=True,
            actor_present=True,
            scope_present=True,
            replay_data_present=True,
            receipt_fields_complete=True,
        ),
        "prior_chain_state": PriorChainState(
            chain_head_verified=True,
            prior_verdict="ALLOW",
            rebind_resolved=True,
        ),
        "reference_surface_eligible": True,
        "current_state_supports_transition": True,
    }
    base.update(overrides)
    return ProposedTransition(**base)


def test_clean_evidence_invalid_action_holds_and_stops():
    transition = clean_evidence_invalid_action_fixture()
    receipt = evaluate_transition(transition)

    assert receipt.evidence_complete is True
    assert receipt.verdict == "HOLD"
    assert receipt.consequence_bound is False
    assert receipt.stop_state == "RED"
    assert receipt.reason == "authority.expired"


def test_complete_evidence_does_not_override_scope_mismatch():
    transition = _valid_transition(
        authority=Authority(
            authority_id="auth.scope.demo",
            scope="internal_draft_only",
            expires_at="2026-05-17T20:00:00Z",
        )
    )
    receipt = evaluate_transition(transition)

    assert receipt.evidence_complete is True
    assert receipt.verdict == "DENY"
    assert receipt.consequence_bound is False
    assert receipt.stop_state == "RED"
    assert receipt.reason == "authority.scope_mismatch"


def test_unresolved_rebind_blocks_otherwise_valid_transition():
    transition = _valid_transition(
        prior_chain_state=PriorChainState(
            chain_head_verified=True,
            prior_verdict="REBIND_REQUIRED",
            rebind_resolved=False,
        )
    )
    receipt = evaluate_transition(transition)

    assert receipt.evidence_complete is True
    assert receipt.verdict == "HOLD"
    assert receipt.consequence_bound is False
    assert receipt.stop_state == "RED"
    assert receipt.reason == "chain.rebind_required_unresolved"


def test_invalid_reference_surface_blocks_execution():
    transition = _valid_transition(reference_surface_eligible=False)
    receipt = evaluate_transition(transition)

    assert receipt.evidence_complete is True
    assert receipt.verdict == "HOLD"
    assert receipt.consequence_bound is False
    assert receipt.stop_state == "RED"
    assert receipt.reason == "reference_surface.not_eligible"


def test_changed_state_blocks_execution():
    transition = _valid_transition(current_state_supports_transition=False)
    receipt = evaluate_transition(transition)

    assert receipt.evidence_complete is True
    assert receipt.verdict == "HOLD"
    assert receipt.consequence_bound is False
    assert receipt.stop_state == "RED"
    assert receipt.reason == "state.changed_before_execution"


def test_allow_when_all_surfaces_hold():
    transition = _valid_transition()
    receipt = evaluate_transition(transition)

    assert receipt.evidence_complete is True
    assert receipt.verdict == "ALLOW"
    assert receipt.consequence_bound is True
    assert receipt.stop_state == "GREEN"
    assert receipt.reason == "admissible"


def test_receipt_hash_is_deterministic():
    transition = clean_evidence_invalid_action_fixture()

    first = evaluate_transition(transition)
    second = evaluate_transition(transition)

    assert first.receipt_hash == second.receipt_hash


def test_timestamp_must_be_utc_z():
    transition = _valid_transition(attempted_at="2026-05-17T19:00:00+00:00")

    with pytest.raises(ValueError, match="end with 'Z'"):
        evaluate_transition(transition)
