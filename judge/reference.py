"""Reference encoder: the judge's oracle for numbers 1..9999.

Implements SPECIFICATION.md sections 3-5 directly: a table of upper-right
(units) motifs and two reflections to place a digit in its quadrant. It is
checked against hand-transcribed fixtures (fixtures/known-values.json), not
against itself, and it is deliberately independent of every implementation
under implementations/.

    python -m judge.reference 1986      # print the JSON geometry of 1986
"""

from __future__ import annotations

import json
import sys

Segment = tuple[tuple[int, int], tuple[int, int]]

MIN_VALUE, MAX_VALUE = 1, 9999
GRID_MAX_X, GRID_MAX_Y = 2, 3
STEM: Segment = ((1, 0), (1, 3))

# Upper-right (units) motifs, SPECIFICATION.md section 4.
UNIT_MOTIFS: dict[int, tuple[Segment, ...]] = {
    1: (((1, 0), (2, 0)),),
    2: (((1, 1), (2, 1)),),
    3: (((1, 0), (2, 1)),),
    4: (((1, 1), (2, 0)),),
    5: (((1, 0), (2, 0)), ((1, 1), (2, 0))),
    6: (((2, 0), (2, 1)),),
    7: (((1, 0), (2, 0)), ((2, 0), (2, 1))),
    8: (((1, 1), (2, 1)), ((2, 0), (2, 1))),
    9: (((1, 0), (2, 0)), ((1, 1), (2, 1)), ((2, 0), (2, 1))),
}

PLACES = ("units", "tens", "hundreds", "thousands")


def digits(n: int) -> tuple[int, int, int, int]:
    """Return (units, tens, hundreds, thousands) of n."""
    return n % 10, n // 10 % 10, n // 100 % 10, n // 1000 % 10


def place_point(point: tuple[int, int], place: int) -> tuple[int, int]:
    """Reflect a units-quadrant point into the quadrant of ``place`` (0..3)."""
    x, y = point
    if place in (1, 3):  # tens, thousands: mirror about the stem
        x = GRID_MAX_X - x
    if place in (2, 3):  # hundreds, thousands: mirror about the midline
        y = GRID_MAX_Y - y
    return x, y


def motif(digit: int, place: int) -> list[Segment]:
    """Segments for one digit (0..9) in one place; 0 draws nothing."""
    return [(place_point(a, place), place_point(b, place)) for a, b in UNIT_MOTIFS.get(digit, ())]


def encode_segments(n: int) -> list[Segment]:
    if type(n) is not int:
        raise TypeError(f"expected int, got {type(n).__name__}")
    if not MIN_VALUE <= n <= MAX_VALUE:
        raise ValueError(f"{n} is outside {MIN_VALUE}..{MAX_VALUE}")
    segments = [STEM]
    for place, digit in enumerate(digits(n)):
        segments.extend(motif(digit, place))
    return segments


def encode(n: int) -> dict:
    """Return the contract-v1 JSON object for n."""
    return {"segments": [[list(a), list(b)] for a, b in encode_segments(n)]}


def main(argv: list[str]) -> int:
    for arg in argv:
        print(json.dumps(encode(int(arg)), separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
