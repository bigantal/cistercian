"""Contract and normalizer tests for judge.geometry (no reference encoder involved)."""

import pytest

from judge.geometry import (
    STEM_EDGES,
    GeometryError,
    describe_difference,
    format_edges,
    normalize,
    normalize_json,
)

STEM = [[1, 0], [1, 3]]
ONE = {"segments": [STEM, [[1, 0], [2, 0]]]}
ONE_EDGES = STEM_EDGES | {((1, 0), (2, 0))}


def n(*segments):
    return normalize({"segments": list(segments)})


# ------------------------------------------------------------- equivalences

def test_stem_only_normalizes_to_three_unit_edges():
    assert n(STEM) == STEM_EDGES


def test_reversed_endpoints_are_equivalent():
    assert n([[1, 3], [1, 0]], [[2, 0], [1, 0]]) == ONE_EDGES


def test_segment_order_is_irrelevant():
    assert n([[1, 0], [2, 0]], STEM) == ONE_EDGES


def test_split_stem_equals_whole_stem():
    assert n([[1, 0], [1, 1]], [[1, 2], [1, 1]], [[1, 2], [1, 3]], [[1, 0], [2, 0]]) == ONE_EDGES


def test_overlapping_and_duplicate_segments_collapse():
    assert n(STEM, STEM, [[1, 0], [1, 2]], [[1, 0], [2, 0]], [[2, 0], [1, 0]]) == ONE_EDGES


def test_long_diagonal_expands_to_unit_edges():
    assert n(STEM, [[0, 0], [2, 2]]) - STEM_EDGES == {((0, 0), (1, 1)), ((1, 1), (2, 2))}


def test_long_horizontal_merges_with_split_pieces():
    assert n(STEM, [[0, 0], [2, 0]]) == n(STEM, [[0, 0], [1, 0]], [[2, 0], [1, 0]])


def test_disconnected_stroke_is_not_bridged():
    six = n(STEM, [[2, 0], [2, 1]])
    eight = n(STEM, [[2, 0], [2, 1]], [[1, 1], [2, 1]])
    assert six != eight
    assert ((1, 1), (2, 1)) not in six


def test_different_diagonals_differ():
    assert n(STEM, [[1, 0], [2, 1]]) != n(STEM, [[1, 1], [2, 0]])


def test_normalize_json_accepts_compact_line():
    assert normalize_json('{"segments":[[[1,0],[1,3]],[[1,0],[2,0]]]}') == ONE_EDGES


# ------------------------------------------------------------- rejections

@pytest.mark.parametrize("numeral, message", [
    ([STEM], "must be a JSON object"),
    ({}, "missing required field 'segments'"),
    ({"segments": [STEM], "value": 1}, "unexpected field(s) ['value']"),
    ({"segments": []}, "non-empty list"),
    ({"segments": STEM}, "segments[0]"),
    ({"segments": [[[1, 0]]]}, "a segment must be"),
    ({"segments": [[[1, 0], [1, 3], [2, 0]]]}, "a segment must be"),
    ({"segments": [[[1, 0, 0], [1, 3]]]}, "a point must be"),
    ({"segments": [[[1.0, 0], [1, 3]]]}, "x must be an integer"),
    ({"segments": [[[1, 0], [1, "3"]]]}, "y must be an integer"),
    ({"segments": [[[True, 0], [1, 3]]]}, "x must be an integer"),
    ({"segments": [[[3, 0], [1, 3]]]}, "x=3 is outside the grid 0..2"),
    ({"segments": [[[1, -1], [1, 3]]]}, "y=-1 is outside the grid 0..3"),
    ({"segments": [[[1, 0], [1, 4]]]}, "y=4 is outside the grid 0..3"),
    ({"segments": [STEM, [[2, 0], [2, 0]]]}, "zero-length"),
    ({"segments": [STEM, [[0, 0], [2, 1]]]}, "not horizontal, vertical or 45-degree"),
    ({"segments": [STEM, [[0, 0], [1, 2]]]}, "not horizontal, vertical or 45-degree"),
    ({"segments": [[[1, 0], [2, 0]]]}, "stem (1,0)-(1,3) is incomplete"),
    ({"segments": [[[1, 0], [1, 2]]]}, "missing (1,2)-(1,3)"),
    ({"segments": [[[1, 0], [1, 1]], [[1, 2], [1, 3]]]}, "missing (1,1)-(1,2)"),
])
def test_invalid_geometry_is_rejected_with_clear_message(numeral, message):
    with pytest.raises(GeometryError) as err:
        normalize(numeral)
    assert message in str(err.value)


@pytest.mark.parametrize("text, message", [
    ("", "invalid JSON"),
    ('{"segments":[[[1,0],[1,3]]]} trailing', "invalid JSON"),
    ('{"segments":[[[1,0],[1,3]]],"segments":[[[1,0],[1,3]]]}', "duplicate JSON key"),
    ('{"segments":[[[NaN,0],[1,3]]]}', "non-standard JSON constant NaN"),
    ('{"segments":[[[1e0,0],[1,3]]]}', "x must be an integer"),
])
def test_malformed_json_is_rejected(text, message):
    with pytest.raises(GeometryError) as err:
        normalize_json(text)
    assert message in str(err.value)


# ------------------------------------------------------------- diagnostics

def test_difference_report_lists_missing_and_extra_edges():
    six = n(STEM, [[2, 0], [2, 1]])
    eight = n(STEM, [[2, 0], [2, 1]], [[1, 1], [2, 1]])
    assert describe_difference(six, six) == ""
    assert describe_difference(eight, six) == "missing edges: (1,1)-(2,1); extra edges: (none)"


def test_format_edges_is_sorted_and_deterministic():
    assert format_edges(STEM_EDGES) == "(1,0)-(1,1) (1,1)-(1,2) (1,2)-(1,3)"
