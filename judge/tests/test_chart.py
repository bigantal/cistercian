"""docs/digit-chart.svg must be regenerated whenever the reference changes."""

import importlib.util

from .conftest import ROOT


def test_digit_chart_is_up_to_date():
    spec = importlib.util.spec_from_file_location("render_digit_chart", ROOT / "scripts" / "render_digit_chart.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    current = (ROOT / "docs" / "digit-chart.svg").read_text(encoding="utf-8")
    assert current == module.render_svg(), "run: python3 scripts/render_digit_chart.py"
