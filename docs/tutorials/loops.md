# Vòng lặp / Loops

!!! warning "Đang phát triển / Under Development"
    Tính năng này đang được phát triển.

---

## khi (while)

```
khai_báo đếm = 0

khi đếm < 5 thì
  in_ra(đếm)
  đếm = đếm + 1
kết_thúc
```

**Kết quả:**
```
0
1
2
3
4
```

## Vòng lặp vô hạn / Infinite Loop

```
khi đúng thì
  in_ra(1)
kết_thúc
```

Dùng `ngắt` để thoát vòng lặp:

```
khai_báo x = 0
khi đúng thì
  nếu x >= 10 thì
    ngắt
  kết_thúc
  x = x + 1
kết_thúc
in_ra(x)
```

## Bước tiếp theo

- [Hàm](functions.md)
- [Tham khảo từ khóa](../reference/keywords.md)
