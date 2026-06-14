"""
Unit tests for vlang.nodes / vlang.visitor — verify the IR emitted when the
``CodeGenVisitor`` walks AST nodes.

Nodes are pure data; IR emission lives in the visitor, so these tests build
nodes and drive them through the ``visitor`` fixture.

Run:
    pytest tests/unit/test_nodes.py -v
"""

from __future__ import annotations

from llvmlite import ir

from vlang.nodes import Div, Mul, Number, Print, Sub, Sum


# ---------------------------------------------------------------------------
# Number Node Tests
# ---------------------------------------------------------------------------

class TestNumberNode:
    """Verify that Number AST node correctly creates LLVM integer constants."""

    def test_number_eval_returns_constant(self, visitor):
        """Visiting a Number should return an ir.Constant."""
        val = visitor.visit(Number("42"), {})
        assert isinstance(val, ir.Constant)

    def test_number_value_is_correct(self, visitor):
        """The constant value should match the parsed integer."""
        val = visitor.visit(Number("42"), {})
        assert val.constant == 42

    def test_number_zero(self, visitor):
        """Zero is evaluated correctly."""
        val = visitor.visit(Number("0"), {})
        assert val.constant == 0

    def test_number_large_value_i64(self, visitor):
        """Large values should use i64 and not overflow/wrap."""
        val = visitor.visit(Number("999"), {})
        assert val.constant == 999
        assert val.type == ir.IntType(64)


# ---------------------------------------------------------------------------
# Binary Operation Node Tests
# ---------------------------------------------------------------------------

class TestBinaryOpNodes:
    """Verify that binary AST nodes generate the correct LLVM IR instructions."""

    def test_sum_eval_emits_add_instruction(self, visitor):
        """Sum node should emit an 'add' instruction."""
        res = visitor.visit(Sum(Number("10"), Number("5")), {})
        assert isinstance(res, ir.Instruction)
        assert res.opname == "add"

    def test_sub_eval_emits_sub_instruction(self, visitor):
        """Sub node should emit a 'sub' instruction."""
        res = visitor.visit(Sub(Number("10"), Number("5")), {})
        assert isinstance(res, ir.Instruction)
        assert res.opname == "sub"

    def test_mul_eval_emits_mul_instruction(self, visitor):
        """Mul node should emit a 'mul' instruction."""
        res = visitor.visit(Mul(Number("10"), Number("5")), {})
        assert isinstance(res, ir.Instruction)
        assert res.opname == "mul"

    def test_div_eval_emits_sdiv_instruction(self, visitor):
        """Div node should emit a signed division instruction ('sdiv')."""
        res = visitor.visit(Div(Number("10"), Number("5")), {})
        assert isinstance(res, ir.Instruction)
        assert res.opname == "sdiv"

    def test_nested_binary_operators(self, visitor):
        """Nested operations emit multiple instructions in sequence."""
        # (1 + 2) * 3
        op1 = Sum(Number("1"), Number("2"))
        op2 = Mul(op1, Number("3"))
        res = visitor.visit(op2, {})
        assert isinstance(res, ir.Instruction)
        assert res.opname == "mul"
        # The operands should be the results of the sub-expressions
        assert len(res.operands) == 2


# ---------------------------------------------------------------------------
# Print Node Tests
# ---------------------------------------------------------------------------

class TestPrintNode:
    """Verify that Print AST nodes correctly declare and call printf."""

    def test_print_calls_printf(self, visitor):
        """Visiting a Print node should call the printf function."""
        visitor.visit(Print(Number("42")), {})

        # The last instruction in the builder's basic block should be a call
        instr = visitor.builder.block.instructions[-1]
        assert instr.opname == "call"
        assert instr.operands[0] == visitor.printf

    def test_print_ir_contains_format_str(self, visitor):
        """Emitted IR text contains the format string literal."""
        visitor.visit(Print(Number("42")), {})
        ir_text = str(visitor.module)
        assert 'c"%i\\0a\\00"' in ir_text

    def test_print_twice_no_conflict(self, visitor):
        """Two print evaluations shouldn't create duplicate global variables."""
        visitor.visit(Print(Number("42")), {})
        visitor.visit(Print(Number("100")), {})  # must not raise a name conflict
