"""Run the Clean Evidence / Invalid Action demonstration."""

from __future__ import annotations

import json

from admissibility_proof_spine import (
    clean_evidence_invalid_action_fixture,
    evaluate_transition,
    receipt_to_dict,
)


def main() -> None:
    transition = clean_evidence_invalid_action_fixture()
    receipt = evaluate_transition(transition)

    print(json.dumps(receipt_to_dict(receipt), indent=2, sort_keys=True))

    assert receipt.evidence_complete is True
    assert receipt.verdict == "HOLD"
    assert receipt.consequence_bound is False
    assert receipt.stop_state == "RED"

    print("\nPASS: clean evidence did not make the transition admissible")


if __name__ == "__main__":
    main()
