import sys
from pathlib import Path
import random

sys.path.append(str(Path(__file__).resolve().parents[1]))

from primitives.consistency_tester.tester import run_consistency_test


def deterministic(x: int) -> int:
    return x * 2


def nondeterministic() -> int:
    return random.randint(0, 9)


def main() -> None:
    r1 = run_consistency_test(deterministic, 10, 7)
    print("deterministic:", r1.deterministic, "unique:", r1.unique_count)

    r2 = run_consistency_test(nondeterministic, 30)
    print("nondeterministic:", r2.deterministic, "unique:", r2.unique_count)
    print("sample outputs:", r2.outputs[:8])


if __name__ == "__main__":
    main()
