# v-lang
## Vietnamese programing language!
Just my hobbie  
Thích thì làm thôi!  
Một ngôn ngữ hướng đối tượng
## Định danh
  Viết như thế nào thì chạy như vậy!
  Ngôn ngữ lập trình hướng đối tượng cơ bản, có các thuộc tính cơ bản của lập trình hướng đối tượng.
  
## Từ khóa
`và (and)`                 Toán tử logic; giống như `&&` và có mức độ ưu tiên thấp hơn.  
`bắt_đầu (begin)`          Bắt đầu một khối mã hoặc một nhóm các câu lệnh; đóng với kết thúc.  
`ngắt (break)`             Chấm dứt một vòng lặp.   
`trường_hợp (case)`        So sánh một biểu thức với mệnh đề khi khớp; đóng với kết thúc.   
`lớp (class)`              Định nghĩa một lớp; đóng với kết thúc.  
`hàm (def, func)`          Định nghĩa một phương thức; đóng với kết thúc.  
`kết_thúc (end)`           Kết thúc một khối mã (nhóm các câu lệnh).  
`sai (false)`              Biến nhi phân `false`  
`lặp (for)`                Bắt đầu vòng lặp for; được sử dụng với trong.  
`nếu (if)`                 Thực thi khối mã nếu đúng. Đóng với kết thúc.  
`khác_thì (else)`                 Thực thi khối mã nếu không đúng. Đóng với kết thúc.  
`tiếp_theo (next)`         Nhảy qua vòng lặp sau.  
`rỗng (null)`               Biến trống, chưa được khởi tạo hoặc không hợp lệ, nhưng không giống với số không.  
`không (not)`              Toán tử logic; giống như !  
`hoặc (or)`                Toán tử logic; giống như ||, có ưu tiên thấp hơn..  
`trả_về (return)`          Trả về một giá trị từ một phương thức hoặc khối. Có thể bỏ qua.  
`thì (then)`               Một sự tiếp tục cho nếu, trừ khi, và khi nào. Có thể bỏ qua.  
`đúng (true)`              Biến nhi phân `false`  
`nếu_không (unless)`       Thực hiện khối mã nếu câu lệnh có điều kiện là sai,ngược lại với nếu.   
`đến_khi (until)`          Thực thi khối mã trong khi câu lệnh điều kiện là sai.   
`khi (while)`              Thực hiện mã trong khi câu lệnh có điều kiện là đúng.  
`mở_rộng (extends)`        Kế thường 1 lớp cha.  
`bản_thân (self)`          Đối tượng cụ thể hiện tại của một lớp.


## Khai báo lớp
  Tất cả các lớp được khai báo có mẫu như sau  
  `lớp <tên> [mở_rộng <tên>] { < thành phần > }`  
  Ví dụ: 
  ```
    lớp cafe {
    vị = 'ngon'
    màu = 'đen'
    }
  ```
## Khai báo biến, khai báo hàm
  `<tên> = <biểu thức>`  
  Ví dụ:  
      `a = 1`  
      `b = 2 + 3`  
      `c = '4 + 4`  

  ## Khai báo hàm  
    `hàm <tên> (< danh sách tham số >) { <thân hàm> }`  
    Ví dụ:
    ```
      hàm nhân_đôi (x) {
        trả_về x * 2
      }
  ```
  ## Toán tử
  ```
    + (cộng)                - (trừ)  
    * (nhân)                / (chia lấy thập phân)  
    \ (chia nguyên)         % (chia lấy số dư)  
    = (gán)                 == (so sánh bằng)  
    < (nhỏ hơn)             > (lớn hơn)  
    <= (nhỏ hơn hoặc bằng)  >= (lớn hơn hoặc bằng)  
    <> (khác)               && (phép và)  
    ! (phép phủ định)       || (phép hoặc)  
    new (khởi tạo đối tượng)   
  ```
  
pip install llvmlite