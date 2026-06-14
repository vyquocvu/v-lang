# Đóng góp cho vylang / Contributing to vylang

Cảm ơn bạn đã quan tâm đến vylang! / Thank you for your interest in contributing!

---

## Mục lục / Table of Contents

- [Quy tắc ứng xử / Code of Conduct](#code-of-conduct)
- [Bắt đầu / Getting Started](#getting-started)
- [Cách đóng góp / How to Contribute](#how-to-contribute)
- [Quy trình phát triển / Development Workflow](#development-workflow)
- [Tiêu chuẩn code / Code Standards](#code-standards)
- [Commit Messages](#commit-messages)
- [Gửi Pull Request / Submitting a Pull Request](#submitting-a-pull-request)

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
By participating you agree to uphold it.

---

## Getting Started

### Prerequisites

- Python 3.11+
- `uv` package manager: `pip install uv`
- LLVM tools: `brew install llvm` (macOS) or `apt install llvm gcc` (Linux)

### Setup

```bash
# Clone the repo
git clone https://github.com/vyquocvu/vylang.git
cd vylang

# Create virtual environment and install dev dependencies
uv sync --all-extras

# Run the test suite to verify everything works
uv run pytest tests/ -v

# Try compiling an example
uv run vlang compile examples/hello.vpl
```

---

## How to Contribute

### 🐛 Reporting Bugs

1. Check [existing issues](https://github.com/vyquocvu/vylang/issues) first
2. Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md)
3. Include: OS, Python version, full error output, minimal `.vpl` file that reproduces it

### 💡 Suggesting Features

1. Open a [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md)
2. For new language keywords, use the [Keyword Proposal](.github/ISSUE_TEMPLATE/new_keyword.md) template
3. Discuss in [GitHub Discussions](https://github.com/vyquocvu/vylang/discussions) before opening a PR for large changes

### 📝 Improving Documentation

- Docs live in `docs/`
- Fix typos, improve examples, add tutorials — all welcome!
- Run locally: `uv run mkdocs serve`

### 🔧 Fixing Bugs / Implementing Features

1. Comment on the issue to claim it
2. Fork → branch → PR (see workflow below)

---

## Development Workflow

```bash
# Create a feature branch
git checkout -b feat/add-while-loop

# Make your changes...

# Run linting
uv run ruff check .
uv run ruff format .

# Run type checking
uv run mypy src/vlang --strict

# Run tests
uv run pytest tests/ -v

# Run the full check (what CI runs)
uv run ruff check . && uv run mypy src/vlang --strict && uv run pytest tests/ -v
```

### Project Structure

```
src/vlang/
├── __init__.py     # Package version
├── lexer.py        # Tokeniser (rply → lark migration in progress)
├── parser.py       # LALR parser
├── nodes.py        # AST node classes
├── codegen.py      # LLVM IR code generator (llvmlite)
├── cli.py          # CLI entry point
├── errors.py       # Error types and diagnostics
└── location.py     # Source location tracking

tests/
├── unit/           # Unit tests per module
├── integration/    # Full compile+run tests
├── conformance/    # Language spec tests
└── fuzz/           # Property-based fuzz tests

docs/               # MkDocs documentation
examples/           # Example .vpl programs
scripts/            # Build/utility scripts
```

---

## Code Standards

### Python Style
- **Formatter**: `ruff format` (PEP 8, line length 100)
- **Linter**: `ruff check` with `E`, `F`, `W`, `I`, `UP` rules
- **Types**: All public functions must have type annotations
- **Docstrings**: All public classes and methods must have docstrings

### Language Design Principles
- **Vietnamese first**: Keywords use Vietnamese words, not abbreviations
- **Explicit over implicit**: Prefer clarity over cleverness
- **Minimal**: Add keywords only when truly necessary
- **Consistent**: Follow patterns established in the README keyword table

### Tests
- Every new feature needs at least one unit test and one integration test
- Bug fixes must include a regression test
- Target: ≥ 85% coverage for new code

---

## Commit Messages

This project uses **Conventional Commits** (required for automated releases):

```
feat: add while loop (khi) support
fix: fix i8 overflow in Number node — use i64
docs: add while loop tutorial
test: add conformance tests for arithmetic precedence
refactor: migrate parser from rply to lark
chore: update llvmlite to 0.44
```

| Prefix | When to use | Version bump |
|---|---|---|
| `feat:` | New language feature or CLI command | Minor |
| `fix:` | Bug fix | Patch |
| `feat!:` or `fix!:` | Breaking change | Major |
| `docs:` | Documentation only | None |
| `test:` | Tests only | None |
| `refactor:` | Code refactor (no behavior change) | None |
| `chore:` | Maintenance, deps, CI | None |

---

## Submitting a Pull Request

1. **Keep PRs focused** — one feature or fix per PR
2. **Fill out the PR template** — describe what and why
3. **Ensure CI passes** — all checks must be green
4. **Add yourself** to `CONTRIBUTORS.md` (optional but appreciated)
5. **Link related issues** — use `Closes #123` in the PR description

### PR Review Process

- PRs need at least one approving review
- Reviewer will focus on: correctness, test coverage, consistency with language design
- Be responsive to feedback — stale PRs (30+ days no activity) may be closed

---

## Questions?

- 💬 [GitHub Discussions](https://github.com/vyquocvu/vylang/discussions) for questions
- 🐛 [GitHub Issues](https://github.com/vyquocvu/vylang/issues) for bugs
- 📧 Email: (maintainer contact in README)

Chúc bạn code vui! / Happy coding! 🇻🇳
