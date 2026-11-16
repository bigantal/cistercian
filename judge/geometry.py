"""Validation and canonical normalization of numeral geometry (contract v1).

A numeral is a JSON object ``{"segments": [[[x1, y1], [x2, y2]], ...]}`` on the
integer grid x 0..2, y 0..3 (see SPECIFICATION.md section 8).

Normalization expands every segment into elementary unit edges and returns
them as a frozenset of undirected edges, so that segment order, endpoint
direction, collinear splitting/merging and duplicates do not matter, while
different drawings never compare equal.

Standard library only; this module never imports the reference encoder.
"""

from __future__ import annotations

import json
from math import gcd
from typing import Any

GRID_MAX_X = 2
GRID_MAX_Y = 3

Point = tuple[int, int]
Edge = tuple[Point, Point]  # endpoints in lexicographic order

STEM_EDGES: frozenset[Edge] = frozenset({((1, 0), (1, 1)), ((1, 1), (1, 2)), ((1, 2), (1, 3))})


class GeometryError(ValueError):
    """Raised when output violates the geometry contract."""


def parse_json(text: str) -> Any:
    """Parse one JSON document strictly: no duplicate keys, no NaN/Infinity."""

    def no_duplicates(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise GeometryError(f"duplicate JSON key {key!r}")
            obj[key] = value
        return obj

    def no_constants(name):
        raise GeometryError(f"non-standard JSON constant {name}")

    try:
        return json.loads(text, object_pairs_hook=no_duplicates, parse_constant=no_constants)
    except json.JSONDecodeError as exc:
        raise GeometryError(f"invalid JSON: {exc}") from None


def _point(value: Any, where: str) -> Point:
    if not isinstance(value, list) or len(value) != 2:
        raise GeometryError(f"{where}: a point must be a list [x, y], got {value!r}")
    for axis, coord, limit in (("x", value[0], GRID_MAX_X), ("y", value[1], GRID_MAX_Y)):
        # bool is a subclass of int in Python; JSON true/false are not coordinates.
        if type(coord) is not int:
            raise GeometryError(f"{where}: {axis} must be an integer, got {coord!r}")
        if not 0 <= coord <= limit:
            raise GeometryError(f"{where}: {axis}={coord} is outside the grid 0..{limit}")
    return value[0], value[1]


def parse_segments(numeral: Any) -> list[tuple[Point, Point]]:
    """Check the object shape and coordinates; return segments as tuples."""
    if not isinstance(numeral, dict):
        raise GeometryError(f"numeral must be a JSON object, got {type(numeral).__name__}")
    keys = set(numeral)
    if keys != {"segments"}:
        extra = sorted(keys - {"segments"})
        if extra:
            raise GeometryError(f"unexpected field(s) {extra}; only 'segments' is allowed")
        raise GeometryError("missing required field 'segments'")
    raw = numeral["segments"]
    if not isinstance(raw, list) or not raw:
        raise GeometryError("'segments' must be a non-empty list")
    segments = []
    for i, seg in enumerate(raw):
        if not isinstance(seg, list) or len(seg) != 2:
            raise GeometryError(f"segments[{i}]: a segment must be [[x1, y1], [x2, y2]], got {seg!r}")
        segments.append((_point(seg[0], f"segments[{i}][0]"), _point(seg[1], f"segments[{i}][1]")))
    return segments


def elementary_edges(segments: list[tuple[Point, Point]]) -> frozenset[Edge]:
    """Expand segments into canonical elementary edges (rejecting bad directions)."""
    edges: set[Edge] = set()
    for i, ((x1, y1), (x2, y2)) in enumerate(segments):
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            raise GeometryError(f"segments[{i}]: zero-length segment at ({x1},{y1})")
        g = gcd(abs(dx), abs(dy))
        sx, sy = dx // g, dy // g
        if abs(sx) > 1 or abs(sy) > 1:
            raise GeometryError(
                f"segments[{i}]: ({x1},{y1})-({x2},{y2}) is not horizontal, vertical or 45-degree diagonal"
            )
        for step in range(g):
            a = (x1 + step * sx, y1 + step * sy)
            b = (a[0] + sx, a[1] + sy)
            edges.add((a, b) if a < b else (b, a))
    return frozenset(edges)


def normalize(numeral: Any) -> frozenset[Edge]:
    """Validate a decoded numeral object and return its canonical edge set."""
    edges = elementary_edges(parse_segments(numeral))
    missing_stem = STEM_EDGES - edges
    if missing_stem:
        raise GeometryError(f"stem (1,0)-(1,3) is incomplete; missing {format_edges(missing_stem)}")
    return edges


def normalize_json(text: str) -> frozenset[Edge]:
    """Validate and normalize one JSON document (e.g. one line of CLI output)."""
    return normalize(parse_json(text))


def format_edges(edges) -> str:
    """Human-readable, deterministic listing such as '(1,0)-(2,0) (2,0)-(2,1)'."""
    if not edges:
        return "(none)"
    return " ".join(f"({a[0]},{a[1]})-({b[0]},{b[1]})" for a, b in sorted(edges))


def describe_difference(expected: frozenset[Edge], actual: frozenset[Edge]) -> str:
    """Explain how two edge sets differ; empty string if they are equal."""
    if expected == actual:
        return ""
    return (f"missing edges: {format_edges(expected - actual)}; "
            f"extra edges: {format_edges(actual - expected)}")
