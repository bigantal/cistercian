package main

import (
	"bytes"
	"strings"
	"testing"
)

func TestRun(t *testing.T) {
	one := `{"segments":[[[1,0],[1,3]],[[1,0],[2,0]]]}` + "\n"
	tests := []struct {
		name       string
		stdin      string
		wantStdout string
		wantExit   int
		wantStderr string
	}{
		{"single", "1\n", one, exitOK, ""},
		{"no trailing newline", "1", one, exitOK, ""},
		{"empty input", "", "", exitOK, ""},
		{"zero", "0\n", "", exitInvalidInput, "line 1"},
		{"too large", "10000\n", "", exitInvalidInput, "line 1"},
		{"leading zero", "01\n", "", exitInvalidInput, "line 1"},
		{"empty line", "\n", "", exitInvalidInput, "line 1"},
		{"crlf", "1\r\n", "", exitInvalidInput, "line 1"},
		{"output before bad line", "1\nx\n1\n", one, exitInvalidInput, "line 2"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var stdout, stderr bytes.Buffer
			exit := run(strings.NewReader(tt.stdin), &stdout, &stderr)
			if exit != tt.wantExit {
				t.Errorf("exit = %d, want %d", exit, tt.wantExit)
			}
			if stdout.String() != tt.wantStdout {
				t.Errorf("stdout = %q, want %q", stdout.String(), tt.wantStdout)
			}
			if !strings.Contains(stderr.String(), tt.wantStderr) {
				t.Errorf("stderr = %q, want it to contain %q", stderr.String(), tt.wantStderr)
			}
		})
	}
}
