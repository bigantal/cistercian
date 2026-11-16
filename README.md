# Cistercian — polyglot numeral playground

Medieval Cistercian numerals write any integer from 1 to 9,999 as a single glyph: four digit motifs arranged around a vertical stem. This repository defines the glyph geometry precisely and tests encoders written in several languages against it.

> **Status:** work in progress (Stage 2: conformance runner and Python implementation). The full README arrives with the website and CI stages.

- [SPECIFICATION.md](SPECIFICATION.md): convention, grid, digit table and JSON contract v1
- [docs/references.md](docs/references.md): historical sources and variants
- [docs/digit-chart.svg](docs/digit-chart.svg): every digit in every quadrant, generated from the reference

## Running the tests (macOS / Linux)

You need Python 3.10 or later.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
./scripts/test-all.sh                         # everything below, with a summary
.venv/bin/python -m pytest                    # judge unit tests only
python3 -m judge.runner --language python     # one implementation, all 9,999 numbers
python3 -m judge.runner --all                 # every implementation
```

`test-all.sh` exits 0 when everything passes, 1 on any failure, and 3 when an implementation could not be tested because its toolchain is missing.

## Implementations

| Language | Directory | Toolchain |
|---|---|---|
| Python | [implementations/python](implementations/python) | Python ≥ 3.10, standard library only |

Each implementation is independent of the judge. It follows the CLI protocol and manifest format in [SPECIFICATION.md](SPECIFICATION.md) §11–12.

Print the reference geometry of a number:

```bash
python3 -m judge.reference 1986
```

After any change to `judge/reference.py`, regenerate the chart:

```bash
python3 scripts/render_digit_chart.py
```

The test suite fails if you forget.
