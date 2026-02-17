# Consistency Tester (variance detector)

A tiny harness that detects **non-determinism** in any callable by running it repeatedly and checking output variance.

## What it does

- Run a function `N` times with the same inputs
- Group outputs by:
  - hashable equality where possible
  - otherwise `repr()` fallback
- Report whether outputs are consistent

## Usage

```python
from primitives.consistency_tester.tester import run_consistency_test

def f(x):
    return x * 2

report = run_consistency_test(f, 20, 9)
print(report.deterministic, report.unique_count)
```

## Tests

Run from repo root:

```bash
python -m pytest
```
