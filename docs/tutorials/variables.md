# Biến và kiểu dữ liệu / Variables and Types

!!! warning "Đang phát triển / Under Development"
    Tính năng này đang được phát triển. Xem [lộ trình](../explanation/architecture.md) để biết thêm.

---

## Khai báo biến / Declaring Variables

```
khai_báo x = 10
khai_báo y = x * 2
in_ra(y)
```

Từ khóa `khai_báo` dùng để khai báo biến.

## Kiểu dữ liệu / Types

| Kiểu | Từ khóa | Ví dụ | LLVM IR |
|---|---|---|---|
| Số nguyên | `số_nguyên` | `42` | `i64` |
| Số thực | `số_thực` | `3.14` | `double` |
| Logic | `đúng`/`sai` | `đúng` | `i1` |
| Chuỗi | `chuỗi` | `"xin chào"` | `i8*` |

## Ví dụ / Examples

```
khai_báo tuổi = 25
khai_báo chiều_cao = 1.75
khai_báo tên = "Nguyễn Văn A"

in_ra(tuổi)
in_ra(chiều_cao)
in_ra(tên)
```

## Bước tiếp theo / Next Steps

- [Điều kiện (if/else)](conditionals.md)
- [Vòng lặp (loops)](loops.md)
