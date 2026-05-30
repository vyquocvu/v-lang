# Changelog

All notable changes to v-lang are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Version numbers follow [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Added
- `src/vlang/` package structure with `src` layout (PEP 517/518)
- `src/vlang/nodes.py` — AST node classes (renamed from `ast.py` to avoid stdlib shadow)
- `src/vlang/cli.py` — `vlang compile <file> [-o <binary>] [--ir-only]` CLI
- `src/vlang/errors.py` — structured error hierarchy (planned)
- `src/vlang/location.py` — source location tracking (planned)
- `pyproject.toml` — modern packaging with `vlang` CLI entry point
- `.gitignore` — covers `__pycache__`, `*.pyc`, LLVM build outputs
- `tests/test_lexer.py` — 13 lexer smoke tests
- `examples/hello.vpl` — cleaned example program
- `scripts/build.sh` — compile + link helper script
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`
- GitHub issue templates and PR template
- MkDocs documentation structure

### Fixed
- **Bug**: Token `NHO_HON)` had a stray `)` in the name — fixed to `NHO_HON`
- **Bug**: `ast.py` shadowed Python's stdlib `ast` module — renamed to `nodes.py`
- **Bug**: `*.pyc` and `__pycache__/` were committed to git — removed and ignored
- Added operator precedence table to parser (`NHAN`/`CHIA` over `CONG`/`TRU`)

### Changed
- Migrated from tabs to spaces throughout (PEP 8)
- Added docstrings and type annotations to all public classes and methods
- Replaced hardcoded `main.py` entry point with proper CLI (`argparse`)
- `main.py` → `src/vlang/cli.py`
- `text.vpl` → `examples/hello.vpl` (removed leading tabs)
- `test.sh` → `scripts/build.sh` (uses `vlang` CLI, accepts arguments)

### Removed
- `lexer.py.bk` — stale backup file (version control replaces it)
- Flat root source files (`main.py`, `ast.py`, `lexer.py`, `parser.py`, `codegen.py`)
- `text.vpl`, `test.sh` (replaced by `examples/hello.vpl`, `scripts/build.sh`)

---

## [0.0.1] — 2024 (Initial Hobby Version)

### Added
- Lexer: integer literals, 4 arithmetic operators, `in_ra` print keyword
- Parser: single `in_ra(expression)` statement, arithmetic with parentheses
- Code generator: LLVM IR via `llvmlite`, `printf` for output
- Build pipeline: `python main.py` → `output.ll` → `llc` → `gcc` → binary

[Unreleased]: https://github.com/vyquocvu/v-lang/compare/v0.1.0...HEAD
[0.0.1]: https://github.com/vyquocvu/v-lang/releases/tag/v0.0.1
