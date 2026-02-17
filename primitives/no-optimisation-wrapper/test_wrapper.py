import pytest
from wrapper import MutationDetected, no_optimisation_wrapper


def test_determinism_passes_for_pure_function():
    def add(a, b):
        return a + b

    w = no_optimisation_wrapper(add)
    assert w(2, 3) == 5
    assert w(2, 3) == 5
    assert w(10, -4) == 6


def test_detects_mutation_in_args():
    def mutator(xs):
        xs.append("boom")
        return len(xs)

    w = no_optimisation_wrapper(mutator)
    xs = [1, 2, 3]
    with pytest.raises(MutationDetected):
        w(xs)


def test_detects_mutation_in_kwargs():
    def mutator(*, cfg):
        cfg["x"] = 999
        return "ok"

    w = no_optimisation_wrapper(mutator)
    cfg = {"x": 1}
    with pytest.raises(MutationDetected):
        w(cfg=cfg)


def test_clean_passthrough_does_not_raise_and_does_not_mutate():
    def pure(xs):
        return tuple(xs)  # reads only

    w = no_optimisation_wrapper(pure)
    xs = [1, 2, 3]
    out = w(xs)
    assert out == (1, 2, 3)
    assert xs == [1, 2, 3]
