"""
Unit tests for vlang.parser — verify AST structure produced by the parser.

TDD status:
  - Tests for single-statement parsing: GREEN (current grammar supports it)
  - Tests for multiple statements:      RED   (grammar bug — only 1 statement works)
  - Tests for error handling:           RED   (structured errors not yet implemented)

When the grammar bug is fixed (multi-statement support), all RED tests
in TestParserMultipleStatements should turn GREEN without touching this file.

Run:
    pytest tests/unit/test_parser.py -v
"""

from __future__ import annotations

import pytest

from vlang.nodes import BinaryOp, Div, Mul, Number, Print, Sub, Sum, Program


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse(source: str):
    """Parse *source* and return the AST root node.

    Raises ValueError if the source is syntactically invalid.
    """
    from vlang.codegen import CodeGen
    from vlang.lexer import Lexer
    from vlang.parser import Parser
    from vlang.nodes import Program

    cg = CodeGen()
    lexer = Lexer().get_lexer()
    tokens = lexer.lex(source)
    pg = Parser(cg.module, cg.builder, cg.printf)
    pg.parse()
    ast = pg.get_parser().parse(tokens)
    if isinstance(ast, Program) and len(ast.statements) == 1:
        return ast.statements[0]
    return ast


def _parse_raises(source: str) -> Exception:
    """Assert that *source* raises during parsing, return the exception."""
    with pytest.raises(Exception) as exc_info:
        _parse(source)
    return exc_info.value


# ---------------------------------------------------------------------------
# Basic single-statement parsing (GREEN)
# ---------------------------------------------------------------------------

class TestParserBasic:
    """Single-statement programs that the current grammar handles correctly."""

    def test_parse_returns_print_node(self):
        """in_ra(42)\\n parses to a Print node."""
        node = _parse("in_ra(42)\n")
        assert isinstance(node, Print)

    def test_parse_literal_wraps_number(self):
        """Print node's value is a Number node for a bare literal."""
        node = _parse("in_ra(42)\n")
        assert isinstance(node.value, Number)

    def test_parse_literal_value_correct(self):
        """The Number node captures the correct string value from the token."""
        node = _parse("in_ra(42)\n")
        assert node.value.value == "42"

    def test_parse_addition_produces_sum(self):
        """in_ra(1+2)\\n → Print(Sum(Number(1), Number(2)))"""
        node = _parse("in_ra(1 + 2)\n")
        assert isinstance(node, Print)
        assert isinstance(node.value, Sum)

    def test_parse_addition_left_operand(self):
        node = _parse("in_ra(1 + 2)\n")
        assert isinstance(node.value.left, Number)
        assert node.value.left.value == "1"

    def test_parse_addition_right_operand(self):
        node = _parse("in_ra(1 + 2)\n")
        assert isinstance(node.value.right, Number)
        assert node.value.right.value == "2"

    def test_parse_subtraction_produces_sub(self):
        node = _parse("in_ra(5 - 3)\n")
        assert isinstance(node.value, Sub)

    def test_parse_multiplication_produces_mul(self):
        node = _parse("in_ra(4 * 3)\n")
        assert isinstance(node.value, Mul)

    def test_parse_division_produces_div(self):
        node = _parse("in_ra(10 / 2)\n")
        assert isinstance(node.value, Div)

    def test_parse_zero_literal(self):
        node = _parse("in_ra(0)\n")
        assert isinstance(node.value, Number)
        assert node.value.value == "0"

    def test_parse_large_literal(self):
        node = _parse("in_ra(99999)\n")
        assert isinstance(node.value, Number)
        assert node.value.value == "99999"


# ---------------------------------------------------------------------------
# Operator precedence (GREEN — rply handles this via _PRECEDENCE table)
# ---------------------------------------------------------------------------

class TestParserPrecedence:
    """Verify that operator precedence is encoded correctly in the AST.

    Multiplication and division bind tighter than addition and subtraction.
    """

    def test_mul_binds_tighter_than_add(self):
        """2 + 3 * 4 → Sum(Number(2), Mul(Number(3), Number(4)))"""
        node = _parse("in_ra(2 + 3 * 4)\n")
        # Top-level binary op should be Sum (addition), not Mul
        assert isinstance(node.value, Sum), (
            f"Expected Sum at top level but got {type(node.value).__name__}"
        )
        # Right operand of Sum should be Mul
        assert isinstance(node.value.right, Mul), (
            f"Expected Mul as right child but got {type(node.value.right).__name__}"
        )

    def test_div_binds_tighter_than_sub(self):
        """10 - 6 / 2 → Sub(Number(10), Div(Number(6), Number(2)))"""
        node = _parse("in_ra(10 - 6 / 2)\n")
        assert isinstance(node.value, Sub)
        assert isinstance(node.value.right, Div)

    def test_parens_override_precedence(self):
        """(2 + 3) * 4 → Mul(Sum(Number(2), Number(3)), Number(4))"""
        node = _parse("in_ra((2 + 3) * 4)\n")
        assert isinstance(node.value, Mul), (
            f"Expected Mul at top level but got {type(node.value).__name__}"
        )
        assert isinstance(node.value.left, Sum)

    def test_left_associative_addition(self):
        """1 + 2 + 3 → Sum(Sum(1, 2), 3)  (left-associative)"""
        node = _parse("in_ra(1 + 2 + 3)\n")
        assert isinstance(node.value, Sum)
        # Left operand should be a Sum (not right — left-associative)
        assert isinstance(node.value.left, Sum)
        assert isinstance(node.value.right, Number)

    def test_deeply_nested_parens(self):
        """((1 + 2)) parses without error."""
        node = _parse("in_ra(((1 + 2)))\n")
        assert isinstance(node.value, Sum)

    def test_mixed_precedence_complex(self):
        """2 * 3 + 4 * 5 → Sum(Mul(2,3), Mul(4,5))"""
        node = _parse("in_ra(2 * 3 + 4 * 5)\n")
        assert isinstance(node.value, Sum)
        assert isinstance(node.value.left, Mul)
        assert isinstance(node.value.right, Mul)


# ---------------------------------------------------------------------------
# Multiple statements — RED (grammar bug: only 1 statement parses)
# ---------------------------------------------------------------------------

class TestParserMultipleStatements:
    """Tests that document the DESIRED behaviour for multi-statement programs.

    These tests are RED right now because the grammar only parses a single
    `in_ra(...)\\n` statement.  They should turn GREEN when the grammar is
    extended to `program : statement+`.

    DO NOT remove the xfail marks until the grammar is fixed.
    """

    def test_two_print_statements(self):
        """Two in_ra lines should both be parsed."""
        source = "in_ra(1)\nin_ra(2)\n"
        # After grammar fix, this should return a list or Program node
        result = _parse(source)
        # result should contain 2 Print nodes
        assert isinstance(result, Program)
        assert len(result.statements) == 2
        assert isinstance(result.statements[0], Print)
        assert isinstance(result.statements[1], Print)

    def test_three_print_statements(self):
        source = "in_ra(1)\nin_ra(2)\nin_ra(3)\n"
        result = _parse(source)
        assert isinstance(result, Program)
        assert len(result.statements) == 3
        assert all(isinstance(stmt, Print) for stmt in result.statements)

    def test_arithmetic_then_print(self):
        """Program with two different arithmetic expressions."""
        source = "in_ra(1 + 2)\nin_ra(3 * 4)\n"
        result = _parse(source)
        assert isinstance(result, Program)
        assert len(result.statements) == 2
        assert isinstance(result.statements[0], Print)
        assert isinstance(result.statements[1], Print)


# ---------------------------------------------------------------------------
# Parser error handling
# ---------------------------------------------------------------------------

class TestParserErrors:
    """Verify that malformed input raises an exception (not a silent wrong result).

    Currently raises ValueError from rply's error handler. In future, this
    should raise a structured vlang.errors.ParseError with location info.
    """

    def test_empty_parens_raises(self):
        """in_ra() with no expression should raise."""
        with pytest.raises(Exception):
            _parse("in_ra()\n")

    def test_double_operator_raises(self):
        """in_ra(1 ++ 2) is a syntax error."""
        with pytest.raises(Exception):
            _parse("in_ra(1 ++ 2)\n")

    def test_operator_only_raises(self):
        """in_ra(+) is a syntax error."""
        with pytest.raises(Exception):
            _parse("in_ra(+)\n")

    def test_unclosed_paren_raises(self):
        """Missing closing paren should raise."""
        with pytest.raises(Exception):
            _parse("in_ra(1 + 2\n")

    def test_unrecognised_token_raises(self):
        """An unknown character in expression position should raise."""
        with pytest.raises(Exception):
            _parse("in_ra(@)\n")

    def test_invalid_start_raises(self):
        """Invalid syntax raises ParseError."""
        with pytest.raises(Exception):
            _parse("+ 42\n")


# ---------------------------------------------------------------------------
# AST node type invariants
# ---------------------------------------------------------------------------

class TestASTNodeTypes:
    """Invariant checks on the types of nodes produced by the parser."""

    @pytest.mark.parametrize("source, expected_type", [
        ("in_ra(1 + 2)\n", Sum),
        ("in_ra(5 - 3)\n", Sub),
        ("in_ra(4 * 3)\n", Mul),
        ("in_ra(8 / 4)\n", Div),
    ])
    def test_binary_op_types(self, source: str, expected_type: type) -> None:
        """Parametrised: each arithmetic op produces the correct BinaryOp subtype."""
        node = _parse(source)
        assert isinstance(node.value, expected_type)

    @pytest.mark.parametrize("source", [
        "in_ra(1 + 2)\n",
        "in_ra(3 - 1)\n",
        "in_ra(4 * 5)\n",
        "in_ra(10 / 2)\n",
    ])
    def test_binary_ops_are_binaryop_subclass(self, source: str) -> None:
        """All binary op nodes must be BinaryOp subclasses."""
        node = _parse(source)
        assert isinstance(node.value, BinaryOp)

    @pytest.mark.parametrize("literal", ["0", "1", "42", "100", "99999"])
    def test_number_node_stores_string(self, literal: str) -> None:
        """Number node stores the value as a string (as-is from lexer)."""
        node = _parse(f"in_ra({literal})\n")
        assert node.value.value == literal
