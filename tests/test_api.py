import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_signup_login_profile():
    client = APIClient()
    # Đăng ký user mới
    signup_data = {
        "hoten": "Test User",
        "sodienthoai": "0999999999",
        "password": "testpass123",
        "email": "testuser@example.com"
    }
    resp = client.post("/api/auth/signup/", signup_data, format="json")
    assert resp.status_code == 201

    # Đăng nhập
    login_data = {"sodienthoai": "0999999999", "password": "testpass123"}
    resp = client.post("/api/auth/login/", login_data, format="json")
    assert resp.status_code == 200
    tokens = resp.json()
    access = tokens["access"]
    refresh = tokens["refresh"]

    # Lấy thông tin user (profile)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    resp = client.get("/api/user/1/")
    assert resp.status_code == 200
    assert resp.json()["soDienThoai"] == "0999999999"

    # Đăng xuất
    resp = client.post("/api/auth/logout/", {"refresh": refresh}, format="json")
    assert resp.status_code == 205

@pytest.mark.django_db
def test_booking_list_for_roles():
    client = APIClient()
    # Tạo user tài xế
    driver = User.objects.create_user(hoten="Driver", sodienthoai="0888888888", password="driverpass", vaitro=1)
    # Đăng nhập tài xế
    resp = client.post("/api/auth/login/", {"sodienthoai": "0888888888", "password": "driverpass"}, format="json")
    access = resp.json()["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    # Lấy danh sách booking (chỉ booking assign cho tài xế)
    resp = client.get("/api/booking/")
    assert resp.status_code == 200
    # Không lỗi quyền và trả về list
    assert isinstance(resp.json(), list)

    # Tạo user nhân viên
    staff = User.objects.create_user(hoten="Staff", sodienthoai="0777777777", password="staffpass", vaitro=2)
    resp = client.post("/api/auth/login/", {"sodienthoai": "0777777777", "password": "staffpass"}, format="json")
    access = resp.json()["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    resp = client.get("/api/booking/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

    # Tạo user khách
    guest = User.objects.create_user(hoten="Guest", sodienthoai="0666666666", password="guestpass", vaitro=3)
    resp = client.post("/api/auth/login/", {"sodienthoai": "0666666666", "password": "guestpass"}, format="json")
    access = resp.json()["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    resp = client.get("/api/booking/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
