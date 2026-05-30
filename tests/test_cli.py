"""
CLI integration tests for the vlang compiler.

Verify argument parsing, file reading, stdout formatting, and error exit codes.

Run:
    pytest tests/test_cli.py -v
"""

from __future__ import annotations

from pathlib import Path
import pytest
from conftest import run_vlang


class TestCLIArgParsing:
    """Verify that argparse rejects malformed arguments and outputs help."""

    def test_no_args_exits_with_error(self):
        """Invoking vlang without any command or options should exit with code 2."""
        res = run_vlang()
        assert res.returncode == 2
        assert "usage:" in res.stderr

    def test_invalid_command_exits_with_error(self):
        """Invoking an invalid command should exit with code 2."""
        res = run_vlang("run", "file.vpl")
        assert res.returncode == 2
        assert "invalid choice" in res.stderr

    def test_compile_missing_source_exits_with_error(self):
        """Invoking compile without specifying the source file should exit with code 2."""
        res = run_vlang("compile")
        assert res.returncode == 2
        assert "the following arguments are required: source" in res.stderr


class TestCLICompile:
    """Verify compile command execution with valid and invalid inputs."""

    def test_compile_valid_source_exit_0(self, run_cli, tmp_path):
        """Compiling a valid file should print a success mark and exit with 0."""
        res = run_cli("in_ra(42)\n")
        assert res.returncode == 0
        assert "✓  LLVM IR written to output.ll" in res.stdout

        # Verify output.ll exists
        ir_file = tmp_path / "output.ll"
        assert ir_file.exists()
        assert "main" in ir_file.read_text()

    def test_compile_missing_file_exit_1(self):
        """Compiling a non-existent file should print an error and exit with 1."""
        res = run_vlang("compile", "non_existent_file_xyz.vpl")
        assert res.returncode == 1
        assert "error: file not found" in res.stderr

    def test_compile_invalid_syntax_exit_1(self, run_cli):
        """Compiling a file with invalid syntax should print error message and exit with 1."""
        res = run_cli("in_ra(@)\n")
        assert res.returncode == 1
        assert "error: " in res.stderr
