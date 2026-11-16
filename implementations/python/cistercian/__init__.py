"""Cistercian numeral encoder (Python implementation).

Each digit is a combination of five named strokes. A stroke is defined once,
in coordinates local to a quadrant: ``across`` runs from the stem (0) to the
outer edge (1), and ``along`` runs from the end of the stem (0) one unit
toward the middle (1). A quadrant knows where its stem end is and in which
directions "across" and "along" point, so placing a stroke is a single affine
map rather than a table per quadrant.

    >>> encode(1)
    {'segments': [[[1, 0], [1, 3]], [[1, 0], [2, 0]]]}
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

__all__ = ["encode", "Quadrant", "Stroke", "DIGIT_STROKES"]

Point = tuple[int, int]
Segment = tuple[Point, Point]

STEM: Segment = ((1, 0), (1, 3))


class Stroke(Enum):
    """Stroke shapes as ((across, along), (across, along)) in local coordinates."""

    END_BAR = ((0, 0), (1, 0))        # bar at the end of the stem
    INNER_BAR = ((0, 1), (1, 1))      # bar one unit toward the middle
    DIAGONAL_IN = ((0, 0), (1, 1))    # from the stem end, slanting inward
    DIAGONAL_OUT = ((0, 1), (1, 0))   # from the stem, slanting out to the end corner
    OUTER = ((1, 0), (1, 1))          # outer edge, not touching the stem


DIGIT_STROKES: dict[int, tuple[Stroke, ...]] = {
    0: (),
    1: (Stroke.END_BAR,),
    2: (Stroke.INNER_BAR,),
    3: (Stroke.DIAGONAL_IN,),
    4: (Stroke.DIAGONAL_OUT,),
    5: (Stroke.END_BAR, Stroke.DIAGONAL_OUT),
    6: (Stroke.OUTER,),
    7: (Stroke.END_BAR, Stroke.OUTER),
    8: (Stroke.INNER_BAR, Stroke.OUTER),
    9: (Stroke.END_BAR, Stroke.INNER_BAR, Stroke.OUTER),
}


@dataclass(frozen=True)
class Quadrant:
    stem_end: Point   # where the stem ends on this quadrant's side
    across: int       # +1: digits extend right of the stem, -1: left
    along: int        # +1: toward the middle is downward, -1: upward

    def place(self, stroke: Stroke) -> Segment:
        (a1, b1), (a2, b2) = stroke.value
        x0, y0 = self.stem_end
        return ((x0 + self.across * a1, y0 + self.along * b1),
                (x0 + self.across * a2, y0 + self.along * b2))


# Units, tens, hundreds, thousands (SPECIFICATION.md section 2).
QUADRANTS = (
    Quadrant(stem_end=(1, 0), across=+1, along=+1),
    Quadrant(stem_end=(1, 0), across=-1, along=+1),
    Quadrant(stem_end=(1, 3), across=+1, along=-1),
    Quadrant(stem_end=(1, 3), across=-1, along=-1),
)


def encode(number: int) -> dict[str, list]:
    """Return ``{"segments": [...]}`` for an integer from 1 to 9999."""
    if isinstance(number, bool) or not isinstance(number, int):
        raise TypeError(f"expected an int, got {type(number).__name__}")
    if not 1 <= number <= 9999:
        raise ValueError(f"{number} is outside 1..9999")

    segments = [STEM]
    for quadrant, digit in zip(QUADRANTS, reversed(f"{number:04d}")):
        segments += [quadrant.place(stroke) for stroke in DIGIT_STROKES[int(digit)]]
    return {"segments": [[list(a), list(b)] for a, b in segments]}
