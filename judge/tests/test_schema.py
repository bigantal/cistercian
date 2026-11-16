"""schema/numeral.schema.json agrees with the geometry validator on structure."""

import json

import pytest

from judge import reference

from .conftest import ROOT

jsonschema = pytest.importorskip("jsonschema", reason="install requirements-dev.txt to run schema tests")

SCHEMA = json.loads((ROOT / "schema" / "numeral.schema.json").read_text(encoding="utf-8"))
VALIDATOR = jsonschema.Draft202012Validator(SCHEMA)


def test_schema_is_a_valid_draft_2020_12_schema():
    jsonschema.Draft202012Validator.check_schema(SCHEMA)


def test_reference_output_matches_schema_for_every_number():
    for n in range(1, 10000):
        errors = list(VALIDATOR.iter_errors(reference.encode(n)))
        assert not errors, (n, errors[0].message)


@pytest.mark.parametrize("numeral", [
    [],
    {},
    {"segments": []},
    {"segments": [[[1, 0], [1, 3]]], "extra": 1},
    {"segments": [[[1, 0], [1, 3], [1, 2]]]},
    {"segments": [[[1, 0]]]},
    {"segments": [[[1, 0, 0], [1, 3]]]},
    {"segments": [[[3, 0], [1, 3]]]},
    {"segments": [[[1, 4], [1, 3]]]},
    {"segments": [[[-1, 0], [1, 3]]]},
    {"segments": [[[1.5, 0], [1, 3]]]},
    {"segments": [[["1", 0], [1, 3]]]},
    {"segments": [[[True, 0], [1, 3]]]},
])
def test_schema_rejects_structurally_invalid_output(numeral):
    assert not VALIDATOR.is_valid(numeral)


def test_schema_alone_is_not_enough():
    """Documented gaps that the semantic validator (judge.geometry) must cover."""
    for numeral in (
        {"segments": [[[1, 0], [2, 0]]]},            # no stem
        {"segments": [[[1, 0], [1, 3]], [[2, 0], [2, 0]]]},  # zero length
        {"segments": [[[1, 0], [1, 3]], [[0, 0], [2, 1]]]},  # bad slope
        {"segments": [[[1.0, 0], [1, 3]]]},           # 1.0 counts as integer in JSON Schema
    ):
        assert VALIDATOR.is_valid(numeral)
