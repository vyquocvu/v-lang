#!/usr/bin/env bash
# scripts/build.sh — compile a .van file all the way to a native binary.
#
# Usage: ./scripts/build.sh [source.van] [output-name]
#   source.van   — defaults to examples/hello.van
#   output-name  — defaults to "output"
#
# Prerequisites: llc (LLVM), gcc
set -euo pipefail

SOURCE="${1:-examples/hello.van}"
BINARY="${2:-output}"

echo "▶  Compiling ${SOURCE} ..."
vlang compile "${SOURCE}" -o "${BINARY}"

echo ""
echo "▶  Running ./${BINARY} ..."
./"${BINARY}"
