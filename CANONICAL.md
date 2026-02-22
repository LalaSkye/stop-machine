# CANONICAL SOURCE OF TRUTH

This repository (`stop-machine`) contains **non-canonical legacy copies** of
primitives whose authoritative implementations live in
[constraint-workshop](https://github.com/LalaSkye/constraint-workshop).

## Canonical Primitive Locations

| Primitive | Canonical Repo | Canonical Path | Pinned Commit |
|-----------|---------------|----------------|---------------|
| `stop_machine` | [constraint-workshop](https://github.com/LalaSkye/constraint-workshop) | `stop_machine.py` | [`3780882`](https://github.com/LalaSkye/constraint-workshop/commit/3780882) |
| `authority_gate` | [constraint-workshop](https://github.com/LalaSkye/constraint-workshop) | `authority_gate.py` | [`70ed2c9`](https://github.com/LalaSkye/constraint-workshop/commit/70ed2c9) |

## Rule

**Do not modify local copies; update canonical then resync.**

The `primitives/stop-machine-v0/` and `primitives/authority-gate-v0/` folders
in this repo contain non-functional stubs that raise on import. They exist
solely to preserve directory structure and provide clear error messages
pointing to the canonical source.

To use these primitives, import directly from `constraint-workshop` or copy
the canonical files at the pinned commit listed above.
