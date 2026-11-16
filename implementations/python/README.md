# Python implementation

Standard library only, Python 3.10 or later. No build step.

```bash
cd implementations/python
printf '1\n1986\n9999\n' | python3 -m cistercian          # CLI (SPECIFICATION.md §11)
python3 -c 'from cistercian import encode; print(encode(1986))'
```

Run the shared conformance suite from the repository root:

```bash
python3 -m judge.runner --language python
```

## Approach

The reference encoder in `judge/` mirrors a table of units-quadrant
segments. This implementation is built differently on purpose:

- **Strokes:** the five basic strokes are an `Enum`, defined once in coordinates local to a quadrant. `across` runs from the stem outward; `along` runs from the end of the stem toward the middle.
- **Digits:** each digit is a tuple of strokes. For example, 8 is `INNER_BAR + OUTER`.
- **Quadrants:** a frozen `Quadrant` dataclass places a stroke with one affine map, using its stem end and two direction signs.

The CLI checks input lines as raw bytes against `[1-9][0-9]{0,3}`. Python's `int()` alone would accept `"１"`, `"1_000"` and `" 1"`.
