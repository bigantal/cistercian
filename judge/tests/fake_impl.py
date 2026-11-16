"""A deliberately configurable fake implementation for testing the runner.

    python fake_impl.py MODE

"good" follows the protocol exactly (using the reference encoder); every other
mode breaks it in one specific way. Test-only code: real implementations must
never import the judge.
"""

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from judge import reference  # noqa: E402

MODE = sys.argv[1]
VALID = re.compile(rb"[1-9][0-9]{0,3}")


def encode(n: int) -> dict:
    obj = reference.encode(n)
    if MODE == "wrong-six" and n % 10 == 6:
        obj["segments"].append([[1, 1], [2, 1]])                 # units 6 drawn as 8
    if MODE == "extra-field":
        obj["value"] = n
    if MODE == "bad-json" and n == 42:
        return "{not json"
    if MODE == "no-stem":
        obj["segments"] = obj["segments"][1:] or [[[0, 0], [1, 0]]]
    if MODE == "reversed-and-split":                              # legal variation
        segs = [[b, a] for a, b in obj["segments"][1:]]
        obj["segments"] = [[[1, 3], [1, 2]], [[1, 0], [1, 2]]] + segs[::-1]
    return json.dumps(obj, separators=(",", ":"))


def main() -> int:
    if MODE == "banner":
        print("Cistercian encoder v1.0")
    if MODE == "hang":
        time.sleep(60)
    if MODE == "crlf":
        sys.stdout.reconfigure(newline="\r\n")
    count = 0
    for i, raw in enumerate(sys.stdin.buffer, 1):
        line = raw.rstrip(b"\n")
        if MODE == "lenient":
            line = line.strip()
            try:
                n = max(1, min(9999, int(line)))
            except ValueError:
                n = 1
            print(encode(n))
            continue
        if not VALID.fullmatch(line):
            if MODE == "exit-1-on-invalid":
                return 1
            if MODE == "no-line-number":
                print("error: bad input", file=sys.stderr)
                return 2
            print(f"error: line {i}: bad input", file=sys.stderr)
            return 2
        count += 1
        if MODE == "crash" and count == 100:
            raise RuntimeError("simulated crash")
        if MODE == "missing-last" and int(line) == 9999:
            continue
        print(encode(int(line)))
        if MODE == "stateful" and count > 5000:
            sys.stdout.write(encode(int(line)) + "\n")              # duplicates late lines
    if MODE == "extra-line":
        print(encode(1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
