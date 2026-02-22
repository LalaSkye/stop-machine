"""AuthorityGate -- deterministic authority wrapper.

Execution requires explicit authority. No implicit permissions.
Authority levels are ordered: NONE < USER_CONFIRMED < OWNER_CONFIRMED < ADMIN_APPROVED.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Callable, List


class Authority(IntEnum):
    NONE = 0
    USER_CONFIRMED = 1
    OWNER_CONFIRMED = 2
    ADMIN_APPROVED = 3


@dataclass(frozen=True)
class Decision:
    required: Authority
    provided: Authority
    allowed: bool


@dataclass
class AuthorityGate:
    """Deterministic authority gate. No implicit permissions."""

    required: Authority = Authority.USER_CONFIRMED
    _history: List[Decision] = field(default_factory=list)

    def call(self, fn: Callable[..., Any], *args: Any, authority: Authority, **kwargs: Any) -> Any:
        """Execute *fn* only if authority >= required. Pure comparison."""
        allowed = authority >= self.required
        self._history.append(Decision(self.required, authority, allowed))
        if not allowed:
            raise PermissionError(f"authority {authority.name} < required {self.required.name}")
        return fn(*args, **kwargs)

    @property
    def history(self) -> List[Decision]:
        return list(self._history)

    def is_satisfied(self, authority: Authority) -> bool:
        return authority >= self.required
