"""
Property-based fuzz testing for the vlang lexer.

Uses Hypothesis to verify lexer invariants over randomized input streams.

Run:
    pytest tests/fuzz/fuzz_lexer.py -v
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from vlang.lexer import Lexer


def _tokenize(source: str) -> list[tuple[str, str]]:
    """Return a list of (token_type, value) pairs for *source*."""
    lexer = Lexer().get_lexer()
    return [(t.gettokentype(), t.value) for t in lexer.lex(source)]


class TestLexerFuzz:
    """Hypothesis-based property verification for vlang tokenization."""

    @given(st.text())
    @settings(max_examples=500)
    def test_lexer_never_panics(self, source: str) -> None:
        """Lexer must not raise unexpected exceptions on arbitrary text."""
        try:
            _tokenize(source)
        except Exception as exc:
            # Only rply LexingError is acceptable
            assert "LexingError" in type(exc).__name__ or "Lex" in type(exc).__name__, (
                f"Unexpected exception type {type(exc).__name__}: {exc!r}"
            )

    @given(st.text(alphabet="0123456789"))
    @settings(max_examples=200)
    def test_numbers_always_produce_so_nguyen(self, digits: str) -> None:
        """Any non-empty string of ASCII digits tokenises as SO_NGUYEN."""
        if not digits:
            return  # empty string is fine — produces no tokens
        tokens = _tokenize(digits)
        assert all(t == "SO_NGUYEN" for t, _ in tokens)

    @given(st.text(alphabet=" \t\n"))
    @settings(max_examples=100)
    def test_whitespace_only_no_crash(self, whitespace: str) -> None:
        """Pure whitespace never crashes the lexer."""
        try:
            _tokenize(whitespace)
        except Exception as exc:
            assert "LexingError" in type(exc).__name__ or "Lex" in type(exc).__name__

    @given(st.text(alphabet="0123456789+-*/()=<>!\n "))
    @settings(max_examples=300)
    def test_valid_chars_no_internal_crash(self, source: str) -> None:
        """Characters used in vlang expressions should not cause internal errors."""
        try:
            _tokenize(source)
        except Exception as exc:
            assert "LexingError" in type(exc).__name__ or "Lex" in type(exc).__name__
