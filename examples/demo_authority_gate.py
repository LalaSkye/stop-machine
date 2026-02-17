# examples/demo_authority_gate.py

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "primitives" / "authority-gate"))

from gate import Authority, AuthorityGate  # noqa: E402

g = AuthorityGate(required=Authority.OWNER_CONFIRMED)
print("required:", g.required.name)
for a in [Authority.NONE, Authority.USER_CONFIRMED, Authority.OWNER_CONFIRMED]:
    try:
        print(a.name, "->", g.call(lambda: "OK", authority=a))
    except PermissionError as e:
        print(a.name, "-> DENY", str(e))
print("history:", g.history)
