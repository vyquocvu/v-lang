# Hàm / Functions

!!! warning "Đang phát triển / Under Development"
    Tính năng này đang được phát triển.

---

## Định nghĩa hàm / Defining Functions

```
hàm cộng(a, b)
  trả_về a + b
kết_thúc

in_ra(cộng(3, 4))
```

**Kết quả:** `7`

## Đệ quy / Recursion

```
hàm giai_thừa(n)
  nếu n <= 1 thì
    trả_về 1
  kết_thúc
  trả_về n * giai_thừa(n - 1)
kết_thúc

in_ra(giai_thừa(5))
```

**Kết quả:** `120`

## Nhiều tham số / Multiple Parameters

```
hàm hình_chữ_nhật(chiều_dài, chiều_rộng)
  trả_về chiều_dài * chiều_rộng
kết_thúc

in_ra(hình_chữ_nhật(4, 5))
```

**Kết quả:** `20`

## Hàm không trả về / Void Functions

```
hàm in_lời_chào(tên)
  in_ra(tên)
kết_thúc

in_lời_chào("Việt Nam")
```

## Bước tiếp theo

- [Tham khảo toán tử](../reference/operators.md)
- [Kiến trúc compiler](../explanation/architecture.md)
