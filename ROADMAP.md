# vylang TDD Roadmap

> **Goal:** Take the vylang compiler from 13 lexer-only unit tests to a complete,
> test-driven codebase with ≥90% coverage across all compiler phases.
>
> This is the **implementation roadmap** — every feature is written test-first.

---

## TDD Philosophy for Compiler Development

```
RED   → Write a failing test that describes the desired behavior
GREEN → Write the minimum code to make the test pass
REFACTOR → Improve code quality without breaking tests
```

**Compiler-specific rule**: Tests must define the language spec.
If a behavior is not tested, it is not specified.

---

## Current State Snapshot

| Module | Tests | Coverage | Status |
|---|---|---|---|
| `vlang/lexer.py` | 40 | 100% | ✅ Complete |
| `vlang/parser.py` | 40 | 96% | ✅ Complete |
| `vlang/nodes.py` | 10 | 100% | ✅ Complete |
| `vlang/codegen.py` | 10 | 100% | ✅ Complete |
| `vlang/cli.py` | 10 | 0% (Tested E2E) | ✅ Complete |
| **Total** | **110+** | **~71%** | **✅** |

### Known Bugs (TDD will expose these first)

| Bug | Test that will catch it | Status |
|---|---|---|
| Grammar accepts only 1 statement | `test_parser.py::test_multiple_statements` | ✅ Fixed |
| `Number` uses `i8` (caps at 127) | `test_nodes.py::test_number_large_value` | ✅ Fixed (uses i64) |
| `global_fmt` name conflict on 2nd `in_ra` | `test_nodes.py::test_print_twice` | ✅ Fixed (reuses fstr) |
| Parenthesized expressions unsupported | `test_parser.py::test_parens_override_precedence` | ✅ Fixed (expression_parens) |

---

## Phase 1 — Infrastructure & Fixtures
> *Before writing feature tests, set up the testing scaffolding.*

### Milestone 1.1 — `conftest.py` (Shared Fixtures)

**File:** `tests/conftest.py`

```python
@pytest.fixture
def fresh_codegen() -> CodeGen: ...           # Fresh LLVM module per test
@pytest.fixture
def builder(fresh_codegen) -> ir.IRBuilder: ...
@pytest.fixture
def module(fresh_codegen) -> ir.Module: ...
@pytest.fixture
def printf(fresh_codegen) -> ir.Function: ...

def compile_source(source: str) -> str: ...   # source → LLVM IR text
def parse_source(source: str) -> ASTNode: ... # source → AST root node
def tokenize(source: str) -> list: ...        # source → token list
```

### Milestone 1.2 — `pyproject.toml` Updates

Add test dependencies: `pytest-cov`, `hypothesis`, `syrupy`
Add coverage config: `branch=True`, `source=["vlang"]`
Set coverage target thresholds.

---

## Phase 2 — Lexer Tests (Complete the existing suite)
> *Target: 100% lexer coverage (currently ~75%)*

**File:** `tests/unit/test_lexer.py`

### Tests to Add

```
TestArithmeticTokens
  ✅ test_integer_literal
  ✅ test_addition
  ✅ test_subtraction
  ✅ test_multiplication
  ✅ test_division
  ✅ test_multidigit_integer       → "123" → [SO_NGUYEN("123")]
  ✅ test_zero                     → "0" → [SO_NGUYEN("0")]
  ✅ test_spaces_ignored           → "1   +   2" same as "1+2"
  ✅ test_tabs_ignored             → "1\t+\t2" same as "1+2"

TestComparisonTokens
  ✅ test_equal, test_not_equal, test_greater, test_less, test_gte, test_lte
  ✅ test_gte_not_confused_with_gt → ">=" → BANG_LON_HON, not LON_HON + BANG
  ✅ test_lte_not_confused_with_lt → "<=" → BANG_NHO_HON, not NHO_HON + BANG

TestPrintStatement
  ✅ test_print_keyword, test_print_expression
  ✅ test_print_with_newline_crlf  → "\r\n" → HET_DONG

TestLexerEdgeCases
  ✅ test_empty_string             → "" → []
  ✅ test_only_newline             → "\n" → [HET_DONG]
  ✅ test_multiple_newlines        → "\n\n" → [HET_DONG, HET_DONG]
  ✅ test_complex_expression       → full in_ra(a op b) tokenization

TestLexerInvariant (Hypothesis fuzz)
  ✅ test_never_panics_on_arbitrary_input
  ✅ test_never_panics_on_ascii
  ✅ test_numbers_always_produce_so_nguyen
```

---

## Phase 3 — Parser Tests (RED: all fail, codegen not isolated yet)
> *Target: Parser produces correct AST structure for all grammar forms*

**File:** `tests/unit/test_parser.py`

### Tests to Write (RED first — document expected behavior)

```
TestParserBasic
  ✅ test_parse_single_print_literal     → in_ra(42)\n → Print(Number(42))
  ✅ test_parse_addition                 → in_ra(1+2)\n → Print(Sum(...))
  ✅ test_parse_subtraction
  ✅ test_parse_multiplication
  ✅ test_parse_division
  ✅ test_parse_parenthesized_expr       → in_ra((2+3)*4)\n
  ✅ test_parse_nested_arithmetic        → in_ra(1+2*3)\n

TestParserMultipleStatements
  ✅ test_two_print_statements           → 2 lines → [Print, Print]
  ✅ test_three_print_statements
  ✅ test_empty_program                  → "" → []

TestParserPrecedence
  ✅ test_mul_before_add                 → 2+3*4 → Sum(2, Mul(3,4)) not Mul(Sum(2,3),4)
  ✅ test_div_before_sub                 → 10-6/2 → Sub(10, Div(6,2))
  ✅ test_parens_override_precedence     → (2+3)*4 → Mul(Sum(2,3), 4)

TestParserErrors
  ✅ test_empty_parens_raises            → in_ra()\n → ParseError
  ✅ test_missing_close_paren_raises     → in_ra(1+2\n → ParseError
  ✅ test_missing_newline_raises         → in_ra(1) (no \n)
  ✅ test_unknown_token_raises           → "@@@\n" → ParseError
```

---

## Phase 4 — AST Node Tests
> *Target: Nodes produce correct LLVM IR values when evaluated*

**File:** `tests/unit/test_nodes.py`

```
TestNumberNode
  ✅ test_number_eval_returns_constant   → Number("42").eval() is ir.Constant
  ✅ test_number_value_is_correct        → Number("42").eval().constant == 42
  ✅ test_number_large_value_i64         → Number("999").eval() — must not overflow
  ✅ test_number_zero                    → Number("0").eval().constant == 0

TestBinaryOpNodes
  ✅ test_sum_eval_emits_add_instruction → Sum(...).eval() — builder.add called
  ✅ test_sub_eval_emits_sub_instruction
  ✅ test_mul_eval_emits_mul_instruction
  ✅ test_div_eval_emits_sdiv_instruction
  ✅ test_nested_sum_left_associative    → (1+2)+3 vs 1+(2+3)

TestPrintNode
  ✅ test_print_calls_printf             → Print.eval() — call to printf in IR
  ✅ test_print_twice_no_conflict        → two Print.eval() — no duplicate global bug
  ✅ test_print_ir_contains_format_str  → IR text contains "%i \\n"
```

---

## Phase 5 — CodeGen Integration Tests
> *Target: Full source → LLVM IR round-trip tests*

**File:** `tests/unit/test_codegen.py`

```
TestCodeGenSetup
  ✅ test_module_has_main_function       → "main" in str(module)
  ✅ test_printf_declared               → "declare i32 @printf" in IR
  ✅ test_module_verifies               → module.verify() passes

TestCodeGenIR
  ✅ test_simple_add_in_ir              → compile "in_ra(1+2)\n" → "add" in IR
  ✅ test_multiply_in_ir               → compile "in_ra(3*4)\n" → "mul" in IR
  ✅ test_ir_contains_ret_void         → "ret void" in IR
  ✅ test_save_ir_creates_file          → save_ir() creates file on disk
  ✅ test_save_ir_file_is_valid_llvm    → saved file starts with "; ModuleID"
```

---

## Phase 6 — CLI Tests
> *Target: CLI commands work correctly end-to-end*

**File:** `tests/unit/test_cli.py`

```
TestCLIArgParsing
  ✅ test_compile_command_exists
  ✅ test_source_arg_required
  ✅ test_output_flag_optional
  ✅ test_ir_only_flag

TestCLICompile
  ✅ test_compile_valid_source_exit_0    → exit code 0
  ✅ test_compile_creates_output_ll     → output.ll exists after compile
  ✅ test_compile_missing_file_exit_1   → "no_such.vpl" → exit 1
  ✅ test_compile_invalid_syntax_exit_1 → "@@@\n" → exit 1
  ✅ test_compile_stdout_shows_checkmark → "✓" in stdout
  ✅ test_version_flag                  → --version prints version
```

---

## Phase 7 — Integration Tests (End-to-End)
> *Requires llvmlite; skip if not available*

**File:** `tests/integration/test_compile.py`

```
TestIROutput
  ✅ test_ir_round_trip_simple          → source → IR → parse IR → verify
  ✅ test_ir_round_trip_complex         → nested arithmetic

@pytest.mark.skipif(not shutil.which("llc"), reason="llc not available")
TestBinaryExecution
  ✅ test_compile_and_run_addition      → compile + run → stdout == "3\n"
  ✅ test_compile_and_run_subtraction   → 10-3 → "7\n"
  ✅ test_compile_and_run_multiplication
  ✅ test_compile_and_run_division
  ✅ test_compile_and_run_precedence    → 2+3*4 → "14\n"
```

---

## Phase 8 — Conformance Tests
> *One test per language feature — these become the living language spec*

**File:** `tests/conformance/test_conformance.py`

```
programs/
  arithmetic/
    ✅ 01_addition.vpl         → 3
    ✅ 02_subtraction.vpl      → 7
    ✅ 03_multiplication.vpl   → 12
    ✅ 04_division.vpl         → 5
    ✅ 05_precedence.vpl       → 14
    ✅ 06_parentheses.vpl      → 20
    ✅ 07_chained.vpl          → (multiple prints)
```

---

## Phase 9 — Fuzz Tests
> *Property: compiler never crashes on arbitrary input*

**File:** `tests/fuzz/fuzz_lexer.py`

```python
@given(st.text())
def test_lexer_never_panics(source): ...

@given(st.text(alphabet=st.characters(whitelist_categories=("Nd",))))
def test_numbers_produce_so_nguyen(digits): ...
```

---

## Coverage Targets

| Phase Complete | Target | Notes |
|---|---|---|
| Phase 1 (infra) | 12% | Baseline |
| Phase 2 (lexer) | 30% | Lexer fully covered |
| Phase 3 (parser) | 45% | Parser covered |
| Phase 4 (nodes) | 60% | Nodes fully covered |
| Phase 5 (codegen) | 72% | CodeGen covered |
| Phase 6 (CLI) | 82% | CLI covered |
| Phase 7 (integration) | 88% | E2E covered |
| Phase 8+9 (conformance+fuzz) | ≥90% | Full coverage |

---

## Test File Hierarchy (Final)

```
tests/
├── conftest.py                  ← shared fixtures (Phase 1)
├── unit/
│   ├── __init__.py
│   ├── test_lexer.py            ← Phase 2 (expand existing)
│   ├── test_parser.py           ← Phase 3 (NEW)
│   ├── test_nodes.py            ← Phase 4 (NEW)
│   └── test_codegen.py          ← Phase 5 (NEW)
├── test_cli.py                  ← Phase 6 (NEW — in tests/ root)
├── integration/
│   ├── __init__.py
│   └── test_compile.py          ← Phase 7 (NEW)
├── conformance/
│   ├── __init__.py
│   ├── test_conformance.py      ← Phase 8 (NEW)
│   └── programs/
│       └── arithmetic/          ← .vpl + .expected files
└── fuzz/
    ├── __init__.py
    └── fuzz_lexer.py            ← Phase 9 (NEW)
```

---

## Running the Full TDD Suite

```bash
# Full suite with coverage
uv run pytest tests/ -v --cov=vlang --cov-report=term-missing --cov-report=html

# Fast feedback (unit only)
uv run pytest tests/unit/ -v

# TDD watch mode (re-run on file change)
uv run pytest tests/unit/ -v -f   # --looponfail

# Run specific phase
uv run pytest tests/unit/test_parser.py -v
uv run pytest tests/integration/ -v -m "not slow"

# Fuzz (run longer in CI)
uv run pytest tests/fuzz/ --hypothesis-seed=0 -v
```
