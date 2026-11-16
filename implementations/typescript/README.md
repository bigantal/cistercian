# TypeScript implementation

The encoder (`src/encoder.ts`) is dependency-free TypeScript. The website in [`web/`](../../web) imports this same file, and the Node CLI adapter (`src/cli.ts`) is built from it, so the website has no encoder of its own.

You need Node.js 20.19 or later and npm.

```bash
cd implementations/typescript
npm ci && npm run build
printf '1\n1986\n9999\n' | node dist/cli.js       # CLI (SPECIFICATION.md §11)
```

Run the shared conformance suite from the repository root. Its build step runs `npm ci` and `tsc` itself:

```bash
python3 -m judge.runner --language typescript
```

## Approach

This design differs from both the reference encoder and the Python implementation:

- **Strokes as bitmasks:** each digit is a 5-bit mask over the five basic strokes of the units quadrant. For example, 8 is `LOWER | OUTER`.
- **Quadrants as functions:** each quadrant is a point transform, built from `mirrorX` and `mirrorY`.
- **Types:** coordinates are readonly tuples, `Point` and `Segment`. `Numeral` is the contract-v1 object.
- **Exports for the website:** `decompose(n)` gives the digits by place for the decomposition table, and `GRID` gives the size for the SVG viewBox.

The CLI reads stdin as raw bytes and splits on `\n` only. Node's `readline` is not used, because it would also treat `\r` as a line break and accept CRLF input, which the protocol forbids.
