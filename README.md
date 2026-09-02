# stop-machine

A three-state halt. GREEN → AMBER → RED. RED does not move through the public API.

## Ceiling

This is not a vault. A caller in the same process can still write `_state` with `object.__setattr__`. Out-of-process stop is out of scope.

See [CEILING.md](CEILING.md).

This repository does not prove adoption, certification, production readiness, or that evidence can be upgraded into permission.

## 30 seconds

```bash
git clone https://github.com/LalaSkye/stop-machine.git
cd stop-machine
python -c "from stop_machine import StopMachine; m=StopMachine(); m.advance(); m.advance(); print(m.state)"
```

Expected: `State.RED`

Then `m.advance()` raises `TerminalStateError`.
`m._state = …` raises `AttributeError`.

## Tests

```bash
pytest test_stop_machine.py -v
```

## Licence

MIT.

Author: Ricky Dean Jones
