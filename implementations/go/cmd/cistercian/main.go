// Command cistercian is the CLI adapter (SPECIFICATION.md section 11): it reads
// one integer per stdin line and writes one compact JSON object per stdout line.
// At the first invalid line it reports the line number on stderr and exits 2.
package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"strconv"

	"github.com/bigantal/cistercian/implementations/go"
)

const (
	exitOK           = 0
	exitInternal     = 1
	exitInvalidInput = 2
)

func main() {
	os.Exit(run(os.Stdin, os.Stdout, os.Stderr))
}

// run implements the protocol. Lines are read with ReadBytes('\n') rather than
// bufio.Scanner, whose ScanLines silently drops a trailing '\r' and would
// therefore accept CRLF input, which the protocol rejects.
func run(in io.Reader, out, errOut io.Writer) int {
	r := bufio.NewReaderSize(in, 1<<16)
	w := bufio.NewWriterSize(out, 1<<16)
	enc := json.NewEncoder(w) // compact, one object per line

	for lineNumber := 1; ; lineNumber++ {
		line, err := r.ReadBytes('\n')
		if err != nil && err != io.EOF {
			w.Flush()
			fmt.Fprintf(errOut, "error: reading stdin: %v\n", err)
			return exitInternal
		}
		if len(line) == 0 && err == io.EOF {
			break
		}
		line = bytes.TrimSuffix(line, []byte{'\n'})
		if !valid(line) {
			w.Flush()
			fmt.Fprintf(errOut, "error: line %d: expected an integer from 1 to 9999 "+
				"(digits only, no sign, spaces or leading zeros), got %q\n", lineNumber, line)
			return exitInvalidInput
		}
		n, _ := strconv.Atoi(string(line)) // cannot fail after valid
		numeral, _ := cistercian.Encode(n)
		if err := enc.Encode(numeral); err != nil {
			fmt.Fprintf(errOut, "error: writing output: %v\n", err)
			return exitInternal
		}
		if err == io.EOF {
			break
		}
	}
	if err := w.Flush(); err != nil {
		fmt.Fprintf(errOut, "error: writing output: %v\n", err)
		return exitInternal
	}
	return exitOK
}

// valid reports whether line is exactly [1-9][0-9]{0,3}.
func valid(line []byte) bool {
	if len(line) < 1 || len(line) > 4 || line[0] < '1' || line[0] > '9' {
		return false
	}
	for _, c := range line {
		if c < '0' || c > '9' {
			return false
		}
	}
	return true
}
