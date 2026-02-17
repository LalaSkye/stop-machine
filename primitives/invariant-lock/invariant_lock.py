# primitives/invariant-lock/invariant_lock.py

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Union


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Union[str, Path]) -> str:
    p = Path(path)
    return sha256_bytes(p.read_bytes())


@dataclass(frozen=True)
class InvariantLock:
    path: str
    digest: str

    @staticmethod
    def seal(path: Union[str, Path]) -> "InvariantLock":
        p = Path(path)
        return InvariantLock(str(p), sha256_file(p))

    def verify(self) -> bool:
        return sha256_file(self.path) == self.digest
