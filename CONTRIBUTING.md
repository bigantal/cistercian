# Contributing

Thanks for your interest! This is a small educational project. Contributions are welcome, especially new language implementations, corrections backed by historical sources, and improvements to clarity.

## Ground rules

- **The geometry contract is frozen.** That covers the grid, the digit table, the JSON format and the CLI protocol in [SPECIFICATION.md](SPECIFICATION.md). Any change to them needs a decision record in `docs/decisions/` and the maintainer's approval. Implementations adapt to the contract, never the other way round.
- **Fixtures are ground truth.** `fixtures/known-values.json` is transcribed by hand from sources and reviewed. Never regenerate it from code. If you believe a glyph is wrong, open an issue with a citation, page number included.
- **Keep it small.** Avoid frameworks, services or infrastructure that a change does not need.

## Adding a language

1. Create `implementations/<name>/` containing:
   - **An encoder library** that exposes a public function taking an integer and returning the contract-v1 geometry. Write it idiomatically for the language. It must not wrap, call or copy another implementation or the judge.
   - **A thin CLI adapter** that follows [§11 of the specification](SPECIFICATION.md#11-cli-protocol-every-implementation) exactly:
     - one number per stdin line in, and one compact JSON object per stdout line out;
     - at the first invalid line, write a diagnostic mentioning `line N` to stderr and exit with status 2;
     - nothing else on stdout.
   - **`manifest.json`** ([§12](SPECIFICATION.md#12-implementation-manifest)): the language name, required tools with minimum versions, an optional build command and the run command, each given as a list of arguments.
   - **`README.md`**: how to build and run it, and a few lines on its approach.
2. Run the shared suite until it passes:
   ```bash
   python3 -m judge.runner --language <name>
   ./scripts/test-all.sh
   ```
   Don't weaken the judge or change other implementations to make a new one pass.
3. Add a CI job, or a matrix entry, in `.github/workflows/test.yml` that installs the toolchain and runs the runner for your language.
4. Add a row to the table in `README.md`.

## Reporting a historical or geometric error

Open an issue that includes:

- the number, and which corner looks wrong;
- what you expected and your source: author, title, page, and the figure if possible;
- whether the source uses the same convention as this project (vertical stem, tens and units on top, thousands and hundreds below). Variants exist, and are listed in [docs/references.md](docs/references.md).

## Development setup

You need Python 3.10 or later. For TypeScript and the website, you also need Node.js 20.19 or later.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
./scripts/test-all.sh
```

If you change `judge/reference.py`, regenerate the SVGs with `python3 scripts/render_digit_chart.py`. The test suite fails if you forget.

## Pull requests

Pull requests from forks run the test workflow with read-only permissions and no secrets. A maintainer may need to approve the first run. Only `main` deploys the website.

By contributing, you agree that your contribution is licensed under the [MIT License](LICENSE).
