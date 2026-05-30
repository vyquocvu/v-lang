"""
Integration and End-to-End tests for the vlang compiler.

Compiles vlang source code down to LLVM IR, optionally invokes llc and gcc to produce
native binaries, and executes them to verify runtime output correctness.

Run:
    pytest tests/integration/test_compile.py -v
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
from conftest import compile_to_ir, run_vlang

# Detect toolchain availability
LLC_AVAILABLE = shutil.which("llc") is not None
GCC_AVAILABLE = shutil.which("gcc") is not None


class TestIROutput:
    """Verify code generation round-trips to textual LLVM IR."""

    def test_ir_round_trip_simple(self) -> None:
        """Compile a simple print expression and check basic IR structures."""
        ir_text = compile_to_ir("in_ra(42)\n")
        assert 'define void @"main"()' in ir_text
        assert 'call i32 (ptr, ...) @"printf"' in ir_text or 'call i32 (i8*, ...) @"printf"' in ir_text
        assert "ret void" in ir_text

    def test_ir_round_trip_complex(self) -> None:
        """Compile a nested arithmetic expression and check instructions in IR."""
        ir_text = compile_to_ir("in_ra(10 - 2 * 3 / 2)\n")
        assert "mul" in ir_text
        assert "sdiv" in ir_text
        assert "sub" in ir_text
        assert "ret void" in ir_text


@pytest.mark.slow
@pytest.mark.skipif(not (LLC_AVAILABLE and GCC_AVAILABLE), reason="Requires llc and gcc in PATH")
class TestBinaryExecution:
    """End-to-end compilation, assembly, linking, and native execution."""

    def _compile_and_run(self, source: str, tmp_path: Path) -> str:
        """Helper to compile, link, execute, and return stdout of a vlang source."""
        src_file = tmp_path / "app.vpl"
        src_file.write_text(source, encoding="utf-8")

        binary_name = "app_bin"
        binary_path = tmp_path / binary_name

        # Invoke the CLI to compile and link
        # CLI command is: vlang compile <file> -o <binary>
        res = run_vlang("compile", str(src_file), "-o", str(binary_path), cwd=tmp_path)
        assert res.returncode == 0, f"Compilation failed: {res.stderr}\n{res.stdout}"

        # Execute the generated native binary
        exec_res = subprocess.run(
            [str(binary_path)],
            capture_output=True,
            text=True,
            check=True,
        )
        return exec_res.stdout

    def test_compile_and_run_addition(self, tmp_path: Path) -> None:
        """Compile and run: addition -> prints '15'."""
        out = self._compile_and_run("in_ra(10 + 5)\n", tmp_path)
        assert out.strip() == "15"

    def test_compile_and_run_subtraction(self, tmp_path: Path) -> None:
        """Compile and run: subtraction -> prints '7'."""
        out = self._compile_and_run("in_ra(10 - 3)\n", tmp_path)
        assert out.strip() == "7"

    def test_compile_and_run_multiplication(self, tmp_path: Path) -> None:
        """Compile and run: multiplication -> prints '16'."""
        out = self._compile_and_run("in_ra(4 * 4)\n", tmp_path)
        assert out.strip() == "16"

    def test_compile_and_run_division(self, tmp_path: Path) -> None:
        """Compile and run: division -> prints '5'."""
        out = self._compile_and_run("in_ra(20 / 4)\n", tmp_path)
        assert out.strip() == "5"

    def test_compile_and_run_precedence(self, tmp_path: Path) -> None:
        """Compile and run: operator precedence -> prints '14' (2 + 3 * 4)."""
        out = self._compile_and_run("in_ra(2 + 3 * 4)\n", tmp_path)
        assert out.strip() == "14"
