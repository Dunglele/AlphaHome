# 🏢 AlphaHome — Internal Property Management & Sales Platform

<div align="center">
  <img src="templates/core/login.html" alt="AlphaHome Banner" style="display: none;" />
  
  [![Python Version](https://img.shields.io/badge/python-3.10%2B-amber?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Django Framework](https://img.shields.io/badge/django-4.2%2B-emerald?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
  [![Bootstrap CSS](https://img.shields.io/badge/bootstrap-5.3-blueviolet?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
  [![Database Support](https://img.shields.io/badge/database-Postgres%20%7C%20SQLite-blue?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
</div>

---

## 🌟 Tổng Quan Dự Án
**AlphaHome** là hệ thống quản lý bất động sản và căn hộ dịch vụ nội bộ dành riêng cho đội ngũ chuyên viên Sales của AlphaHome Group. Nền tảng được tối ưu hóa toàn diện về hiệu năng, giao diện Glassmorphism độc bản và trải nghiệm người dùng di động (Mobile First UX) giúp đội ngũ Sale chốt giao dịch nhanh chóng và chính xác.

> [!NOTE]
> Dự án được xây dựng trên nền tảng **Django** kết hợp với hệ thống Front-end tối ưu bằng **Bootstrap 5** và **Vanilla CSS** tùy biến cao độ.

---

## 🎯 Tính Năng Cốt Lõi (Đẳng Cấp & Toàn Diện)

### 📊 1. Dashboard Quản Trị Đa Chiều
*   Thống kê trực quan số lượng phòng **Đang Trống**, **Đã Thuê**, **Chờ Duyệt Hợp Đồng** theo thời gian thực.
*   Nút tác vụ nhanh **"Chốt Sale"** tối ưu hóa công thái học trên thiết bị di động.
*   Báo cáo doanh số và lịch sử chốt giao dịch của từng cá nhân bán hàng.

### 🗺️ 2. Bản Đồ Bất Động Sản Tương Tác
*   Tích hợp bản đồ trực quan chỉ lọc hiển thị các **phòng còn trống**.
*   Tự động ẩn các phòng đã thuê hoặc đang trong trạng thái chờ duyệt nhằm tăng tốc độ định vị giỏ hàng trống cho Sale.

### 🔍 3. Bộ Lọc Tìm Kiếm Đa Tiêu Chí
*   Lọc phòng theo: *Khoảng giá (Min/Max)*, *Quận/Huyện*, *Trạng thái*.
*   Thuật toán phân trang (Pagination) thông minh không mất trạng thái bộ lọc khi chuyển trang.
*   Loại bỏ hoàn toàn trùng lặp dữ liệu trong các dropdown bộ lọc.

### 📱 4. Trang Chi Tiết Phòng Siêu Trải Nghiệm (High-Fidelity Mobile UI)
*   **Touch Carousel:** Bộ sưu tập ảnh cảm ứng nhạy bén, tích hợp cơ chế đồng bộ thumbnail thông minh qua phương thức cuộn nội bộ `scrollTo` giúp triệt tiêu hoàn toàn lỗi giật màn hình trên iOS và Android.
*   **Related Products Carousel:** Hiển thị danh sách các phòng khác cùng khu vực dưới dạng Slide trượt ngang mượt mà tích hợp `scroll-snap` chuẩn Native App trên di động.

---

## 🏗️ Kiến Trúc Thư Mục Dự Án

```bash
cartAlphahome/
│
├── core/                       # App nghiệp vụ chính của hệ thống
│   ├── models.py               # Thiết kế cơ sở dữ liệu (OOP, Đóng gói cao)
│   ├── views.py                # Xử lý Logic nghiệp vụ (Hàm ngắn < 40 dòng)
│   └── urls.py                 # Định tuyến Endpoint hệ thống
│
├── static/                     # Tài nguyên tĩnh
│   ├── css/
│   │   └── style.css           # Design System & các Token CSS cốt lõi
│   └── img/                    # Asset hình ảnh & Logo chính thức
│
├── templates/                  # Hệ thống giao diện Django Templates
│   ├── base.html               # Layout gốc (Chứa Navbar & Sidebar cố định)
│   └── core/
│       ├── login.html          # Trang đăng nhập Glassmorphism responsive
│       ├── product_list.html   # Bộ lọc & Danh sách phòng
│       ├── product_detail.html # Trang chi tiết & Carousel vuốt chạm
│       └── dashboard.html      # Thống kê nghiệp vụ Sales
│
├── manage.py                   # Lệnh điều hành Django
└── requirements.txt            # Danh sách thư viện phụ thuộc
```

---

## ⚡ Hướng Dẫn Cài Đặt Dưới Môi Trường Local

### 1. Chuẩn bị môi trường
Yêu cầu cài đặt sẵn **Python 3.10** trở lên.

```bash
# Clone dự án về máy
git clone <repository_url>
cd cartAlphahome

# Tạo và kích hoạt môi trường ảo (Virtual Environment)
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Cài đặt các thư viện dependencies
pip install -r requirements.txt
```

### 2. Đồng bộ Database & Chạy Server phát triển
Hệ thống sử dụng SQLite mặc định ở môi trường phát triển local để đảm bảo tính nhẹ nhàng, cơ động.

```bash
# Chạy migration để khởi tạo cấu trúc bảng dữ liệu
python manage.py migrate

# Tạo tài khoản Admin/Quản lý cấp cao
python manage.py createsuperuser

# Khởi chạy server phát triển
python manage.py runserver
```
Truy cập hệ thống tại: `http://127.0.0.1:8000/`

---

## 🚀 Quy Trình Deploy Chuẩn Lên Railway (Production)

Railway sử dụng hệ thống Container với ổ cứng lưu trữ tạm thời (Ephemeral Filesystem). Để bảo toàn dữ liệu bền vững, hệ thống đã được tích hợp bộ kết nối tự động sang **PostgreSQL**.

### 1. Thiết lập Database PostgreSQL trên Railway
1. Trên Dashboard của Railway, chọn **New Project** -> **Provision PostgreSQL**.
2. Railway sẽ tự động cung cấp biến môi trường `DATABASE_URL` cho Project.

### 2. Thiết lập cấu hình biến động trong `settings.py`
Hệ thống sử dụng thư viện `dj-database-url` để tự động nhận dạng môi trường kết nối:

```python
import os
import dj_database_url

# Tự động chuyển đổi sang PostgreSQL trên Cloud, giữ SQLite khi code Local
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        ssl_require=True if os.environ.get('DATABASE_URL') else False
    )
}
```

### 3. Deploy
Đẩy code lên GitHub và kết nối Git Repository với Railway. Hệ thống sẽ tự động build, tạo container và kết nối trực tiếp đến PostgreSQL một cách an toàn và bền vững.

---

## 📐 Chuẩn Mực Phát Triển Mã Nguồn (Coding Standards)

Để đảm bảo dự án luôn dễ bảo trì và mở rộng, đội ngũ kỹ sư của AlphaHome cam kết tuân thủ chặt chẽ:
*   **Đóng gói hướng đối tượng (OOP):** Tất cả các Logic liên quan đến thuộc tính dữ liệu đều được đóng gói an toàn trong Model.
*   **Quy tắc 40 dòng:** Giới hạn mỗi hàm xử lý (View/Helper) không vượt quá 40 dòng để đảm bảo tính module hóa và dễ viết Unit Test.
*   **Type Hinting:** Mọi định nghĩa hàm đều đi kèm mô tả kiểu dữ liệu đầu vào & đầu ra rõ ràng.
*   **Self-documenting code:** Viết code tường minh, Comment chỉ được viết để trả lời câu hỏi *"Tại sao lại viết như thế này"* thay vì giải thích *"Đoạn code này làm gì"*.

---

<div align="center">
  <p>Được phát triển và duy trì bởi <b>Đội ngũ Công nghệ AlphaHome</b> © 2026. Mọi quyền được bảo lưu.</p>
</div>
