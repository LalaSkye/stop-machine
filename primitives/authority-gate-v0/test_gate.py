"""Stub test: confirms the v0 authority_gate raises RuntimeError on import."""
import pytest
import importlib.util
import sys
from pathlib import Path


def test_import_authority_gate_v0_raises():
    """Importing the v0 stub must raise RuntimeError."""
    stub = Path(__file__).resolve().parent / "gate.py"
    spec = importlib.util.spec_from_file_location("gate_v0_stub", stub)
    mod = importlib.util.module_from_spec(spec)
    with pytest.raises(RuntimeError, match="non-canonical legacy stub"):
        spec.loader.exec_module(mod)
