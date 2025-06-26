from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .serializers import (
    CaCreateUpdateSerializer, CreateShiftDetailSerializer, CheckSlotInputSerializer,
    GetCaByDateInputSerializer, AssignDriverInputSerializer
)

"""
Schema definitions for Shift-related API endpoints.
"""

def create_shift_schema():
    return {
        "description": "Tạo ca làm việc mới. Cần nhập giờ xuất phát, ngày xuất phát và huyện xuất phát.",
        "request": CaCreateUpdateSerializer,
        "responses": {
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
        "description": "Quản lý chi tiết ca (gán tài xế và xe vào ca). Hỗ trợ POST (tạo), GET (xem danh sách), DELETE (xóa chi tiết ca).",
        "request": CreateShiftDetailSerializer,
        "responses": {
            200: {
                "description": "GET - Danh sách chi tiết ca với thông tin đầy đủ về xe và tài xế",
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "Tìm thấy 2 chi tiết ca"},
                    "ca_info": {
                        "type": "object",
                        "properties": {
                            "maca": {"type": "integer", "example": 1},
                            "gioxuatphat": {"type": "string", "example": "06:00:00"},
                            "ngayxuatphat": {"type": "string", "example": "2025-06-20"},
                            "huyen_xuat_phat": {"type": "integer", "example": 1}
                        }
                    },
                    "data": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "machitietca": {"type": "integer", "example": 123},
                                "maca": {"type": "integer", "example": 1},
                                "xe_info": {
                                    "type": "object",
                                    "properties": {
                                        "maxe": {"type": "integer", "example": 1},
                                        "biensoxe": {"type": "string", "example": "43A-12345"},
                                        "loaixe": {"type": "string", "example": "Sedan 4 chỗ"},
                                        "sochongoi": {"type": "integer", "example": 4},
                                        "bienso_color": {"type": "string", "example": "white"}
                                    }
                                },
                                "taixe_info": {
                                    "type": "object",
                                    "properties": {
                                        "mataixe": {"type": "integer", "example": 3},
                                        "hoten": {"type": "string", "example": "Nguyễn Văn Hùng"},
                                        "sodienthoai": {"type": "string", "example": "0977000001"},
                                        "email": {"type": "string", "example": "hung@gmail.com"},
                                        "cccd": {"type": "string", "example": "123456789012"},
                                        "gplx": {"type": "string", "example": "B2-987654321"},
                                        "trangthai": {"type": "boolean", "example": True}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            201: {
                "description": "POST - Tạo chi tiết ca thành công",
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "Tạo chi tiết ca thành công"},
                    "data": {
                        "type": "object",
                        "properties": {
                            "machitietca": {"type": "integer", "example": 123},
                            "maca": {"type": "integer", "example": 1},
                            "xe_info": {
                                "type": "object",
                                "properties": {
                                    "maxe": {"type": "integer", "example": 1},
                                    "biensoxe": {"type": "string", "example": "43A-12345"},
                                    "loaixe": {"type": "string", "example": "Sedan 4 chỗ"},
                                    "sochongoi": {"type": "integer", "example": 4}
                                }
                            },
                            "taixe_info": {
                                "type": "object",
                                "properties": {
                                    "mataixe": {"type": "integer", "example": 3},
                                    "hoten": {"type": "string", "example": "Nguyễn Văn Hùng"},
                                    "sodienthoai": {"type": "string", "example": "0977000001"},
                                    "cccd": {"type": "string", "example": "123456789012"},
                                    "gplx": {"type": "string", "example": "B2-987654321"},
                                    "trangthai": {"type": "boolean", "example": True}
                                }
                            }
                        }
                    }
                }
            }
        },
        "examples": [
            OpenApiExample(
                name='Tạo chi tiết ca (POST)',
                summary='Gán tài xế và xe vào ca',
                description='Tạo chi tiết ca mới bằng cách gán tài xế và xe vào ca',
                value={"maxe": 1, "mataixe": 3},
                request_only=True,
            ),
            OpenApiExample(
                name='Xóa chi tiết ca (DELETE)',
                summary='Xóa chi tiết ca khỏi ca',
                description='Xóa chi tiết ca (cần cung cấp chitietca_id)',
                value={"chitietca_id": 123},
                request_only=True,
            ),
        ],
    }