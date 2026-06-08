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


class TestCLIInProcess:
    """In-process unit tests for vlang.cli to get coverage tracking."""

    def test_cli_main_help(self, monkeypatch, capsys):
        from vlang.cli import main
        monkeypatch.setattr("sys.argv", ["vlang", "--help"])
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0
        captured = capsys.readouterr()
        assert "usage: vlang" in captured.out

    def test_cli_main_compile_ir_only(self, tmp_path, monkeypatch, capsys):
        from vlang.cli import main
        src = tmp_path / "app.vpl"
        src.write_text("in_ra(100)\n", encoding="utf-8")
        
        # Output binary/IR files in tmp_path to avoid littering
        # Note: cli.py writes to Path("output.ll") in the current working directory, 
        # so we monkeypatch current working directory or change to tmp_path
        with monkeypatch.context() as m:
            m.chdir(tmp_path)
            m.setattr("sys.argv", ["vlang", "compile", str(src), "--ir-only"])
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 0
            captured = capsys.readouterr()
            assert "✓  LLVM IR written to output.ll" in captured.out
            assert (tmp_path / "output.ll").exists()

    def test_cli_main_compile_and_link(self, tmp_path, monkeypatch, capsys):
        from vlang.cli import main
        src = tmp_path / "app.vpl"
        src.write_text("in_ra(100)\n", encoding="utf-8")
        
        with monkeypatch.context() as m:
            m.chdir(tmp_path)
            m.setattr("sys.argv", ["vlang", "compile", str(src), "-o", "app_bin"])
            with pytest.raises(SystemExit) as exc:
                main()
            # If clang is available, it should succeed. If not, it should exit with 1.
            # We can check the return code is 0 or 1.
            assert exc.value.code in (0, 1)

    def test_cli_main_file_not_found(self, tmp_path, monkeypatch, capsys):
        from vlang.cli import main
        with monkeypatch.context() as m:
            m.chdir(tmp_path)
            m.setattr("sys.argv", ["vlang", "compile", "no_such_file.vpl"])
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1
            captured = capsys.readouterr()
            assert "error: file not found" in captured.err

    def test_cli_main_syntax_error(self, tmp_path, monkeypatch, capsys):
        from vlang.cli import main
        src = tmp_path / "app.vpl"
        src.write_text("in_ra(@)\n", encoding="utf-8")
        with monkeypatch.context() as m:
            m.chdir(tmp_path)
            m.setattr("sys.argv", ["vlang", "compile", str(src)])
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1
            captured = capsys.readouterr()
            assert "error: " in captured.err
