"""
Unit tests for vlang.nodes — verify behavior of AST nodes when evaluated.

TDD status:
  - Primitive and binary nodes: GREEN (eval returns correct LLVM IR types)
  - Large value support:       RED   (xfail — Number uses i8, caps at 127/255)
  - Multiple print statements:  RED   (xfail — fstr global name conflict)

Run:
    pytest tests/unit/test_nodes.py -v
"""

from __future__ import annotations

import pytest
from llvmlite import ir

from vlang.nodes import Div, Mul, Number, Print, Sub, Sum


# ---------------------------------------------------------------------------
# Number Node Tests
# ---------------------------------------------------------------------------

class TestNumberNode:
    """Verify that Number AST node correctly creates LLVM integer constants."""

    def test_number_eval_returns_constant(self, builder, module):
        """Number.eval() should return an ir.Constant."""
        node = Number(builder, module, "42")
        val = node.eval()
        assert isinstance(val, ir.Constant)

    def test_number_value_is_correct(self, builder, module):
        """The constant value returned by Number.eval() should match the parsed integer."""
        node = Number(builder, module, "42")
        val = node.eval()
        assert val.constant == 42

    def test_number_zero(self, builder, module):
        """Zero is evaluated correctly."""
        node = Number(builder, module, "0")
        val = node.eval()
        assert val.constant == 0

    @pytest.mark.xfail(
        reason="Bug: Number uses 8-bit integers which caps/overflows above 127",
        strict=True,
    )
    def test_number_large_value_i64(self, builder, module):
        """Large values should use i64 (or at least i32) and not overflow/wrap."""
        node = Number(builder, module, "999")
        val = node.eval()
        # If it uses i8, 999 becomes 999 % 256 = 231 (or signed -25), not 999!
        assert val.constant == 999
        assert val.type == ir.IntType(64)


# ---------------------------------------------------------------------------
# Binary Operation Node Tests
# ---------------------------------------------------------------------------

class TestBinaryOpNodes:
    """Verify that binary AST nodes generate the correct LLVM IR instructions."""

    def test_sum_eval_emits_add_instruction(self, builder, module):
        """Sum node should emit an 'add' instruction."""
        left = Number(builder, module, "10")
        right = Number(builder, module, "5")
        node = Sum(builder, module, left, right)
        res = node.eval()
        assert isinstance(res, ir.Instruction)
        assert res.opname == "add"

    def test_sub_eval_emits_sub_instruction(self, builder, module):
        """Sub node should emit a 'sub' instruction."""
        left = Number(builder, module, "10")
        right = Number(builder, module, "5")
        node = Sub(builder, module, left, right)
        res = node.eval()
        assert isinstance(res, ir.Instruction)
        assert res.opname == "sub"

    def test_mul_eval_emits_mul_instruction(self, builder, module):
        """Mul node should emit a 'mul' instruction."""
        left = Number(builder, module, "10")
        right = Number(builder, module, "5")
        node = Mul(builder, module, left, right)
        res = node.eval()
        assert isinstance(res, ir.Instruction)
        assert res.opname == "mul"

    def test_div_eval_emits_sdiv_instruction(self, builder, module):
        """Div node should emit a signed division instruction ('sdiv')."""
        left = Number(builder, module, "10")
        right = Number(builder, module, "5")
        node = Div(builder, module, left, right)
        res = node.eval()
        assert isinstance(res, ir.Instruction)
        assert res.opname == "sdiv"

    def test_nested_binary_operators(self, builder, module):
        """Nested operations emit multiple instructions in sequence."""
        # (1 + 2) * 3
        op1 = Sum(builder, module, Number(builder, module, "1"), Number(builder, module, "2"))
        op2 = Mul(builder, module, op1, Number(builder, module, "3"))
        res = op2.eval()
        assert isinstance(res, ir.Instruction)
        assert res.opname == "mul"
        # The operands should be the results of the sub-expressions
        assert len(res.operands) == 2


# ---------------------------------------------------------------------------
# Print Node Tests
# ---------------------------------------------------------------------------

class TestPrintNode:
    """Verify that Print AST nodes correctly declare and call printf."""

    def test_print_calls_printf(self, builder, module, printf):
        """Print.eval() should call printf function."""
        val = Number(builder, module, "42")
        node = Print(builder, module, printf, val)
        node.eval()

        # The last instruction in the builder's basic block should be a call
        instr = builder.block.instructions[-1]
        assert instr.opname == "call"
        assert instr.operands[0] == printf

    def test_print_ir_contains_format_str(self, builder, module, printf):
        """Emitted IR text contains the format string literal."""
        val = Number(builder, module, "42")
        node = Print(builder, module, printf, val)
        node.eval()
        ir_text = str(module)
        assert 'c"%i \\0a\\00"' in ir_text

    @pytest.mark.xfail(
        reason="Bug: duplicate global fstr name conflict on 2nd print",
        strict=True,
    )
    def test_print_twice_no_conflict(self, builder, module, printf):
        """Two print node evaluations shouldn't result in duplicate global variables in the module."""
        val1 = Number(builder, module, "42")
        node1 = Print(builder, module, printf, val1)
        node1.eval()

        val2 = Number(builder, module, "100")
        node2 = Print(builder, module, printf, val2)
        node2.eval()  # Should not raise a duplicate name / symbol conflict
