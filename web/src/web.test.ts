import { readdirSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

import * as viaAlias from "cistercian-encoder";
import * as direct from "../../implementations/typescript/src/encoder.ts";
import { parseNumber } from "./input.ts";
import { canvasSize, DEFAULT_LAYOUT, toPixel, toPixelLines } from "./render.ts";

describe("the website uses the real TypeScript encoder", () => {
  it("resolves 'cistercian-encoder' to implementations/typescript/src/encoder.ts", () => {
    expect(viaAlias.encode).toBe(direct.encode);
    expect(viaAlias.decompose).toBe(direct.decompose);
  });

  it("contains no glyph geometry of its own", () => {
    const dir = fileURLToPath(new URL(".", import.meta.url));
    for (const file of readdirSync(dir).filter((f) => f.endsWith(".ts") && !f.endsWith(".test.ts"))) {
      const source = readFileSync(dir + file, "utf8");
      // Coordinate literals such as [1, 0] or [[2,0],[2,1]] would indicate a second encoder.
      expect(source, file).not.toMatch(/\[\s*\[?\s*\d\s*,\s*\d\s*\]/);
      const imports = [...source.matchAll(/from\s+"([^"]+)"/g)].map((m) => m[1]);
      expect(imports.every((s) => s === "cistercian-encoder" || s?.startsWith("./")), file).toBe(true);
    }
  });
});

describe("SVG geometry mapping", () => {
  const { unit, margin } = DEFAULT_LAYOUT;

  it("maps grid corners to the padded canvas", () => {
    expect(toPixel(0)).toBe(margin);
    expect(canvasSize()).toEqual({ width: 2 * unit + 2 * margin, height: 3 * unit + 2 * margin });
  });

  it("draws exactly the encoder's segments, scaled", () => {
    const numeral = viaAlias.encode(1);
    expect(toPixelLines(numeral)).toEqual([
      { x1: margin + unit, y1: margin, x2: margin + unit, y2: margin + 3 * unit },
      { x1: margin + unit, y1: margin, x2: margin + 2 * unit, y2: margin },
    ]);
  });

  it("keeps the detached units-6 stroke clear of the stem (1986)", () => {
    const lines = toPixelLines(viaAlias.encode(1986));
    const stemX = toPixel(1);
    const strokeWidth = unit * DEFAULT_LAYOUT.stroke;
    const outer = lines.find((l) => l.x1 === toPixel(2) && l.x2 === toPixel(2) && Math.max(l.y1, l.y2) === toPixel(1));
    expect(outer).toBeDefined();
    // Round caps extend by half the stroke width; the visible gap must stay large.
    expect(toPixel(2) - stemX - strokeWidth).toBeGreaterThan(unit / 2);
    // No line joins the outer vertical to the stem at the top or at y=1.
    expect(lines.some((l) => l.y1 === l.y2 && l.y1 === toPixel(0) && Math.max(l.x1, l.x2) === toPixel(2))).toBe(false);
    expect(lines.some((l) => l.y1 === l.y2 && l.y1 === toPixel(1) && Math.max(l.x1, l.x2) === toPixel(2))).toBe(false);
  });
});

describe("number input", () => {
  it.each([
    ["1986", 1986],
    [" 7085 ", 7085],
    ["9,999", 9999],
    ["1", 1],
  ])("accepts %j", (raw, value) => {
    expect(parseNumber(raw)).toEqual({ ok: true, value });
  });

  it.each([
    ["", "Enter a whole number"],
    ["0", "no Cistercian zero"],
    ["10000", "at most 9,999"],
    ["-5", "digits only"],
    ["12.5", "digits only"],
    ["abc", "digits only"],
  ])("rejects %j", (raw, message) => {
    const result = parseNumber(raw);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.message).toContain(message);
  });
});
