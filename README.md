# Pet Shop Flask Application

Ứng dụng web cửa hàng thú cưng với Flask, SQLAlchemy và MySQL

## Mô tả

Pet Shop là một ứng dụng web hiện đại giúp quản lý và kinh doanh sản phẩm thú cưng. Ứng dụng được xây dựng với Flask, SQLAlchemy ORM và cơ sở dữ liệu MySQL.

### Tính năng chính

- Quản lý danh mục và sản phẩm
- Quản lý đơn hàng và chi tiết đơn hàng
- Hệ thống đánh giá và phản hồi sản phẩm
- Quản lý người dùng và phân quyền
- Giao diện người dùng thân thiện, responsive

## Cài đặt và Chạy

### Yêu cầu

- Python 3.8+
- MySQL 5.7+
- pip (Python package manager)

### Bước 1: Clone dự án

```bash
git clone <repository-url>
cd petshop_app
```

### Bước 2: Tạo môi trường ảo Python và kích hoạt

```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo - Windows
venv\Scripts\activate
# Kích hoạt môi trường ảo - macOS/Linux
source venv/bin/activate
```

### Bước 3: Cài đặt các thư viện cần thiết

```bash
pip install -r requirements.txt
```

### Bước 4: Thiết lập môi trường

Sao chép file `.env.example` thành `.env` và cập nhật các thông tin cấu hình:

```bash
cp .env.example .env
```

Mở file `.env` và cập nhật thông tin kết nối MySQL:

```
DEV_DATABASE_URL=mysql+pymysql://username:password@localhost/petshop_dev?charset=utf8mb4
```

Thay `username`, `password` bằng thông tin đăng nhập MySQL của bạn.

### Bước 5: Tạo cơ sở dữ liệu

Đăng nhập vào MySQL và tạo cơ sở dữ liệu:

```sql
CREATE DATABASE petshop_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Bước 6: Khởi tạo cơ sở dữ liệu

```bash
# Khởi tạo cơ sở dữ liệu và các bảng
flask init-db

# Tạo dữ liệu mẫu (tùy chọn)
flask create-sample-data
```

### Bước 7: Chạy ứng dụng

```bash
flask run
```

Truy cập ứng dụng tại: http://localhost:5000

## Cấu trúc dự án

```
petshop_app/
├── app/                    # Thư mục chính của ứng dụng
│   ├── __init__.py         # Khởi tạo ứng dụng Flask
│   ├── config.py           # Cấu hình ứng dụng
│   ├── commands.py         # Các lệnh CLI
│   ├── extensions.py       # Khởi tạo các extension
│   ├── models/             # Models SQLAlchemy
│   ├── routes/             # Routes của ứng dụng
│   ├── static/             # Tài nguyên tĩnh (CSS, JS, images)
│   ├── templates/          # Templates Jinja2
│   └── utils/              # Tiện ích và helpers
├── migrations/             # Thư mục cho Flask-Migrate
├── .env                    # Biến môi trường
├── .env.example            # Mẫu biến môi trường
├── requirements.txt        # Danh sách thư viện cần thiết
└── run.py                  # Entry point để chạy ứng dụng
```

## Quản lý phiên bản cơ sở dữ liệu với Flask-Migrate

```bash
# Khởi tạo repository migrations
flask db init

# Tạo migration khi có thay đổi models
flask db migrate -m "Initial migration."

# Áp dụng migrations
flask db upgrade
```

## Tác giả

- Huy Trinh
