# Ví dụ / Examples

Thư mục này chứa các chương trình vylang ví dụ.

---

## Danh sách / List

| File | Mô tả |
|---|---|
| `hello.vpl` | Chương trình cơ bản nhất |
| `arithmetic.vpl` | Các phép tính số học |
| `calculator.vpl` | Máy tính đơn giản (sau khi có biến) |
| `fibonacci.vpl` | Dãy Fibonacci (sau khi có hàm) |

---

## Cách chạy / How to Run

```bash
# Biên dịch và chạy
vlang compile examples/hello.vpl -o hello
./hello

# Hoặc dùng script
./scripts/build.sh examples/hello.vpl hello
```
