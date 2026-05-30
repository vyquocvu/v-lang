# Tests

Bộ kiểm thử của v-lang / v-lang test suite.

---

## Cấu trúc / Structure

```
tests/
├── unit/              # Unit tests — kiểm tra từng module riêng lẻ
│   ├── test_lexer.py  ✅ 13 tests (DONE)
│   ├── test_parser.py 🔄 (planned: AST shape tests)
│   ├── test_nodes.py  🔄 (planned: AST eval with mock builder)
│   └── test_codegen.py 🔄 (planned: LLVM IR snapshot tests)
├── integration/       # Integration tests — compile + run thực tế
│   ├── test_compile.py 🔄 (.vpl → LLVM IR round-trips)
│   ├── test_run.py    🔄 (compile + link + execute, check stdout)
│   └── test_errors.py 🔄 (bad input → specific error messages)
├── conformance/       # Conformance tests — spec test per feature
│   ├── programs/      (one .vpl file + .expected per language feature)
│   └── test_conformance.py
└── fuzz/              # Property-based fuzzing
    ├── fuzz_lexer.py  (Hypothesis: lexer never panics)
    └── fuzz_parser.py (Hypothesis: parser never panics)
```

---

## Chạy tests / Running Tests

```bash
# Tất cả tests / All tests
uv run pytest tests/ -v

# Chỉ unit tests / Unit tests only (nhanh hơn / faster)
uv run pytest tests/unit/ -v

# Với coverage
uv run pytest tests/ --cov=vlang --cov-report=term-missing

# Một test cụ thể / Specific test
uv run pytest tests/unit/test_lexer.py::TestArithmeticTokens -v
```

---

## Viết test mới / Writing New Tests

### Unit Test (Lexer)
```python
def test_my_token():
    tokens = _tokenize("in_ra")
    assert tokens == [("IN_RA", "in_ra")]
```

### Integration Test (Compile + Run)
```python
def test_arithmetic_output(tmp_path):
    source = tmp_path / "test.vpl"
    source.write_text("in_ra(2 + 3)\n")
    result = subprocess.run(
        ["vlang", "compile", str(source), "-o", str(tmp_path / "out")],
        capture_output=True
    )
    assert result.returncode == 0
    output = subprocess.run([str(tmp_path / "out")], capture_output=True, text=True)
    assert output.stdout.strip() == "5"
```

### Conformance Test Format
```
# tests/conformance/programs/addition.vpl
in_ra(1 + 2)
```
```
# tests/conformance/programs/addition.expected
3
```

---

## Bất biến cốt lõi / Core Invariant

> **Compiler không bao giờ được crash trên bất kỳ input nào.**  
> The compiler must never crash on any input — valid or malformed.
> 
> Chỉ `VlangError` được phép raise. Không có bare Python exceptions.

---

## Mục tiêu coverage / Coverage Targets

| Phase | Target |
|---|---|
| Hiện tại | ~40% (chỉ unit lexer tests) |
| Phase 1 (Language features) | ≥ 60% |
| Phase 2 (Integration tests) | ≥ 75% |
| Phase 3 (Conformance suite) | ≥ 85% |
| v1.0 | ≥ 90% |
