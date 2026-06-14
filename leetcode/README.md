# LeetCode Solutions in vylang 🇻🇳

Thư mục này chứa các lời giải cho các bài toán LeetCode được cài đặt bằng ngôn ngữ lập trình tiếng Việt **vylang**.

## Các bài toán đã cài đặt (Implemented Problems)

1. **[LeetCode 1: Two Sum](file:///Users/vyquocvu/Development/vylang/leetcode/001-two-sum.vpl)**
   - **Tập tin:** `001-two-sum.vpl`
   - **Mô tả:** Tìm chỉ số của 2 số có tổng bằng Target. Sử dụng thuật toán duyệt hai vòng lặp lồng nhau (`khi`). Mảng kết quả được truyền dưới dạng con trỏ và cập nhật trực tiếp.

2. **[LeetCode 9: Palindrome Number](file:///Users/vyquocvu/Development/vylang/leetcode/009-palindrome-number.vpl)**
   - **Tập tin:** `009-palindrome-number.vpl`
   - **Mô tả:** Kiểm tra số đối xứng. Sử dụng toán tử `%` mới được tích hợp vào trình biên dịch để lấy chữ số cuối cùng. Số âm được biểu diễn bằng biểu thức hiệu với không: `0 - 121` (do chưa hỗ trợ dấu âm unary `-` trực tiếp).

3. **[LeetCode 26: Remove Duplicates from Sorted Array](file:///Users/vyquocvu/Development/vylang/leetcode/026-remove-duplicates.vpl)**
   - **Tập tin:** `026-remove-duplicates.vpl`
   - **Mô tả:** Loại bỏ các phần tử trùng lặp trong mảng đã sắp xếp. Sửa đổi mảng trực tiếp (in-place) và trả về số lượng phần tử duy nhất còn lại.

4. **[LeetCode 70: Climbing Stairs](file:///Users/vyquocvu/Development/vylang/leetcode/070-climbing-stairs.vpl)**
   - **Tập tin:** `070-climbing-stairs.vpl`
   - **Mô tả:** Tính số cách leo cầu thang (quy hoạch động/Fibonacci tối ưu không gian). Sử dụng vòng lặp `khi` và điều kiện `nếu` lồng nhau.

5. **[LeetCode 167: Two Sum II - Input Array Is Sorted](file:///Users/vyquocvu/Development/vylang/leetcode/167-two-sum-ii.vpl)**
   - **Tập tin:** `167-two-sum-ii.vpl`
   - **Mô tả:** Tìm 2 số có tổng bằng Target trên mảng đã sắp xếp. Sử dụng kỹ thuật hai con trỏ co dần từ hai đầu (`trái`, `phải`) chạy trong $O(n)$. Trả về chỉ số bắt đầu từ 1 (1-indexed).

6. **[LeetCode 189: Rotate Array](file:///Users/vyquocvu/Development/vylang/leetcode/189-rotate-array.vpl)**
   - **Tập tin:** `189-rotate-array.vpl`
   - **Mô tả:** Xoay mảng sang phải `k` bước trực tiếp (in-place) bằng thuật toán 3 lần đảo ngược mảng. Sử dụng toán tử `%` mới được bổ sung để tối giản số bước xoay `k % n`.

---

## Hướng dẫn Biên dịch và Chạy (How to Compile and Run)

Kích hoạt môi trường ảo Python trước khi thực hiện:
```bash
source .venv/bin/activate
```

### 1. LeetCode 1: Two Sum
```bash
python -m vlang.cli compile leetcode/001-two-sum.vpl -o leetcode/two-sum && ./leetcode/two-sum
```
**Kết quả mong đợi:**
```
0
1
```

### 2. LeetCode 9: Palindrome Number
```bash
python -m vlang.cli compile leetcode/009-palindrome-number.vpl -o leetcode/palindrome && ./leetcode/palindrome
```
**Kết quả mong đợi:**
```
1
0
0
```

### 3. LeetCode 26: Remove Duplicates
```bash
python -m vlang.cli compile leetcode/026-remove-duplicates.vpl -o leetcode/remove-duplicates && ./leetcode/remove-duplicates
```
**Kết quả mong đợi:**
```
5
1
2
3
4
5
```

### 4. LeetCode 70: Climbing Stairs
```bash
python -m vlang.cli compile leetcode/070-climbing-stairs.vpl -o leetcode/climb && ./leetcode/climb
```
**Kết quả mong đợi:**
```
2
3
5
8
```

### 5. LeetCode 167: Two Sum II
```bash
python -m vlang.cli compile leetcode/167-two-sum-ii.vpl -o leetcode/two-sum-ii && ./leetcode/two-sum-ii
```
**Kết quả mong đợi:**
```
1
2
```

### 6. LeetCode 189: Rotate Array
```bash
python -m vlang.cli compile leetcode/189-rotate-array.vpl -o leetcode/rotate-array && ./leetcode/rotate-array
```
**Kết quả mong đợi:**
```
5
6
7
1
2
3
4
```

## Dọn dẹp các tệp nhị phân (Cleanup)
```bash
rm -f leetcode/two-sum leetcode/palindrome leetcode/remove-duplicates leetcode/climb leetcode/two-sum-ii leetcode/rotate-array output.ll
```
