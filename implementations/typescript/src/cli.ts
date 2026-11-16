/**
 * CLI adapter (SPECIFICATION.md section 11): one integer per stdin line,
 * one compact JSON object per stdout line; exit 2 at the first invalid line.
 *
 * Lines are split on "\n" only and checked as raw bytes (latin1 maps each
 * byte to one character), so "\r", non-ASCII digits and invalid UTF-8 are
 * all rejected rather than normalized.
 */

import { encode } from "./encoder.ts";

const VALID_LINE = /^[1-9][0-9]{0,3}$/;
const EXIT_INVALID_INPUT = 2;

function fail(lineNumber: number, line: string): void {
  process.stderr.write(
    `error: line ${lineNumber}: expected an integer from 1 to 9999 ` +
      `(digits only, no sign, spaces or leading zeros), got ${JSON.stringify(line)}\n`,
  );
  process.exitCode = EXIT_INVALID_INPUT;
}

async function main(): Promise<void> {
  let pending = "";
  let lineNumber = 0;

  const answer = (lines: string[]): boolean => {
    let out = "";
    for (const line of lines) {
      lineNumber += 1;
      if (!VALID_LINE.test(line)) {
        process.stdout.write(out);
        fail(lineNumber, line);
        return false;
      }
      out += JSON.stringify(encode(Number(line))) + "\n";
    }
    process.stdout.write(out);
    return true;
  };

  for await (const chunk of process.stdin) {
    const lines = (pending + (chunk as Buffer).toString("latin1")).split("\n");
    pending = lines.pop() ?? "";
    if (!answer(lines)) return;
  }
  if (pending !== "") answer([pending]);
}

await main();
