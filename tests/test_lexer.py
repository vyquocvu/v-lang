"""
Tests for vlang.lexer — verify that the tokenizer produces the
expected token types for basic vlang source snippets.

Run with:  pytest tests/ -v
"""

import pytest
from vlang.lexer import Lexer


def _tokenize(source: str) -> list[tuple[str, str]]:
    """Return a list of (token_type, value) pairs for *source*."""
    lexer = Lexer().get_lexer()
    return [(t.gettokentype(), t.value) for t in lexer.lex(source)]


class TestArithmeticTokens:
    def test_integer_literal(self):
        tokens = _tokenize("42")
        assert tokens == [("SO_NGUYEN", "42")]

    def test_addition(self):
        tokens = _tokenize("1 + 2")
        assert [t for t, _ in tokens] == ["SO_NGUYEN", "CONG", "SO_NGUYEN"]

    def test_subtraction(self):
        tokens = _tokenize("3 - 1")
        assert [t for t, _ in tokens] == ["SO_NGUYEN", "TRU", "SO_NGUYEN"]

    def test_multiplication(self):
        tokens = _tokenize("4 * 5")
        assert [t for t, _ in tokens] == ["SO_NGUYEN", "NHAN", "SO_NGUYEN"]

    def test_division(self):
        tokens = _tokenize("8 / 2")
        assert [t for t, _ in tokens] == ["SO_NGUYEN", "CHIA", "SO_NGUYEN"]


class TestComparisonTokens:
    def test_equal(self):
        tokens = _tokenize("1 == 1")
        assert [t for t, _ in tokens] == ["SO_NGUYEN", "BANG", "SO_NGUYEN"]

    def test_greater_than(self):
        tokens = _tokenize("2 > 1")
        assert [t for t, _ in tokens] == ["SO_NGUYEN", "LON_HON", "SO_NGUYEN"]

    def test_less_than(self):
        tokens = _tokenize("1 < 2")
        assert [t for t, _ in tokens] == ["SO_NGUYEN", "NHO_HON", "SO_NGUYEN"]

    def test_not_equal(self):
        tokens = _tokenize("1 != 2")
        assert [t for t, _ in tokens] == ["SO_NGUYEN", "KHAC", "SO_NGUYEN"]

    def test_gte(self):
        tokens = _tokenize("2 >= 1")
        assert [t for t, _ in tokens] == ["SO_NGUYEN", "BANG_LON_HON", "SO_NGUYEN"]

    def test_lte(self):
        tokens = _tokenize("1 <= 2")
        assert [t for t, _ in tokens] == ["SO_NGUYEN", "BANG_NHO_HON", "SO_NGUYEN"]


class TestPrintStatement:
    def test_print_keyword(self):
        tokens = _tokenize("in_ra")
        assert tokens == [("IN_RA", "in_ra")]

    def test_print_expression(self):
        source = "in_ra(1 + 2)\n"
        token_types = [t for t, _ in _tokenize(source)]
        assert token_types == [
            "IN_RA",
            "MO_NGOAC_TRON",
            "SO_NGUYEN",
            "CONG",
            "SO_NGUYEN",
            "DONG_NGOAC_TRON",
            "HET_DONG",
        ]
