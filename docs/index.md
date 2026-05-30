# v-lang — Ngôn ngữ lập trình tiếng Việt 🇻🇳

> A hobby compiler for a programming language with Vietnamese keywords,
> targeting native binaries via LLVM.

---

## Cài đặt / Installation

**Yêu cầu / Requirements:** Python ≥ 3.11, LLVM (`llc`), GCC

```bash
pip install vlang
```

Hoặc cài từ source / Or install from source:

```bash
git clone https://github.com/vyquocvu/v-lang.git
cd v-lang
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

---

## Chương trình đầu tiên / First Program

Tạo file `xin_chao.vpl`:

```
in_ra(10 + 5)
in_ra(10 - 3)
in_ra(4 * 4)
```

Biên dịch và chạy:

```bash
vlang compile xin_chao.vpl -o xin_chao
./xin_chao
```

Kết quả / Output:
```
15
7
16
```

---

## Tính năng hiện tại / Current Features

| Tính năng | Trạng thái |
|---|---|
| Số nguyên (integer literals) | ✅ |
| Phép tính cơ bản (`+`, `-`, `*`, `/`) | ✅ |
| Lệnh in (`in_ra`) | ✅ |
| Biến (variables) | 🔄 Đang phát triển |
| Điều kiện `nếu`/`khác_thì` | 🔄 Đang phát triển |
| Vòng lặp `khi` | 🔄 Đang phát triển |
| Hàm (`hàm`) | 🔄 Đang phát triển |
| Kiểu dữ liệu đầy đủ | 📋 Kế hoạch |

---

## Điều hướng tài liệu / Documentation Navigation

<div class="grid cards" markdown>

- :material-school: **[Hướng dẫn](tutorials/hello-world.md)**

    Bắt đầu với v-lang từ đầu.

- :material-book-open: **[Tham khảo](reference/keywords.md)**

    Từ khóa, toán tử, và cú pháp đầy đủ.

- :material-tools: **[Hướng dẫn sử dụng](guides/cli.md)**

    CLI, cài đặt editor, và đóng góp.

- :material-lightbulb: **[Kiến trúc](explanation/architecture.md)**

    Tại sao v-lang? Compiler hoạt động như thế nào?

</div>
