"""Unit tests for the reference encoder (structure, boundaries, full domain)."""

import json

import pytest

from judge import reference
from judge.geometry import STEM_EDGES, normalize, normalize_json


def edges(n):
    return normalize(reference.encode(n))


def motif_edges(n):
    return edges(n) - STEM_EDGES


@pytest.mark.parametrize("n, expected", [
    (1, (1, 0, 0, 0)),
    (1986, (6, 8, 9, 1)),
    (7085, (5, 8, 0, 7)),
    (9999, (9, 9, 9, 9)),
    (1000, (0, 0, 0, 1)),
])
def test_digit_decomposition(n, expected):
    assert reference.digits(n) == expected


@pytest.mark.parametrize("bad", [0, -1, 10000, 123456])
def test_out_of_range_is_rejected(bad):
    with pytest.raises(ValueError, match="outside 1..9999"):
        reference.encode(bad)


@pytest.mark.parametrize("bad", [1.0, "1", True, None])
def test_non_integer_is_rejected(bad):
    with pytest.raises(TypeError):
        reference.encode(bad)


def test_zero_digits_add_nothing():
    assert edges(1000) | edges(1) == edges(1001)
    assert motif_edges(1001) == motif_edges(1000) | motif_edges(1)


def test_glyph_is_union_of_its_place_values():
    for n in (1986, 4723, 9433, 8888):
        u, t, h, k = reference.digits(n)
        parts = [v for v in (u, 10 * t, 100 * h, 1000 * k) if v]
        assert edges(n) == frozenset().union(*(edges(p) for p in parts))


def test_quadrants_are_disjoint():
    for d in range(1, 10):
        quads = [motif_edges(d * 10**p) for p in range(4)]
        for i in range(4):
            for j in range(i + 1, 4):
                assert not quads[i] & quads[j], (d, i, j)


def test_tens_mirror_units_and_hundreds_flip_units():
    def mirror_x(e):
        return frozenset(tuple(sorted(((2 - x, y) for x, y in edge))) for edge in e)

    def flip_y(e):
        return frozenset(tuple(sorted(((x, 3 - y) for x, y in edge))) for edge in e)

    for d in range(1, 10):
        assert motif_edges(10 * d) == mirror_x(motif_edges(d))
        assert motif_edges(100 * d) == flip_y(motif_edges(d))
        assert motif_edges(1000 * d) == mirror_x(flip_y(motif_edges(d)))


def test_units_six_is_the_only_motif_detached_from_stem():
    # Units 6 is the only units motif with no point on the stem (x=1).
    detached = [d for d in range(1, 10) if all(x != 1 for e in motif_edges(d) for x, _ in e)]
    assert detached == [6]


def test_every_number_is_valid_and_distinct():
    seen = {}
    for n in range(1, 10000):
        obj = reference.encode(n)
        line = json.dumps(obj, separators=(",", ":"))
        e = normalize_json(line)
        assert e not in seen, f"{n} and {seen.get(e)} draw the same glyph"
        seen[e] = n
    assert len(seen) == 9999


def test_output_is_deterministic_and_compact():
    out = json.dumps(reference.encode(1), separators=(",", ":"))
    assert out == '{"segments":[[[1,0],[1,3]],[[1,0],[2,0]]]}'
    assert reference.encode(1986) == reference.encode(1986)
