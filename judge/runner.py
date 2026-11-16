"""Conformance runner: checks an implementation's CLI against the reference.

    python -m judge.runner --language python
    python -m judge.runner --all

For each implementation directory under implementations/ with a
manifest.json (see SPECIFICATION.md section 12) the runner:

1. checks that required tools are installed (else: UNAVAILABLE, never PASS);
2. runs the build command once, if any;
3. starts the program ONCE with all 9,999 numbers in order, then once more in
   a seeded shuffled order, and compares every output line with the
   reference after normalization;
4. runs the invalid-input cases from SPECIFICATION.md section 11, each in its
   own process.

Failure categories: requirements, build, protocol, contract, geometry.
Commands come from maintainer-controlled manifests and are executed as
argument lists, never through a shell.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

from judge import reference
from judge.geometry import Edge, GeometryError, describe_difference, format_edges, normalize, normalize_json

ROOT = Path(__file__).resolve().parent.parent
IMPLEMENTATIONS = ROOT / "implementations"
DOMAIN = range(reference.MIN_VALUE, reference.MAX_VALUE + 1)

DEFAULT_SEED = 1986
BUILD_TIMEOUT = 600.0
BATCH_TIMEOUT = 120.0
CASE_TIMEOUT = 20.0
MAX_REPORTED = 10          # failures shown per category
STDERR_EXCERPT = 1500      # characters

# Lines that must be rejected (SPECIFICATION.md section 11). Each is sent
# alone, followed by "\n", as raw bytes.
INVALID_LINES: tuple[bytes, ...] = (
    b"0", b"00", b"10000", b"99999", b"-1", b"+1", b"01", b"0001",
    b"1.0", b"1e3", b"1_000", b"abc", b"", b" 1", b"1 ", b"\t1", b"1\r",
    b"1\x00", "１".encode(), "١".encode(), b"\xff",
)


# ------------------------------------------------------------------ manifest

class ManifestError(ValueError):
    pass


@dataclass
class Requirement:
    tool: str
    min_version: str | None = None
    version_args: list[str] = field(default_factory=lambda: ["--version"])


@dataclass
class Manifest:
    name: str
    directory: Path
    language: str
    run: list[str]
    build: list[str] | None
    requires: list[Requirement]


def _argv(value, where: str) -> list[str]:
    if not isinstance(value, list) or not value or not all(isinstance(s, str) and s for s in value):
        raise ManifestError(f"{where} must be a non-empty list of non-empty strings")
    return value


def load_manifest(directory: Path) -> Manifest:
    path = directory / "manifest.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"{path}: {exc}") from None
    if not isinstance(data, dict):
        raise ManifestError(f"{path}: must be a JSON object")
    unknown = set(data) - {"language", "run", "build", "requires"}
    if unknown:
        raise ManifestError(f"{path}: unknown key(s) {sorted(unknown)}")
    if not isinstance(data.get("language"), str) or not data["language"]:
        raise ManifestError(f"{path}: 'language' must be a non-empty string")
    run = _argv(data.get("run"), f"{path}: 'run'")
    build = _argv(data["build"], f"{path}: 'build'") if data.get("build") is not None else None
    requires = []
    for i, req in enumerate(data.get("requires", [])):
        where = f"{path}: requires[{i}]"
        if not isinstance(req, dict) or not isinstance(req.get("tool"), str) or not req["tool"]:
            raise ManifestError(f"{where} must be an object with a 'tool' string")
        if set(req) - {"tool", "min_version", "version_args"}:
            raise ManifestError(f"{where}: unknown key(s) {sorted(set(req) - {'tool', 'min_version', 'version_args'})}")
        min_version = req.get("min_version")
        if min_version is not None and not re.fullmatch(r"\d+(\.\d+)*", str(min_version)):
            raise ManifestError(f"{where}: 'min_version' must look like 3.10")
        version_args = _argv(req.get("version_args", ["--version"]), f"{where}: 'version_args'")
        requires.append(Requirement(req["tool"], min_version, version_args))
    return Manifest(directory.name, directory, data["language"], run, build, requires)


def discover() -> list[Path]:
    return sorted(p.parent for p in IMPLEMENTATIONS.glob("*/manifest.json"))


# ------------------------------------------------------------------ processes

@dataclass
class Completed:
    returncode: int | None    # None on timeout
    stdout: bytes
    stderr: bytes
    seconds: float

    @property
    def timed_out(self) -> bool:
        return self.returncode is None


def execute(argv: list[str], cwd: Path, stdin: bytes, timeout: float) -> Completed:
    start = time.monotonic()
    try:
        proc = subprocess.run(argv, cwd=cwd, input=stdin, capture_output=True, timeout=timeout)
        return Completed(proc.returncode, proc.stdout, proc.stderr, time.monotonic() - start)
    except subprocess.TimeoutExpired as exc:
        return Completed(None, exc.stdout or b"", exc.stderr or b"", time.monotonic() - start)
    except OSError as exc:
        return Completed(127, b"", f"cannot start {argv[0]!r}: {exc}".encode(), time.monotonic() - start)


def excerpt(stderr: bytes) -> str:
    text = stderr.decode("utf-8", errors="replace").strip()
    if len(text) > STDERR_EXCERPT:
        text = "..." + text[-STDERR_EXCERPT:]
    return text


def version_tuple(text: str) -> tuple[int, ...]:
    return tuple(int(p) for p in text.split("."))


# ------------------------------------------------------------------ checking

@dataclass
class Failure:
    category: str   # requirements | build | protocol | contract | geometry
    message: str


@dataclass
class Result:
    name: str
    language: str
    status: str = "PASS"            # PASS | FAIL | UNAVAILABLE
    failures: list[Failure] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


_EXPECTED: dict[int, frozenset[Edge]] = {}


def expected(n: int) -> frozenset[Edge]:
    if n not in _EXPECTED:
        _EXPECTED[n] = normalize(reference.encode(n))
    return _EXPECTED[n]


def check_requirements(m: Manifest) -> tuple[list[Failure], list[str]]:
    failures, notes = [], []
    for req in m.requires:
        if shutil.which(req.tool) is None:
            failures.append(Failure("requirements", f"required tool {req.tool!r} not found on PATH"))
            continue
        if req.min_version is None:
            notes.append(f"{req.tool}: found")
            continue
        proc = execute([req.tool, *req.version_args], m.directory, b"", CASE_TIMEOUT)
        found = re.search(r"(\d+(?:\.\d+)+)", (proc.stdout + proc.stderr).decode("utf-8", "replace"))
        if not found:
            failures.append(Failure("requirements", f"cannot determine {req.tool} version"))
        elif version_tuple(found.group(1)) < version_tuple(req.min_version):
            failures.append(Failure("requirements",
                                    f"{req.tool} {found.group(1)} is older than required {req.min_version}"))
        else:
            notes.append(f"{req.tool} {found.group(1)} (>= {req.min_version})")
    return failures, notes


def split_output(stdout: bytes) -> tuple[list[str], list[str]]:
    """Split stdout into response lines; return (lines, protocol problems)."""
    problems = []
    try:
        text = stdout.decode("utf-8")
    except UnicodeDecodeError as exc:
        return [], [f"stdout is not valid UTF-8: {exc}"]
    if "\r" in text:
        problems.append("stdout contains carriage returns; lines must end with \\n only")
    if text and not text.endswith("\n"):
        problems.append("last stdout line is not terminated by \\n")
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return lines, problems


def compare_lines(numbers: list[int], lines: list[str], label: str) -> list[Failure]:
    failures = []
    for n, line in zip(numbers, lines):
        try:
            actual = normalize_json(line)
        except GeometryError as exc:
            failures.append(Failure("contract", f"{label}: input {n}: {exc}; output was {line[:160]!r}"))
            continue
        if actual != expected(n):
            failures.append(Failure("geometry", (
                f"{label}: input {n}: {describe_difference(expected(n), actual)}\n"
                f"      expected: {format_edges(expected(n))}\n"
                f"      actual:   {format_edges(actual)}")))
    return failures


def check_batch(m: Manifest, numbers: list[int], label: str, timeout: float) -> tuple[list[Failure], bool]:
    """Run one batch; return (failures, timed_out)."""
    stdin = "".join(f"{n}\n" for n in numbers).encode()
    proc = execute(m.run, m.directory, stdin, timeout)
    failures = []
    if proc.timed_out:
        failures.append(Failure("protocol", f"{label}: timed out after {timeout:g}s"))
    elif proc.returncode != 0:
        failures.append(Failure("protocol", f"{label}: exit status {proc.returncode} (expected 0)"))
    lines, problems = split_output(proc.stdout)
    failures += [Failure("protocol", f"{label}: {p}") for p in problems]
    if len(lines) != len(numbers):
        failures.append(Failure("protocol",
                                f"{label}: expected {len(numbers)} output lines, got {len(lines)}"))
    failures += compare_lines(numbers, lines, label)
    if failures and proc.stderr.strip():
        failures.append(Failure("protocol", f"{label}: stderr:\n{excerpt(proc.stderr)}"))
    return failures, proc.timed_out


def check_invalid_inputs(m: Manifest, timeout: float = CASE_TIMEOUT) -> list[Failure]:
    failures = []

    def case(stdin: bytes, want_exit: int, want_numbers: list[int], want_line: int | None):
        label = f"stdin {stdin!r}"
        proc = execute(m.run, m.directory, stdin, timeout)
        if proc.timed_out:
            failures.append(Failure("protocol", f"{label}: timed out after {timeout:g}s"))
            return
        if proc.returncode != want_exit:
            failures.append(Failure("protocol", f"{label}: exit status {proc.returncode} (expected {want_exit})"))
        lines, problems = split_output(proc.stdout)
        failures.extend(Failure("protocol", f"{label}: {p}") for p in problems)
        if len(lines) != len(want_numbers):
            failures.append(Failure("protocol",
                                    f"{label}: expected {len(want_numbers)} stdout line(s), got {len(lines)}"))
        failures.extend(compare_lines(want_numbers, lines, label))
        if want_line is not None and f"line {want_line}" not in proc.stderr.decode("utf-8", "replace"):
            failures.append(Failure("protocol",
                                    f"{label}: stderr must mention 'line {want_line}', got {excerpt(proc.stderr)!r}"))

    for bad in INVALID_LINES:
        case(bad + b"\n", 2, [], 1)
    case(b"1\n1986\nabc\n9999\n", 2, [1, 1986], 3)      # output before the bad line, nothing after
    case(b"", 0, [], None)                               # empty input
    case(b"7085", 0, [7085], None)                       # no trailing newline
    case(b"1986\n1986\n", 0, [1986, 1986], None)         # repeated input
    return failures


def evaluate(directory: Path, seed: int = DEFAULT_SEED, batch_timeout: float = BATCH_TIMEOUT,
             case_timeout: float = CASE_TIMEOUT, numbers: list[int] | None = None) -> Result:
    m = load_manifest(directory)
    result = Result(m.name, m.language)
    req_failures, result.notes = check_requirements(m)
    if req_failures:
        result.status, result.failures = "UNAVAILABLE", req_failures
        return result

    if m.build:
        proc = execute(m.build, m.directory, b"", BUILD_TIMEOUT)
        if proc.returncode != 0:
            why = "timed out" if proc.timed_out else f"exit status {proc.returncode}"
            result.status = "FAIL"
            result.failures.append(Failure("build", f"build {m.build} failed ({why}):\n{excerpt(proc.stderr)}"))
            return result
        result.notes.append(f"build ok ({proc.seconds:.1f}s)")

    in_order = list(numbers) if numbers is not None else list(DOMAIN)
    shuffled = in_order[:]
    random.Random(seed).shuffle(shuffled)
    start = time.monotonic()
    failures, timed_out = check_batch(m, in_order, "ordered batch", batch_timeout)
    result.failures += failures
    if timed_out:  # a hanging program would only time out again; stop here
        result.status = "FAIL"
        result.notes.append("stopped after the ordered batch timed out")
        return result
    result.failures += check_batch(m, shuffled, f"shuffled batch (seed {seed})", batch_timeout)[0]
    result.notes.append(f"{len(in_order)} numbers x 2 batches ({time.monotonic() - start:.1f}s)")
    result.failures += check_invalid_inputs(m, case_timeout)
    result.notes.append(f"{len(INVALID_LINES) + 4} invalid-input / edge cases")
    if result.failures:
        result.status = "FAIL"
    return result


# ------------------------------------------------------------------ reporting

def report(result: Result, out=None) -> None:
    out = out or sys.stdout
    print(f"== {result.name} ({result.language}) ==", file=out)
    for note in result.notes:
        print(f"  {note}", file=out)
    by_category: dict[str, list[Failure]] = {}
    for f in result.failures:
        by_category.setdefault(f.category, []).append(f)
    for category, items in by_category.items():
        print(f"  {category} failures: {len(items)}", file=out)
        for f in items[:MAX_REPORTED]:
            print(f"    - {f.message}", file=out)
        if len(items) > MAX_REPORTED:
            print(f"    ... and {len(items) - MAX_REPORTED} more", file=out)
    print(f"{result.status} {result.name}", file=out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m judge.runner", description=__doc__.split("\n\n")[0])
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--language", action="append", metavar="NAME",
                        help="implementation directory name under implementations/ (repeatable)")
    target.add_argument("--all", action="store_true", help="every implementation with a manifest.json")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="seed for the shuffled batch")
    parser.add_argument("--timeout", type=float, default=BATCH_TIMEOUT, help="seconds per 9,999-number batch")
    args = parser.parse_args(argv)

    dirs = discover() if args.all else [IMPLEMENTATIONS / name for name in args.language]
    if not dirs:
        print("no implementations found", file=sys.stderr)
        return 1
    results = []
    for d in dirs:
        try:
            result = evaluate(d, seed=args.seed, batch_timeout=args.timeout)
        except ManifestError as exc:
            result = Result(d.name, "?", "FAIL", [Failure("build", f"invalid manifest: {exc}")])
        report(result)
        results.append(result)

    print("\nSummary:")
    for r in results:
        print(f"  {r.status:<11} {r.name}")
    if any(r.status == "FAIL" for r in results):
        return 1
    if any(r.status == "UNAVAILABLE" for r in results):
        print("Some implementations were NOT tested because a toolchain is unavailable.")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
