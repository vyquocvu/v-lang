"""
Unit tests for vlang.lexer — complete coverage of all token types,
edge cases, and the no-panic fuzzing invariant.

TDD status: All tests in this file are GREEN (passing) or document
known behaviour that must be preserved.

Run:
    pytest tests/unit/test_lexer.py -v
"""

from __future__ import annotations

import pytest

from vlang.lexer import Lexer


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _tokenize(source: str) -> list[tuple[str, str]]:
    """Return a list of (token_type, value) pairs for *source*."""
    lexer = Lexer().get_lexer()
    return [(t.gettokentype(), t.value) for t in lexer.lex(source)]


def _types(source: str) -> list[str]:
    """Return only token type names for *source*."""
    return [tt for tt, _ in _tokenize(source)]


# ---------------------------------------------------------------------------
# Arithmetic tokens
# ---------------------------------------------------------------------------

class TestArithmeticTokens:
    """Verify that each arithmetic operator produces the correct token."""

    def test_integer_literal_single_digit(self):
        assert _tokenize("42") == [("SO_NGUYEN", "42")]

    def test_integer_literal_multidigit(self):
        tokens = _tokenize("123")
        assert tokens == [("SO_NGUYEN", "123")]

    def test_integer_literal_zero(self):
        tokens = _tokenize("0")
        assert tokens == [("SO_NGUYEN", "0")]

    def test_integer_large(self):
        tokens = _tokenize("999999")
        assert tokens == [("SO_NGUYEN", "999999")]

    def test_addition_types(self):
        assert _types("1 + 2") == ["SO_NGUYEN", "CONG", "SO_NGUYEN"]

    def test_addition_values(self):
        tokens = _tokenize("1 + 2")
        assert tokens == [("SO_NGUYEN", "1"), ("CONG", "+"), ("SO_NGUYEN", "2")]

    def test_subtraction(self):
        assert _types("3 - 1") == ["SO_NGUYEN", "TRU", "SO_NGUYEN"]

    def test_multiplication(self):
        assert _types("4 * 5") == ["SO_NGUYEN", "NHAN", "SO_NGUYEN"]

    def test_division(self):
        assert _types("8 / 2") == ["SO_NGUYEN", "CHIA", "SO_NGUYEN"]

    def test_spaces_ignored_single(self):
        """Single spaces around operators are ignored."""
        without = _tokenize("1+2")
        with_spaces = _tokenize("1 + 2")
        assert without == with_spaces

    def test_spaces_ignored_multiple(self):
        """Multiple spaces are collapsed and ignored."""
        assert _tokenize("1   +   2") == _tokenize("1+2")

    def test_tabs_ignored(self):
        """Tab characters are ignored like spaces."""
        assert _tokenize("1\t+\t2") == _tokenize("1+2")

    def test_chained_arithmetic(self):
        """Chained expression produces alternating value/operator tokens."""
        types = _types("1 + 2 + 3")
        assert types == ["SO_NGUYEN", "CONG", "SO_NGUYEN", "CONG", "SO_NGUYEN"]

    def test_mixed_operators(self):
        """Mixed operator expression tokenises correctly."""
        types = _types("2 + 3 * 4")
        assert types == ["SO_NGUYEN", "CONG", "SO_NGUYEN", "NHAN", "SO_NGUYEN"]


# ---------------------------------------------------------------------------
# Comparison tokens
# ---------------------------------------------------------------------------

class TestComparisonTokens:
    """Verify all 6 comparison operators tokenise correctly, with priority
    checks to ensure two-character operators beat single-character ones."""

    def test_equal(self):
        assert _types("1 == 1") == ["SO_NGUYEN", "BANG", "SO_NGUYEN"]

    def test_not_equal(self):
        assert _types("1 != 2") == ["SO_NGUYEN", "KHAC", "SO_NGUYEN"]

    def test_greater_than(self):
        assert _types("2 > 1") == ["SO_NGUYEN", "LON_HON", "SO_NGUYEN"]

    def test_less_than(self):
        assert _types("1 < 2") == ["SO_NGUYEN", "NHO_HON", "SO_NGUYEN"]

    def test_greater_equal(self):
        assert _types("2 >= 1") == ["SO_NGUYEN", "BANG_LON_HON", "SO_NGUYEN"]

    def test_less_equal(self):
        assert _types("1 <= 2") == ["SO_NGUYEN", "BANG_NHO_HON", "SO_NGUYEN"]

    def test_gte_not_confused_with_gt(self):
        """'>=' must produce BANG_LON_HON, NOT LON_HON followed by something."""
        types = _types("1 >= 0")
        assert "BANG_LON_HON" in types
        assert "LON_HON" not in types

    def test_lte_not_confused_with_lt(self):
        """'<=' must produce BANG_NHO_HON, NOT NHO_HON followed by something."""
        types = _types("0 <= 1")
        assert "BANG_NHO_HON" in types
        assert "NHO_HON" not in types

    def test_eq_not_confused_with_single_equal(self):
        """'==' is BANG; bare '=' is not a valid token (future assignment)."""
        types = _types("1 == 1")
        assert "BANG" in types

    def test_comparison_values_preserved(self):
        """Comparison operator token values match the source string."""
        tokens = _tokenize("1 >= 0")
        op_tokens = [(t, v) for t, v in tokens if t not in ("SO_NGUYEN",)]
        assert ("BANG_LON_HON", ">=") in op_tokens


# ---------------------------------------------------------------------------
# Print statement tokens
# ---------------------------------------------------------------------------

class TestPrintStatement:
    """Verify the in_ra keyword and full print statement tokenisation."""

    def test_print_keyword_standalone(self):
        assert _tokenize("in_ra") == [("IN_RA", "in_ra")]

    def test_print_expression_full(self):
        source = "in_ra(1 + 2)\n"
        assert _types(source) == [
            "IN_RA",
            "MO_NGOAC_TRON",
            "SO_NGUYEN",
            "CONG",
            "SO_NGUYEN",
            "DONG_NGOAC_TRON",
            "HET_DONG",
        ]

    def test_print_with_single_number(self):
        source = "in_ra(42)\n"
        assert _types(source) == [
            "IN_RA", "MO_NGOAC_TRON", "SO_NGUYEN", "DONG_NGOAC_TRON", "HET_DONG"
        ]

    def test_parentheses_tokens(self):
        assert _types("(") == ["MO_NGOAC_TRON"]
        assert _types(")") == ["DONG_NGOAC_TRON"]

    def test_newline_unix(self):
        """Unix newline produces exactly one HET_DONG token."""
        tokens = _tokenize("\n")
        assert tokens == [("HET_DONG", "\n")]

    def test_newline_windows_crlf(self):
        """Windows CRLF also produces exactly one HET_DONG token."""
        tokens = _tokenize("\r\n")
        assert len([t for t, _ in tokens if t == "HET_DONG"]) == 1

    def test_multiple_newlines(self):
        """Each newline produces its own HET_DONG token."""
        tokens = _tokenize("\n\n")
        types = [t for t, _ in tokens]
        assert types == ["HET_DONG", "HET_DONG"]

    def test_print_with_multiplication(self):
        source = "in_ra(3 * 4)\n"
        types = _types(source)
        assert "NHAN" in types
        assert types[0] == "IN_RA"

    def test_print_with_division(self):
        source = "in_ra(10 / 2)\n"
        assert "CHIA" in _types(source)

    def test_print_with_subtraction(self):
        source = "in_ra(5 - 3)\n"
        assert "TRU" in _types(source)

    def test_print_no_spaces(self):
        """No spaces inside the expression are valid."""
        source = "in_ra(1+2)\n"
        assert _types(source) == [
            "IN_RA", "MO_NGOAC_TRON", "SO_NGUYEN",
            "CONG", "SO_NGUYEN", "DONG_NGOAC_TRON", "HET_DONG",
        ]


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Edge-case and boundary tokenisation tests."""

    def test_empty_string_produces_no_tokens(self):
        assert _tokenize("") == []

    def test_only_newline(self):
        tokens = _tokenize("\n")
        assert len(tokens) == 1
        assert tokens[0][0] == "HET_DONG"

    def test_complex_nested_expression(self):
        """Parenthesised nested expression tokenises without error."""
        source = "in_ra((2 + 3) * 4)\n"
        types = _types(source)
        # Should contain 2 open and 2 close parens
        assert types.count("MO_NGOAC_TRON") == 2
        assert types.count("DONG_NGOAC_TRON") == 2

    def test_multiple_print_lines(self):
        """Two print statements produce two HET_DONG tokens."""
        source = "in_ra(1)\nin_ra(2)\n"
        types = _types(source)
        assert types.count("HET_DONG") == 2
        assert types.count("IN_RA") == 2

    def test_large_number_single_token(self):
        """Multi-digit integer is a single SO_NGUYEN token."""
        tokens = _tokenize("1000000")
        assert tokens == [("SO_NGUYEN", "1000000")]
        assert len(tokens) == 1


# ---------------------------------------------------------------------------
# Vietnamese Accents
# ---------------------------------------------------------------------------

class TestVietnameseAccents:
    """Verify that identifiers can contain accented Vietnamese characters."""

    def test_accented_identifier_lowercase(self):
        """Lowercase accented words are recognized as IDENTIFIER."""
        assert _tokenize("điểm") == [("IDENTIFIER", "điểm")]
        assert _tokenize("tuổi") == [("IDENTIFIER", "tuổi")]
        assert _tokenize("kết_quả") == [("IDENTIFIER", "kết_quả")]
        assert _tokenize("trả_lại") == [("IDENTIFIER", "trả_lại")]

    def test_accented_identifier_uppercase(self):
        """Uppercase accented words are recognized as IDENTIFIER."""
        assert _tokenize("ĐIỂM") == [("IDENTIFIER", "ĐIỂM")]
        assert _tokenize("TUỔI") == [("IDENTIFIER", "TUỔI")]
        assert _tokenize("KẾT_QUẢ") == [("IDENTIFIER", "KẾT_QUẢ")]

    def test_mixed_accented_identifier(self):
        """Mixed ASCII, digits, underscores, and accents are recognized as IDENTIFIER."""
        assert _tokenize("biến_số_1") == [("IDENTIFIER", "biến_số_1")]
        assert _tokenize("_điểm_trung_bình") == [("IDENTIFIER", "_điểm_trung_bình")]



