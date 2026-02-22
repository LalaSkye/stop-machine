"""Stub test: confirms the v0 authority_gate raises RuntimeError on import."""
import pytest


def test_import_authority_gate_v0_raises():
    """Importing the v0 stub must raise RuntimeError."""
    with pytest.raises(RuntimeError, match="non-canonical legacy stub"):
        import importlib
        importlib.import_module("gate")
