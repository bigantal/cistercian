# Java implementation

You need a JDK, version 25 or later. There are no dependencies, and no Maven or Gradle: two source files compile with plain `javac`.

```bash
cd implementations/java
javac --release 25 -d build/classes src/cistercian/Cistercian.java src/cistercian/Main.java
printf '1\n1986\n9999\n' | java -cp build/classes cistercian.Main     # CLI (SPECIFICATION.md §11)
```

From other Java code:

```java
String json = cistercian.Cistercian.encode(1986).toJson();
```

Run the shared conformance suite from the repository root. Its build step compiles the code itself:

```bash
python3 -m judge.runner --language java
```

## Approach

This design differs from the reference, Python and TypeScript versions:

- **`enum Stroke`:** names the five basic strokes. Each value carries its segment in the units (upper-right) quadrant.
- **`enum Place`:** each decimal place carries its weight and a `UnaryOperator<Point>` that moves a units stroke into its quadrant (`Point::mirrorX`, `Point::mirrorY`, or both).
- **Digits:** a `switch` expression maps each digit to an `EnumSet<Stroke>`. For example, `case 8 -> EnumSet.of(LOWER, OUTER)`.
- **Geometry values** are immutable records (`Point`, `Segment`, `Numeral`). `Numeral.toJson()` writes compact JSON by hand, so no JSON library is needed.

The code compiles with `--release 25 -Xlint:all -Werror` and uses features finalised in recent Java releases:

- **Markdown documentation comments** (`///`, Java 23).
- **Module import declarations** (`import module java.base;` in `Main.java`, Java 25).
- **Instance main methods:** `Main` declares `void main()`, without `public static` or `String[] args` (Java 25).

The library class `Cistercian` keeps explicit single-type imports, which is still the clearer style for reusable code. No preview features are used.

The CLI reads stdin as raw bytes and splits on `\n` only. `BufferedReader.readLine()` is avoided because it would also treat `\r` as a line end and accept CRLF input.

The manifest runs the JVM with `-XX:+UseSerialGC -XX:TieredStopAtLevel=1`. These flags shorten start-up, which matters because the conformance suite starts about 27 short-lived processes.
