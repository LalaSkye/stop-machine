# examples/demo_invariant_lock.py

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "primitives" / "invariant-lock"))

from invariant_lock import InvariantLock  # noqa: E402

p = Path("demo_lock.txt")
p.write_text("alpha", encoding="utf-8")
lock = InvariantLock.seal(p)
print("sealed:", lock.digest, "verify:", lock.verify())
p.write_text("beta", encoding="utf-8")
print("tampered verify:", lock.verify())
