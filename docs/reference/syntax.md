# Cú pháp / Syntax Reference

---

## Cấu trúc chương trình / Program Structure

Một chương trình v-lang là một chuỗi các câu lệnh (statements).
Mỗi câu lệnh nằm trên một dòng riêng.

```
# Đây là chú thích
in_ra(1 + 1)
in_ra(2 * 3)
```

## Chú thích / Comments

```
# Chú thích một dòng
in_ra(42)   # Chú thích cuối dòng
```

## Kiểu dữ liệu nguyên thủy / Primitive Types

```
# Số nguyên (i64)
in_ra(42)
in_ra(-10)
in_ra(1_000_000)   # Dấu gạch dưới để dễ đọc (planned)

# Số thực (f64) — planned
in_ra(3.14)
in_ra(-0.5)

# Logic (bool) — planned
khai_báo x = đúng
khai_báo y = sai

# Chuỗi (UTF-8 string) — planned
in_ra("Xin chào thế giới")
in_ra("Số: " + 42)
```

## Biểu thức / Expressions

```
# Số học
2 + 3
10 - 4
6 * 7
15 / 3

# So sánh — returns bool
5 > 3
5 == 5
5 != 3

# Nhóm bằng ngoặc
(2 + 3) * 4
```

## Câu lệnh / Statements

### In ra / Print
```
in_ra(biểu_thức)
```

### Khai báo biến / Variable Declaration (planned)
```
khai_báo tên = biểu_thức
```

### Điều kiện / Conditional (planned)
```
nếu điều_kiện thì
  # khối lệnh
kết_thúc

nếu điều_kiện thì
  # khối lệnh
khác_thì
  # khối lệnh
kết_thúc
```

### Vòng lặp / Loop (planned)
```
khi điều_kiện thì
  # khối lệnh
kết_thúc
```

### Hàm / Function (planned)
```
hàm tên_hàm(tham_số_1, tham_số_2)
  # thân hàm
  trả_về giá_trị
kết_thúc
```

## Định danh / Identifiers

v-lang hỗ trợ hoàn toàn tiếng Việt có dấu cho các định danh (tên biến, tên hàm, tham số):

- Định danh hợp lệ phải bắt đầu bằng một chữ cái (bao gồm cả chữ cái tiếng Việt có dấu như `đ`, `á`, `ệ`, `ở`...) hoặc dấu gạch dưới `_`.
- Theo sau có thể là chữ cái, chữ số, hoặc dấu gạch dưới.

**Ví dụ định danh hợp lệ:**
- `điểm`
- `tuổi`
- `kết_quả`
- `_biến_số_1`
- `ĐIỂM_SỐ`

## Grammar (EBNF)

```ebnf
program      = statement+ ;
statement    = print_stmt | assignment | if_stmt | while_stmt | func_def ;
print_stmt   = "in_ra" "(" expression ")" NEWLINE ;
assignment   = "khai_báo" IDENTIFIER "=" expression NEWLINE ;
if_stmt      = "nếu" expression "thì" NEWLINE
               statement+
               [ "khác_thì" NEWLINE statement+ ]
               "kết_thúc" NEWLINE ;
while_stmt   = "khi" expression "thì" NEWLINE
               statement+
               "kết_thúc" NEWLINE ;
func_def     = "hàm" IDENTIFIER "(" param_list ")" NEWLINE
               statement+
               "kết_thúc" NEWLINE ;
expression   = expression ( "+" | "-" | "*" | "/" ) expression
             | expression ( "==" | "!=" | "<" | ">" | "<=" | ">=" ) expression
             | "(" expression ")"
             | NUMBER
             | IDENTIFIER
             | IDENTIFIER "(" arg_list ")" ;
```
