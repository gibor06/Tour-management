<p align="center">

# 🌍 TOUR MANAGEMENT SYSTEM

### Hệ thống Quản lý Tour Du lịch

Ứng dụng quản lý tour du lịch được phát triển bằng **Python** và **Tkinter**, hỗ trợ quản lý thông tin tour, khách hàng và hướng dẫn viên trong môi trường mô phỏng doanh nghiệp lữ hành.

</p>

---

<p align="center">

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square\&logo=python)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-green?style=flat-square)
![JSON](https://img.shields.io/badge/Data-JSON-orange?style=flat-square)
![GitHub](https://img.shields.io/badge/Version-GitHub-black?style=flat-square\&logo=github)

</p>

---

# 📖 Mục lục

* [1. Giới thiệu](#-1-giới-thiệu)
* [2. Mục tiêu dự án](#-2-mục-tiêu-dự-án)
* [3. Chức năng hệ thống](#-3-chức-năng-hệ-thống)
* [4. Công nghệ sử dụng](#-4-công-nghệ-sử-dụng)
* [5. Cấu trúc dự án](#-5-cấu-trúc-dự-án)
* [6. Hướng dẫn cài đặt](#-6-hướng-dẫn-cài-đặt)
* [7. Hướng dẫn sử dụng](#-7-hướng-dẫn-sử-dụng)
* [8. Đóng gói ứng dụng](#-8-đóng-gói-ứng-dụng)
* [9. Kết luận](#-9-kết-luận)
* [Tác giả](#-tác-giả)
* [Liên hệ](#-liên-hệ)

---

# 📌 1. Giới thiệu

Trong bối cảnh ngành du lịch ngày càng phát triển, việc quản lý thông tin tour, khách hàng và lịch trình trở nên quan trọng đối với các doanh nghiệp lữ hành. Các phương pháp quản lý thủ công thường gây ra nhiều hạn chế như khó theo dõi dữ liệu, dễ xảy ra sai sót và thiếu tính đồng bộ.

Dự án **Tour Management System** được xây dựng nhằm mô phỏng một hệ thống quản lý tour du lịch cơ bản. Hệ thống hỗ trợ quản lý thông tin tour, danh sách khách hàng đặt tour và phân công hướng dẫn viên.

Ứng dụng được phát triển bằng **Python** với thư viện **Tkinter** để xây dựng giao diện đồ họa người dùng (GUI).

---

# 🎯 2. Mục tiêu dự án

Mục tiêu của dự án bao gồm:

* Xây dựng một hệ thống quản lý tour du lịch cơ bản
* Áp dụng kiến thức lập trình Python vào phát triển phần mềm
* Thiết kế giao diện người dùng bằng Tkinter
* Lưu trữ dữ liệu bằng JSON
* Rèn luyện kỹ năng quản lý mã nguồn bằng Git và GitHub

---

# ⚙️ 3. Chức năng hệ thống

## Quản lý Tour

Hệ thống cho phép quản trị viên:

* Thêm tour du lịch
* Cập nhật thông tin tour
* Xóa tour khỏi hệ thống
* Hiển thị danh sách tour
* Xem thông tin chi tiết tour

Thông tin tour bao gồm:

* Mã tour
* Tên tour
* Điểm khởi hành
* Điểm đến
* Ngày khởi hành
* Giá tour
* Số lượng khách
* Hướng dẫn viên phụ trách
* Trạng thái tour

---

## Quản lý Booking

Hệ thống hỗ trợ quản lý khách hàng đặt tour:

* Tên khách hàng
* Số điện thoại
* Số lượng người tham gia
* Mã booking
* Trạng thái booking

Ngoài ra hệ thống còn cho phép:

* Theo dõi số lượng khách của từng tour
* Hiển thị danh sách khách tham gia

---

## Quản lý Hướng dẫn viên

Hệ thống cho phép:

* Phân công hướng dẫn viên cho tour
* Xem danh sách tour được phân công
* Theo dõi khách tham gia tour

---

# 🧰 4. Công nghệ sử dụng

| Công nghệ    | Mô tả                           |
| ------------ | ------------------------------- |
| Python       | Ngôn ngữ lập trình chính        |
| Tkinter      | Thư viện xây dựng giao diện GUI |
| JSON         | Lưu trữ dữ liệu                 |
| Git & GitHub | Quản lý mã nguồn                |

---

# 📂 5. Cấu trúc dự án

```
Tour-management
│
├── GUI/        
│   └── (các module giao diện)
│
├── dist/       
│   └── main.exe
│
└── main.py     
```

| Thành phần | Mô tả                          |
| ---------- | ------------------------------ |
| `main.py`  | File khởi chạy chương trình    |
| `GUI`      | Chứa các module giao diện      |
| `dist`     | Chứa file `.exe` sau khi build |

---

# 💻 6. Hướng dẫn cài đặt

Clone repository

```
git clone https://github.com/gibor06/Tour-management.git
```

Di chuyển vào thư mục dự án

```
cd Tour-management
```

Chạy chương trình

```
python main.py
```

---

# 🧭 7. Hướng dẫn sử dụng

### Quản lý tour

* Nhấn **Thêm tour mới** để tạo tour
* Chọn tour trong bảng để xem chi tiết
* Nhấn **Cập nhật** để chỉnh sửa
* Nhấn **Xóa tour** để xóa khỏi hệ thống

### Xem chi tiết tour

Khi chọn một tour trong danh sách, hệ thống sẽ hiển thị:

* Thông tin tour
* Lộ trình
* Giá tour
* Hướng dẫn viên
* Danh sách khách tham gia

---

# 🚀 8. Đóng gói ứng dụng

Cài đặt PyInstaller

```
pip install pyinstaller
```

Build ứng dụng

```
pyinstaller --onefile --windowed main.py
```

Sau khi build, file `.exe` sẽ nằm trong:

```
dist/
```

---

# 📊 9. Kết luận

Dự án **Tour Management System** là một ứng dụng mô phỏng hệ thống quản lý tour du lịch được xây dựng nhằm phục vụ mục đích học tập và nghiên cứu.

Thông qua dự án này, người thực hiện có cơ hội áp dụng các kiến thức về:

* Lập trình Python
* Thiết kế giao diện người dùng
* Tổ chức dữ liệu
* Quản lý mã nguồn

Trong tương lai, hệ thống có thể được mở rộng với các chức năng như:

* Kết nối cơ sở dữ liệu SQL
* Quản lý tài khoản người dùng
* Phát triển phiên bản Web
* Tích hợp đặt tour trực tuyến

---

# 👨‍💻 Tác giả

**Trần Gia Bảo** — **gibor06** và **Nguyễn Thị Phương Nhung**

Sinh viên ngành **Công Nghệ Thông Tin**
**Trường Đại học Công Thương TP.HCM (HUIT)**

📍 TP.HCM, Việt Nam

---

# 📬 Liên hệ

📧 Email
[gibor06.dev@gmail.com](mailto:gibor06.dev@gmail.com)

🌐 Facebook
https://www.facebook.com/gibor06

---

# 📜 License

Repository được phát triển phục vụ **mục đích học tập và nghiên cứu**.
