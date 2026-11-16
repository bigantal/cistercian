"""The reference encoder against independent, hand-transcribed fixtures.

Also proves the fixtures have teeth: every possible digit-shape mutation of
the reference table (including the historical 6/8 mix-up) must be caught.
"""

import pytest

from judge import reference
from judge.geometry import describe_difference, normalize

from .conftest import fixture_edges, load_fixtures

FIXTURES = load_fixtures()
ALL_ENTRIES = FIXTURES["motifs"] + FIXTURES["composites"]


def failures(entries):
    bad = []
    for entry in entries:
        diff = describe_difference(fixture_edges(entry), normalize(reference.encode(entry["value"])))
        if diff:
            bad.append(f"{entry['value']} ({entry['source']}): {diff}")
    return bad


def test_fixture_file_covers_every_digit_in_every_quadrant():
    values = sorted(e["value"] for e in FIXTURES["motifs"])
    assert values == sorted(d * 10**p for d in range(1, 10) for p in range(4))


def test_fixture_entries_are_well_formed():
    values = [e["value"] for e in ALL_ENTRIES]
    assert len(values) == len(set(values)), "duplicate fixture values"
    for entry in ALL_ENTRIES:
        assert entry["source"] in FIXTURES["sources"], entry
        fixture_edges(entry)  # raises GeometryError on malformed strokes


@pytest.mark.parametrize("entry", ALL_ENTRIES, ids=lambda e: f"{e['value']}-{e['source']}")
def test_reference_matches_fixture(entry):
    expected = fixture_edges(entry)
    actual = normalize(reference.encode(entry["value"]))
    assert actual == expected, describe_difference(expected, actual)


def test_king_composites_are_present():
    king = {e["value"] for e in FIXTURES["composites"] if e["source"] == "king-2001-p36"}
    assert king == {1992, 4723, 6859, 7085, 8971, 9938}


def test_swapping_six_and_eight_is_detected(monkeypatch):
    table = dict(reference.UNIT_MOTIFS)
    table[6], table[8] = table[8], table[6]
    monkeypatch.setattr(reference, "UNIT_MOTIFS", table)
    bad = failures(FIXTURES["composites"])
    assert any(line.startswith("1986 ") for line in bad), bad
    assert any(line.startswith("6859 ") for line in bad), bad


@pytest.mark.parametrize("digit", range(1, 10))
def test_any_wrong_digit_shape_is_detected_by_independent_fixtures(monkeypatch, digit):
    """Replace one digit's motif by every other digit's motif; fixtures must notice."""
    for other in range(1, 10):
        if other == digit:
            continue
        table = dict(reference.UNIT_MOTIFS)
        table[digit] = reference.UNIT_MOTIFS[other]
        monkeypatch.setattr(reference, "UNIT_MOTIFS", table)
        assert failures(FIXTURES["motifs"]), f"motif {digit}->{other} not detected"
        # The composites alone (King + reviewed) must also catch it when the digit occurs in them.
        if any(str(digit) in str(e["value"]) for e in FIXTURES["composites"]):
            assert failures(FIXTURES["composites"]), f"composite fixtures missed {digit}->{other}"


def test_wrong_quadrant_reflection_is_detected(monkeypatch):
    original = reference.place_point
    # Bug: hundreds treated like tens (mirror x instead of flipping y).
    monkeypatch.setattr(reference, "place_point",
                        lambda p, place: original(p, 1 if place == 2 else place))
    assert failures(ALL_ENTRIES)
