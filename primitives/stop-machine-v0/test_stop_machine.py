"""Stub test: confirms the v0 stop_machine raises RuntimeError on import."""
import pytest


def test_import_stop_machine_v0_raises():
    """Importing the v0 stub must raise RuntimeError."""
    with pytest.raises(RuntimeError, match="non-canonical legacy stub"):
        import importlib
        importlib.import_module("stop_machine")
