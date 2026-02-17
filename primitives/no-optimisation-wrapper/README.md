# No-Optimisation Wrapper (mutation guard)

A tiny, deterministic wrapper that **refuses hidden in-place mutation** of input arguments.

## What it does

- Takes a deep snapshot of `args`/`kwargs` *before* calling your function
- Calls the function normally
- Compares *after* call fingerprints + deep-equality
- Raises `MutationDetected` if **any argument was mutated**

This is a "boring but airtight" guard: it does not try to infer intent; it just detects mutation.

## Usage

```python
from primitives.no_optimisation_wrapper.wrapper import no_optimisation_wrapper

@no_optimisation_wrapper
def safe_fn(xs):
    return sum(xs)

print(safe_fn([1, 2, 3]))
```

If a function mutates its inputs:

```python
@no_optimisation_wrapper
def bad(xs):
    xs.append("oops")
    return xs

bad([1, 2, 3])  # raises MutationDetected
```

## Tests

Run from repo root:

```bash
python -m pytest
```
