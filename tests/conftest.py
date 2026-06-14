"""
Shared pytest fixtures for the v-lang test suite.

Fixtures are organised into tiers:
  - Tier 1  (low-level)  : CodeGen / LLVM primitives
  - Tier 2  (mid-level)  : helpers that call the compiler pipeline
  - Tier 3  (high-level) : file-system helpers for CLI / integration tests

Usage
-----
All fixtures are auto-available via pytest's conftest mechanism — no import
is needed in test files that live under `tests/`.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    pass

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"
CONFORMANCE_DIR = Path(__file__).parent / "conformance" / "programs"


# ---------------------------------------------------------------------------
# Tier 1 — Low-level LLVM / CodeGen fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def fresh_codegen():
    """Return a freshly initialised CodeGen instance.

    Each test that needs LLVM interaction should request this fixture so that
    a clean module, builder, and printf declaration are available.  LLVM is
    initialised exactly once per fixture invocation.
    """
    from vlang.codegen import CodeGen  # import lazily — llvmlite may be absent
    return CodeGen()


@pytest.fixture()
def module(fresh_codegen):
    """The ``ir.Module`` from a fresh CodeGen instance."""
    return fresh_codegen.module


@pytest.fixture()
def builder(fresh_codegen):
    """The ``ir.IRBuilder`` from a fresh CodeGen instance."""
    return fresh_codegen.builder


@pytest.fixture()
def printf(fresh_codegen):
    """The ``printf`` ``ir.Function`` declared in the fresh module."""
    return fresh_codegen.printf


@pytest.fixture()
def visitor(fresh_codegen):
    """A ``CodeGenVisitor`` wired to a fresh CodeGen's module/builder/printf.

    Use ``visitor.visit(node, {})`` or ``visitor.generate(node)`` to emit IR,
    then assert on ``str(visitor.module)``.
    """
    from vlang.visitor import CodeGenVisitor

    return CodeGenVisitor(
        fresh_codegen.module, fresh_codegen.builder, fresh_codegen.printf
    )


# ---------------------------------------------------------------------------
# Tier 2 — Pipeline helpers
# ---------------------------------------------------------------------------

def tokenize(source: str) -> list[tuple[str, str]]:
    """Lex *source* and return a list of (token_type, value) pairs.

    This is the same helper used in ``test_lexer.py`` — replicated here so
    other test modules can also import it from conftest or call it directly.
    """
    from vlang.lexer import Lexer

    lexer = Lexer().get_lexer()
    return [(t.gettokentype(), t.value) for t in lexer.lex(source)]


def token_types(source: str) -> list[str]:
    """Return only the token type names for *source* (no values)."""
    return [tt for tt, _ in tokenize(source)]


def compile_to_ir(source: str) -> str:
    """Compile *source* through the full pipeline and return LLVM IR as text.

    This helper creates a temporary CodeGen and Parser, evaluates the AST,
    and returns ``str(module)`` — the LLVM IR text representation.

    Raises
    ------
    ValueError
        If the source has a parse or code-generation error.
    """
    from vlang.codegen import CodeGen
    from vlang.lexer import Lexer
    from vlang.parser import Parser

    lexer = Lexer().get_lexer()
    tokens = lexer.lex(source)

    cg = CodeGen()
    pg = Parser()
    pg.parse()
    parser = pg.get_parser()

    ast = parser.parse(tokens)
    cg.generate(ast)
    cg.create_ir()
    return str(cg.module)


def parse_source(source: str):
    """Parse *source* and return the AST root node (not yet evaluated).

    Useful for testing AST node types and structure without triggering
    LLVM IR emission.
    """
    from vlang.lexer import Lexer
    from vlang.parser import Parser

    lexer = Lexer().get_lexer()
    tokens = lexer.lex(source)

    pg = Parser()
    pg.parse()
    parser = pg.get_parser()
    return parser.parse(tokens)


# ---------------------------------------------------------------------------
# Tier 3 — Filesystem / CLI helpers
# ---------------------------------------------------------------------------

@pytest.fixture()
def van_file(tmp_path):
    """Factory fixture: creates a .vpl source file in a temp directory.

    Usage in tests::

        def test_something(van_file):
            path = van_file("in_ra(1 + 2)\\n")
            result = subprocess.run(["vlang", "compile", str(path)], ...)
    """

    def _make(source: str, name: str = "test.vpl") -> Path:
        p = tmp_path / name
        p.write_text(source, encoding="utf-8")
        return p

    return _make


def run_vlang(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Run the vlang CLI with *args* and return the completed process.

    Uses the same Python interpreter that is running pytest so that the
    installed (editable) vlang package is always on the path.
    """
    return subprocess.run(
        [sys.executable, "-m", "vlang.cli", *args],
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
    )


@pytest.fixture()
def run_cli(tmp_path):
    """Fixture that provides a ``run_cli(source, *extra_args)`` callable.

    Writes *source* to a temporary file, invokes ``vlang compile``, and
    returns the ``CompletedProcess`` result.
    """

    def _run(source: str, *extra_args: str) -> subprocess.CompletedProcess[str]:
        p = tmp_path / "prog.vpl"
        p.write_text(source, encoding="utf-8")
        return run_vlang("compile", str(p), *extra_args, cwd=tmp_path)

    return _run


# ---------------------------------------------------------------------------
# Markers
# ---------------------------------------------------------------------------

def pytest_configure(config):  # type: ignore[no-untyped-def]
    """Register custom markers so pytest doesn't emit PytestUnknownMarkWarning."""
    config.addinivalue_line("markers", "slow: mark test as slow (integration / E2E)")
    config.addinivalue_line("markers", "requires_llc: mark test that needs llc binary")
    config.addinivalue_line("markers", "requires_gcc: mark test that needs gcc binary")
