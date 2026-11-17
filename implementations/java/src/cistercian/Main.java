package cistercian;

import module java.base;

/// CLI adapter (SPECIFICATION.md section 11): one integer per stdin line, one compact JSON object
/// per stdout line; exit status 2 at the first invalid line.
///
/// Input is split on `'\n'` only and validated as raw bytes. `BufferedReader.readLine` is
/// deliberately not used: it also treats `'\r'` as a line end and would accept CRLF input.
final class Main {

    private static final int EXIT_INVALID_INPUT = 2;

    /// Instance main method (Java 25): the launcher creates a `Main` and calls this.
    void main() throws IOException {
        InputStream in = new BufferedInputStream(System.in, 1 << 16);
        OutputStream out = new BufferedOutputStream(new FileOutputStream(FileDescriptor.out), 1 << 16);
        var line = new ByteArrayOutputStream(8);
        int lineNumber = 0;
        boolean pending = false;

        for (int b = in.read(); ; b = in.read()) {
            if (b == '\n' || (b == -1 && pending)) {
                lineNumber++;
                byte[] bytes = line.toByteArray();
                if (!isValid(bytes)) {
                    out.flush();
                    System.err.println("error: line " + lineNumber + ": expected an integer from 1 to 9999 "
                        + "(digits only, no sign, spaces or leading zeros), got " + describe(bytes));
                    System.exit(EXIT_INVALID_INPUT);
                }
                int n = Integer.parseInt(new String(bytes, StandardCharsets.US_ASCII));
                out.write(Cistercian.encode(n).toJson().getBytes(StandardCharsets.US_ASCII));
                out.write('\n');
                line.reset();
                pending = false;
            }
            if (b == -1) {
                break;
            }
            if (b != '\n') {
                line.write(b);
                pending = true;
            }
        }
        out.flush();
    }

    /// Exactly `[1-9][0-9]{0,3}`.
    static boolean isValid(byte[] line) {
        if (line.length < 1 || line.length > 4 || line[0] < '1' || line[0] > '9') {
            return false;
        }
        for (byte c : line) {
            if (c < '0' || c > '9') {
                return false;
            }
        }
        return true;
    }

    /// Quote a line for diagnostics, escaping anything that is not printable ASCII.
    private static String describe(byte[] line) {
        var text = new StringBuilder("\"");
        for (byte b : line) {
            int c = b & 0xff;
            if (c >= 0x20 && c < 0x7f && c != '"' && c != '\\') text.append((char) c);
            else text.append(String.format("\\x%02x", c));
        }
        return text.append('"').toString();
    }
}
