"""CLI adapter: one integer per stdin line -> one JSON object per stdout line.

Protocol: SPECIFICATION.md section 11. Input is matched as raw bytes so that
inputs Python's int() would accept ("１", "1_000", " 1") are still rejected.
"""

import json
import re
import sys

from cistercian import encode

VALID_LINE = re.compile(rb"[1-9][0-9]{0,3}")
EXIT_INVALID_INPUT = 2


def main() -> int:
    out = sys.stdout
    for line_number, raw in enumerate(sys.stdin.buffer, start=1):
        line = raw[:-1] if raw.endswith(b"\n") else raw
        if not VALID_LINE.fullmatch(line):
            out.flush()
            print(f"error: line {line_number}: expected an integer from 1 to 9999 "
                  f"(digits only, no sign, spaces or leading zeros), got {line!r}", file=sys.stderr)
            return EXIT_INVALID_INPUT
        out.write(json.dumps(encode(int(line)), separators=(",", ":")) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
