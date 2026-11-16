/** Validation of the number typed by the visitor. */

import { MAX_VALUE, MIN_VALUE } from "cistercian-encoder";

export type ParseResult = { ok: true; value: number } | { ok: false; message: string };

export function parseNumber(raw: string): ParseResult {
  const text = raw.trim().replace(/[,\s]/g, "");
  if (text === "") {
    return { ok: false, message: `Enter a whole number from ${MIN_VALUE} to ${MAX_VALUE.toLocaleString("en")}.` };
  }
  if (!/^[0-9]+$/.test(text)) {
    return { ok: false, message: "Use digits only — no signs, decimals or letters." };
  }
  const value = Number(text);
  if (value === 0) {
    return { ok: false, message: "There is no Cistercian zero: the system starts at 1." };
  }
  if (value > MAX_VALUE) {
    return { ok: false, message: `A single glyph reaches at most ${MAX_VALUE.toLocaleString("en")}.` };
  }
  return { ok: true, value };
}
