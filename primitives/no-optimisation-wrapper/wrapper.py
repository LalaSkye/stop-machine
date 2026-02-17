# primitives/no-optimisation-wrapper/wrapper.py

from __future__ import annotations

import copy
import hashlib
import pickle
from dataclasses import dataclass
from typing import Any, Callable, Dict, Tuple


class MutationDetected(RuntimeError):
    """Raised when a wrapped callable mutates its input arguments."""


def _fingerprint(obj: Any) -> str:
    try:
        data = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception:
        data = repr(obj).encode("utf-8", errors="replace")
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class Snapshot:
    args_copy: Tuple[Any, ...]
    kwargs_copy: Dict[str, Any]
    args_fp: Tuple[str, ...]
    kwargs_fp: Dict[str, str]


def snapshot(args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> Snapshot:
    args_copy = copy.deepcopy(args)
    kwargs_copy = copy.deepcopy(kwargs)
    args_fp = tuple(_fingerprint(a) for a in args)
    kwargs_fp = {k: _fingerprint(v) for k, v in kwargs.items()}
    return Snapshot(
        args_copy=args_copy, kwargs_copy=kwargs_copy,
        args_fp=args_fp, kwargs_fp=kwargs_fp,
    )


def _diff_snapshot(
    before: Snapshot, args: Tuple[Any, ...], kwargs: Dict[str, Any],
) -> str | None:
    after_args_fp = tuple(_fingerprint(a) for a in args)
    after_kwargs_fp = {k: _fingerprint(v) for k, v in kwargs.items()}
    if after_args_fp != before.args_fp:
        return "args"
    if after_kwargs_fp != before.kwargs_fp:
        return "kwargs"
    try:
        if args != before.args_copy:
            return "args"
    except Exception:
        pass
    try:
        if kwargs != before.kwargs_copy:
            return "kwargs"
    except Exception:
        pass
    return None


def no_optimisation_wrapper(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Wrap fn and refuse hidden state mutation of arguments."""
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        before = snapshot(args, kwargs)
        result = fn(*args, **kwargs)
        changed = _diff_snapshot(before, args, kwargs)
        if changed is not None:
            raise MutationDetected(
                f"Input mutation detected in {changed} for {getattr(fn, '__name__', 'callable')}"
            )
        return result
    wrapped.__name__ = getattr(fn, "__name__", "wrapped")
    wrapped.__doc__ = getattr(fn, "__doc__", None)
    return wrapped
