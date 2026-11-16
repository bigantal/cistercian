#!/usr/bin/env bash
# Run everything: judge unit tests, chart freshness, and conformance of every
# implementation. Exit status: 0 all passed, 1 something failed,
# 3 nothing failed but some implementation could not be tested (toolchain missing).
set -uo pipefail
cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-.venv/bin/python}"
if [ ! -x "$PYTHON" ]; then
  echo "error: $PYTHON not found. Set up the dev environment first:" >&2
  echo "  python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt" >&2
  exit 1
fi

status=0
step() {
  echo
  echo "### $1"
  shift
  "$@"
  local rc=$?
  if [ $rc -ne 0 ] && { [ $status -eq 0 ] || [ $rc -eq 1 ]; }; then status=$rc; fi
}

step "Judge unit tests" "$PYTHON" -m pytest
step "Digit chart is up to date" "$PYTHON" scripts/render_digit_chart.py --check
step "Conformance of all implementations" "$PYTHON" -m judge.runner --all

echo
case $status in
  0) echo "ALL PASSED" ;;
  3) echo "NO FAILURES, BUT SOME IMPLEMENTATIONS WERE NOT TESTED (missing toolchain)" ;;
  *) echo "FAILED" ;;
esac
exit $status
