"""conftest.py -- isolate envelope-gate imports from sibling primitives.

Uses pytest_configure hook (runs before collection) to ensure
this directory is first on sys.path and that any cached 'gate'
module from a sibling primitive (authority-gate) is evicted.
"""

import sys
from pathlib import Path

_HERE = str(Path(__file__).resolve().parent)
_PRIMITIVES = str(Path(__file__).resolve().parent.parent)


def pytest_configure(config):
    """Runs before test collection -- guaranteed early."""
    # Evict any cached modules that shadow our local ones.
    # If authority-gate/gate.py was imported first, 'gate' in
    # sys.modules points to the wrong file.
    for mod_name in ["gate", "envelope_parser", "rules"]:
        if mod_name in sys.modules:
            cached = sys.modules[mod_name]
            origin = getattr(cached, "__file__", "") or ""
            if _HERE not in origin:
                del sys.modules[mod_name]

    # Remove sibling primitive dirs from sys.path
    to_remove = []
    for p in sys.path:
        if (
            p != _HERE
            and p.startswith(_PRIMITIVES)
            and Path(p, "gate.py").exists()
        ):
            to_remove.append(p)
    for p in to_remove:
        sys.path.remove(p)

    # Ensure our directory is first
    if _HERE in sys.path:
        sys.path.remove(_HERE)
    sys.path.insert(0, _HERE)
