# Cistercian — polyglot numeral playground

Medieval Cistercian numerals write any integer from 1 to 9,999 as a single glyph: four digit motifs arranged around a vertical stem. This repository defines the glyph geometry precisely and tests encoders written in several languages against it.

> **Status:** work in progress (Stage 1: contract, normalizer, reference encoder). The full README arrives with the website and CI stages.

- [SPECIFICATION.md](SPECIFICATION.md): convention, grid, digit table and JSON contract v1
- [docs/references.md](docs/references.md): historical sources and variants
- [docs/digit-chart.svg](docs/digit-chart.svg): every digit in every quadrant, generated from the reference

## Running the tests (macOS / Linux)

You need Python 3.10 or later.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest            # all judge tests
```

Print the reference geometry of a number:

```bash
python3 -m judge.reference 1986
```

After any change to `judge/reference.py`, regenerate the chart:

```bash
python3 scripts/render_digit_chart.py
```

The test suite fails if you forget.
