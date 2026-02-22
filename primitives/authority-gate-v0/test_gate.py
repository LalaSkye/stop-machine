# primitives/authority-gate/test_gate.py

import pytest
from gate import Authority, AuthorityGate

ALL = list(Authority)


def add(a, b):
    return a + b


def test_determinism_replay_history_and_result():
    g1 = AuthorityGate(required=Authority.OWNER_CONFIRMED)
    g2 = AuthorityGate(required=Authority.OWNER_CONFIRMED)
    seq = [Authority.NONE, Authority.USER_CONFIRMED, Authority.OWNER_CONFIRMED, Authority.ADMIN_APPROVED]
    out1, out2 = [], []
    for a in seq:
        try:
            out1.append(g1.call(add, 1, 2, authority=a))
        except PermissionError:
            out1.append("DENY")
        try:
            out2.append(g2.call(add, 1, 2, authority=a))
        except PermissionError:
            out2.append("DENY")
    assert out1 == out2
    assert g1.history == g2.history


@pytest.mark.parametrize("required", ALL)
@pytest.mark.parametrize("provided", ALL)
def test_monotonicity_authority_required_is_threshold(required, provided):
    g = AuthorityGate(required=required)
    ok = provided >= required
    assert g.is_satisfied(provided) is ok
    if ok:
        assert g.call(add, 2, 3, authority=provided) == 5
    else:
        with pytest.raises(PermissionError):
            g.call(add, 2, 3, authority=provided)


def test_history_records_decisions_in_order():
    g = AuthorityGate(required=Authority.USER_CONFIRMED)
    with pytest.raises(PermissionError):
        g.call(add, 1, 1, authority=Authority.NONE)
    assert g.call(add, 1, 1, authority=Authority.USER_CONFIRMED) == 2
    assert len(g.history) == 2
    assert g.history[0].allowed is False
    assert g.history[1].allowed is True
