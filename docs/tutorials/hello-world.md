# Hướng dẫn: Xin chào, thế giới! / Hello, World!

Hướng dẫn này sẽ đưa bạn qua chương trình vylang đầu tiên.

---

## 1. Cài đặt / Installation

```bash
pip install vlang
vlang --version
```

---

## 2. Chương trình đầu tiên / Your First Program

Tạo file `xin_chao.vpl` với nội dung:

```
in_ra(1 + 1)
```

`in_ra` là từ tiếng Việt có nghĩa là "in ra" (print out).

---

## 3. Biên dịch / Compile

```bash
# Chỉ tạo LLVM IR (không cần GCC)
vlang compile xin_chao.vpl

# Biên dịch thành chương trình chạy được
vlang compile xin_chao.vpl -o xin_chao
./xin_chao
```

**Kết quả / Output:**
```
2
```

---

## 4. Phép tính / Arithmetic

vylang hỗ trợ các phép tính cơ bản:

```
in_ra(10 + 5)    # Cộng  → 15
in_ra(10 - 3)    # Trừ   → 7
in_ra(4 * 4)     # Nhân  → 16
in_ra(10 / 2)    # Chia  → 5
```

Biên dịch file nhiều dòng:

```bash
vlang compile phep_tinh.vpl -o phep_tinh
./phep_tinh
```

**Kết quả:**
```
15
7
16
5
```

---

## 5. Thứ tự ưu tiên / Operator Precedence

vylang tuân theo thứ tự ưu tiên toán học chuẩn:

```
in_ra(2 + 3 * 4)    # = 2 + 12 = 14  (nhân trước)
in_ra((2 + 3) * 4)  # = 5 * 4  = 20  (ngoặc trước)
```

---

## Bước tiếp theo / Next Steps

- [Biến (Variables)](variables.md) — lưu trữ và sử dụng giá trị
- [Tham khảo từ khóa](../reference/keywords.md) — danh sách đầy đủ từ khóa
- [Hướng dẫn CLI](../guides/cli.md) — tất cả lệnh `vlang`
