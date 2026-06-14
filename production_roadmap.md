# Lộ trình Phát triển / Production Roadmap — vylang 🇻🇳

This document details the production roadmap for **vylang** — a programming language with Vietnamese keywords designed to target native binaries using LLVM.

---

## 🎯 Tầm nhìn / Vision

vylang aims to lower the barrier to entry for Vietnamese speakers (especially students and hobbyists) who want to learn programming and compiler engineering. It is not just an interpreted scripting language; it is a **native compiled language** powered by LLVM, providing high performance and cross-platform compatibility.

---

## 🛠️ Lộ trình Phát triển / Development Phases

The roadmap is structured into 4 main phases, spanning approximately **5 months (20 weeks)** from prototype to v1.0.

```
┌────────────────────────────────────────────────────────┐
│  Phase 1: Core Language & Type System  (Weeks 1 - 8)   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  Phase 2: Tooling & DX (Developer Exp) (Weeks 9 - 14)  │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  Phase 3: Integration, Opt & CI/CD    (Weeks 15 - 17)  │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  Phase 4: Package Manager & Ecosystem (Weeks 18 - 20)  │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
                     🚀 vylang v1.0
```

---

## 📌 Chi tiết các Giai đoạn / Phase Details

### Phase 1 — Core Language & Type System (Weeks 1 - 8)
*Focus: Move from a single-type toy language to a typed, feature-complete programming language.*

*   **Syntax Evolution**:
    *   **Accented & Accentless Keywords**: Support both Unicode-accented and plain ASCII equivalents to ease typing on systems without a Vietnamese input method editor (IME) like Unikey/Telex.
        *   e.g. `nếu` / `neu`, `hàm` / `ham`, `trả_về` / `tra_ve`, `khai_báo` / `khai_bao`.
    *   **Mutability Control**: Introduce `hằng` (const) for immutable variables and `khai_báo` (let/var) for mutable ones.
*   **Rich Data Types**:
    *   `số_nguyên` (64-bit integer, current default).
    *   `số_thực` (64-bit double-precision float).
    *   `đúng_sai` (Boolean values: `đúng` / `sai`).
    *   `chuỗi` (UTF-8 string literals and manipulation APIs).
    *   `danh_sách` (Arrays/lists) & `từ_điển` (Hash Maps).
*   **Bidirectional Type Checking**:
    *   Implement `vlang/typechecker.py` to run semantic analysis on the AST.
    *   Infer types dynamically where possible and enforce type safety at compile time.
*   **User-defined Types & OOP**:
    *   `cấu_trúc` (Structs) for packing data.
    *   `lớp` (Classes) with basic inheritance (`mở_rộng` / `kế_thừa`) and constructor methods.
*   **Memory Management**:
    *   Introduce stack-allocated structures (`alloca`).
    *   Introduce heap allocation for strings and dynamic lists with a simple garbage collector (e.g., Boehm GC integration) or RAII/lifetime tracking.

---

### Phase 2 — Tooling & Developer Experience (Weeks 9 - 14)
*Focus: Build high-quality developer tooling to support code formatting, debugging, and live editing.*

*   **Compiler Frontend Upgrade**:
    *   Migrate the parser/lexer from `rply` to `lark` or implement a **hand-written recursive descent parser**.
    *   **Source Positions**: Track file name, line, and column numbers for all tokens and AST nodes to provide rich compiler warnings and errors.
*   **Interactive REPL**:
    *   Build `vlang repl` utilizing the LLVM MCJIT execution engine.
    *   Support line editing, command history, and inspectable memory state.
*   **Syntax Highlighting & IDE Extensions**:
    *   Develop a VS Code extension for `.vpl` files using TextMate grammar.
    *   Integrate with tree-sitter for modern editors (Neovim, Helix, Emacs).
*   **Language Server Protocol (LSP)**:
    *   Build `vlang-lsp` providing diagnostics, hover tooltips, autocomplete, and go-to-definition.
*   **Code Formatter**:
    *   Build `vlang-format` (similar to `gofmt` or `rustfmt`) to enforce a single code style.
*   **DWARF Debugging Info**:
    *   Emit LLVM debug metadata so developers can use `gdb` or `lldb` to debug native binaries written in vylang.

---

### Phase 3 — Integration, Optimizations & CI/CD (Weeks 15 - 17)
*Focus: Enhance compiler performance, verify stability, and distribute binaries.*

*   **LLVM Optimization Passes**:
    *   Enable optimization flags (`-O1`, `-O2`, `-O3`).
    *   Integrate LLVM Pass Managers to run dead code elimination, constant folding, and loop unrolling.
*   **Foreign Function Interface (FFI)**:
    *   Add ability to call C libraries using `nạp_ngoài` (external import).
    *   Support compiling vylang functions into static (`.a`) or shared (`.so` / `.dylib`) libraries.
*   **Testing & Quality Assurance**:
    *   Implement compiler fuzzing with Hypothesis to test edge cases.
    *   Increase unit and integration test coverage to ≥95%.
*   **Cross-Compilation**:
    *   Configure the compiler to output target binaries for `x86_64` and `aarch64` across Windows, macOS, and Linux.

---

### Phase 4 — Ecosystem & Distribution (Weeks 18 - 20)
*Focus: Launching vylang to the public, documenting APIs, and building a community.*

*   **Standard Library (`thư_viện_chuẩn`)**:
    *   `toán`: Standard math functions.
    *   `tập_tin`: File input/output.
    *   `hệ_thống`: System calls, arguments, and environment variables.
    *   `mạng`: Basic TCP/UDP socket wrapper.
*   **Package Manager (`gói`)**:
    *   Build a simple dependency manager `vlang-pkg` to download, build, and link third-party packages.
*   **Distribution**:
    *   Publish the compiler toolchain on PyPI: `pip install vlang`.
    *   Provide standalone executable installer scripts for macOS/Linux/Windows.
*   **Documentation Site**:
    *   Create a complete documentation site (Vietnamese/English) with tutorials, language specification, and interactive playground in the browser using WebAssembly (WASM).

---

## 📊 Tóm tắt các Cột mốc / Milestone Summary

| Milestone | Deliverables | Timeline | Status |
|---|---|---|---|
| **M1: Core Syntax** | Float, Boolean, String support; accented/accentless keys | Week 2 | 📋 Planned |
| **M2: Type System** | Symbol table, bidirectional type checker, strict validation | Week 5 | 📋 Planned |
| **M3: Data Structures** | Structs, OOP classes, lists/arrays | Week 8 | 📋 Planned |
| **M4: Lark Migration** | High-fidelity parser with source locations and line:col tracking | Week 10 | 📋 Planned |
| **M5: Toolchain CLI** | REPL shell, formatter, LSP syntax highlighter | Week 14 | 📋 Planned |
| **M6: LLVM O3 & FFI** | Optimization passes, C FFI library linking | Week 16 | 📋 Planned |
| **M7: StdLib & v1.0** | Core libraries, package manager, PyPI deployment | Week 20 | 📋 Planned |

---

## 📈 Kiến trúc Mục tiêu / Target Architecture

A look at the final compiler execution flow:

```
                  ┌─────────────────┐
                  │ Source (.vpl)   │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Lark Parser    │  (With line:col locations)
                  └────────┬────────┘
                           │  AST
                           ▼
                  ┌─────────────────┐
                  │   Type Checker  │  (Bidirectional inference)
                  └────────┬────────┘
                           │  Typed AST
                           ▼
                  ┌─────────────────┐
                  │ LLVM IR Emitter │  (llvmlite IR Builder)
                  └────────┬────────┘
                           │  LLVM IR (Optimized)
                           ▼
                  ┌─────────────────┐
                  │   LLVM MCJIT    ├─► JIT Execution (REPL)
                  └────────┬────────┘
                           │  Object Code
                           ▼
                  ┌─────────────────┐
                  │   Linker (gcc)  ├─► Native Binary / Shared Lib
                  └─────────────────┘
```

---

## 📝 Đóng góp / Contributing

We follow a test-driven development (TDD) approach. Every feature added must first be defined with a failing test inside `tests/` before implementation. 

For syntax guidelines, refer to [Tài liệu cú pháp / Syntax Guide](docs/reference/syntax.md).
