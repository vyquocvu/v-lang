# Tại sao vylang? / Why vylang?

---

## Động lực / Motivation

vylang được tạo ra từ một câu hỏi đơn giản:

> **Điều gì xảy ra nếu một ngôn ngữ lập trình được viết hoàn toàn bằng tiếng Việt?**

Hầu hết các ngôn ngữ lập trình đều dùng từ khóa tiếng Anh:
`if`, `while`, `for`, `return`, `class`... Điều này tạo ra rào cản ngôn ngữ
cho người học lập trình không thành thạo tiếng Anh.

vylang là thử nghiệm: Liệu một ngôn ngữ với từ khóa hoàn toàn tiếng Việt
có giúp người Việt học lập trình dễ hơn không?

```
# Python                    # vylang
if x > 0:          →       nếu x > 0 thì
    print(x)       →         in_ra(x)
                   →       hết
```

---

## Triết lý thiết kế / Design Philosophy

### 1. Tiếng Việt thuần / Pure Vietnamese
Từ khóa phải là từ tiếng Việt thực sự, không phải viết tắt hay Latinh hóa.
- ✅ `hết` (end)
- ✅ `trả_về` (return)  
- ❌ `ret` hoặc `return`

### 2. Rõ ràng hơn ngắn gọn / Clarity over brevity
```
# Không dùng:   nếu x>0: in(x)
# Dùng:
nếu x > 0 thì
  in_ra(x)
hết
```

### 3. LLVM làm backend / LLVM as backend
- Native performance — không phải interpreter
- Tận dụng LLVM optimization passes
- Hỗ trợ nhiều kiến trúc CPU: x86, ARM, WASM

### 4. Hobby project với tiêu chuẩn cao / Hobby project with high standards
"Thích thì làm thôi!" — nhưng làm đúng cách.

---

## Hướng đi tương lai / Future Direction

Xem [Production Roadmap](architecture.md#roadmap) để biết kế hoạch phát triển.
