import random
import pytest
from tester import run_consistency_test


def test_deterministic_function_passes():
    def f(x):
        return x * 2

    r = run_consistency_test(f, 10, 7)
    assert r.deterministic is True
    assert r.unique_count == 1
    assert all(o == 14 for o in r.outputs)


def test_random_function_fails():
    def f():
        return random.randint(0, 999999)

    r = run_consistency_test(f, 50)
    assert r.deterministic is False
    assert r.unique_count > 1


def test_runs_one_is_trivially_deterministic():
    def f():
        return object()

    r = run_consistency_test(f, 1)
    assert r.deterministic is True
    assert r.unique_count == 1


def test_runs_must_be_positive():
    with pytest.raises(ValueError):
        run_consistency_test(lambda: 1, 0)
