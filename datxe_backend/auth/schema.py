from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .serializers import (
    SignupSerializer, LoginSerializer, LogoutInputSerializer, OTPVerifySerializer, ResetPasswordSerializer,
    UserProfileSerializer, UserSearchSerializer, UserUpdateSerializer
)

"""
Schema definitions for Auth-related API endpoints.
"""

def signup_schema():
    return {
        "description": "Đăng ký tài khoản mới. Staff có thể tạo trực tiếp, user thường sẽ nhận OTP để xác thực. Dữ liệu sẽ được lưu tạm và kích hoạt sau khi verify OTP.",
        "request": SignupSerializer,
        "responses": {
            201: {"description": "Staff tạo tài khoản thành công"},
            200: {"description": "OTP đã được gửi, cần verify để hoàn thành đăng ký"}
        },
        "examples": [
            OpenApiExample(
                name='Staff tạo tài khoản',
                summary='Staff tạo tài khoản trực tiếp',
                description='Staff có thể tạo tài khoản ngay lập tức',
                value={"hoten": "Nguyen Van A", "sodienthoai": "0123456789", "password": "matkhau123", "email": "a@gmail.com"},
                request_only=True,
            ),
            OpenApiExample(
                name='User đăng ký với OTP',
                summary='User thường đăng ký qua OTP',
                description='Dữ liệu sẽ được lưu tạm, OTP gửi về để xác thực',
                value={"hoten": "Nguyen Van B", "sodienthoai": "0987654321", "password": "matkhau123", "email": "b@gmail.com"},
                request_only=True,
            ),
        ],
    }

def login_schema():
    return {
        "description": "Đăng nhập vào hệ thống. Có thể dùng password truyền thống hoặc OTP qua SMS. Nếu không có password, hệ thống sẽ gửi OTP.",
        "request": LoginSerializer,
        "responses": {
            200: {
                "description": "Đăng nhập thành công hoặc OTP đã được gửi",
                "example": {
                    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    "user": {
                        "id": 1,
                        "hoten": "Admin",
                        "sodienthoai": "admin",
                        "vaitro": 0
                    }
                }
            }
        },
        "examples": [
            OpenApiExample(
                name='Đăng nhập bằng password',
                summary='Đăng nhập truyền thống',
                value={"sodienthoai": "0123456789", "password": "matkhau123"},
                request_only=True,
            ),
            OpenApiExample(
                name='Yêu cầu OTP đăng nhập',
                summary='Đăng nhập bằng OTP',
                value={"sodienthoai": "0123456789"},
                request_only=True,            ),
        ],
    }

def logout_schema():
    return {
        "description": "Đăng xuất khỏi hệ thống (thu hồi refresh token). Phải đính kèm refresh token.",
        "request": LogoutInputSerializer,
        "responses": {200: {"description": "Đăng xuất thành công"}},
        "examples": [
            OpenApiExample(
                name='Đăng xuất mẫu',
                summary='Ví dụ đăng xuất',
                description='Sử dụng refresh token để đăng xuất',
                value={"refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."},
                request_only=True,
            ),
        ],
    }

def reset_password_schema():
    return {
        "description": "Yêu cầu đặt lại mật khẩu qua SMS OTP. Nhập số điện thoại và mật khẩu mới, hệ thống sẽ gửi OTP để xác thực.",
        "request": ResetPasswordSerializer,
        "responses": {
            200: {
                "description": "OTP đã được gửi",
                "example": {
                    "message": "OTP đã được gửi đến số điện thoại của bạn",
                    "phone": "0123456789",
                    "expires_in": 300,
                    "requires_otp": True
                }
            },
            400: {"description": "Số điện thoại chưa đăng ký hoặc lỗi khác"}
        },
        "examples": [
            OpenApiExample(
                'Yêu cầu reset password',
                summary='Gửi OTP để reset mật khẩu với password mới',
                value={
                    "sodienthoai": "0123456789",
                    "password": "matkhaumoi123"
                },
                request_only=True,
            ),
        ],
    }

def sms_signup_verify_schema():
    return {
        "description": "Xác thực mã OTP cho các flow: đăng ký, đăng nhập, hoặc đặt lại mật khẩu.",
        "request": OTPVerifySerializer,
        "responses": {
            201: {
                "description": "Thành công - Đăng ký", 
                "example": {
                    "message": "Đăng ký thành công",
                    "user": {
                        "id": 124,
                        "hoten": "Nguyen Van A",
                        "sodienthoai": "0987654321",
                        "vaitro": 1
                    },
                    "tokens": {
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
                    }
                }
            },
            200: {
                "description": "Thành công - Đăng nhập hoặc đặt lại mật khẩu",
                "example": {
                    "message": "Đăng nhập thành công",
                    "user": {
                        "id": 124,
                        "hoten": "Nguyen Van A", 
                        "sodienthoai": "0987654321",
                        "vaitro": 1
                    },
                    "tokens": {
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
                    }
                }
            },
            400: {
                "description": "Lỗi",
                "example": {"error": "Mã OTP không đúng"}
            }
        },
        "examples": [
            OpenApiExample(
                'Xác thực OTP',
                summary='Xác thực OTP cho tất cả các flow',
                description='Chỉ cần nhập số điện thoại và OTP, hệ thống tự nhận diện và xử lý action tương ứng',
                value={
                    "sodienthoai": "0987654321",
                    "otp": "123456"
                },
                request_only=True,
            ),
        ],
    }


# Profile Management Schemas
def get_profile_schema():
    return {
        "description": "Lấy thông tin profile của người dùng hiện tại",
        "responses": {
            200: {
                "description": "Thông tin profile thành công",
                "example": {
                    "manguoidung": 123,
                    "hoten": "Nguyen Van A",
                    "sodienthoai": "0123456789",
                    "email": "user@example.com",
                    "vaitro": "Khách hàng"
                }
            },
            401: {"description": "Chưa đăng nhập"}
        }
    }

def search_user_schema():
    return {
        "description": "Tìm kiếm thông tin người dùng khác theo ID hoặc số điện thoại. Email sẽ bị ẩn nếu không phải tài khoản của bản thân.",
        "request": UserSearchSerializer,
        "responses": {
            200: {
                "description": "Tìm thấy người dùng",
                "example": {
                    "manguoidung": 124,
                    "hoten": "Tran Van B",
                    "sodienthoai": "0987654321",
                    "vaitro": "Tài xế"
                }
            },
            404: {"description": "Không tìm thấy người dùng"},
            400: {"description": "Thiếu thông tin tìm kiếm"}
        },
        "examples": [
            OpenApiExample(
                'Tìm theo ID',
                summary='Tìm kiếm user theo ID',
                value={"manguoidung": 124},
                request_only=True,
            ),
            OpenApiExample(
                'Tìm theo số điện thoại',
                summary='Tìm kiếm user theo số điện thoại',
                value={"sodienthoai": "0987654321"},
                request_only=True,
            ),
        ],
    }

def update_profile_schema():
    return {
        "description": "Cập nhật thông tin cá nhân. Chỉ được phép sửa họ tên và email. Không thể thay đổi số điện thoại, ID, mật khẩu hoặc vai trò.",
        "request": UserUpdateSerializer,
        "responses": {
            200: {
                "description": "Cập nhật thành công",
                "example": {
                    "message": "Cập nhật thông tin thành công",
                    "user": {
                        "manguoidung": 123,
                        "hoten": "Nguyen Van A Updated",
                        "sodienthoai": "0123456789",
                        "email": "newemail@example.com",
                        "vaitro": "Khách hàng"
                    }
                }
            },
            400: {"description": "Dữ liệu không hợp lệ"},
            401: {"description": "Chưa đăng nhập"}
        },
        "examples": [
            OpenApiExample(
                'Cập nhật đầy đủ',
                summary='Cập nhật cả họ tên và email',
                value={
                    "hoten": "Nguyen Van A Updated",
                    "email": "newemail@example.com"
                },
                request_only=True,
            ),
            OpenApiExample(
                'Chỉ cập nhật họ tên',
                summary='Chỉ cập nhật họ tên',
                value={"hoten": "Nguyen Van A New"},
                request_only=True,
            ),
            OpenApiExample(
                'Chỉ cập nhật email',
                summary='Chỉ cập nhật email',
                value={"email": "another@example.com"},
                request_only=True,
            ),
        ],
    }