# Cistercian numeral geometry — specification

Status: **Approved by the owner on 2026-11-16 (Stage 0 review). Contract v1 is frozen.** Any change to the grid, the digit table or the JSON contract needs a new decision record and owner approval. Sources are listed in [`docs/references.md`](docs/references.md). The grid choice is explained in [`docs/decisions/0001-grid-and-normalization.md`](docs/decisions/0001-grid-and-normalization.md).

## 1. Scope

- Integers **1 through 9,999**. **0 is out of scope**, since there is no historical zero glyph.
- A number is split into thousands **K**, hundreds **H**, tens **T** and units **U**: `n = 1000K + 100H + 10T + U`.
- Each nonzero digit adds a motif in its quadrant. A zero digit adds nothing.
- The stem is always drawn.

## 2. Convention

Vertical stem, King (2001: 36) arrangement:

```
   T | U        tens      | units
  ---+---       ----------+----------
   K | H        thousands | hundreds
```

Other arrangements and digit forms are listed in `docs/references.md` and are **not** used.

## 3. Grid

- Integer coordinates `x ∈ {0,1,2}` and `y ∈ {0,1,2,3}`.
- Origin `(0,0)` is the **top-left**, and `y` grows downward, as in SVG.
- The **stem** runs from `(1,0)` to `(1,3)`.
- Digit squares (each 1×1):

  | Quadrant | x range | y range |
  |---|---|---|
  | units | 1..2 | 0..1 |
  | tens | 0..1 | 0..1 |
  | hundreds | 1..2 | 2..3 |
  | thousands | 0..1 | 2..3 |

- Between `y=1` and `y=2` only the stem is drawn. This grid is a change from the 0..4 × 0..4 grid in the initial design proposal; the ADR explains why.
- Allowed segment directions: **horizontal, vertical and 45° diagonal**. Diagonals are required by digits 3, 4 and 5.

## 4. Upper-right (units) motifs — canonical table

| Digit | Description | Segments |
|---|---|---|
| 1 | top bar, from the stem outward | (1,0)–(2,0) |
| 2 | lower bar, from the stem outward, one unit below the top | (1,1)–(2,1) |
| 3 | diagonal from the **top of the stem** down to the outer lower corner | (1,0)–(2,1) |
| 4 | diagonal from the stem one unit down, **up** to the outer top corner | (1,1)–(2,0) |
| 5 | 1 + 4: a closed triangle with the stem | (1,0)–(2,0), (1,1)–(2,0) |
| 6 | **outer vertical only; does not touch the stem** | (2,0)–(2,1) |
| 7 | 1 + 6 | (1,0)–(2,0), (2,0)–(2,1) |
| 8 | 2 + 6 | (1,1)–(2,1), (2,0)–(2,1) |
| 9 | 1 + 2 + 6: a closed square with the stem | (1,0)–(2,0), (1,1)–(2,1), (2,0)–(2,1) |

No diagonal crosses another stroke between grid points. The two diagonals of one square (3 and 4) never occur together, so every intersection lies on an integer grid point.

## 5. Quadrant transformations

Each transformation maps a point of the units motif to its place in another quadrant:

| Place | Transformation | Meaning |
|---|---|---|
| units | `(x, y) → (x, y)` | identity |
| tens | `(x, y) → (2 − x, y)` | mirror left↔right about the stem |
| hundreds | `(x, y) → (x, 3 − y)` | mirror top↔bottom about the midline |
| thousands | `(x, y) → (2 − x, 3 − y)` | both mirrors (a 180° rotation) |

### Derived motif table (canonical elementary edges, endpoints sorted)

| Digit | Units (upper right) | Tens (upper left) | Hundreds (lower right) | Thousands (lower left) |
|---|---|---|---|---|
| 1 | (1,0)–(2,0) | (0,0)–(1,0) | (1,3)–(2,3) | (0,3)–(1,3) |
| 2 | (1,1)–(2,1) | (0,1)–(1,1) | (1,2)–(2,2) | (0,2)–(1,2) |
| 3 | (1,0)–(2,1) | (0,1)–(1,0) | (1,3)–(2,2) | (0,2)–(1,3) |
| 4 | (1,1)–(2,0) | (0,0)–(1,1) | (1,2)–(2,3) | (0,3)–(1,2) |
| 5 | (1,0)–(2,0), (1,1)–(2,0) | (0,0)–(1,0), (0,0)–(1,1) | (1,2)–(2,3), (1,3)–(2,3) | (0,3)–(1,2), (0,3)–(1,3) |
| 6 | (2,0)–(2,1) | (0,0)–(0,1) | (2,2)–(2,3) | (0,2)–(0,3) |
| 7 | (1,0)–(2,0), (2,0)–(2,1) | (0,0)–(0,1), (0,0)–(1,0) | (1,3)–(2,3), (2,2)–(2,3) | (0,2)–(0,3), (0,3)–(1,3) |
| 8 | (1,1)–(2,1), (2,0)–(2,1) | (0,0)–(0,1), (0,1)–(1,1) | (1,2)–(2,2), (2,2)–(2,3) | (0,2)–(0,3), (0,2)–(1,2) |
| 9 | (1,0)–(2,0), (1,1)–(2,1), (2,0)–(2,1) | (0,0)–(0,1), (0,0)–(1,0), (0,1)–(1,1) | (1,2)–(2,2), (1,3)–(2,3), (2,2)–(2,3) | (0,2)–(0,3), (0,2)–(1,2), (0,3)–(1,3) |

The stem expands to three elementary edges: (1,0)–(1,1), (1,1)–(1,2), (1,2)–(1,3).

The visual chart is [`docs/digit-chart.svg`](docs/digit-chart.svg). `scripts/render_digit_chart.py` generates it deterministically from the reference encoder (`judge/reference.py`), and `--check` verifies it is up to date. A test fails if the chart is stale.

## 6. Digit 6 vs digit 8 (the known trouble spot)

These motifs have been confused before, so here is each one stated precisely, in the units quadrant:

- **6** is a **single vertical stroke on the outer edge**, (2,0)–(2,1). It is **detached** from the stem. Units-6 alone is the only digit whose motif does not touch the stem.
- **8** is **6 plus the lower bar (digit 2)**: (2,0)–(2,1) and (1,1)–(2,1). With the stem, it makes a "⊔" shape on its side, open at the **top**: stem on one side, outer vertical on the other, joined at the bottom (y=1).
- **7** is 6 plus the **top** bar: the same outer vertical, joined at the top and open at the bottom.
- **9** combines both bars and the vertical, closing the square.

The sources agree on this:

- R3 defines 6 = segment BD, the outer vertical, and 8 = "2 and 6".
- King's p. 36 chart (R2 Fig. 2) shows 6 as a lone stroke beside the stem, and 8 as the lower bar plus outer vertical.
- King's printed composites check both digits in other quadrants:
  - 6859: thousands-6 is a detached left vertical (0,2)–(0,3); hundreds-8 is a lower-right bar at y=2 plus an outer vertical.
  - 8971: thousands-8.
  - 7085: tens-8.
  - 9938: units-8.

  All match the derived table.

## 7. Worked composites

Each list below is the full canonical elementary-edge set, stem included.

### King's printed composites (independent check)

We transcribed these six by eye from King 2001: 36, as reproduced in R2 Fig. 2, then compared them with the generator output. **All six match exactly.**

| n | K H T U | Edges (excluding the three stem edges) |
|---|---|---|
| 1992 | 1 9 9 2 | (0,0)–(0,1), (0,0)–(1,0), (0,1)–(1,1), (0,3)–(1,3), (1,1)–(2,1), (1,2)–(2,2), (1,3)–(2,3), (2,2)–(2,3) |
| 4723 | 4 7 2 3 | (0,1)–(1,1), (0,3)–(1,2), (1,0)–(2,1), (1,3)–(2,3), (2,2)–(2,3) |
| 6859 | 6 8 5 9 | (0,0)–(1,0), (0,0)–(1,1), (0,2)–(0,3), (1,0)–(2,0), (1,1)–(2,1), (1,2)–(2,2), (2,0)–(2,1), (2,2)–(2,3) |
| 7085 | 7 0 8 5 | (0,0)–(0,1), (0,1)–(1,1), (0,2)–(0,3), (0,3)–(1,3), (1,0)–(2,0), (1,1)–(2,0) |
| 8971 | 8 9 7 1 | (0,0)–(0,1), (0,0)–(1,0), (0,2)–(0,3), (0,2)–(1,2), (1,0)–(2,0), (1,2)–(2,2), (1,3)–(2,3), (2,2)–(2,3) |
| 9938 | 9 9 3 8 | (0,1)–(1,0), (0,2)–(0,3), (0,2)–(1,2), (0,3)–(1,3), (1,1)–(2,1), (1,2)–(2,2), (1,3)–(2,3), (2,0)–(2,1), (2,2)–(2,3) |

### Derived examples (owner review required — not found in any source)

**1986** = K1 H9 T8 U6:

- **Units 6:** a lone outer vertical at the upper right, (2,0)–(2,1). It does **not** touch the stem.
- **Tens 8:** a bar at y=1 from the stem leftward, (0,1)–(1,1), plus a left outer vertical, (0,0)–(0,1). It is attached to the stem at its lower end and open at the top.
- **Hundreds 9:** a closed square at the lower right, (1,2)–(2,2), (2,2)–(2,3), (1,3)–(2,3).
- **Thousands 1:** a bottom bar to the left, (0,3)–(1,3).
- **Full edge set:** (0,0)–(0,1), (0,1)–(1,1), (0,3)–(1,3), (1,0)–(1,1), (1,1)–(1,2), (1,2)–(1,3), (1,2)–(2,2), (1,3)–(2,3), (2,0)–(2,1), (2,2)–(2,3).
- **Key visual check:** the upper half has *two* outer verticals. The left one is joined to the stem by a bar at y=1. The right one is free-standing. If the right one were joined by a bar, the glyph would show units 8 (1988). If it were joined at the top, it would show units 7 (1987).

**1993** = K1 H9 T9 U3:

- (0,0)–(0,1), (0,0)–(1,0), (0,1)–(1,1), (0,3)–(1,3), (1,0)–(1,1), (1,0)–(2,1), (1,1)–(1,2), (1,2)–(1,3), (1,2)–(2,2), (1,3)–(2,3), (2,2)–(2,3)

**9433** = K9 H4 T3 U3:

- (0,1)–(1,0), (0,2)–(0,3), (0,2)–(1,2), (0,3)–(1,3), (1,0)–(1,1), (1,0)–(2,1), (1,1)–(1,2), (1,2)–(1,3), (1,2)–(2,3)

### Boundary cases

| n | Glyph |
|---|---|
| 1 | stem + (1,0)–(2,0) |
| 9999 | stem + all four closed squares |
| 1000, 100, 10 | stem plus a single motif |

Number 2 and number 200 are different glyphs: the bar sits at y=1 for 2 and at y=2 for 200. An exhaustive check confirms that all 9,999 numbers give **distinct** edge sets.

## 8. JSON contract v1

```json
{"segments": [[[1,0],[1,3]], [[1,0],[2,0]]]}
```

The example above is the number **1**.

- **Shape:** exactly one top-level key, `segments`, holding a non-empty array of segments. Each segment is `[[x1,y1],[x2,y2]]`.
- **Values:** integer coordinates with `0 ≤ x ≤ 2` and `0 ≤ y ≤ 3`.
- **Forbidden:** any other key, floats, strings or extra nesting.
- **Semantic rules** (enforced by the judge, not by JSON Schema):
  - A segment must be horizontal, vertical or exactly 45° diagonal.
  - Zero-length segments are invalid.
  - The full stem (1,0)–(1,3) must be present, either as one segment or as collinear pieces.
  - Disconnected strokes stay disconnected; gaps are never bridged automatically.
- **Machine-readable forms:**
  - [`schema/numeral.schema.json`](schema/numeral.schema.json) (JSON Schema 2020-12) checks the structure only. JSON Schema counts `1.0` as an integer, so the judge rejects floats itself.
  - [`judge/geometry.py`](judge/geometry.py) enforces both the structural and the semantic rules. It also rejects JSON with duplicate keys or `NaN`/`Infinity`.

### Normalization

1. Expand each segment with delta `(dx,dy)` into `g = gcd(|dx|,|dy|)` unit steps of `(dx/g, dy/g)`. Every step must be one of (±1,0), (0,±1) or (±1,±1).
2. Write each elementary edge with its endpoints in lexicographic `(x,y)` order.
3. Compare the resulting **sets** of edges.

This makes segment order, endpoint direction, splitting or merging of collinear runs, and duplicates irrelevant, while different shapes stay distinct.

## 9. Decisions (owner approval, 2026-11-16)

- **Grid:** x 0..2 × y 0..3. This replaces the initial design proposal's 0..4 × 0..4; ADR 0001 gives the reasons.
- **Digit 5:** drawn as 1 + 4, the triangle formed with the stem. The medieval dot and short-stroke forms are recorded as variants and are not supported.
- **Quadrant arrangement:** tens and units on top, thousands and hundreds below (T|U over K|H).
- **Proportions:** the stem is three digit-squares long, matching King's chart. This is cosmetic.

## 10. Ground truth

- [`fixtures/known-values.json`](fixtures/known-values.json) is written by hand and never generated by code. It holds:
  - all 36 digit/quadrant motifs, transcribed from the approved table in §5;
  - King's six printed composites;
  - the owner-reviewed derived examples;
  - hand-derived edge cases 1001, 1010 and 202 (zero digits, and 2 vs 200), which the owner reviewed in Stage 1. They are marked `derived-reviewed-stage1`.
- The reference encoder (`judge/reference.py`) is tested against this file.
- The tests also show that replacing any digit's motif with another digit's motif (including the 6/8 swap) or using the wrong quadrant reflection makes the fixture tests fail.
