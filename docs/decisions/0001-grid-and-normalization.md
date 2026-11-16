# ADR 0001 — Integer grid and edge-set normalization

- Status: **Accepted.** The owner approved it on 2026-11-16 at the Stage 0 review.
- Date: 2026-11-16

## Context

The initial design proposal used integer coordinates `0..4 × 0..4` with the stem at x=2. It also required the grid to be revised before the contract was frozen if it could not represent the historical shapes faithfully.

King's schematic chart (King 2001: 36, reproduced in Miller L2/20-290 Fig. 2) has these properties:

- Every digit motif fits in a **square** next to the stem: upper squares for units and tens, lower squares for hundreds and thousands.
- The motifs use the square's edges and **one diagonal**: digit 3 uses one diagonal, digits 4 and 5 the other.
- Upper and lower squares are separated by a stretch of bare stem. In King's figure the stem is about three squares long.
- Units 2 sits at the bottom edge of the upper square. Hundreds 2 sits at the top edge of the lower square. These must stay distinct, or 2 and 200 become the same glyph.

The grid in the initial design proposal works only one of two ways:

1. **2-unit squares** (e.g. units in x 2..4, y 0..2). Upper and lower squares share the line y=2. Then units-2 and hundreds-2 are both (2,2)–(4,2), so **2, 200 and 202 are the same glyph**. This rules the option out.
2. **1-unit squares** (units in x 2..3, y 0..1). This works, and gives MathWorld's proportions with a two-unit gap. But x=0 and x=4 are never used. That invites off-by-one confusion and tempts implementations to use coordinates that are always wrong.

## Decision

- **Grid:** `x ∈ 0..2`, `y ∈ 0..3`, origin top-left, y down, stem (1,0)–(1,3), 1×1 digit squares.
- **Bare stem:** the stretch (1,1)–(1,2) belongs to no digit square.
- **Directions:** horizontal, vertical and 45° diagonal segments are allowed. Diagonals are historically required (digits 3, 4, 5).
- **Quadrant mapping:** reflections `x → 2 − x` and `y → 3 − y`.

Every coordinate in this grid is reachable, and every point and edge has exactly one meaning. The proportions match King's chart. Diagonals only ever meet other strokes at grid points: the two diagonals of a square never coexist, and no diagonal crosses a bar or the stem in its interior. So the canonical form needs no intersection splitting.

## Normalization

Comparison works on the **set of elementary undirected edges**:

1. **Expand.** A segment with delta `(dx,dy)` becomes `g = gcd(|dx|,|dy|)` steps of `(dx/g, dy/g)`.
2. **Check direction.** Each step must be axis-aligned or a unit diagonal. Anything else is rejected rather than approximated.
3. **Order endpoints** of each edge lexicographically by `(x,y)`.
4. **Compare as sets**, so duplicates collapse.

Two outputs that draw the same strokes compare equal, regardless of segment order, endpoint direction, or whether collinear pieces are split or merged. Different drawings never compare equal, because each elementary edge is a distinct unit of ink.

All arithmetic is integer, so no tolerance is needed.

## Consequences

- The JSON bounds in the schema become `x ≤ 2`, `y ≤ 3`. This **differs from the initial design proposal**.
- Within this grid, every number 1–9,999 maps to a distinct edge set (checked exhaustively in Stage 0).
- The owner chose 5 = 1 + 4. Supporting the medieval dot form later would need a primitive other than a segment, and therefore a new contract version.
- Renderers scale the grid freely. A 1-unit gap between motifs and the stroke width keeps round line caps from visually joining disconnected strokes, such as units-6 and the stem.

## Alternatives considered

- **0..4 × 0..4 (initial design proposal).** Rejected for the reasons above.
- **0..2 × 0..4** (MathWorld proportions, two-unit gap). Also valid. It is rejected only because the extra row contains nothing but the stem. The owner may prefer it, and it is a one-line change in the table.
- **Scaled grid such as 0..4 × 0..6.** No benefit. It only adds non-elementary edges.
