from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .serializers import (
    UpdateChitietdatxeSerializer, CreateBookingSerializer, CreateStaffBookingSerializer,
    CheckSlotInputSerializer, CreateDiadiemSerializer, DiadiemSerializer, 
    GetCaByDateInputSerializer, CaSerializer
)

"""
Schema definitions for Booking-related API endpoints.
"""

def create_booking_schema():
    return {
        "description": "Tạo mới một booking (đặt xe). Bắt buộc nhập mã ca để xác định giờ xuất phát và hướng di chuyển. Tuyến đường sẽ được tự động tìm từ điểm đi và điểm đến.",
        "request": CreateBookingSerializer,
        "responses": {201: "BookingSerializer"},
        "examples": [                  
            OpenApiExample(                
                'Đặt xe mẫu',                
                value={
                    "maca": 1,  # mã ca (bắt buộc) - xác định giờ xuất phát và hướng
                    "diemdon": 1,
                    "diemtra": 2,
                    "soghe": 4,
                    "ghichu": "Booking cho nhóm gia đình",
                    "chitietdatxe": [
                        {
                            "tenkhach": "Nguyen Van B", 
                            "sodienthoaikhach": "0987654321",
                            "diemdon": 1,
                            "diemtra": 2,
                            "soghe": 1,
                            "ghichu": "Ghi chú cho hành khách"
                        }
                    ]
                },
                request_only=True,
            ),
        ],
    }

def create_staff_booking_schema():
    return {
        "description": "Nhân viên tạo booking cho khách hàng. Cần cung cấp mã khách hàng và mã nhân viên (tùy chọn).",
        "request": CreateStaffBookingSerializer,
        "responses": {201: "BookingSerializer"},
        "examples": [
            OpenApiExample(
                'Staff đặt xe mẫu',
                value={
                    "maca": 1,
                    "diemdon": 1,
                    "diemtra": 2,
                    "soghe": 4,
                    "ghichu": "Booking do nhân viên tạo cho khách",
                    "ma_khach": 3,  # Mã khách hàng
                    "ma_nhanvien": 2,  # Mã nhân viên (tùy chọn)
                    "chitietdatxe": [
                        {
                            "tenkhach": "Nguyen Van B", 
                            "sodienthoaikhach": "0987654321",
                            "diemdon": 1,
                            "diemtra": 2,
                            "soghe": 1,
                            "ghichu": "Chi tiết được nhân viên tạo"
                        }
                    ]
                },
                request_only=True,
            ),
        ],
    }

def check_slot_schema():
    return {
        "description": "Kiểm tra số chỗ còn lại trong một chi tiết ca theo hướng và thời gian. Trả về tổng số chỗ, số khách đã đặt, số chỗ còn lại.",
        "request": CheckSlotInputSerializer,
        "responses": {200: OpenApiExample('Kết quả', value={"sochongoi": 16, "sokhach": 10, "conlai": 6})},
        "examples": [
            OpenApiExample(
                'Check slot mẫu',
                value={"machitietca": 1, "huong": 1},
                request_only=True,
            ),
        ],
    }

def create_location_schema():
    return {
        "description": "Tạo địa điểm mới với tên và tọa độ lat/lon",
        "request": CreateDiadiemSerializer,
        "responses": {
            201: {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "Tạo địa điểm thành công"},
                    "madiadiem": {"type": "integer", "example": 123},
                    "data": {
                        "type": "object",
                        "properties": {
                            "madiadiem": {"type": "integer", "example": 123},
                            "tendiadiem": {"type": "string", "example": "Bến xe Đà Nẵng"},
                            "vido": {"type": "integer", "example": 16050000},
                            "kinhdo": {"type": "integer", "example": 108200000}
                        }
                    }
                }
            }
        },
        "examples": [
            OpenApiExample(
                'Tạo địa điểm mẫu',
                value={
                    "tendiadiem": "Bến xe Đà Nẵng",
                    "lat": 16.05,
                    "lon": 108.2
                },
                request_only=True,
            ),
        ],
    }

def get_locations_schema():
    return {
        "description": "Lấy danh sách tất cả địa điểm có sẵn",
        "responses": {200: DiadiemSerializer(many=True)},
        "examples": [
            OpenApiExample(
                'Danh sách địa điểm',
                value=[
                    {
                        "madiadiem": 1,
                        "tendiadiem": "Bến xe Đà Nẵng",
                        "vido": 16.0544,
                        "kinhdo": 108.2022
                    },
                    {
                        "madiadiem": 2,
                        "tendiadiem": "Bến xe Tam Kỳ",
                        "vido": 15.5700,
                        "kinhdo": 108.4800
                    }
                ],
                response_only=True,
            ),
        ],
    }

def get_ca_by_date_schema():
    return {
        "description": "Lấy danh sách ca theo ngày. Có thể lọc theo huyện xuất phát.",
        "request": GetCaByDateInputSerializer,
        "responses": {200: CaSerializer(many=True)},
        "examples": [
            OpenApiExample(
                'Lấy ca theo ngày mẫu',
                value={
                    "ngay": "2025-06-20",
                    "huyen_xuatphat": 1
                },
                request_only=True,
            ),
            OpenApiExample(
                'Kết quả ca theo ngày',
                value=[
                    {
                        "maca": 1,
                        "gioxuatphat": "08:00:00",
                        "ngayxuatphat": "2025-06-20",
                        "mahuyenxuatphat": {
                            "mahuyen": 1,
                            "tenhuyen": "Tam Kỳ"
                        }
                    }
                ],
                response_only=True,
            )
        ],
    }

def update_chitietdatxe_schema():
    """Schema cho API cập nhật chi tiết đặt xe"""
    return {
        "description": "Cập nhật thông tin chi tiết đặt xe (hành khách). Chỉ được phép sửa thông tin khách hàng, điểm đón/trả, số ghế và ghi chú. Không được sửa mã đặt xe, mã chi tiết ca, tuyến đường hay trạng thái.",
        "request": {
            "type": "object",
            "properties": {
                "tenkhach": {"type": "string", "example": "Nguyen Van B", "description": "Tên khách hàng"},
                "sodienthoaikhach": {"type": "string", "example": "0987654321", "description": "Số điện thoại khách hàng"},
                "diemdon": {"type": "integer", "example": 1, "description": "Mã địa điểm đón"},
                "diemtra": {"type": "integer", "example": 2, "description": "Mã địa điểm trả"},
                "soghe": {"type": "integer", "example": 2, "description": "Số ghế đặt"},
                "ghichu": {"type": "string", "example": "Cập nhật ghi chú", "description": "Ghi chú thêm"}
            }
        },
        "responses": {
            200: {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "Cập nhật chi tiết đặt xe thành công"},
                    "data": {
                        "type": "object",
                        "properties": {
                            "machitiet": {"type": "integer", "example": 123},
                            "tenkhach": {"type": "string", "example": "Nguyen Van B"},
                            "sodienthoaikhach": {"type": "string", "example": "0987654321"},
                            "diemdon": {"type": "integer", "example": 1},
                            "diemtra": {"type": "integer", "example": 2},
                            "soghe": {"type": "integer", "example": 2},
                            "ghichu": {"type": "string", "example": "Cập nhật ghi chú"}
                        }
                    }
                }
            },
            404: {"description": "Không tìm thấy chi tiết đặt xe"},
            400: {"description": "Dữ liệu đầu vào không hợp lệ"}
        },
        "examples": [
            OpenApiExample(
                name='Cập nhật chi tiết đặt xe',
                summary='Sửa thông tin hành khách trong booking',
                description='Cập nhật thông tin khách hàng, điểm đón/trả, số ghế, ghi chú',
                value={
                    "tenkhach": "Nguyen Van B Updated",
                    "sodienthoaikhach": "0987654322",
                    "diemdon": 1,
                    "diemtra": 2,
                    "soghe": 3,
                    "ghichu": "Đã cập nhật thông tin khách hàng"
                },
                request_only=True,
            ),
        ],
    }