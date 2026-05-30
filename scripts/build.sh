#!/usr/bin/env bash
# scripts/build.sh — compile a .vpl file all the way to a native binary.
#
# Usage: ./scripts/build.sh [source.vpl] [output-name]
#   source.vpl   — defaults to examples/hello.vpl
#   output-name  — defaults to "output"
#
# Prerequisites: llc (LLVM), gcc
set -euo pipefail

SOURCE="${1:-examples/hello.vpl}"
BINARY="${2:-output}"

echo "▶  Compiling ${SOURCE} ..."
vlang compile "${SOURCE}" -o "${BINARY}"

echo ""
echo "▶  Running ./${BINARY} ..."
./"${BINARY}"
