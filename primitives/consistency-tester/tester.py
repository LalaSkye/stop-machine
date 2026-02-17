from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, List, Tuple


@dataclass(frozen=True)
class ConsistencyReport:
    runs: int
    deterministic: bool
    unique_count: int
    outputs: Tuple[Any, ...]


def _key(o: Any) -> Any:
    """Stable-ish grouping key for outputs."""
    try:
        hash(o)
        return ("hashable", o)
    except Exception:
        return ("repr", repr(o))


def run_consistency_test(
    fn: Callable[..., Any], runs: int, *args: Any, **kwargs: Any
) -> ConsistencyReport:
    """
    Run `fn(*args, **kwargs)` `runs` times and measure output consistency.

    Deterministic = all outputs fall into one equivalence class
    (hashable equality or repr fallback).
    """
    if runs <= 0:
        raise ValueError("runs must be >= 1")

    outputs: List[Any] = []
    keys: List[Any] = []
    for _ in range(runs):
        out = fn(*args, **kwargs)
        outputs.append(out)
        keys.append(_key(out))

    unique_count = len(set(keys))
    deterministic = unique_count == 1

    return ConsistencyReport(
        runs=runs,
        deterministic=deterministic,
        unique_count=unique_count,
        outputs=tuple(outputs),
    )
