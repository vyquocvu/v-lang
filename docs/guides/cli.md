# Hướng dẫn sử dụng CLI / CLI Reference

## Tổng quan / Overview

```bash
vlang [command] [options]
```

---

## vlang compile

Biên dịch file `.vpl` thành LLVM IR hoặc binary.

### Cú pháp / Syntax

```bash
vlang compile <source.vpl> [options]
```

### Tùy chọn / Options

| Option | Mô tả |
|---|---|
| `<source.vpl>` | File nguồn cần biên dịch |
| `-o <name>` | Tên binary đầu ra (yêu cầu `llc` + `gcc`) |
| `--ir-only` | Chỉ xuất LLVM IR (`output.ll`), không link |

### Ví dụ / Examples

```bash
# Chỉ tạo LLVM IR
vlang compile hello.vpl
# → Tạo output.ll

# Biên dịch thành binary
vlang compile hello.vpl -o hello
# → Tạo output.ll, output.o, và ./hello

# Chạy binary
./hello
```

### Quy trình biên dịch / Compilation Pipeline

```
hello.vpl
   ↓  Lexer (vlang.lexer)
Tokens
   ↓  Parser (vlang.parser)
AST
   ↓  CodeGen (vlang.codegen + llvmlite)
output.ll  (LLVM IR)
   ↓  llc (LLVM compiler)
output.o   (Object file)
   ↓  gcc (Linker)
./hello    (Native binary)
```

---

## vlang repl

*(Đang phát triển / In development)*

Khởi động REPL tương tác.

```bash
vlang repl
```

```
v-lang 0.1.0 — Nhập 'thoát' hoặc Ctrl-D để thoát.
>>> in_ra(1 + 2)
3
>>> khai_báo x = 10
>>> in_ra(x * 2)
20
```

---

## vlang fmt

*(Đang phát triển / In development)*

Định dạng file `.vpl`.

```bash
vlang fmt file.vpl          # Định dạng tại chỗ
vlang fmt --check file.vpl  # Kiểm tra (dùng trong CI)
vlang fmt .                 # Định dạng tất cả file trong thư mục hiện tại
```

---

## vlang lsp

*(Đang phát triển / In development)*

Khởi động Language Server Protocol server.

```bash
vlang lsp    # Chạy trên stdio (dùng với IDE)
```

---

## Mã thoát / Exit Codes

| Code | Ý nghĩa |
|---|---|
| `0` | Thành công |
| `1` | Lỗi cú pháp hoặc lỗi biên dịch |
| `2` | Lỗi liên kết (`llc`/`gcc` thất bại) |

---

## Yêu cầu / Requirements

| Công cụ | Khi nào cần | Cách cài đặt |
|---|---|---|
| Python ≥ 3.11 | Luôn luôn | `brew install python` |
| `llc` | Biên dịch sang binary | `brew install llvm` |
| `gcc` | Liên kết binary | `brew install gcc` hoặc Xcode CLT |
