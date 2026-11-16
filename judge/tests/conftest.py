import json
from pathlib import Path

import pytest

from judge.geometry import STEM_EDGES, elementary_edges

ROOT = Path(__file__).resolve().parents[2]


def load_fixtures() -> dict:
    return json.loads((ROOT / "fixtures" / "known-values.json").read_text(encoding="utf-8"))


def fixture_edges(entry: dict):
    """Expected edge set of a fixture entry: its strokes plus the stem."""
    strokes = [tuple(tuple(p) for p in seg) for seg in entry["strokes"]]
    return elementary_edges(strokes) | STEM_EDGES


@pytest.fixture(scope="session")
def fixtures() -> dict:
    return load_fixtures()
