"""conftest.py -- ensure this directory is first on sys.path.

Prevents pytest from importing 'gate' from a sibling primitive
(e.g. authority-gate/gate.py) instead of this one.
"""

import sys
from pathlib import Path

_HERE = str(Path(__file__).resolve().parent)
if _HERE not in sys.path or sys.path[0] != _HERE:
    if _HERE in sys.path:
        sys.path.remove(_HERE)
    sys.path.insert(0, _HERE)
