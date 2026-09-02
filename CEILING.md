# Ceiling

Public methods will not leave RED.
`m._state = GREEN` raises AttributeError.

Same-process poke still works:

```python
object.__setattr__(m, "_state", State.GREEN)
```

This object is not a vault. It is not another process. It is not an OS halt.

Licence is MIT. That is the whole grant.
