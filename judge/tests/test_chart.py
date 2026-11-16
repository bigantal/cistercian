"""Generated SVGs must be regenerated whenever the reference changes."""

import importlib.util

import pytest

from .conftest import ROOT

spec = importlib.util.spec_from_file_location("render_digit_chart", ROOT / "scripts" / "render_digit_chart.py")
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)


@pytest.mark.parametrize("path", sorted(render.outputs()), ids=lambda p: p.name)
def test_generated_svg_is_up_to_date(path):
    assert path.read_text(encoding="utf-8") == render.outputs()[path], "run: python3 scripts/render_digit_chart.py"
