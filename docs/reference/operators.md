# Toán tử / Operators

---

## Toán tử số học / Arithmetic Operators

| Toán tử | Tên | Ví dụ | Kết quả | Trạng thái |
|---|---|---|---|---|
| `+` | Cộng | `3 + 2` | `5` | ✅ |
| `-` | Trừ | `5 - 3` | `2` | ✅ |
| `*` | Nhân | `4 * 3` | `12` | ✅ |
| `/` | Chia | `10 / 2` | `5` | ✅ |
| `\` | Chia nguyên | `10 \ 3` | `3` | 📋 |
| `%` | Lấy số dư | `10 % 3` | `1` | 📋 |

## Toán tử so sánh / Comparison Operators

| Toán tử | Tên | Ví dụ | Kết quả | Trạng thái |
|---|---|---|---|---|
| `==` | Bằng | `5 == 5` | `đúng` | ✅ (lexer) |
| `!=` | Khác | `5 != 3` | `đúng` | ✅ (lexer) |
| `<` | Nhỏ hơn | `3 < 5` | `đúng` | ✅ (lexer) |
| `>` | Lớn hơn | `5 > 3` | `đúng` | ✅ (lexer) |
| `<=` | Nhỏ hơn hoặc bằng | `3 <= 3` | `đúng` | ✅ (lexer) |
| `>=` | Lớn hơn hoặc bằng | `5 >= 3` | `đúng` | ✅ (lexer) |

## Toán tử gán / Assignment Operators

| Toán tử | Tên | Ví dụ | Trạng thái |
|---|---|---|---|
| `=` | Gán | `x = 10` | 🔄 |

## Toán tử logic / Logical Operators

| Toán tử | Từ khóa | Ý nghĩa | Trạng thái |
|---|---|---|---|
| `&&` | `và` | Phép và (AND) | 📋 |
| `\|\|` | `hoặc` | Phép hoặc (OR) | 📋 |
| `!` | `không` | Phủ định (NOT) | 📋 |

## Toán tử khác / Other

| Toán tử | Tên | Ví dụ | Trạng thái |
|---|---|---|---|
| `new` | Khởi tạo đối tượng | `new Xe()` | 📋 |

## Thứ tự ưu tiên / Precedence (cao → thấp)

| Mức độ | Toán tử | Kết hợp |
|---|---|---|
| 1 (cao nhất) | `!`, `không` | Phải → Trái |
| 2 | `*`, `/`, `\`, `%` | Trái → Phải |
| 3 | `+`, `-` | Trái → Phải |
| 4 | `<`, `>`, `<=`, `>=` | Trái → Phải |
| 5 | `==`, `!=` | Trái → Phải |
| 6 | `&&`, `và` | Trái → Phải |
| 7 (thấp nhất) | `\|\|`, `hoặc` | Trái → Phải |

**Ví dụ:**
```
in_ra(2 + 3 * 4)     # = 14  (nhân trước)
in_ra((2 + 3) * 4)   # = 20  (ngoặc tròn ưu tiên cao nhất)
```
