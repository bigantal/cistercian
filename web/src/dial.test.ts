import { describe, expect, it } from "vitest";

import { digitSegments, encode } from "cistercian-encoder";
import { digitsToNumber, numberToDigits, wheelSteps, wrapDigit, WHEEL_STEP_PX } from "./dial.ts";
import { toPixelLines } from "./render.ts";

describe("dial arithmetic", () => {
  it("wraps digits around like a drum", () => {
    expect([wrapDigit(10), wrapDigit(-1), wrapDigit(-11), wrapDigit(7)]).toEqual([0, 9, 9, 7]);
  });

  it("splits and joins numbers by place", () => {
    expect(numberToDigits(1986)).toEqual([1, 9, 8, 6]);
    expect(numberToDigits(42)).toEqual([0, 0, 4, 2]);
    for (const n of [1, 9, 42, 365, 1986, 7085, 9999]) {
      expect(digitsToNumber(numberToDigits(n))).toBe(n);
    }
  });

  it("turns accumulated scroll into whole steps, keeping the remainder", () => {
    expect(wheelSteps(WHEEL_STEP_PX - 1)).toEqual([0, WHEEL_STEP_PX - 1]);
    expect(wheelSteps(WHEEL_STEP_PX * 2 + 5)).toEqual([2, 5]);
    expect(wheelSteps(-WHEEL_STEP_PX - 3)).toEqual([-1, -3]);
  });
});

describe("corner highlight", () => {
  it("highlights exactly the turned digit's strokes, which are part of the glyph", () => {
    const glyph = new Set(toPixelLines(encode(1986)).map((l) => JSON.stringify(l)));
    const tens = toPixelLines({ segments: digitSegments(8, "tens") });
    expect(tens.length).toBe(2);
    for (const line of tens) expect(glyph.has(JSON.stringify(line))).toBe(true);
  });

  it("has nothing to highlight for a zero digit", () => {
    expect(digitSegments(0, "hundreds")).toEqual([]);
  });
});
