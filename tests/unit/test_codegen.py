"""
Unit tests for vlang.codegen — verify the code generation setup, LLVM module
configuration, and compiled IR correctness.

Run:
    pytest tests/unit/test_codegen.py -v
"""

from __future__ import annotations

from pathlib import Path
from vlang.codegen import CodeGen


class TestCodeGenSetup:
    """Verify the default state of the CodeGen compiler instance."""

    def test_codegen_initializes_module(self, fresh_codegen):
        """CodeGen should set up a default module and target triple."""
        assert fresh_codegen.module is not None
        assert fresh_codegen.module.triple != ""

    def test_module_has_main_function(self, fresh_codegen):
        """Module must declare a main function as entry point."""
        main_func = fresh_codegen.module.get_global("main")
        assert main_func is not None
        assert "main" in str(fresh_codegen.module)

    def test_printf_declared(self, fresh_codegen):
        """printf must be forward-declared in the module."""
        printf_func = fresh_codegen.module.get_global("printf")
        assert printf_func is not None
        assert "printf" in str(fresh_codegen.module)


class TestCodeGenIR:
    """Verify compiled IR output format and values using the conftest helpers."""

    def test_simple_add_in_ir(self):
        """Compiling an addition should emit the 'add' instruction in IR."""
        from conftest import compile_to_ir
        ir_text = compile_to_ir("in_ra(1 + 2)\n")
        assert "add" in ir_text

    def test_multiply_in_ir(self):
        """Compiling a multiplication should emit the 'mul' instruction in IR."""
        from conftest import compile_to_ir
        ir_text = compile_to_ir("in_ra(3 * 4)\n")
        assert "mul" in ir_text

    def test_ir_contains_ret_void(self):
        """main function must end with 'ret void' when finalised."""
        from conftest import compile_to_ir
        ir_text = compile_to_ir("in_ra(42)\n")
        assert "ret void" in ir_text

    def test_save_ir_creates_file(self, tmp_path):
        """save_ir() must write the LLVM IR representation to disk."""
        cg = CodeGen()
        # Emit IR for a dummy number node
        from vlang.nodes import Number
        cg.generate(Number("10"))
        cg.create_ir()

        output_path = tmp_path / "output.ll"
        cg.save_ir(str(output_path))

        assert output_path.exists()
        content = output_path.read_text(encoding="utf-8")
        assert "ModuleID" in content
        assert "main" in content
        assert "ret void" in content
