# primitives/invariant-lock/test_invariant_lock.py

from pathlib import Path
from invariant_lock import InvariantLock, sha256_bytes


def test_sha256_bytes_is_deterministic():
    a = sha256_bytes(b"hello")
    b = sha256_bytes(b"hello")
    assert a == b


def test_seal_and_verify_passes_then_fails_on_tamper(tmp_path: Path):
    f = tmp_path / "x.txt"
    f.write_text("alpha", encoding="utf-8")
    lock = InvariantLock.seal(f)
    assert lock.verify() is True
    f.write_text("beta", encoding="utf-8")
    assert lock.verify() is False


def test_verify_is_replay_stable(tmp_path: Path):
    f = tmp_path / "y.txt"
    f.write_text("same", encoding="utf-8")
    lock = InvariantLock.seal(f)
    assert lock.verify() is True
    assert lock.verify() is True
