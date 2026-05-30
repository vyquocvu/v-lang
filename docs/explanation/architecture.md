# Kiến trúc Compiler / Compiler Architecture

---

## Tổng quan pipeline / Pipeline Overview

```
Mã nguồn .vpl
      │
      ▼
┌─────────────┐
│   Lexer     │  vlang/lexer.py   — rply → lark (migration)
│  (Tokenize) │  Input:  "in_ra(4 + 4)\n"
│             │  Output: [IN_RA, LPAREN, INT(4), PLUS, INT(4), RPAREN, NEWLINE]
└─────┬───────┘
      │
      ▼
┌─────────────┐
│   Parser    │  vlang/parser.py  — LALR(1)
│ (Build AST) │  Input:  Token stream
│             │  Output: AST (Print(Sum(Number(4), Number(4))))
└─────┬───────┘
      │
      ▼
┌─────────────┐
│  Type Check │  vlang/typechecker.py  — Bidirectional (planned)
│  (Semantic) │  Input:  AST
│             │  Output: Typed AST or Diagnostics
└─────┬───────┘
      │
      ▼
┌─────────────┐
│   CodeGen   │  vlang/codegen.py  — llvmlite
│  (LLVM IR)  │  Input:  Typed AST
│             │  Output: output.ll
└─────┬───────┘
      │
      ▼
   output.ll  (LLVM IR text)
      │
      ▼  llc -filetype=obj
   output.o   (Object file)
      │
      ▼  gcc
   ./binary   (Native executable)
```

---

## Các module / Modules

### `vlang/lexer.py` — Tokeniser
Chuyển đổi chuỗi ký tự thành danh sách token.

**Hiện tại**: dùng `rply.LexerGenerator`  
**Kế hoạch**: migrate sang `lark` để có source positions

| Token | Pattern | Ý nghĩa |
|---|---|---|
| `IN_RA` | `in_ra` | Lệnh in |
| `SO_NGUYEN` | `\d+` | Số nguyên |
| `CONG` | `\+` | Phép cộng |
| `TRU` | `\-` | Phép trừ |
| `NHAN` | `\*` | Phép nhân |
| `CHIA` | `\/` | Phép chia |
| `HET_DONG` | `\n` | Hết dòng |

### `vlang/parser.py` — LALR Parser
Xây dựng cây cú pháp trừu tượng (AST) từ token stream.

**Grammar hiện tại (cần mở rộng):**
```
program    : statement+
statement  : IN_RA ( expression ) HET_DONG
expression : expression NHAN expression
           | expression CHIA expression
           | expression CONG expression
           | expression TRU  expression
           | SO_NGUYEN
```

### `vlang/nodes.py` — AST Nodes
Mỗi node đại diện cho một cấu trúc ngôn ngữ và có method `eval()`.

```python
Number(value)          → ir.Constant(i64, value)
Sum(left, right)       → builder.add(left, right)
Sub(left, right)       → builder.sub(left, right)
Mul(left, right)       → builder.mul(left, right)
Div(left, right)       → builder.sdiv(left, right)
Print(printf, value)   → builder.call(printf, [fmt, value])
```

### `vlang/codegen.py` — LLVM Code Generator
Thiết lập LLVM module, builder, và execution engine.

**Các thành phần:**
- `ir.Module` — container cho toàn bộ chương trình
- `ir.IRBuilder` — xây dựng LLVM IR instructions
- `ir.Function("main")` — hàm entry point
- `binding.create_mcjit_compiler()` — JIT engine (dùng cho REPL)

---

## Luồng dữ liệu ví dụ / Data Flow Example

**Input:** `in_ra(4 + 2)`

```
Lexer output:
  [IN_RA, LPAREN, INT(4), CONG, INT(2), RPAREN, NEWLINE]

Parser output:
  Print(
    value=Sum(
      left=Number(value="4"),
      right=Number(value="2")
    )
  )

LLVM IR output:
  define void @main() {
  entry:
    %0 = add i8 4, 2          ; Sum.eval()
    %1 = call i32 @printf(...)  ; Print.eval()
    ret void
  }
```

---

## Lỗi đã biết / Known Issues

| Lỗi | Mô tả | Ưu tiên |
|---|---|---|
| Single-statement | Chỉ một câu lệnh mỗi chương trình | 🚨 Blocker |
| `i8` overflow | Số nguyên giới hạn 0–127 | 🚨 Blocker |
| `fstr` conflict | Gọi `in_ra` 2 lần → crash | 🚨 Blocker |
| No source locations | Lỗi không có file:line:col | 🔴 High |
| No error recovery | Lỗi đầu tiên dừng compilation | 🟡 Medium |

---

## Lộ trình / Roadmap

Xem [Production Roadmap](../../production_roadmap.md) để biết kế hoạch chi tiết.

**Tóm tắt:**
- **Phase 1**: Variables, if/else, while, functions, bidirectional types (~8 tuần)
- **Phase 2**: REPL, formatter, LSP, DWARF, LLVM O2 (~6 tuần)
- **Phase 3**: Test suite, CI/CD, fuzzing (~3 tuần)
- **Phase 4**: Docs, package manager, PyPI (~3 tuần)
- **v1.0**: ~5 tháng tổng cộng
