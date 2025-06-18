from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .serializers import (
    UserSerializer, SignupSerializer, LoginSerializer, BookingSerializer, 
    BookingDetailSerializer, ChitietdatxeInputSerializer, CheckSlotInputSerializer, GetDirectionInputSerializer, 
    GetDistrictInputSerializer, GetPriceInputSerializer, TuyenduongSerializer, 
    HuyenSerializer, CaSerializer, CaCreateUpdateSerializer, ChitietcaSerializer, TaixeSerializer, XeSerializer, CreateShiftDetailSerializer, GetHuyenInputSerializer, 
    GetHuyenOutputSerializer, GetTuyenDuongInputSerializer, GetTuyenDuongByCoordinatesInputSerializer
)

"""
File này chứa định nghĩa schema cho API để tách khỏi logic view.
Mỗi schema được định nghĩa dưới dạng hàm trả về dict với các tham số cho decorator @extend_schema.
"""

# AuthViewSet schemas
def signup_schema():
    return {
        "description": "Đăng ký tài khoản mới. Nhập họ tên, số điện thoại, mật khẩu và (tùy chọn) email.",
        "request": SignupSerializer,
        "responses": {201: {"description": "Đăng ký thành công"}},
        "examples": [
            OpenApiExample(
                name='Đăng ký mẫu',
                summary='Ví dụ đăng ký tài khoản',
                description='Thông tin cần thiết để đăng ký tài khoản mới',
                value={"hoten": "Nguyen Van A", "sodienthoai": "0123456789", "password": "matkhau123", "email": "a@gmail.com"},
                request_only=True,
            ),
        ],
    }

def login_schema():
    return {
        "description": "Đăng nhập vào hệ thống bằng số điện thoại và mật khẩu. API sẽ trả về access token và refresh token.",
        "request": LoginSerializer,
        "responses": {
            200: {
                "type": "object",
                "properties": {
                    "access_token": {"type": "string", "example": "eyJ0eXAiOiJKV1QiLCJhbGc..."},
                    "refresh_token": {"type": "string", "example": "eyJ0eXAiOiJKV1QiLCJhbGc..."},
                    "user": {
                        "type": "object",
                        "properties": {
                            "manguoidung": {"type": "integer", "example": 1},
                            "hoten": {"type": "string", "example": "Admin"},
                            "sodienthoai": {"type": "string", "example": "admin"},
                            "vaitro": {"type": "integer", "example": 0}
                        }
                    }
                }
            }
        },
        "examples": [
            OpenApiExample(
                name='Admin',
                summary='Tài khoản admin',
                description='Đăng nhập với quyền admin (vai trò 0)',
                value={"sodienthoai": "admin", "password": "admin123"},
                request_only=True,
            ),
            OpenApiExample(
                name='Tài xế 1 - Nguyễn Văn Hùng',
                summary='Tài xế',
                description='Tài xế 1 (vai trò 1)',
                value={"sodienthoai": "0977000001", "password": "txpass1"},
                request_only=True,
            ),
            OpenApiExample(
                name='Tài xế 2 - Trần Quốc Toàn',
                summary='Tài xế',
                description='Tài xế 2 (vai trò 1)',
                value={"sodienthoai": "0977000002", "password": "txpass2"},
                request_only=True,
            ),
            OpenApiExample(
                name='Tài xế 3 - Lê Văn Tám',
                summary='Tài xế',
                description='Tài xế 3 (vai trò 1)',
                value={"sodienthoai": "0977000003", "password": "txpass3"},
                request_only=True,
            ),
            OpenApiExample(
                name='Tài xế 4 - Phan Văn Cường',
                summary='Tài xế',
                description='Tài xế 4 (vai trò 1)',
                value={"sodienthoai": "0977000004", "password": "txpass4"},
                request_only=True,
            ),
            OpenApiExample(
                name='Nhân viên 1 - Lê Văn Chính',
                summary='Nhân viên',
                description='Nhân viên 1 (vai trò 2)',
                value={"sodienthoai": "0909090909", "password": "mypassword789"},
                request_only=True,
            ),
            OpenApiExample(
                name='Nhân viên 2 - Ngô Thị Hạnh',
                summary='Nhân viên',
                description='Nhân viên 2 (vai trò 2)',
                value={"sodienthoai": "0955555555", "password": "nhanvienpass"},
                request_only=True,
            ),
            OpenApiExample(
                name='Hành khách 1 - Nguyễn Văn An',
                summary='Hành khách',
                description='Hành khách 1 (vai trò 3)',
                value={"sodienthoai": "0912345678", "password": "password123"},
                request_only=True,
            ),
            OpenApiExample(
                name='Hành khách 2 - Phạm Minh Đức',
                summary='Hành khách',
                description='Hành khách 2 (vai trò 3)',
                value={"sodienthoai": "0933123456", "password": "userpass321"},
                request_only=True,
            ),
            OpenApiExample(
                name='Hành khách 3 - Hoàng Thị Em',
                summary='Hành khách',
                description='Hành khách 3 (vai trò 3)',
                value={"sodienthoai": "0944987654", "password": "strongpass654"},
                request_only=True,
            ),
            OpenApiExample(
                name='Hành khách 4 - Đặng Văn Phúc',
                summary='Hành khách',
                description='Hành khách 4 (vai trò 3)',
                value={"sodienthoai": "0967894321", "password": "safe123pass"},
                request_only=True,
            ),
            OpenApiExample(
                name='Hành khách 5 - Vũ Minh Tuấn',
                summary='Hành khách',
                description='Hành khách 5 (vai trò 3)',
                value={"sodienthoai": "0933555777", "password": "khachpass1"},
                request_only=True,
            ),
            OpenApiExample(
                name='Hành khách 6 - Lý Thị Hoa',
                summary='Hành khách',
                description='Hành khách 6 (vai trò 3)',
                value={"sodienthoai": "0922444666", "password": "khachpass2"},
                request_only=True,
            ),
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

# RouteViewSet schemas
def get_price_schema():
    return {
        "description": "Tính giá tiền cho chuyến đi dựa theo địa chỉ hoặc tọa độ. Cần cung cấp đủ thông tin để xác định tuyến đường.",
        "request": GetPriceInputSerializer,
        "responses": {200: {"description": "Thành công - trả về giá tiền và thông tin tuyến đường"}},
        "examples": [
            OpenApiExample(
                name='Tính giá bằng địa chỉ',
                summary='Sử dụng địa chỉ',
                description='Tính giá dựa trên địa chỉ điểm đón và điểm trả',
                value={"diachi_don": "Đà Nẵng", "diachi_tra": "Tam Kỳ"},
                request_only=True,
            ),
            OpenApiExample(
                name='Tính giá bằng tọa độ',
                summary='Sử dụng tọa độ',
                description='Tính giá dựa trên tọa độ vĩ độ/kinh độ',
                value={"lat_don": "16.05", "lon_don": "108.2", "lat_tra": "15.57", "lon_tra": "108.48"},
                request_only=True,
            ),
        ],
    }

def list_routes_schema():
    return {
        "description": "Lấy danh sách các tuyến đường (đã có mã tuyến đường). Chỉ admin mới xem được danh sách này.",
        "responses": {
            200: {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "matuyenduong": {"type": "integer", "example": 1},
                        "tentuyenduong": {"type": "string", "example": "Đà Nẵng - Tam Kỳ"},
                        "giatien": {"type": "integer", "example": 30000}
                    }
                }
            }
        },
        "examples": [
            OpenApiExample(
                'Tuyến đường mẫu',
                value=[{"matuyenduong": 1, "tentuyenduong": "Đà Nẵng - Tam Kỳ", "giatien": 30000}],
                response_only=True,
            ),
        ],
    }

def create_route_schema():
    return {
        "description": "Tạo mới một tuyến đường (chưa có mã tuyến đường). Chỉ admin mới có quyền này.",
        "request": TuyenduongSerializer,
        "responses": {
            201: {
                "type": "object",
                "properties": {
                    "matuyenduong": {"type": "integer", "example": 1},
                    "tentuyenduong": {"type": "string", "example": "Tam Kỳ - Hội An"},
                    "giatien": {"type": "integer", "example": 40000}
                }
            }
        },
        "examples": [
            OpenApiExample(
                'Thêm tuyến đường mẫu',
                value={"tentuyenduong": "Tam Kỳ - Hội An", "giatien": 40000},
                request_only=True,
            ),
        ],
    }

def update_route_schema():
    return {
        "description": "Cập nhật thông tin một tuyến đường (đã có mã tuyến đường). Chỉ admin mới có quyền này.",
        "request": TuyenduongSerializer,
        "responses": {
            200: {
                "type": "object",
                "properties": {
                    "matuyenduong": {"type": "integer", "example": 1},
                    "tentuyenduong": {"type": "string", "example": "Đà Nẵng - Tam Kỳ"},
                    "giatien": {"type": "integer", "example": 35000}
                }
            }
        },
        "examples": [
            OpenApiExample(
                'Cập nhật tuyến đường mẫu',
                value={"matuyenduong": 1, "tentuyenduong": "Đà Nẵng - Hội An", "giatien": 35000},
                request_only=True,
            ),
        ],
    }

def delete_route_schema():
    return {
        "description": "Xóa một tuyến đường (đã có mã tuyến đường). Chỉ admin mới có quyền này.",
        "responses": {204: OpenApiExample('Xóa thành công', value={})},
        "examples": [
            OpenApiExample(
                'Xóa tuyến đường mẫu',
                value={"matuyenduong": 1},
                request_only=True,
            ),
        ],
    }

def get_tuyen_duong_by_address_schema():
    return {
        "description": "Tìm tuyến đường từ 2 địa chỉ. API này chấp nhận địa chỉ dạng text.",
        "request": GetTuyenDuongInputSerializer,
        "responses": {200: {"description": "Thành công - trả về thông tin tuyến đường"}},
        "examples": [
            OpenApiExample(
                name='Tìm tuyến đường mẫu',
                summary='Đà Nẵng đến Tam Kỳ',
                description='Tìm tuyến đường từ Đà Nẵng đến Tam Kỳ',
                value={"diachi_don": "Đà Nẵng", "diachi_tra": "Tam Kỳ"},
                request_only=True,
            ),
            OpenApiExample(
                name='Tuyến đường khác',
                summary='Đà Nẵng đến Điện Bàn',
                description='Tìm tuyến đường từ Đà Nẵng đến Điện Bàn',
                value={"diachi_don": "Đà Nẵng", "diachi_tra": "Điện Bàn"},
                request_only=True,
            ),
        ],
    }

def get_tuyen_duong_by_coordinates_schema():
    return {
        "description": "Tìm tuyến đường từ 2 tọa độ. API này chấp nhận tọa độ vĩ độ/kinh độ.",
        "request": GetTuyenDuongByCoordinatesInputSerializer,
        "responses": {200: {"description": "Thành công - trả về thông tin tuyến đường"}},
        "examples": [
            OpenApiExample(
                name='Tìm tuyến đường bằng tọa độ',
                summary='Sử dụng vĩ độ/kinh độ',
                description='Tìm tuyến đường từ tọa độ Đà Nẵng đến Tam Kỳ',
                value={"lat_don": "16.05", "lon_don": "108.2", "lat_tra": "15.57", "lon_tra": "108.48"},
                request_only=True,
            ),
        ],
    }

def search_address_schema():
    return {
        "description": "Tìm kiếm địa chỉ (geocoding) sử dụng Nominatim.",
        "request": SearchAddressInputSerializer,
        "responses": {200: OpenApiExample('Kết quả', value=[{"display_name": "Địa chỉ mẫu", "lat": "16.05", "lon": "108.2"}])},
        "examples": [
            OpenApiExample(
                'Tìm kiếm địa chỉ mẫu',
                value={"query": "Đà Nẵng"},
                request_only=True,
            ),
        ],
    }

def reverse_geocode_schema():
    return {
        "description": "Chuyển đổi tọa độ thành địa chỉ (reverse geocoding) sử dụng Nominatim.",
        "request": ReverseGeocodeInputSerializer,
        "responses": {200: OpenApiExample('Kết quả', value={"display_name": "Địa chỉ mẫu", "address": {"city": "Đà Nẵng"}})},
        "examples": [
            OpenApiExample(
                'Tìm địa chỉ từ tọa độ mẫu',
                value={"lat": "16.05", "lon": "108.2"},
                request_only=True,
            ),
        ],
    }

def get_huyen_schema():
    return {
        "description": "Lấy mã huyện từ tọa độ với mapping thông minh cho vùng Đà Nẵng - Quảng Nam",
        "request": GetHuyenInputSerializer,
        "responses": {
            200: {
                "type": "object",
                "properties": {
                    "mahuyen": {"type": "integer", "example": 2},
                    "tenhuyen": {"type": "string", "example": "Đà Nẵng"},
                    "matched_field": {"type": "string", "example": "da nang"},
                    "matched_keyword": {"type": "string", "example": "da nang"}
                }
            }
        },
        "examples": [
            OpenApiExample(
                'Lấy huyện từ tọa độ mẫu',
                value={"lat": "16.05", "lon": "108.2"},
                request_only=True,
            ),
            OpenApiExample(
                'Kết quả Đà Nẵng',
                value={
                    "mahuyen": 2,
                    "tenhuyen": "Đà Nẵng",
                    "matched_field": "da nang",
                    "matched_keyword": "da nang"
                },
                response_only=True,
            ),
        ],
    }

from rest_framework import serializers

class LogoutInputSerializer(serializers.Serializer):
    refresh = serializers.CharField(help_text="Refresh token cần thu hồi")

class SearchAddressInputSerializer(serializers.Serializer):
    query = serializers.CharField(help_text="Địa chỉ cần tìm kiếm")

class ReverseGeocodeInputSerializer(serializers.Serializer):
    lat = serializers.CharField(help_text="Vĩ độ")
    lon = serializers.CharField(help_text="Kinh độ")

# ShiftViewSet schemas
def create_shift_schema():
    return {
        "description": "Tạo ca làm việc mới. Cần nhập giờ xuất phát, ngày xuất phát và huyện xuất phát.",
        "request": CaCreateUpdateSerializer,        "responses": {
            201: {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "Tạo ca thành công"},
                    "maca": {"type": "integer", "example": 123},
                    "data": {
                        "type": "object",
                        "properties": {
                            "maca": {"type": "integer", "example": 123},
                            "gioxuatphat": {"type": "string", "format": "time", "example": "06:00:00"},
                            "ngayxuatphat": {"type": "string", "format": "date", "example": "2025-06-20"},
                            "mahuyenxuatphat": {
                                "type": "object",
                                "properties": {
                                    "mahuyen": {"type": "integer", "example": 2},
                                    "tenhuyen": {"type": "string", "example": "Đà Nẵng"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "examples": [
            OpenApiExample(
                name='Ca Đà Nẵng',
                summary='Tạo ca tại Đà Nẵng',
                description='Ca làm việc xuất phát từ Đà Nẵng',
                value={
                    "gioxuatphat": "06:00:00",
                    "ngayxuatphat": "2025-06-20",
                    "mahuyenxuatphat_id": 2
                },
                request_only=True,
            ),
            OpenApiExample(
                name='Ca Tam Kỳ',
                summary='Tạo ca tại Tam Kỳ',
                description='Ca làm việc xuất phát từ Tam Kỳ',
                value={
                    "gioxuatphat": "07:00:00",
                    "ngayxuatphat": "2025-06-21",
                    "mahuyenxuatphat_id": 1
                },
                request_only=True,
            ),
            OpenApiExample(
                name='Response thành công',
                summary='Kết quả tạo ca thành công',
                description='Response trả về khi tạo ca thành công',
                value={
                    "message": "Tạo ca thành công",
                    "maca": 123,
                    "data": {
                        "maca": 123,
                        "gioxuatphat": "06:00:00",
                        "ngayxuatphat": "2025-06-20",
                        "mahuyenxuatphat": {
                            "mahuyen": 2,
                            "tenhuyen": "Đà Nẵng"
                        }
                    }
                },
                response_only=True,
            ),
        ],
    }

def list_shifts_schema():
    return {
        "description": "Lấy danh sách tất cả ca làm việc",
        "responses": {
            200: {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "maca": {"type": "integer", "example": 123},
                        "gioxuatphat": {"type": "string", "format": "time", "example": "06:00:00"},
                        "ngayxuatphat": {"type": "string", "format": "date", "example": "2025-06-20"},
                        "mahuyenxuatphat": {
                            "type": "object",
                            "properties": {
                                "mahuyen": {"type": "integer", "example": 2},
                                "tenhuyen": {"type": "string", "example": "Đà Nẵng"}
                            }
                        }
                    }
                }
            }
        },
    }

def update_shift_schema():
    return {
        "description": "Cập nhật thông tin ca làm việc",
        "request": CaCreateUpdateSerializer,
        "responses": {
            200: {
                "type": "object",
                "properties": {
                    "maca": {"type": "integer", "example": 123},
                    "gioxuatphat": {"type": "string", "format": "time", "example": "06:00:00"},
                    "ngayxuatphat": {"type": "string", "format": "date", "example": "2025-06-20"},
                    "mahuyenxuatphat": {
                        "type": "object",
                        "properties": {
                            "mahuyen": {"type": "integer", "example": 2},
                            "tenhuyen": {"type": "string", "example": "Đà Nẵng"}
                        }
                    }
                }
            }
        },
    }

def delete_shift_schema():
    return {
        "description": "Xóa ca làm việc",
        "responses": {204: {"description": "Xóa thành công"}},
    }

def create_shift_detail_schema():
    return {
        "description": "Tạo chi tiết ca (gán tài xế và xe vào ca)",
        "request": CreateShiftDetailSerializer,
        "responses": {
            201: {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "Tạo chi tiết ca thành công"},
                    "data": {
                        "type": "object",
                        "properties": {
                            "machitietca": {"type": "integer", "example": 123},
                            "maca": {
                                "type": "object",
                                "properties": {
                                    "maca": {"type": "integer", "example": 1},
                                    "gioxuatphat": {"type": "string", "format": "time", "example": "06:00:00"},
                                    "ngayxuatphat": {"type": "string", "format": "date", "example": "2025-06-20"}
                                }
                            },
                            "maxe": {
                                "type": "object",
                                "properties": {
                                    "maxe": {"type": "integer", "example": 1},
                                    "biensoxe": {"type": "string", "example": "43A-12345"},
                                    "loaixe": {"type": "string", "example": "Sedan 4 chỗ"},
                                    "sochongoi": {"type": "integer", "example": 4}
                                }
                            },
                            "mataixe": {
                                "type": "object",
                                "properties": {
                                    "mataixe": {"type": "integer", "example": 3},
                                    "hoten": {"type": "string", "example": "Nguyễn Văn Hùng"},
                                    "sodienthoai": {"type": "string", "example": "0977000001"},
                                    "cccd": {"type": "string", "example": "123456789012"},
                                    "trangthai": {"type": "integer", "example": 1}
                                }
                            }
                        }
                    }
                }
            },
            400: {
                "type": "object", 
                "properties": {
                    "error": {"type": "string", "example": "Cần cung cấp cả maxe và mataixe"}
                }
            }
        },
        "examples": [
            OpenApiExample(
                name='Gán tài xế và xe vào ca',
                summary='Thêm tài xế và xe vào ca làm việc',
                description='Gán tài xế Nguyễn Văn Hùng và xe 43A-12345 vào ca',
                value={
                    "maxe": 1,
                    "mataixe": 3
                },
                request_only=True,
            ),
        ],
    }
