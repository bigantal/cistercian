"""The runner detects and reports every class of failure, using fake implementations."""

import json
import sys
from pathlib import Path

import pytest

from judge import runner

FAKE = Path(__file__).with_name("fake_impl.py")
SMALL = list(range(1, 200)) + [1986, 4723, 9999]   # keeps fake runs fast where possible


def make_impl(tmp_path: Path, mode: str, **manifest) -> Path:
    directory = tmp_path / mode
    directory.mkdir()
    data = {"language": f"Fake ({mode})", "run": [sys.executable, str(FAKE), mode]}
    data.update(manifest)
    (directory / "manifest.json").write_text(json.dumps(data))
    return directory


def evaluate(tmp_path, mode, numbers=SMALL, **kwargs):
    return runner.evaluate(make_impl(tmp_path, mode), numbers=numbers, **kwargs)


def categories(result):
    return {f.category for f in result.failures}


def messages(result):
    return "\n".join(f.message for f in result.failures)


# ------------------------------------------------------------- passing

def test_correct_fake_passes_full_domain(tmp_path):
    result = evaluate(tmp_path, "good", numbers=None)
    assert result.status == "PASS", messages(result)


def test_reversed_and_split_segments_are_accepted(tmp_path):
    result = evaluate(tmp_path, "reversed-and-split")
    assert result.status == "PASS", messages(result)


# ------------------------------------------------------------- geometry / contract

def test_wrong_digit_shape_gives_actionable_report(tmp_path, capsys):
    result = evaluate(tmp_path, "wrong-six")
    assert result.status == "FAIL"
    assert categories(result) == {"geometry"}
    text = messages(result)
    assert "input 6: missing edges: (none); extra edges: (1,1)-(2,1)" in text
    assert "input 1986:" in text
    runner.report(result)
    out = capsys.readouterr().out
    assert "geometry failures:" in out and "FAIL wrong-six" in out


@pytest.mark.parametrize("mode, needle", [
    ("extra-field", "unexpected field(s) ['value']"),
    ("bad-json", "input 42: invalid JSON"),
    ("no-stem", "stem (1,0)-(1,3) is incomplete"),
])
def test_contract_violations(tmp_path, mode, needle):
    result = evaluate(tmp_path, mode)
    assert result.status == "FAIL"
    assert "contract" in categories(result)
    assert needle in messages(result)


# ------------------------------------------------------------- protocol

@pytest.mark.parametrize("mode, needle", [
    ("banner", "expected 202 output lines, got 203"),
    ("missing-last", "expected 202 output lines, got 201"),
    ("extra-line", "expected 202 output lines, got 203"),
    ("stateful", "output lines, got"),
    ("crlf", "carriage returns"),
    ("crash", "exit status 1 (expected 0)"),
    ("exit-1-on-invalid", "exit status 1 (expected 2)"),
    ("no-line-number", "stderr must mention 'line 1'"),
    ("lenient", "stdin b'0\\n': exit status 0 (expected 2)"),
])
def test_protocol_violations(tmp_path, mode, needle):
    numbers = None if mode == "stateful" else SMALL
    result = evaluate(tmp_path, mode, numbers=numbers)
    assert result.status == "FAIL"
    assert "protocol" in categories(result)
    assert needle in messages(result)


def test_crash_report_includes_stderr(tmp_path):
    result = evaluate(tmp_path, "crash")
    assert "RuntimeError: simulated crash" in messages(result)


def test_timeout_is_reported(tmp_path):
    result = evaluate(tmp_path, "hang", batch_timeout=1, case_timeout=1, numbers=[1])
    assert result.status == "FAIL"
    assert "ordered batch: timed out after 1s" in messages(result)
    assert "stopped after the ordered batch timed out" in result.notes


def test_lenient_parsing_is_caught_for_each_kind_of_bad_line(tmp_path):
    text = messages(evaluate(tmp_path, "lenient"))
    for bad in (b"0", b"10000", b"-1", b"01", b" 1", b"1_000", "１".encode()):
        stdin = bad + b"\n"
        assert f"stdin {stdin!r}: exit status 0 (expected 2)" in text


# ------------------------------------------------------------- environment / manifest

def test_missing_toolchain_is_unavailable_not_pass(tmp_path):
    impl = make_impl(tmp_path, "good", requires=[{"tool": "no-such-tool-cistercian"}])
    result = runner.evaluate(impl, numbers=SMALL)
    assert result.status == "UNAVAILABLE"
    assert categories(result) == {"requirements"}


def test_too_old_toolchain_is_unavailable(tmp_path):
    impl = make_impl(tmp_path, "good", requires=[{"tool": "python3", "min_version": "99.0"}])
    result = runner.evaluate(impl, numbers=SMALL)
    assert result.status == "UNAVAILABLE"
    assert "older than required 99.0" in messages(result)


def test_build_failure_stops_evaluation(tmp_path):
    impl = make_impl(tmp_path, "good",
                     build=[sys.executable, "-c", "import sys; sys.stderr.write('compile error'); sys.exit(3)"])
    result = runner.evaluate(impl, numbers=SMALL)
    assert result.status == "FAIL"
    assert categories(result) == {"build"}
    assert "exit status 3" in messages(result) and "compile error" in messages(result)


def test_unstartable_command_is_reported(tmp_path):
    impl = make_impl(tmp_path, "good", run=["./does-not-exist"])
    result = runner.evaluate(impl, numbers=[1])
    assert result.status == "FAIL"
    assert "cannot start './does-not-exist'" in messages(result)


@pytest.mark.parametrize("manifest, needle", [
    ({"run": ["x"]}, "'language' must be"),
    ({"language": "X"}, "'run' must be"),
    ({"language": "X", "run": "python3 main.py"}, "'run' must be"),
    ({"language": "X", "run": ["x"], "shell": True}, "unknown key(s) ['shell']"),
    ({"language": "X", "run": ["x"], "requires": [{"tool": "x", "min_version": "new"}]}, "min_version"),
])
def test_invalid_manifest_is_rejected(tmp_path, manifest, needle):
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(runner.ManifestError, match=__import__("re").escape(needle)):
        runner.load_manifest(tmp_path)


def test_cli_exit_codes(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(runner, "IMPLEMENTATIONS", tmp_path)
    monkeypatch.setattr(runner, "DOMAIN", range(1, 50))
    make_impl(tmp_path, "good")
    assert runner.main(["--language", "good"]) == 0
    make_impl(tmp_path, "wrong-six")
    assert runner.main(["--all"]) == 1
    capsys.readouterr()
    (tmp_path / "wrong-six" / "manifest.json").unlink()
    make_impl(tmp_path, "missing", requires=[{"tool": "no-such-tool-cistercian"}])
    assert runner.main(["--all"]) == 3
    assert "NOT tested" in capsys.readouterr().out


# ------------------------------------------------------------- independence

def test_implementations_do_not_use_judge_internals():
    for path in runner.IMPLEMENTATIONS.rglob("*"):
        if {"node_modules", "dist", "build", "target", "__pycache__"} & set(path.parts):
            continue
        if path.is_file() and path.suffix not in {".md", ".json"}:
            text = path.read_text(encoding="utf-8", errors="replace")
            assert "judge" not in text, f"{path} references the judge"
