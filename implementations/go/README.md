# Go implementation

You need Go 1.26 or later, which covers both currently supported Go releases. It uses only the standard library and has no dependencies.

```bash
cd implementations/go
go build -o build/cistercian ./cmd/cistercian
printf '1\n1986\n9999\n' | ./build/cistercian      # CLI (SPECIFICATION.md §11)
go test ./...                                       # unit tests and the Encode example
```

From other Go code:

```go
import "github.com/bigantal/cistercian/implementations/go" // package cistercian

numeral, err := cistercian.Encode(1986)
```

Run the shared conformance suite from the repository root. It runs `go build` itself:

```bash
python3 -m judge.runner --language go
```

## Approach

This design differs from the reference and the other implementations:

- **Strokes:** the five basic strokes are bit flags declared with `iota`. Each digit is a set of flags; for example, 8 is `lower | outer`.
- **Lookup table:** at package initialisation, `init()` places every digit's strokes into every quadrant and stores them in a fixed-size table, `motifs[place][digit]`. `Encode` then only concatenates precomputed slices.
- **Quadrants** are a small struct of two mirror flags.
- **JSON:** `Point` and `Segment` are array types (`[2]int` and `[2]Point`), so `encoding/json` produces exactly the contract's `[[x,y],[x,y]]` shape with no custom marshalling.
- **The CLI** is a `run(in, out, errOut) int` function behind `main`, which makes the protocol unit-testable (`cmd/cistercian/main_test.go`).

Input is read with `bufio.Reader.ReadBytes('\n')`. `bufio.Scanner` is avoided because its line splitter silently drops a trailing `\r`, which would accept CRLF input.
