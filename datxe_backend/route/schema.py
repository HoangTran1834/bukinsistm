from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .serializers import (
    GetPriceInputSerializer, TuyenduongSerializer, GetTuyenDuongInputSerializer,
    GetTuyenDuongByCoordinatesInputSerializer, GetHuyenInputSerializer
)

"""
Schema definitions for Route-related API endpoints.
"""

# Some additional serializers needed for route schemas
from rest_framework import serializers

class SearchAddressInputSerializer(serializers.Serializer):
    query = serializers.CharField(help_text="Địa chỉ cần tìm kiếm")

class ReverseGeocodeInputSerializer(serializers.Serializer):
    lat = serializers.CharField(help_text="Vĩ độ")
    lon = serializers.CharField(help_text="Kinh độ")

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

def get_direction_schema():
    return {
        "description": "Tính hướng di chuyển giữa hai địa điểm (theo địa chỉ hoặc mã địa điểm). Hiện tại trả về mặc định 1 (Đà Nẵng đi Tam Kỳ).",
        "request": "GetDirectionInputSerializer",
        "responses": {200: OpenApiExample('Kết quả', value={"huong": 1})},
        "examples": [
            OpenApiExample(
                'Tính hướng mẫu',
                value={"diemdon": 1, "diemtra": 2},
                request_only=True,
            ),
        ],
    }

def assign_driver_for_shift_schema():
    return {
        "description": "Phân bổ tài xế cho ca. API sẽ tự động lấy danh sách đặt xe + chi tiết đặt xe có mã ca trùng, tính toán số ghế và phân bổ hành khách cho các tài xế theo capacity xe một cách tối ưu.",
        "request": "AssignDriverInputSerializer",
        "responses": {
            200: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                    "ca_id": {"type": "integer"},
                    "total_passengers": {"type": "integer"},
                    "total_seats_needed": {"type": "integer"},
                    "total_capacity": {"type": "integer"},
                    "assignments": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "object",
                            "properties": {
                                "machitietca": {"type": "integer"},
                                "mataixe": {"type": "integer"},
                                "tentaixe": {"type": "string"},
                                "maxe": {"type": "integer"},
                                "biensoxe": {"type": "string"},
                                "capacity": {"type": "integer"},
                                "seats_used": {"type": "integer"},
                                "seats_available": {"type": "integer"},
                                "passengers": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "type": {"type": "string"},
                                            "ten": {"type": "string"},
                                            "sdt": {"type": "string"},
                                            "soghe": {"type": "integer"},
                                            "diemdon": {"type": "string"},
                                            "diemtra": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "examples": [
            OpenApiExample(
                'Phân bổ tài xế mẫu',
                value={"ca_id": 1},
                request_only=True,
            ),
            OpenApiExample(
                'Kết quả phân bổ',
                value={
                    "success": True,
                    "message": "Đã phân bổ 5 hành khách cho 2 tài xế",
                    "ca_id": 1,
                    "total_passengers": 5,
                    "total_seats_needed": 8,
                    "total_capacity": 32,
                    "assignments": {
                        "chitietca_1": {
                            "machitietca": 1,
                            "mataixe": 2,
                            "tentaixe": "Nguyen Van A",
                            "maxe": 1,
                            "biensoxe": "43A-12345",
                            "capacity": 16,
                            "seats_used": 5,
                            "seats_available": 11,
                            "passengers": [
                                {
                                    "type": "datxe",
                                    "ten": "Tran Van B",
                                    "sdt": "0987654321",
                                    "soghe": 2,
                                    "diemdon": "Bến xe Tam Kỳ",
                                    "diemtra": "Bến xe Đà Nẵng"
                                }
                            ]
                        }
                    }
                },
                response_only=True,
            )
        ],
    }