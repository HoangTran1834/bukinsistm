# Hướng dẫn cài đặt và chạy hệ thống

## 1. Tạo môi trường ảo và cài đặt phụ thuộc Python

Chạy script sau (trên Linux/WSL):
```sh
bash scripts/setup_venv.sh
```
Sau đó kích hoạt môi trường ảo:
```sh
. .venv/bin/activate
```

Nếu dùng Windows CMD/PowerShell, hãy tự tạo môi trường ảo và kích hoạt:
```sh
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Khởi động database MySQL

**Với WSL/Linux:**
```sh
sudo service mysql start
```

**Với Windows:**
- Hãy đảm bảo MySQL đã chạy (qua XAMPP, MySQL Workbench, ...)

## 3. Khởi tạo/migrate database và nạp dữ liệu mẫu
Chạy lần lượt các lệnh sau (có thể copy từ Makefile):

```sh
mysql -u root -pAbc123!@# hethongdatxe < HeThongDatXe.sql
python manage.py makemigrations datxe_backend
python manage.py migrate
python scripts/hash_user_password.py
```

**Lưu ý:** Để tạo được trigger trong MySQL, bạn cần chạy lệnh với quyền root. Nếu không cảm thấy an toàn khi dùng tài khoản root, bạn có thể tự tạo một tài khoản MySQL riêng và cấu hình lại thông tin kết nối trong file `settings.py` của dự án.

## 4. Chạy backend Django

```sh
python manage.py runserver
```

## 5. Chạy frontend UI (React)

```sh
cd datxe_frontend
npm install
npm run dev
```

Sau đó truy cập FE tại http://localhost:5173 và BE tại http://localhost:8000

---
Nếu có Makefile, bạn có thể dùng các lệnh tắt:
- `make run-ser` (chạy backend)
- `make run-ui` (chạy frontend)
- `make migrate`, `make update-database`, ...

**Lưu ý:**
- Luôn kích hoạt môi trường ảo trước khi chạy các lệnh Python/Django.
- Đảm bảo MySQL đã chạy trước khi migrate hoặc nạp dữ liệu.
