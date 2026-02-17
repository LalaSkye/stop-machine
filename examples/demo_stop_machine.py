"""Demo: shows the full StopMachine lifecycle in ~15 lines."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "primitives" / "stop-machine"))

from stop_machine import Event, StopMachine  # noqa: E402

m = StopMachine()
print(m)                                # StopMachine(state=GREEN)

m.send(Event.TICK)
print(m)                                # StopMachine(state=GREEN)

m.send(Event.WARN)
print(m)                                # StopMachine(state=AMBER)

m.send(Event.STOP)
print(m)                                # StopMachine(state=RED)

m.send(Event.RESET)                     # attempt escape
print(m)                                # StopMachine(state=RED)  <- absorbed

print(f"\nTerminal: {m.is_terminal()}")
print(f"History:  {m.history}")
