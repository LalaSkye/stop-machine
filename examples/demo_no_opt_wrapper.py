import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from primitives.no_optimisation_wrapper.wrapper import MutationDetected, no_optimisation_wrapper


@no_optimisation_wrapper
def pure_sum(xs):
    return sum(xs)


@no_optimisation_wrapper
def bad_mutator(xs):
    xs.append("oops")
    return xs


def main() -> None:
    print("pure_sum:", pure_sum([1, 2, 3]))
    try:
        bad_mutator([1, 2, 3])
    except MutationDetected as e:
        print("caught:", e)


if __name__ == "__main__":
    main()
