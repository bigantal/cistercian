# Historical references

Status: **Stage 0 draft, awaiting owner review.** Last checked 2026-11-16.

## Sources consulted

| # | Source | What it was used for | Access / licensing |
|---|--------|----------------------|--------------------|
| R1 | David A. King, *The Ciphers of the Monks: A Forgotten Number-Notation of the Middle Ages*. Stuttgart: Franz Steiner Verlag, 2001. ISBN 3-515-07640-9. | The primary scholarly authority. The digit table and composites we use come from King's schematic **vertical** chart (p. 36) and his variant table (p. 39). We consulted these pages **only as reproduced in R2**. We have not read the book directly. | In copyright. Do not copy its figures into this repository. Our chart is drawn from our own data. |
| R2 | Kirk Miller, "Background for Unicode consideration of Cistercian numerals", Unicode Technical Committee document **L2/20-290**, 10 December 2020. <https://www.unicode.org/L2/L2020/20290-cistercian-digits.pdf> | This document reproduces King (2001) pp. 34, 36, 39 and others as figures. It surveys which corner holds which place value across manuscripts. It also lists variant digit forms. | A UTC document register file. The figures are King's and remain under his copyright. We cite them and do not redistribute them. |
| R3 | Eric W. Weisstein, "Cistercian Numerals", *MathWorld* (Wolfram Research). <https://mathworld.wolfram.com/CistercianNumerals.html> | Independent secondary description. It defines digits 1, 2, 3, 4, 6 as segments on a stave, and 5, 7, 8, 9 as unions of those. It gives the same quadrant assignment and cites King (2001, p. 36). | Web page. We cite it only. |
| R4 | Wikipedia, "Cistercian numerals". <https://en.wikipedia.org/wiki/Cistercian_numerals> | A general overview and list of variants: early forms swap 3/4 with 7/8, 5 drawn as a dot, short stroke or triangle, a round 9, and some manuscripts assign corners differently. It also cites King 1995 (*Cîteaux: Commentarii Cistercienses* 46:183–217) and Chrisomalis, *Numerical Notation* (CUP 2010), p. 350. | CC BY-SA. We cite it only and copy no text. |

Earlier assistant conversations, AI-generated images and the initial design proposal's own sketches are **not** sources.

## Selected convention

We use the **vertical-stem** form in the arrangement King gives as standard (King 2001: 36; R2 Fig. 2; R3):

```
 tens      | units
-----------+-----------
 thousands | hundreds
```

- **Units:** upper right. **Tens:** the units motif mirrored left↔right. **Hundreds:** the units motif mirrored top↔bottom. **Thousands:** mirrored both ways.
- Digit motifs follow King's schematic vertical digits and match R3 exactly:
  - 1 = top bar, 2 = lower bar.
  - 3 = diagonal down from the stem top, 4 = diagonal up to the outer top corner.
  - 6 = outer vertical, not touching the stem.
  - 5 = 1+4, 7 = 1+6, 8 = 2+6, 9 = 1+2+6.

R2 states that most vertical-stem manuscripts use this corner arrangement. Units sit upper right in every tradition it surveys.

## Known variants (not used; recorded so they are not mixed in)

| Variant | Source | Note |
|---------|--------|------|
| Horizontal stave (the units motif rotated) | R2 (King 1993: 47; King 2001: 34) | The *more common* form in Cistercian use. Vertical forms dominated later and in modern accounts. |
| Hundreds and thousands swapped (T\|U over H\|K) | R2 Fig. 9 (15th-c. Norman treatise); some modern sources | Units stay upper right. |
| Units and tens swapped (U\|T over H\|K) | R2 Fig. 15 (Masonic, c. 1780) | |
| Early Cistercian forms: 3/4 swapped with 7/8; dots for 5/6 | R2 Fig. 3–4 (King 2001: 39, 97); R4 | Found in only two manuscripts. |
| **5 as a dot or a short stroke** instead of 1+4 | R2 Fig. 1–2 captions; R4 | **Most medieval sources** use a dot or a stroke. R2 calls King's triangular 5 (which equals 1+4 joined to the stem) "not representative". R3 likewise says the triangular 5 "is not universal". See open question Q2 in `SPECIFICATION.md`. |
| Round 9 | R2 Fig. 5; R4 | A handwriting variant. |
| Extensions above 9,999 | R2 Fig. 9, 12 | Out of scope. |

## Independent composites used as fixtures

King prints these composites in the selected convention (King 2001: 36, reproduced as R2 Fig. 2): **1992, 4723, 6859, 7085, 8971, 9938**. For Stage 0 we transcribed each by eye into grid edges, independently of the generator. The generator's output matches every one (see `SPECIFICATION.md` §7).

**1986, 1993, 9433** do not appear in any source we found. They are derived from the chart, so they can only be checked by reviewing the chart.

## Verification gaps

- We have not checked King (2001) directly. R2 reproduces the relevant pages as images, and the derived glyphs match them.
- We have not compared individual manuscripts. The convention is King's schematic standardisation, not any single manuscript.
