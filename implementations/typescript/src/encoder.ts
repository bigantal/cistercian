/**
 * Cistercian numeral encoder (TypeScript implementation).
 *
 * Approach: every digit is a 5-bit mask over the five basic strokes of the
 * units (upper-right) quadrant. A quadrant is a point transform. Encoding a
 * number walks its four decimal places, expands each digit's mask into
 * strokes and maps them through the place's transform.
 *
 * This module is the single source of truth for both the CLI adapter
 * (cli.ts) and the website (web/), which imports it directly.
 */

export type Point = readonly [x: number, y: number];
export type Segment = readonly [from: Point, to: Point];

/** Contract v1 geometry (SPECIFICATION.md section 8). */
export interface Numeral {
  readonly segments: readonly Segment[];
}

export type Place = "units" | "tens" | "hundreds" | "thousands";

export interface PlaceDigit {
  readonly place: Place;
  readonly digit: number;
  readonly value: number;
}

export const MIN_VALUE = 1;
export const MAX_VALUE = 9999;

/** Integer grid: x in 0..GRID.width, y in 0..GRID.height, origin top-left. */
export const GRID = { width: 2, height: 3 } as const;

export const STEM: Segment = [[1, 0], [1, 3]];

/** The five basic strokes, in units-quadrant coordinates. */
const STROKES = [
  [[1, 0], [2, 0]], // bit 0: top bar
  [[1, 1], [2, 1]], // bit 1: lower bar
  [[1, 0], [2, 1]], // bit 2: diagonal down from the stem top
  [[1, 1], [2, 0]], // bit 3: diagonal up to the outer top corner
  [[2, 0], [2, 1]], // bit 4: outer vertical (detached from the stem)
] as const satisfies readonly Segment[];

const TOP = 1 << 0;
const LOWER = 1 << 1;
const DIAGONAL_DOWN = 1 << 2;
const DIAGONAL_UP = 1 << 3;
const OUTER = 1 << 4;

/** Stroke mask for digits 0..9. */
const DIGIT_MASKS: readonly number[] = [
  0,
  TOP,
  LOWER,
  DIAGONAL_DOWN,
  DIAGONAL_UP,
  TOP | DIAGONAL_UP,
  OUTER,
  TOP | OUTER,
  LOWER | OUTER,
  TOP | LOWER | OUTER,
];

const mirrorX = ([x, y]: Point): Point => [GRID.width - x, y];
const mirrorY = ([x, y]: Point): Point => [x, GRID.height - y];

/** Places from least to most significant, each with its quadrant transform. */
const PLACES: readonly { place: Place; transform: (p: Point) => Point }[] = [
  { place: "units", transform: (p) => p },
  { place: "tens", transform: mirrorX },
  { place: "hundreds", transform: mirrorY },
  { place: "thousands", transform: (p) => mirrorX(mirrorY(p)) },
];

export function isEncodable(n: number): boolean {
  return Number.isInteger(n) && n >= MIN_VALUE && n <= MAX_VALUE;
}

function assertEncodable(n: number): void {
  if (!isEncodable(n)) {
    throw new RangeError(`expected an integer from ${MIN_VALUE} to ${MAX_VALUE}, got ${n}`);
  }
}

/** Digits of n by place, most significant first (thousands .. units). */
export function decompose(n: number): PlaceDigit[] {
  assertEncodable(n);
  return PLACES.map(({ place }, i) => {
    const digit = Math.floor(n / 10 ** i) % 10;
    return { place, digit, value: digit * 10 ** i };
  }).reverse();
}

/** Strokes of one digit in one place (empty for 0). */
export function digitSegments(digit: number, place: Place): Segment[] {
  const mask = DIGIT_MASKS[digit];
  const entry = PLACES.find((p) => p.place === place);
  if (mask === undefined || entry === undefined) {
    throw new RangeError(`invalid digit ${digit} or place ${place}`);
  }
  return STROKES.filter((_, bit) => mask & (1 << bit)).map(
    ([a, b]): Segment => [entry.transform(a), entry.transform(b)],
  );
}

/** Encode n (1..9999) as contract-v1 geometry: the stem plus each digit's strokes. */
export function encode(n: number): Numeral {
  const segments = decompose(n).flatMap(({ digit, place }) => digitSegments(digit, place));
  return { segments: [STEM, ...segments] };
}
