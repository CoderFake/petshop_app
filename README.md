# Pet Shop - Hệ thống quản lý cửa hàng thú cưng

Ứng dụng web hiện đại để quản lý và kinh doanh các sản phẩm thú cưng, xây dựng trên nền tảng Flask, hỗ trợ cả MySQL và SQLite.

## Tính năng chính

### Tổng quan
- **Đa nền tảng cơ sở dữ liệu**: Hỗ trợ cả MySQL và SQLite
- **Đa ngôn ngữ**: Giao diện tiếng Việt
- **Thiết kế responsive**: Tương thích với mọi thiết bị
- **Phân quyền chi tiết**: Hệ thống RBAC linh hoạt (Role-Based Access Control)
- **Giỏ hàng cho cả khách vãng lai và người dùng đã đăng nhập**
- **Soft delete**: Cơ chế xóa mềm cho tất cả đối tượng trong hệ thống

### Dành cho người dùng cuối
- **Đăng ký tài khoản** với xác thực email
- **Đăng nhập** với chức năng "Ghi nhớ đăng nhập"
- **Quên mật khẩu và đặt lại mật khẩu**
- **Quản lý hồ sơ cá nhân** và thông tin người dùng
- **Xem, tìm kiếm và lọc sản phẩm** theo nhiều tiêu chí
- **Đánh giá và phản hồi sản phẩm**
- **Giỏ hàng thông minh** với chuyển đổi từ ẩn danh sang đã đăng nhập
- **Đặt hàng không cần đăng nhập**
- **Thanh toán đa phương thức**: COD và VNPay
- **Xem và theo dõi trạng thái đơn hàng**
- **Email thông báo** cho mọi hoạt động quan trọng

### Dành cho quản trị viên
- **Dashboard** với thống kê tổng quan
- **Quản lý người dùng**: Thêm, sửa, xóa, kích hoạt/hủy kích hoạt
- **Quản lý sản phẩm**: Thêm, sửa, xóa, quản lý hình ảnh
- **Quản lý danh mục**: Thêm, sửa, xóa
- **Quản lý đơn hàng**: Xem, cập nhật trạng thái, gửi thông báo
- **Quản lý đánh giá và phản hồi**
- **Phân quyền người dùng**: Tạo vai trò, phân quyền chi tiết
- **Cấu hình cửa hàng**: Thông tin liên hệ, phương thức thanh toán

## Cài đặt

### Yêu cầu

- Python 3.9+
- MySQL 5.7+ (nếu sử dụng MySQL)
- pip (Python package manager)

### Cài đặt từ mã nguồn

1. **Clone repository:**
```bash
git clone https://github.com/coderfake/petshop_app.git
cd petshop_app
```

2. **Tạo môi trường ảo Python:**
```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường - Windows
venv\Scripts\activate
# Kích hoạt môi trường - macOS/Linux
source venv/bin/activate
```

3. **Cài đặt dependencies:**
```bash
pip install -r requirements.txt
```

4. **Tạo file cấu hình:**
```bash
cp .env.example .env
```

5. **Cấu hình database trong file .env:**
```
# MySQL
DEV_DATABASE_URL=mysql+pymysql://username:password@localhost/petshop_dev?charset=utf8mb4

# SQLite
SQLITE_DATABASE_URL=sqlite:///petshop.sqlite

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# VNPay
VNPAY_TMN_CODE=your-merchant-code
VNPAY_HASH_SECRET=your-hash-secret
VNPAY_URL=https://sandbox.vnpayment.vn/paymentv2/vpcpay.html

# Timezone
TIMEZONE=Asia/Ho_Chi_Minh
```

6. **Khởi tạo cơ sở dữ liệu:**

   **Với MySQL (mặc định):**
   ```bash
   # Tạo database (nếu chưa có)
   mysql -u root -p -e "CREATE DATABASE petshop_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
   
   # Khởi tạo database schema
   flask db upgrade
   
   # Khởi tạo dữ liệu ban đầu
   flask seed-db
   
   # Khởi tạo permissions
   flask init-permissions
   
   # Tạo tài khoản admin
   flask create-admin admin@example.com "Admin Name" --password
   ```

   **Với SQLite:**
   ```bash
   # Khởi tạo database schema
   flask --sql db upgrade
   
   # Khởi tạo dữ liệu ban đầu
   flask --sql seed-db
   
   # Khởi tạo permissions
   flask --sql init-permissions
   
   # Tạo tài khoản admin
   flask --sql create-admin admin@example.com "Admin Name" --password
   ```

7. **Chạy ứng dụng:**
   ```bash
   # Với MySQL
   flask run
   
   # Với SQLite
   flask run --sql
   ```

8. **Truy cập ứng dụng:**
   Mở trình duyệt và truy cập http://localhost:5000

## Cấu trúc dự án

```
petshop_app/
├── app/                    # Thư mục chính của ứng dụng
│   ├── __init__.py         # Khởi tạo ứng dụng Flask
│   ├── config.py           # Cấu hình ứng dụng
│   ├── commands.py         # Các lệnh CLI
│   ├── extensions.py       # Khởi tạo các extension
│   ├── models/             # Models SQLAlchemy
│   │   ├── base.py         # Model cơ sở
│   │   ├── user.py         # Người dùng
│   │   ├── role.py         # Vai trò và quyền
│   │   ├── category.py     # Danh mục
│   │   ├── product.py      # Sản phẩm
│   │   ├── order.py        # Đơn hàng
│   │   └── ...
│   ├── routes/             # Routes của ứng dụng
│   │   ├── main.py         # Trang chính
│   │   ├── auth.py         # Xác thực
│   │   ├── payment.py      # Thanh toán
│   │   ├── admin.py        # Admin
│   │   └── ...
│   ├── static/             # Tài nguyên tĩnh (CSS, JS, images)
│   ├── templates/          # Templates Jinja2
│   │   ├── auth/           # Giao diện xác thực
│   │   ├── admin/          # Giao diện admin
│   │   ├── payment/        # Giao diện thanh toán
│   │   ├── emails/         # Email templates
│   │   └── ...
│   └── utils/              # Tiện ích
│       ├── decorators.py   # Các decorator
│       ├── email.py        # Gửi email
│       ├── vnpay.py        # Tích hợp VNPay
│       ├── validators.py   # Hàm validate
│       ├── datetime_helpers.py # Xử lý múi giờ
│       └── ...
├── migrations/             # Thư mục cho Flask-Migrate
├── .env                    # Biến môi trường
├── .env.example            # Mẫu biến môi trường
├── requirements.txt        # Danh sách thư viện cần thiết
└── run.py                  # Entry point để chạy ứng dụng
```

## Quy trình thanh toán

### COD (Thanh toán khi nhận hàng)
1. Người dùng chọn sản phẩm và thêm vào giỏ hàng
2. Người dùng tiến hành thanh toán và chọn phương thức "COD"
3. Hệ thống tạo đơn hàng với trạng thái "pending" và phương thức thanh toán "cod"
4. Người dùng nhận được email xác nhận đơn hàng
5. Admin xử lý đơn hàng và cập nhật trạng thái
6. Khi đơn hàng được giao và người dùng thanh toán, admin cập nhật trạng thái thanh toán thành "paid"

### VNPay (Thanh toán trực tuyến)
1. Người dùng chọn sản phẩm và thêm vào giỏ hàng
2. Người dùng tiến hành thanh toán và chọn phương thức "VNPay"
3. Hệ thống tạo đơn hàng với trạng thái "pending" và phương thức thanh toán "vnpay"
4. Người dùng được chuyển hướng đến cổng thanh toán VNPay
5. Sau khi thanh toán, người dùng được chuyển về trang thành công với thông tin đơn hàng
6. Hệ thống cập nhật trạng thái thanh toán của đơn hàng thành "paid"
7. Người dùng nhận được email xác nhận đơn hàng và thanh toán

## Múi giờ

Ứng dụng sử dụng múi giờ Việt Nam (Asia/Ho_Chi_Minh) cho tất cả các hoạt động liên quan đến thời gian. Cấu hình múi giờ có thể được điều chỉnh trong file `.env` thông qua biến `TIMEZONE`.

## Phân quyền

Hệ thống sử dụng mô hình RBAC (Role-Based Access Control) với hai vai trò mặc định:

- **Admin**: Có đầy đủ quyền trong hệ thống
- **User**: Quyền hạn giới hạn cho người dùng thông thường

Các quyền có thể được quản lý thông qua giao diện admin, cho phép tạo các vai trò tùy chỉnh với các quyền cụ thể.

## Chế độ test

```bash
# Chạy test với MySQL
flask test

# Chạy test với SQLite
flask --sql test
```

## Đóng góp

1. Fork repository
2. Tạo nhánh mới (`git checkout -b feature/new-feature`)
3. Commit thay đổi (`git commit -m 'Add some new feature'`)
4. Push lên nhánh (`git push origin feature/new-feature`)
5. Tạo Pull Request

## Giấy phép

Phát hành theo giấy phép MIT. Xem [LICENSE](LICENSE) để biết thêm chi tiết.

## Tác giả

- **HOANGDIEUIT** - [GitHub](https://github.com/coderfake)

## Công nghệ sử dụng

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM
- [Flask-Migrate](https://flask-migrate.readthedocs.io/) - Database migrations
- [Flask-Marshmallow](https://flask-marshmallow.readthedocs.io/) - Object serialization/deserialization
- [Bootstrap](https://getbootstrap.com/) - Frontend framework
- [jQuery](https://jquery.com/) - JavaScript library
- [VNPay](https://vnpay.vn/) - Payment integration