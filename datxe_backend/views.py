from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError, AccessToken
from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import NguoiDung, Datxe, Chitietdatxe, Danhgia, Nhanvien, Tuyenduong, Ca, Chitietca, Taixe, Xe, Diadiem
from .serializers import UserSerializer, SignupSerializer, LoginSerializer, BookingSerializer, CreateBookingSerializer, BookingDetailSerializer, CheckSlotInputSerializer, GetDirectionInputSerializer, GetDistrictInputSerializer, GetPriceInputSerializer, TuyenduongSerializer, HuyenSerializer, CaSerializer, CaCreateUpdateSerializer, ChitietcaSerializer, TaixeSerializer, XeSerializer, CreateShiftDetailSerializer, DiadiemSerializer, CreateDiadiemSerializer, GetHuyenInputSerializer, GetHuyenOutputSerializer, GetTuyenDuongInputSerializer, GetTuyenDuongByCoordinatesInputSerializer, GetCaByDateInputSerializer, AssignDriverInputSerializer
from .models_access_blacklist import BlacklistedAccessToken
from .schemas import (
    signup_schema, login_schema, logout_schema, list_routes_schema, create_route_schema,
    update_route_schema, delete_route_schema, get_price_schema, get_tuyen_duong_by_address_schema,
    get_tuyen_duong_by_coordinates_schema, search_address_schema, reverse_geocode_schema,
    get_huyen_schema, create_shift_schema, list_shifts_schema, update_shift_schema, delete_shift_schema,
    create_shift_detail_schema, LogoutInputSerializer, SearchAddressInputSerializer, ReverseGeocodeInputSerializer
)
import requests
import urllib.parse

"""
API ViewSets cho hệ thống đặt xe taxi:
- AuthViewSet: Đăng ký, đăng nhập, đăng xuất, sử dụng JWT, có ví dụ mẫu cho Swagger UI.
- UserViewSet: Xem/sửa thông tin tài khoản, cho phép tất cả user xem thông tin nhau, chỉ cho phép tự sửa thông tin cá nhân.
- ShiftViewSet: Quản lý ca tài xế, chỉ nhân viên/admin được chỉnh sửa, tài xế/nhân viên được xem.
- BookingViewSet: Đặt xe, xem danh sách booking, trả về đầy đủ chi tiết liên quan, hỗ trợ đặt nhiều khách/lượt.

Các API đều có mô tả chi tiết, ví dụ mẫu, hỗ trợ tốt cho thử nghiệm trên Swagger UI (drf-spectacular).
"""

"""
Các serializer này đã di chuyển sang schemas.py.
Bây giờ được import vào từ module schemas.
"""

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    @extend_schema(**signup_schema())
    @action(detail=False, methods=['post'], url_path='signup')
    def signup(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Đăng ký thành công'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
    
    @extend_schema(**login_schema())
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response({
            "error": "Thông tin đăng nhập không hợp lệ",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    @extend_schema(**logout_schema())
    @action(detail=False, methods=['post'], url_path='logout', permission_classes=[IsAuthenticated])
    def logout(self, request):
        refresh_token = request.data.get("refresh")
        # Blacklist access token
        access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if access_token:
            try:
                token = AccessToken(access_token)
                jti = token['jti']
                BlacklistedAccessToken.objects.get_or_create(jti=jti)
            except Exception:
                pass
        if not refresh_token:
            return Response({"error": "Thiếu refresh token."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Đăng xuất thành công."}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({"error": "Token không hợp lệ hoặc đã bị thu hồi."}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Đặt lại mật khẩu cho tài khoản đang đăng nhập. Chỉ cần nhập mật khẩu mới, không cần nhập số điện thoại.",
        request={
            "type": "object",
            "properties": {
                "new_password": {"type": "string", "description": "Mật khẩu mới"}
            },
            "required": ["new_password"]
        },
        responses={200: OpenApiExample('Thành công', value={"message": "Đặt lại mật khẩu thành công"}), 404: OpenApiExample('Không tìm thấy', value={"error": "Không tìm thấy tài khoản với số điện thoại này."})},
        examples=[
            OpenApiExample(
                'Reset mật khẩu mẫu',
                value={"new_password": "matkhaumoi123"},
                request_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['post'], url_path='reset_pw', permission_classes=[IsAuthenticated])
    def reset_pw(self, request):
        new_password = request.data.get('new_password')
        user = request.user
        user.set_password(new_password)
        user.save()
        return Response({"message": "Đặt lại mật khẩu thành công"})

class UserViewSet(viewsets.ModelViewSet):
    queryset = NguoiDung.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Cho phép tất cả user xem thông tin tài khoản của nhau
        return NguoiDung.objects.all()

    @extend_schema(
        description="Lấy thông tin tài khoản của user hiện tại.",
        responses={200: UserSerializer},
    )
    @action(detail=False, methods=['get'], url_path='profile')
    def profile(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        description="Lấy danh sách tất cả user (ẩn trường nhạy cảm như mật khẩu, email của người khác).",
        responses={200: UserSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Danh sách user mẫu',
                value=[
                    {"maNguoiDung": 1, "hoTen": "Nguyen Van A", "sodienthoai": "0123456789", "vaitro": "Hành khách"},
                    {"maNguoiDung": 2, "hoTen": "Tran Thi B", "sodienthoai": "0987654321", "vaitro": "Tài xế"}
                ],
                response_only=True,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []
        for user in queryset:
            item = self.get_serializer(user).data
            if request.user.pk != user.pk:
                item.pop('password', None)
                item.pop('matkhau', None)
                item.pop('email', None)
            else:
                item.pop('password', None)
                item.pop('matkhau', None)
            data.append(item)
        return Response(data)

    @extend_schema(
        description="Lấy thông tin chi tiết một user theo id (ẩn trường nhạy cảm nếu không phải chính mình).",
        responses={200: UserSerializer},
        examples=[
            OpenApiExample(
                'User mẫu',
                value={"maNguoiDung": 1, "hoTen": "Nguyen Van A", "sodienthoai": "0123456789", "vaitro": "Hành khách"},
                response_only=True,
            ),
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.get_serializer(instance).data
        if request.user.pk != instance.pk:
            data.pop('password', None)
            data.pop('matkhau', None)
            data.pop('email', None)
        else:
            data.pop('password', None)
            data.pop('matkhau', None)
        return Response(data)

    def update(self, request, *args, **kwargs):
        # Chỉ cho phép update user hiện tại
        instance = self.get_object()
        if request.user.pk != instance.pk:
            return Response({'detail': 'Bạn chỉ được phép sửa thông tin của chính mình.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        data = serializer.data
        data.pop('password', None)
        data.pop('matkhau', None)
        return Response(data)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

class IsNhanVien(BasePermission):
    def has_permission(self, request, view):
        # Admin (vaiTro=0) hoặc Nhân viên (vaiTro=2) đều có quyền
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'vaitro', None) in [0, 2])

class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Ca.objects.all()
    serializer_class = CaSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        # Sử dụng serializer khác nhau cho create/update vs list/retrieve
        if self.action in ['create', 'update', 'partial_update']:
            return CaCreateUpdateSerializer
        return CaSerializer

    def get_queryset(self):
        # Tất cả user đã đăng nhập đều được xem        
        return super().get_queryset()
    
    @extend_schema(**create_shift_schema())
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ca_instance = serializer.save()
        
        # Sử dụng CaSerializer để trả về đầy đủ thông tin
        response_serializer = CaSerializer(ca_instance)
        return Response({
            "message": "Tạo ca thành công",
            "maca": ca_instance.maca,
            "data": response_serializer.data
        }, status=status.HTTP_201_CREATED)

    @extend_schema(**list_shifts_schema())
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(**update_shift_schema())
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(**update_shift_schema())
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)    
    
    @extend_schema(**delete_shift_schema())
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='taixe')
    def get_drivers(self, request):
        """Lấy danh sách tài xế"""
        drivers = Taixe.objects.all()
        serializer = TaixeSerializer(drivers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='xe')
    def get_vehicles(self, request):
        """Lấy danh sách xe"""
        vehicles = Xe.objects.all()
        serializer = XeSerializer(vehicles, many=True)
        return Response(serializer.data)    
    
    @extend_schema(**create_shift_detail_schema())
    @action(detail=True, methods=['post'], url_path='chitiet')
    def create_shift_detail(self, request, pk=None):
        """Tạo chi tiết ca (gán tài xế và xe vào ca)"""
        ca = self.get_object()
        
        maca = ca.maca
        maxe = request.data.get('maxe')
        mataixe = request.data.get('mataixe')
        
        if not maxe or not mataixe:
            return Response({
                'error': 'Cần cung cấp cả maxe và mataixe'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Kiểm tra xe và tài xế có tồn tại không
        try:
            xe = Xe.objects.get(maxe=maxe)
            taixe = Taixe.objects.get(mataixe=mataixe)
        except Xe.DoesNotExist:
            return Response({'error': 'Xe không tồn tại'}, status=status.HTTP_400_BAD_REQUEST)
        except Taixe.DoesNotExist:
            return Response({'error': 'Tài xế không tồn tại'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Tạo chi tiết ca
        chitiet_ca = Chitietca.objects.create(
            maca=ca,
            maxe=xe,
            mataixe=taixe
        )
        
        serializer = ChitietcaSerializer(chitiet_ca)
        return Response({
            'message': 'Tạo chi tiết ca thành công',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Datxe.objects.all()
    serializer_class = BookingSerializer

    def get_queryset(self):
        user = self.request.user
        # Nếu là tài xế (vaiTro=1) chỉ xem các booking có chi tiết ca tài xế thuộc về mình
        if getattr(user, 'vaitro', None) == 1:
            return Datxe.objects.filter(machitietca__mataixe=user.pk).distinct()
        # Nếu là admin hoặc nhân viên thì xem tất cả
        if getattr(user, 'vaitro', None) in [0, 2]:
            return super().get_queryset()
        # Hành khách chỉ xem booking của mình        
        return Datxe.objects.filter(manguoidung_id=user.pk)

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateBookingSerializer
        return BookingSerializer      @extend_schema(
        description="Tạo mới một booking (đặt xe). Bắt buộc nhập mã ca để xác định giờ xuất phát và hướng di chuyển. Tuyến đường sẽ được tự động tìm từ điểm đi và điểm đến. SAU KHI TẠO BOOKING THÀNH CÔNG, HỆ THỐNG SẼ TỰ ĐỘNG GỌI assign_driver_for_shift ĐỂ PHÂN BỔ LẠI TOÀN BỘ CA MỘT CÁCH TỐI ƯU.",
        request=CreateBookingSerializer,
        responses={201: BookingSerializer},
        examples=[                  OpenApiExample(                
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
            ),        ],
    )
    def create(self, request, *args, **kwargs):
        # Logic tạo booking và tìm tuyến đường đã được chuyển vào CreateBookingSerializer
        # CreateBookingSerializer.create() cũng sẽ tự động gọi assign_driver_for_shift
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        
        # Trả về response với BookingSerializer để hiển thị đầy đủ thông tin
        response_serializer = BookingSerializer(booking)
        response_data = response_serializer.data
        
        # Thêm thông tin về auto-assign
        response_data['auto_assign_info'] = {
            'message': 'Hệ thống đã tự động phân bổ lại toàn bộ ca sau khi tạo booking',
            'ca_id': booking.maca.maca,
            'note': 'Kiểm tra log để xem chi tiết quá trình auto-assign'
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description="Tự động xếp hành khách vào chi tiết ca còn chỗ. Chỉ cần cung cấp thông tin khách, hướng, thời gian mong muốn. API sẽ tự xếp vào chi tiết ca còn chỗ đầu tiên.",
        request={
            "type": "object",
            "properties": {
                "tenkhach": {"type": "string"},
                "sodienthoaikhach": {"type": "string"},
                "huong": {"type": "integer", "description": "1: Đà Nẵng đi Tam Kỳ, 2: Tam Kỳ đi Đà Nẵng"},
                "thoigian": {"type": "string", "format": "date-time"}
            },
            "required": ["tenkhach", "sodienthoaikhach", "huong", "thoigian"]
        },
        responses={201: BookingSerializer},
        examples=[
            OpenApiExample(
                'Tự động xếp mẫu',
                value={"tenkhach": "Nguyen Van C", "sodienthoaikhach": "0912345678", "huong": 1, "thoigian": "2025-06-16T08:00:00"},
                request_only=True,
            ),        ],
    )
    
    @extend_schema(
        description="Kiểm tra số chỗ còn trống theo ca (khuyến nghị) hoặc chi tiết ca. API trả về thông tin rõ ràng để frontend dễ xử lý: can_book (có thể đặt), slots_available (số chỗ trống), slots_needed (số chỗ cần).",
        request=OpenApiTypes.OBJECT,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "can_book": {"type": "boolean", "example": True, "description": "Có thể đặt booking không"},
                    "slots_available": {"type": "integer", "example": 15, "description": "Số chỗ trống"},
                    "slots_needed": {"type": "integer", "example": 2, "description": "Số chỗ cần"},
                    "message": {"type": "string", "example": "Ca có 15 chỗ trống, đủ cho 2 ghế cần thiết"}
                }
            }
        },
        examples=[
            OpenApiExample(
                'Kiểm tra slot theo ca (khuyến nghị)',
                summary='Kiểm tra toàn bộ ca',
                description='Sử dụng ca_id để kiểm tra tổng số chỗ trống trong tất cả xe của ca',
                value={"ca_id": 1, "soghe_can": 2},
                request_only=True,
            ),
            OpenApiExample(
                'Kiểm tra slot theo xe cụ thể',
                summary='Kiểm tra xe cụ thể (tương thích API cũ)',
                description='Sử dụng machitietca để kiểm tra chỗ trống của xe cụ thể',
                value={"machitietca": 1, "soghe_can": 1},
                request_only=True,
            ),
        ],
    )
    
    @action(detail=False, methods=['post'], url_path='check_slot', permission_classes=[IsAuthenticated])
    def check_slot(self, request):
        """
        Kiểm tra số ghế còn trống theo ca (ưu tiên) hoặc chi tiết ca.
        Input:
        - ca_id: Kiểm tra toàn bộ ca (khuyến nghị cho frontend)
        - machitietca: Kiểm tra xe cụ thể (để tương thích với API cũ)
        - soghe_can: Số ghế cần kiểm tra (mặc định 1)
        
        Response rõ ràng cho frontend:
        - can_book: có thể đặt không
        - slots_available: số chỗ trống
        - slots_needed: số chỗ cần
        """
        try:
            ca_id = request.data.get('ca_id')
            machitietca = request.data.get('machitietca')
            soghe_can = request.data.get('soghe_can', 1)
            
            # Ưu tiên kiểm tra theo ca_id (cho frontend)
            if ca_id:
                return self._check_slot_by_ca(ca_id, soghe_can)
            elif machitietca:
                return self._check_slot_by_chitietca(machitietca, soghe_can)
            else:
                return Response({
                    "error": "Cần cung cấp ca_id (kiểm tra toàn ca) hoặc machitietca (kiểm tra xe cụ thể)",
                    "suggestion": "Khuyến nghị sử dụng ca_id để kiểm tra toàn bộ ca"
                }, status=400)
            
        except ValueError as e:
            return Response({"error": f"Dữ liệu đầu vào không hợp lệ: {str(e)}"}, status=400)
        except Exception as e:
            print(f"🎫 [CHECK_SLOT] Lỗi: {str(e)}")
            return Response({"error": f"Lỗi hệ thống: {str(e)}"}, status=500)
    
    def _check_slot_by_ca(self, ca_id, soghe_can):
        """Kiểm tra slot theo ca - logic chính cho frontend"""
        try:
            ca_id = int(ca_id)
            soghe_can = int(soghe_can)
            
            print(f"🎫 [CHECK_SLOT_CA] Kiểm tra slot cho ca {ca_id}, cần {soghe_can} ghế")
            
            # Lấy thông tin ca
            ca = Ca.objects.get(maca=ca_id)
            print(f"🎫 [CHECK_SLOT_CA] Ca: {ca.gioxuatphat} ngày {ca.ngayxuatphat}")
            
            # Lấy danh sách xe trong ca
            chitietca_list = list(Chitietca.objects.select_related('maxe', 'mataixe').filter(maca=ca_id))
            if not chitietca_list:
                return Response({
                    "success": False,
                    "can_book": False,
                    "error": "Không có xe nào trong ca này",
                    "ca_id": ca_id,
                    "slots_available": 0,
                    "slots_needed": soghe_can
                }, status=400)
            
            # Tính tổng capacity
            total_capacity = sum(cc.maxe.sochongoi for cc in chitietca_list)
            
            # Đếm ghế đã sử dụng trong ca
            datxe_list = list(Datxe.objects.filter(maca=ca_id))
            total_seats_datxe = sum(dx.soghe for dx in datxe_list)
            
            chitietdatxe_list = list(Chitietdatxe.objects.filter(madatxe__maca=ca_id))
            total_seats_chitiet = sum(
                getattr(ct, 'soghe', 0) or ct.madatxe.soghe 
                for ct in chitietdatxe_list
            )
            
            total_used = total_seats_datxe + total_seats_chitiet
            slots_available = total_capacity - total_used
            can_book = slots_available >= soghe_can
            
            print(f"🎫 [CHECK_SLOT_CA] Capacity: {total_capacity}, đã dùng: {total_used}, còn: {slots_available}")
            print(f"🎫 [CHECK_SLOT_CA] Cần {soghe_can} ghế → {'✅ CÓ THỂ ĐẶT' if can_book else '❌ KHÔNG ĐỦ CHỖ'}")
            
            # Chi tiết từng xe (cho debug)
            xe_details = []
            for cc in chitietca_list:
                xe_datxe = [dx for dx in datxe_list if dx.machitietca_id == cc.machitietca]
                xe_chitiet = [ct for ct in chitietdatxe_list if ct.machitietca_id == cc.machitietca]
                
                xe_used = sum(dx.soghe for dx in xe_datxe) + sum(getattr(ct, 'soghe', 0) or ct.madatxe.soghe for ct in xe_chitiet)
                xe_available = cc.maxe.sochongoi - xe_used
                
                xe_details.append({
                    "machitietca": cc.machitietca,
                    "bien_so": cc.maxe.biensoxe,
                    "tai_xe": cc.mataixe.mataixe.hoten,
                    "capacity": cc.maxe.sochongoi,
                    "used": xe_used,
                    "available": xe_available
                })
            
            return Response({
                "success": True,
                "can_book": can_book,
                "ca_id": ca_id,
                "slots_available": slots_available,
                "slots_needed": soghe_can,
                "slots_total": total_capacity,
                "slots_used": total_used,
                "message": f"Ca có {slots_available} chỗ trống, {'đủ' if can_book else 'không đủ'} cho {soghe_can} ghế cần thiết",
                "ca_info": {
                    "gio_xuat_phat": str(ca.gioxuatphat),
                    "ngay_xuat_phat": str(ca.ngayxuatphat),
                    "so_xe": len(chitietca_list)
                },
                "summary": {
                    "total_bookings": len(datxe_list),
                    "total_details": len(chitietdatxe_list),
                    "seats_from_bookings": total_seats_datxe,
                    "seats_from_details": total_seats_chitiet
                },
                "xe_details": xe_details
            })
            
        except Ca.DoesNotExist:
            return Response({
                "success": False,
                "can_book": False,
                "error": f"Không tìm thấy ca với ID {ca_id}",
                "ca_id": ca_id,
                "slots_available": 0,
                "slots_needed": soghe_can
            }, status=404)
    
    def _check_slot_by_chitietca(self, machitietca, soghe_can):
        """Kiểm tra slot theo chi tiết ca - để tương thích API cũ"""
        try:
            machitietca = int(machitietca)
            soghe_can = int(soghe_can)
            
            print(f"🎫 [CHECK_SLOT_XE] Kiểm tra slot cho xe {machitietca}, cần {soghe_can} ghế")
            
            # Lấy thông tin chi tiết ca
            chitietca = Chitietca.objects.get(machitietca=machitietca)
            xe = chitietca.maxe
            capacity = xe.sochongoi if xe else 0
            
            # Đếm ghế đã sử dụng
            datxe_list = Datxe.objects.filter(machitietca=machitietca)
            seats_datxe = sum(dx.soghe for dx in datxe_list)
            
            chitietdatxe_list = Chitietdatxe.objects.filter(machitietca=machitietca)
            seats_chitiet = sum(
                getattr(ct, 'soghe', 0) or ct.madatxe.soghe 
                for ct in chitietdatxe_list
            )
            
            total_used = seats_datxe + seats_chitiet
            slots_available = capacity - total_used
            can_book = slots_available >= soghe_can
            
            print(f"🎫 [CHECK_SLOT_XE] Xe {xe.biensoxe}: {slots_available}/{capacity} chỗ trống")
            
            return Response({
                "success": True,
                "can_book": can_book,
                "machitietca": machitietca,
                "slots_available": slots_available,
                "slots_needed": soghe_can,
                "slots_total": capacity,
                "slots_used": total_used,
                "message": f"Xe có {slots_available} chỗ trống, {'đủ' if can_book else 'không đủ'} cho {soghe_can} ghế cần thiết",
                "xe_info": {
                    "bien_so": xe.biensoxe if xe else None,
                    "tai_xe": chitietca.mataixe.mataixe.hoten,
                    "capacity": capacity
                },
                "detail": {
                    "bookings_count": len(datxe_list),
                    "details_count": len(chitietdatxe_list),
                    "seats_from_bookings": seats_datxe,
                    "seats_from_details": seats_chitiet
                }
            })
            
        except Chitietca.DoesNotExist:
            return Response({
                "success": False,
                "can_book": False,
                "error": f"Không tìm thấy chi tiết ca {machitietca}",
                "machitietca": machitietca,
                "slots_available": 0,
                "slots_needed": soghe_can
            }, status=404)

    @extend_schema(
        description="Tạo địa điểm mới với tên và tọa độ lat/lon",
        request=CreateDiadiemSerializer,
        responses={
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
        examples=[
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
    )
    @action(detail=False, methods=['post'], url_path='create_location')
    def create_location(self, request):
        """Tạo địa điểm mới"""
        serializer = CreateDiadiemSerializer(data=request.data)
        if serializer.is_valid():
            diadiem = serializer.save()
            result_serializer = DiadiemSerializer(diadiem)
            return Response({
                'message': 'Tạo địa điểm thành công',
                'madiadiem': diadiem.madiadiem,
                'data': result_serializer.data            
                }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Lấy danh sách tất cả địa điểm có sẵn",
        responses={200: DiadiemSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Danh sách địa điểm',
                value=[                    {
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
        ],    )
    @action(detail=False, methods=['get'], url_path='locations')
    def get_locations(self, request):
        """Lấy danh sách tất cả địa điểm"""
        locations = Diadiem.objects.all()
        serializer = DiadiemSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Lấy danh sách ca theo ngày. Có thể lọc theo huyện xuất phát.",
        request=GetCaByDateInputSerializer,
        responses={200: CaSerializer(many=True)},
        examples=[
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
    )
    @action(detail=False, methods=['post'], url_path='get_ca_by_date')
    def get_ca_by_date(self, request):
        """Lấy danh sách ca theo ngày"""
        serializer = GetCaByDateInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        ngay = serializer.validated_data['ngay']
        huyen_xuatphat = serializer.validated_data.get('huyen_xuatphat')
        
        print(f"🔍 [GET_CA] Tìm ca theo ngày: {ngay}")
        if huyen_xuatphat:
            print(f"🔍 [GET_CA] Lọc theo huyện xuất phát: {huyen_xuatphat}")
        
        # Query ca theo ngày
        queryset = Ca.objects.filter(ngayxuatphat=ngay)
        
        # Lọc theo huyện xuất phát nếu có
        if huyen_xuatphat:
            queryset = queryset.filter(mahuyenxuatphat=huyen_xuatphat)
        
        # Sắp xếp theo giờ xuất phát
        queryset = queryset.order_by('gioxuatphat')
        
        print(f"🔍 [GET_CA] Tìm thấy {queryset.count()} ca")
        
        ca_serializer = CaSerializer(queryset, many=True)
        return Response({
            'message': f'Tìm thấy {queryset.count()} ca trong ngày {ngay}',
            'ngay': ngay,
            'huyen_xuatphat': huyen_xuatphat,
            'data': ca_serializer.data
        }, status=status.HTTP_200_OK)

class RouteViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Lấy danh sách các tuyến đường (đã có mã tuyến đường). Chỉ admin mới xem được danh sách này.",
        responses={200: TuyenduongSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Tuyến đường mẫu',
                value=[{"matuyenduong": 1, "tentuyenduong": "Đà Nẵng - Tam Kỳ", "giatien": 30000}],
                response_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['get'], url_path='routes')
    def list_routes(self, request):
        if request.user.vaitro != 0:
            return Response({"error": "Chỉ admin mới có quyền truy cập."}, status=status.HTTP_403_FORBIDDEN)
        routes = Tuyenduong.objects.all()
        serializer = TuyenduongSerializer(routes, many=True)
        return Response(serializer.data)    
    
    @extend_schema(**get_price_schema())
    @action(detail=False, methods=['post'], url_path='get_price')
    def get_price(self, request):
        """Tính giá tiền cho chuyến đi"""
        
        print(f"💰 [GET_PRICE] Bắt đầu tính giá cho chuyến đi")
        
        # Kiểm tra xem có đầy đủ thông tin tọa độ không
        lat_don = request.data.get('lat_don')
        lon_don = request.data.get('lon_don')
        lat_tra = request.data.get('lat_tra')
        lon_tra = request.data.get('lon_tra')
        
        # Kiểm tra xem có đầy đủ thông tin địa chỉ không
        diachi_don = request.data.get('diachi_don')
        diachi_tra = request.data.get('diachi_tra')
        
        print(f"💰 [GET_PRICE] Thông tin đầu vào:")
        print(f"  - Tọa độ: đón({lat_don}, {lon_don}), trả({lat_tra}, {lon_tra})")
        print(f"  - Địa chỉ: đón('{diachi_don}'), trả('{diachi_tra}')")
        
        route_response = None
        
        # Trường hợp 1: Có đầy đủ tọa độ
        if all([lat_don, lon_don, lat_tra, lon_tra]):
            try:
                lat_don, lon_don = float(lat_don), float(lon_don)
                lat_tra, lon_tra = float(lat_tra), float(lon_tra)
                print(f"💰 [GET_PRICE] Sử dụng tọa độ để tìm tuyến đường")
                route_response = self.find_route_by_coordinates(lat_don, lon_don, lat_tra, lon_tra)
            except (ValueError, TypeError) as e:
                return Response({
                    "success": False,
                    "message": f"Tọa độ không hợp lệ: {str(e)}",
                    "error_type": "invalid_coordinates"
                }, status=400)
        
        # Trường hợp 2: Có đầy đủ địa chỉ
        elif all([diachi_don, diachi_tra]):
            print(f"💰 [GET_PRICE] Sử dụng địa chỉ để tìm tuyến đường")
            # Tạo request giả lập để gọi API get_tuyen_duong
            temp_request = type('obj', (object,), {'data': {'diachi_don': diachi_don, 'diachi_tra': diachi_tra}})
            # Sử dụng hàm get_tuyen_duong để tìm tuyến đường từ địa chỉ
            route_response = self.get_tuyen_duong(temp_request)
        
        # Trường hợp 3: Không đủ thông tin
        else:
            return Response({
                "success": False,
                "message": "Không đủ thông tin để xác định tuyến đường. Cần cung cấp hoặc (1) cả 2 địa chỉ đón/trả hoặc (2) cả 4 tọa độ đón/trả.",
                "error_type": "missing_information",
                "required": {
                    "option_1": ["diachi_don", "diachi_tra"],
                    "option_2": ["lat_don", "lon_don", "lat_tra", "lon_tra"]
                }
            }, status=400)
            
        # Nếu không tìm thấy tuyến đường, trả về lỗi
        if not route_response or route_response.status_code != 200:
            error_msg = "Không thể tìm thấy tuyến đường"
            if route_response and hasattr(route_response, 'data'):
                error_msg = route_response.data.get('message', error_msg)
            
            print(f"💰 [GET_PRICE] Lỗi tìm tuyến đường: {error_msg}")
            return Response({
                "success": False,
                "message": error_msg,
                "error_type": "route_not_found"
            }, status=404)
            
        # Tìm thấy tuyến đường, tính giá
        try:
            route_data = route_response.data
            tuyenduong = route_data.get('tuyenduong')
            
            if not tuyenduong:
                return Response({
                    "success": False,
                    "message": "Không tìm thấy thông tin tuyến đường",
                    "error_type": "invalid_route_data"
                }, status=400)
            
            giacuoc = tuyenduong.get('giacuoc')
            if giacuoc is None:
                return Response({
                    "success": False,
                    "message": "Không tìm thấy thông tin giá cước",
                    "error_type": "missing_price"
                }, status=400)
            
            try:
                giacuoc = float(giacuoc)
            except (ValueError, TypeError):
                return Response({
                    "success": False,
                    "message": "Giá cước không hợp lệ",
                    "error_type": "invalid_price"
                }, status=400)
            
            print(f"💰 [GET_PRICE] Tìm thấy tuyến đường: {tuyenduong.get('tentuyen', 'N/A')}")
            print(f"💰 [GET_PRICE] Giá cước: {giacuoc:,.0f} VNĐ")
            
            # Trả về kết quả với giá tiền và thông tin tuyến đường
            result = {
                "success": True,
                "giatien": giacuoc,
                "thong_tin_tuyen": {
                    "tentuyen": tuyenduong.get('tentuyen'),
                    "khoangcach": tuyenduong.get('khoangcach'),
                    "thoigian": tuyenduong.get('thoigian'),
                    "giacuoc": giacuoc
                }
            }
            
            # Copy các thông tin khác từ route_response
            for key in route_data:
                if key not in ['message', 'tuyenduong']:  # Tránh duplicate
                    result[key] = route_data[key]
            
            # Thêm lại tuyenduong để đảm bảo completeness
            result['tuyenduong'] = tuyenduong
                    
            return Response(result)
            
        except Exception as e:
            print(f"💰 [GET_PRICE] Lỗi khi xử lý dữ liệu: {str(e)}")
            return Response({
                "success": False,
                "message": f"Lỗi khi tính giá: {str(e)}",
                "error_type": "calculation_error"
            }, status=500)

    @extend_schema(
        description="Tính hướng di chuyển giữa hai địa điểm (theo địa chỉ hoặc mã địa điểm). Hiện tại trả về mặc định 1 (Đà Nẵng đi Tam Kỳ).",
        request=GetDirectionInputSerializer,
        responses={200: OpenApiExample('Kết quả', value={"huong": 1})},
        examples=[
            OpenApiExample(
                'Tính hướng mẫu',
                value={"diemdon": 1, "diemtra": 2},
                request_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['post'], url_path='get_direction')
    def get_direction(self, request):
        return Response({"huong": 1})

    @extend_schema(
        description="Tìm kiếm địa chỉ (geocoding) sử dụng Nominatim.",
        request=SearchAddressInputSerializer,
        responses={200: OpenApiExample('Kết quả', value=[{"display_name": "Địa chỉ mẫu", "lat": "16.05", "lon": "108.2"}])},
        examples=[
            OpenApiExample(
                'Tìm kiếm địa chỉ mẫu',
                value={"query": "Đà Nẵng"},
                request_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['post'], url_path='search_address')
    def search_address_nominatim(self, request):
        NOMINATIM_BASE_URL = "http://localhost:8080"
        query = request.data.get('query')
        if not query:
            return Response({"error": "Thiếu tham số query"}, status=status.HTTP_400_BAD_REQUEST)
        endpoint = f"{NOMINATIM_BASE_URL}/search"
        params = {
            "q": query,
            "format": "json"
        }
        try:
            response = requests.get(endpoint, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            return Response(data)
        except requests.exceptions.RequestException as e:
            return Response({"error": f"Lỗi khi gọi API Geocoding: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)

    @extend_schema(
        description="Reverse geocoding (tìm địa chỉ từ lat/lon) sử dụng Nominatim.",
        request=ReverseGeocodeInputSerializer,
        responses={200: OpenApiExample('Kết quả', value={"display_name": "Địa chỉ mẫu", "address": {}})},
        examples=[
            OpenApiExample(
                'Reverse geocoding mẫu',
                value={"lat": "16.05", "lon": "108.2"},
                request_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['post'], url_path='reverse_geocode')
    def reverse_geocode_nominatim(self, request):
        NOMINATIM_BASE_URL = "http://localhost:8080"
        lat = request.data.get('lat')
        lon = request.data.get('lon')
        if not lat or not lon:
            return Response({"error": "Thiếu tham số lat hoặc lon"}, status=status.HTTP_400_BAD_REQUEST)
        endpoint = f"{NOMINATIM_BASE_URL}/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json"
        }
        try:
            response = requests.get(endpoint, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            return Response(data)
        except requests.exceptions.RequestException as e:
            return Response({"error": f"Lỗi khi gọi API Reverse Geocoding: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)

    @extend_schema(
        description="Phân bổ tài xế cho ca. API sẽ tự động lấy danh sách đặt xe + chi tiết đặt xe có mã ca trùng, tính toán số ghế và phân bổ hành khách cho các tài xế theo capacity xe một cách tối ưu.",
        request=AssignDriverInputSerializer,
        responses={
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
        examples=[
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
    )
    @action(detail=False, methods=['post'], url_path='assign_driver_for_shift', permission_classes=[IsAuthenticated])
    def assign_driver_for_shift(self, request):
        """
        API nhận vào ca_id, tự lấy danh sách tài xế (Chitietca) và danh sách đặt xe + chi tiết đặt xe có mã ca trùng,
        tính tổng số ghế cần thiết, chia đều khách cho tài xế theo capacity xe.
        
        QUAN TRỌNG: API này sẽ GHI ĐÈ tự động assignment cũ (nếu có) mà không cảnh báo.
        Tất cả đặt xe và chi tiết đặt xe thuộc ca sẽ được assign lại theo thuật toán VRP tối ưu.
        """
        from django.db import transaction
        
        ca_id = request.data.get('ca_id')
        if not ca_id:
            return Response({'error': 'Thiếu ca_id'}, status=400)
        
        print(f"🚌 [ASSIGN] Bắt đầu phân bổ tài xế cho ca {ca_id}")
        
        try:
            # 1. Lấy thông tin ca
            ca = Ca.objects.get(maca=ca_id)
            print(f"🚌 [ASSIGN] Ca: {ca.gioxuatphat} ngày {ca.ngayxuatphat}, xuất phát từ huyện {ca.mahuyenxuatphat_id}")
            
            # 2. Lấy danh sách chi tiết ca (tài xế + xe) của ca này
            chitietca_list = list(Chitietca.objects.select_related('maxe', 'mataixe').filter(maca=ca_id))
            if not chitietca_list:
                return Response({'error': 'Không có tài xế nào trong ca này'}, status=400)
            
            print(f"🚌 [ASSIGN] Tìm thấy {len(chitietca_list)} tài xế trong ca")              # 3. Lấy tất cả đặt xe có maca = ca_id (bao gồm cả đã assign và chưa assign)
            datxe_list = list(Datxe.objects.select_related('manguoidung', 'diemdon', 'diemtra').filter(
                maca=ca_id
            ))
            print(f"🚌 [ASSIGN] Tìm thấy {len(datxe_list)} đặt xe chính với mã ca {ca_id}")
            
            # Đếm số đặt xe đã assign và chưa assign
            datxe_assigned = [dx for dx in datxe_list if dx.machitietca_id is not None]
            datxe_unassigned = [dx for dx in datxe_list if dx.machitietca_id is None]
            print(f"🚌 [ASSIGN] Đặt xe: {len(datxe_assigned)} đã assign (sẽ ghi đè), {len(datxe_unassigned)} chưa assign")
            
            # 4. Lấy tất cả chi tiết đặt xe thuộc về các đặt xe trên (bao gồm cả đã assign và chưa assign)
            chitietdatxe_list = list(Chitietdatxe.objects.select_related('madatxe', 'diemdon', 'diemtra').filter(
                madatxe__maca=ca_id
            ))
            print(f"🚌 [ASSIGN] Tìm thấy {len(chitietdatxe_list)} chi tiết đặt xe")
            
            # Đếm số chi tiết đặt xe đã assign và chưa assign
            chitiet_assigned = [ct for ct in chitietdatxe_list if ct.machitietca_id is not None]
            chitiet_unassigned = [ct for ct in chitietdatxe_list if ct.machitietca_id is None]
            print(f"🚌 [ASSIGN] Chi tiết: {len(chitiet_assigned)} đã assign (sẽ ghi đè), {len(chitiet_unassigned)} chưa assign")
            
            # Cảnh báo khi ghi đè assignment cũ
            if datxe_assigned or chitiet_assigned:
                print(f"⚠️  [ASSIGN] CẢNH BÁO: Sẽ ghi đè {len(datxe_assigned)} đặt xe và {len(chitiet_assigned)} chi tiết đã được assign!")
              # 5. Tạo danh sách hành khách (bao gồm cả đặt xe chính và chi tiết)
            passengers = []
            
            # Thêm đặt xe chính vào danh sách hành khách
            print(f"🚌 [ASSIGN] Xử lý {len(datxe_list)} đặt xe chính:")
            for datxe in datxe_list:
                passenger_info = {
                    'type': 'datxe',
                    'id': datxe.madatxe,
                    'ten': datxe.manguoidung.hoten,
                    'sdt': datxe.manguoidung.sodienthoai,
                    'soghe': datxe.soghe,
                    'diemdon': datxe.diemdon.tendiadiem,
                    'diemtra': datxe.diemtra.tendiadiem,
                    'ghichu': datxe.ghichu or '',
                    'object': datxe
                }
                passengers.append(passenger_info)
                print(f"  + Đặt xe {datxe.madatxe}: {passenger_info['ten']} ({passenger_info['soghe']} ghế) - {passenger_info['diemdon']} → {passenger_info['diemtra']}")
            
            # Thêm chi tiết đặt xe vào danh sách hành khách 
            print(f"🚌 [ASSIGN] Xử lý {len(chitietdatxe_list)} chi tiết đặt xe:")
            for chitiet in chitietdatxe_list:
                # Nếu chi tiết thiếu thông tin, lấy từ đặt xe chính
                soghe = getattr(chitiet, 'soghe', None) or chitiet.madatxe.soghe
                diemdon = chitiet.diemdon.tendiadiem if chitiet.diemdon else chitiet.madatxe.diemdon.tendiadiem
                diemtra = chitiet.diemtra.tendiadiem if chitiet.diemtra else chitiet.madatxe.diemtra.tendiadiem
                ghichu = chitiet.ghichu if chitiet.ghichu else chitiet.madatxe.ghichu or ''
                
                passenger_info = {
                    'type': 'chitietdatxe',
                    'id': chitiet.machitiet,
                    'ten': chitiet.tenkhach,
                    'sdt': chitiet.sodienthoaikhach,
                    'soghe': soghe,
                    'diemdon': diemdon,
                    'diemtra': diemtra,
                    'ghichu': ghichu,
                    'object': chitiet
                }
                passengers.append(passenger_info)
                print(f"  + Chi tiết {chitiet.machitiet}: {passenger_info['ten']} ({passenger_info['soghe']} ghế) - {passenger_info['diemdon']} → {passenger_info['diemtra']} [thuộc đặt xe {chitiet.madatxe.madatxe}]")
            
            total_seats_needed = sum(p['soghe'] for p in passengers)
            print(f"🚌 [ASSIGN] Tổng số ghế cần: {total_seats_needed}")
            print(f"🚌 [ASSIGN] Tổng số hành khách: {len(passengers)} (gồm {len(datxe_list)} đặt xe chính + {len(chitietdatxe_list)} chi tiết)")
            
            # 6. Tính capacity tổng của các xe
            total_capacity = sum(cc.maxe.sochongoi for cc in chitietca_list)
            print(f"🚌 [ASSIGN] Tổng capacity xe: {total_capacity} chỗ")
            
            if total_seats_needed > total_capacity:
                return Response({
                    'error': f'Không đủ chỗ! Cần {total_seats_needed} ghế nhưng chỉ có {total_capacity} chỗ'
                }, status=400)
            
            # 7. Sử dụng VRP algorithm để tối ưu assignment
            assignments = self.assign_passengers_with_vrp(passengers, chitietca_list)
            
            if not assignments:
                return Response({
                    'error': 'Không thể tối ưu hóa việc phân bổ hành khách'
                }, status=400)              # 8. Cập nhật database - gán machitietca cho đặt xe và chi tiết đặt xe
            print(f"🚌 [ASSIGN] Bắt đầu cập nhật database...")
            with transaction.atomic():
                total_updated_datxe = 0
                total_updated_chitiet = 0
                
                for machitietca, assignment in assignments.items():
                    chitietca_obj = next(cc for cc in chitietca_list if cc.machitietca == machitietca)
                    print(f"🚌 [ASSIGN] Cập nhật cho chi tiết ca {machitietca} (Tài xế: {chitietca_obj.mataixe.mataixe.hoten}, Xe: {chitietca_obj.maxe.biensoxe})")
                    print(f"         → {len(assignment['passengers'])} hành khách, {assignment['seats_used']}/{assignment['capacity']} ghế")
                    
                    for i, passenger in enumerate(assignment['passengers'], 1):
                        if passenger['type'] == 'datxe':
                            datxe_obj = passenger['object']
                            old_machitietca = datxe_obj.machitietca_id
                            datxe_obj.machitietca_id = machitietca
                            datxe_obj.save(update_fields=['machitietca'])
                            total_updated_datxe += 1
                            
                            status_icon = "🔄" if old_machitietca else "✨"
                            action = "GHI ĐÈ" if old_machitietca else "GÁN MỚI"
                            print(f"  {i:2d}. {status_icon} ĐẶT XE {datxe_obj.madatxe}: {passenger['ten']} (SĐT: {passenger['sdt']}, {passenger['soghe']} ghế)")
                            print(f"       🎯 {action}: machitietca {old_machitietca or 'NULL'} → {machitietca}")
                            print(f"       📍 {passenger['diemdon']} → {passenger['diemtra']}")
                            
                        elif passenger['type'] == 'chitietdatxe':
                            chitiet_obj = passenger['object']
                            old_machitietca = chitiet_obj.machitietca_id
                            chitiet_obj.machitietca_id = machitietca
                            chitiet_obj.save(update_fields=['machitietca'])
                            total_updated_chitiet += 1
                            
                            status_icon = "🔄" if old_machitietca else "✨"
                            action = "GHI ĐÈ" if old_machitietca else "GÁN MỚI"
                            print(f"  {i:2d}. {status_icon} CHI TIẾT {chitiet_obj.machitiet}: {passenger['ten']} (SĐT: {passenger['sdt']}, {passenger['soghe']} ghế)")
                            print(f"       🎯 {action}: machitietca {old_machitietca or 'NULL'} → {machitietca}")
                            print(f"       📍 {passenger['diemdon']} → {passenger['diemtra']}")
                            print(f"       🔗 Thuộc đặt xe: {chitiet_obj.madatxe.madatxe}")
                    print(f"")  # Dòng trống giữa các xe
                
                print(f"🚌 [ASSIGN] ✅ HOÀN THÀNH CẬP NHẬT:")
                print(f"         - Đặt xe chính: {total_updated_datxe}")
                print(f"         - Chi tiết đặt xe: {total_updated_chitiet}")
                print(f"         - Tổng cộng: {total_updated_datxe + total_updated_chitiet} bản ghi")
                
                if datxe_assigned or chitiet_assigned:
                    total_overwritten = len([dx for dx in datxe_list if dx.madatxe in [p['id'] for assignment in assignments.values() for p in assignment['passengers'] if p['type'] == 'datxe' and datxe_assigned]]) + len([ct for ct in chitietdatxe_list if ct.machitiet in [p['id'] for assignment in assignments.values() for p in assignment['passengers'] if p['type'] == 'chitietdatxe' and chitiet_assigned]])
                    print(f"🔄 [ASSIGN] Đã ghi đè assignment cũ cho {len(datxe_assigned)} đặt xe + {len(chitiet_assigned)} chi tiết")
            
            # 9. Tạo kết quả trả về
            result = {}
            for machitietca, assignment in assignments.items():
                # Tìm chitietca object
                cc = next(cc for cc in chitietca_list if cc.machitietca == machitietca)
                result[f'chitietca_{machitietca}'] = {
                    'machitietca': machitietca,
                    'mataixe': cc.mataixe_id,
                    'tentaixe': cc.mataixe.mataixe.hoten,
                    'maxe': cc.maxe_id,
                    'biensoxe': cc.maxe.biensoxe,
                    'capacity': cc.maxe.sochongoi,
                    'seats_used': assignment['seats_used'],
                    'seats_available': assignment['capacity'] - assignment['seats_used'],
                    'route': assignment.get('route', []),
                    'passengers': [
                        {
                            'type': p['type'],
                            'id': p['id'],
                            'ten': p['ten'],
                            'sdt': p['sdt'],
                            'soghe': p['soghe'],
                            'diemdon': p['diemdon'],
                            'diemtra': p['diemtra'],
                            'ghichu': p['ghichu']
                        } for p in assignment['passengers']
                    ]
                }
            print(f"🚌 [ASSIGN] Hoàn thành phân bổ cho {len(assignments)} xe")
            
            # Tạo message phù hợp
            overwrite_message = ""
            if datxe_assigned or chitiet_assigned:
                overwrite_message = f" (đã ghi đè {len(datxe_assigned)} đặt xe + {len(chitiet_assigned)} chi tiết cũ)"
            
            return Response({
                'success': True,
                'message': f'Đã phân bổ {len(passengers)} hành khách cho {len(assignments)} tài xế{overwrite_message}',
                'ca_id': ca_id,
                'total_passengers': len(passengers),
                'total_seats_needed': total_seats_needed,
                'total_capacity': total_capacity,
                'overwrite_info': {
                    'had_previous_assignment': len(datxe_assigned) > 0 or len(chitiet_assigned) > 0,
                    'overwritten_bookings': len(datxe_assigned),
                    'overwritten_details': len(chitiet_assigned),
                    'new_assignments': len(datxe_unassigned) + len(chitiet_unassigned)
                },
                'assignments': result
            })
            
        except Ca.DoesNotExist:
            return Response({'error': f'Không tìm thấy ca với ID {ca_id}'}, status=404)
        except Exception as e:
            print(f"🚌 [ASSIGN] Lỗi: {str(e)}")
            return Response({'error': f'Lỗi hệ thống: {str(e)}'}, status=500)

    def create_time_matrix_for_vrp(self, passengers, chitietca_list):
        """Tạo ma trận thời gian từ tọa độ các điểm đón/trả và depot"""
        import requests
        import json
        
        # Tạo danh sách locations
        all_locations = []
        
        # Depot (điểm xuất phát chung) - lấy từ ca đầu tiên hoặc default
        # Giả sử depot là Đà Nẵng hoặc Tam Kỳ tùy thuộc vào huyện xuất phát
        depot_location = {"lat": 16.080, "lon": 108.230}  # Mặc định Đà Nẵng
        all_locations.append(depot_location)
        
        # Thêm các điểm đón và trả của hành khách
        pickup_delivery_pairs = []
        location_index = 1
        
        for passenger in passengers:
            # Lấy tọa độ từ đối tượng địa điểm
            if passenger['type'] == 'datxe':
                diemdon_obj = passenger['object'].diemdon
                diemtra_obj = passenger['object'].diemtra
            else:  # chitietdatxe
                diemdon_obj = passenger['object'].diemdon or passenger['object'].madatxe.diemdon
                diemtra_obj = passenger['object'].diemtra or passenger['object'].madatxe.diemtra
            
            # Điểm đón
            pickup_location = {"lat": diemdon_obj.vido, "lon": diemdon_obj.kinhdo}
            all_locations.append(pickup_location)
            pickup_index = location_index
            location_index += 1
            
            # Điểm trả  
            dropoff_location = {"lat": diemtra_obj.vido, "lon": diemtra_obj.kinhdo}
            all_locations.append(dropoff_location)
            dropoff_index = location_index
            location_index += 1
            
            pickup_delivery_pairs.append([pickup_index, dropoff_index])
            
        print(f"🚌 [VRP] Tạo {len(all_locations)} locations, {len(pickup_delivery_pairs)} pickup-delivery pairs")
        
        # Gọi Valhalla API để tạo time matrix
        valhalla_url = "http://localhost:8002/sources_to_targets"
        request_data = {
            "sources": all_locations,
            "targets": all_locations,
            "costing": "auto",
            "costing_options": {
                "auto": {
                    "country_crossing_penalty": 2000.0
                }
            }
        }
        
        try:
            headers = {'Content-type': 'application/json'}
            response = requests.post(valhalla_url, data=json.dumps(request_data), headers=headers)
            response.raise_for_status()
            
            results = response.json()
            print(f"🚌 [VRP] Valhalla API response successful")
            
            # Parse kết quả thành time matrix
            if isinstance(results, dict) and 'sources_to_targets' in results:
                items = results['sources_to_targets']
            else:
                items = results

            num_locations = len(all_locations)
            time_matrix = [[0] * num_locations for _ in range(num_locations)]

            # Flatten items
            flat_items = []
            for sub in items:
                if isinstance(sub, list):
                    flat_items.extend(sub)
                else:
                    flat_items.append(sub)

            for item in flat_items:
                if isinstance(item, dict) and 'from_index' in item and 'to_index' in item:
                    from_idx = item['from_index']
                    to_idx = item['to_index']
                    time_matrix[from_idx][to_idx] = int(item['time'])
                    
            return time_matrix, pickup_delivery_pairs
            
        except Exception as e:
            print(f"🚌 [VRP] Lỗi gọi Valhalla API: {str(e)}")
            # Fallback: sử dụng ma trận khoảng cách Euclidean
            return self.create_fallback_time_matrix(all_locations), pickup_delivery_pairs

    def create_fallback_time_matrix(self, locations):
        """Tạo ma trận thời gian fallback dựa trên khoảng cách Euclidean"""
        import math
        
        num_locations = len(locations)
        time_matrix = [[0] * num_locations for _ in range(num_locations)]
        
        for i in range(num_locations):
            for j in range(num_locations):
                if i != j:
                    lat1, lon1 = locations[i]["lat"], locations[i]["lon"]
                    lat2, lon2 = locations[j]["lat"], locations[j]["lon"]
                    
                    # Tính khoảng cách Euclidean và chuyển thành thời gian (giây)
                    distance = math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
                    time_matrix[i][j] = int(distance * 3600)  # Giả sử 1 độ = 1 giờ
                    
        return time_matrix

    def assign_passengers_with_vrp(self, passengers, chitietca_list):
        """Sử dụng OR-Tools VRP để tối ưu phân bổ hành khách"""
        try:
            from ortools.constraint_solver import routing_enums_pb2
            from ortools.constraint_solver import pywrapcp
        except ImportError:
            print("🚌 [VRP] OR-Tools không có sẵn, sử dụng greedy algorithm")
            return self.assign_passengers_greedy(passengers, chitietca_list)
        
        print("🚌 [VRP] Bắt đầu tối ưu hóa với OR-Tools")
        
        # Tạo time matrix và pickup-delivery pairs
        time_matrix, pickup_delivery_pairs = self.create_time_matrix_for_vrp(passengers, chitietca_list)
        
        if not time_matrix:
            print("🚌 [VRP] Không thể tạo time matrix, sử dụng greedy")
            return self.assign_passengers_greedy(passengers, chitietca_list)
        
        # Chuẩn bị dữ liệu cho OR-Tools
        num_vehicles = len(chitietca_list)
        vehicle_capacities = [cc.maxe.sochongoi for cc in chitietca_list]
        depot = 0
        
        # Tạo demands array
        demands = [0] * len(time_matrix)  # Depot có demand = 0
        passenger_index = 0
        for i in range(len(pickup_delivery_pairs)):
            pickup_idx, delivery_idx = pickup_delivery_pairs[i]
            passenger = passengers[passenger_index]
            demands[pickup_idx] = passenger['soghe']    # Điểm đón: +demand
            demands[delivery_idx] = -passenger['soghe']  # Điểm trả: -demand
            passenger_index += 1
        
        # Tạo VRP data
        data = {
            'time_matrix': time_matrix,
            'pickups_deliveries': pickup_delivery_pairs,
            'num_vehicles': num_vehicles,
            'vehicle_capacities': vehicle_capacities,
            'depot': depot,
            'demands': demands
        }
        
        # Giải VRP
        solution_routes = self.solve_vrp_for_assignment(data)
        
        if not solution_routes:
            print("🚌 [VRP] Không tìm được solution, sử dụng greedy")
            return self.assign_passengers_greedy(passengers, chitietca_list)
          # Chuyển đổi solution thành assignments
        assignments = {}
        for vehicle_id, route in solution_routes.items():
            if vehicle_id < len(chitietca_list):
                cc = chitietca_list[vehicle_id]
                assignments[cc.machitietca] = {
                    'passengers': [],
                    'seats_used': 0,
                    'capacity': cc.maxe.sochongoi,
                    'route': route
                }
                print(f"🚌 [VRP] Khởi tạo assignment cho xe {cc.maxe.biensoxe} (capacity: {cc.maxe.sochongoi})")
        
        # Gán passengers vào assignments dựa trên route
        print(f"🚌 [VRP] Bắt đầu map {len(passengers)} passengers vào {len(solution_routes)} vehicles")
        self.map_passengers_to_assignments(passengers, pickup_delivery_pairs, solution_routes, assignments, chitietca_list)
        
        # Debug: In ra kết quả assignment
        for machitietca, assignment in assignments.items():
            print(f"🚌 [VRP] Xe {machitietca}: {len(assignment['passengers'])} passengers, {assignment['seats_used']}/{assignment['capacity']} ghế")
        
        return assignments

    def solve_vrp_for_assignment(self, data):
        """Giải VRP và trả về routes cho mỗi vehicle"""
        try:
            from ortools.constraint_solver import routing_enums_pb2
            from ortools.constraint_solver import pywrapcp
            
            print(f"🚌 [VRP] Thiết lập VRP với {data['num_vehicles']} vehicles, {len(data['time_matrix'])} locations")
            print(f"🚌 [VRP] Vehicle capacities: {data['vehicle_capacities']}")
            print(f"🚌 [VRP] Pickup-delivery pairs: {data['pickups_deliveries']}")
            
            # Create routing manager và model
            manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']), data['num_vehicles'], data['depot'])
            routing = pywrapcp.RoutingModel(manager)
            
            # Define cost callback
            def time_callback(from_index, to_index):
                from_node = manager.IndexToNode(from_index)
                to_node = manager.IndexToNode(to_index)
                return data['time_matrix'][from_node][to_node]
            
            transit_callback_index = routing.RegisterTransitCallback(time_callback)
            routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
            
            # Add capacity constraint
            def demand_callback(from_index):
                from_node = manager.IndexToNode(from_index)
                return data['demands'][from_node]
            
            demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
            routing.AddDimensionWithVehicleCapacity(
                demand_callback_index,
                0,  # null capacity slack
                data['vehicle_capacities'],
                True,  # start cumul to zero
                'Capacity')
            
            # Add pickup and delivery constraints
            print(f"🚌 [VRP] Thêm {len(data['pickups_deliveries'])} pickup-delivery constraints")
            for i, request in enumerate(data['pickups_deliveries']):
                pickup_index = manager.NodeToIndex(request[0])
                delivery_index = manager.NodeToIndex(request[1])
                routing.AddPickupAndDelivery(pickup_index, delivery_index)
                routing.solver().Add(
                    routing.VehicleVar(pickup_index) == routing.VehicleVar(delivery_index))
                print(f"  - Constraint {i+1}: pickup {request[0]} -> delivery {request[1]}")
            
            # Set search parameters
            search_parameters = pywrapcp.DefaultRoutingSearchParameters()
            search_parameters.first_solution_strategy = (
                routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
            search_parameters.local_search_metaheuristic = (
                routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
            search_parameters.time_limit.FromSeconds(5)
            
            print(f"🚌 [VRP] Bắt đầu giải VRP...")
            # Solve
            solution = routing.SolveWithParameters(search_parameters)
            
            if solution:
                print(f"🚌 [VRP] Tìm được solution! Objective value: {solution.ObjectiveValue()}")
                return self.extract_solution_routes(data, manager, routing, solution)
            else:
                print(f"🚌 [VRP] Không tìm được solution")
                return None
                
        except Exception as e:
            print(f"🚌 [VRP] Lỗi khi giải VRP: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def extract_solution_routes(self, data, manager, routing, solution):
        """Trích xuất routes từ solution"""
        routes = {}
        
        print(f"🚌 [VRP] Trích xuất routes cho {data['num_vehicles']} vehicles")
        
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            route = []
            
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route.append(node_index)
                index = solution.Value(routing.NextVar(index))
            
            route.append(manager.IndexToNode(index))  # End node
            routes[vehicle_id] = route
            print(f"🚌 [VRP] Vehicle {vehicle_id}: route = {route}")
            
        return routes

    def map_passengers_to_assignments(self, passengers, pickup_delivery_pairs, solution_routes, assignments, chitietca_list):
        """Map passengers vào assignments dựa trên VRP solution"""
        
        # Tạo mapping từ pickup/delivery index sang passenger
        pickup_to_passenger = {}
        for i, (pickup_idx, delivery_idx) in enumerate(pickup_delivery_pairs):
            pickup_to_passenger[pickup_idx] = passengers[i]
            pickup_to_passenger[delivery_idx] = passengers[i]
        
        # Gán passengers vào từng vehicle
        for vehicle_id, route in solution_routes.items():
            if vehicle_id < len(chitietca_list):
                cc = chitietca_list[vehicle_id]
                assignment = assignments[cc.machitietca]
                assigned_passenger_ids = set()  # Lưu ID thay vì object
                
                for node in route:
                    if node in pickup_to_passenger:
                        passenger = pickup_to_passenger[node]
                        # Sử dụng ID làm key để tránh lỗi unhashable
                        passenger_key = f"{passenger['type']}_{passenger['id']}"
                        
                        if passenger_key not in assigned_passenger_ids:
                            assignment['passengers'].append(passenger)
                            assignment['seats_used'] += passenger['soghe']
                            assigned_passenger_ids.add(passenger_key)
                            print(f"🚌 [VRP] Gán {passenger['ten']} vào xe {cc.maxe.biensoxe}")

    def assign_passengers_greedy(self, passengers, chitietca_list):
        """Fallback greedy algorithm nếu VRP không khả dụng"""
        print("🚌 [ASSIGN] Sử dụng greedy algorithm")
        
        chitietca_sorted = sorted(chitietca_list, key=lambda x: x.maxe.sochongoi, reverse=True)
        assignments = {cc.machitietca: {'passengers': [], 'seats_used': 0, 'capacity': cc.maxe.sochongoi} 
                      for cc in chitietca_sorted}
        
        passengers_sorted = sorted(passengers, key=lambda x: x['soghe'], reverse=True)
        
        for passenger in passengers_sorted:
            assigned = False
            for cc in chitietca_sorted:
                assignment = assignments[cc.machitietca]
                if assignment['seats_used'] + passenger['soghe'] <= assignment['capacity']:
                    assignment['passengers'].append(passenger)
                    assignment['seats_used'] += passenger['soghe']
                    assigned = True
                    break
            
            if not assigned:
                return None
                
        return assignments

    @extend_schema(
        description="Lấy mã huyện từ tọa độ lat/lon sử dụng Nominatim và mapping thông minh cho vùng Đà Nẵng - Quảng Nam.",
        request=GetHuyenInputSerializer,
        responses={200: GetHuyenOutputSerializer},
        examples=[
            OpenApiExample(
                'Get huyện mẫu',
                value={"lat": "16.05", "lon": "108.2"},
                request_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['post'], url_path='get_huyen')
    def get_huyen_from_coordinates(self, request):
        """
        Lấy mã huyện từ tọa độ với mapping thông minh cho vùng Đà Nẵng - Quảng Nam
        """
        # Validate input bằng serializer
        serializer = GetHuyenInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        lat = serializer.validated_data['lat']
        lon = serializer.validated_data['lon']
        
        # Mapping keywords để nhận diện huyện/thành phố
        huyen_mapping = {
            # Đà Nẵng
            "đà nẵng": 2,
            "da nang": 2,
            "thanh pho da nang": 2,
            "thành phố đà nẵng": 2,
            "hai chau": 2,
            "hải châu": 2,
            "cam le": 2,
            "cẩm lệ": 2,
            "lien chieu": 2,
            "liên chiểu": 2,
            "ngu hanh son": 2,
            "ngũ hành sơn": 2,
            "son tra": 2,
            "sơn trà": 2,
            "hoa vang": 2,
            "hòa vang": 2,
            
            # Tam Kỳ
            "tam ky": 1,
            "tam kỳ": 1,
            "thanh pho tam ky": 1,
            "thành phố tam kỳ": 1,
            
            # Thăng Bình
            "thang binh": 3,
            "thăng bình": 3,
            "huyen thang binh": 3,
            "huyện thăng bình": 3,
            
            # Quế Sơn
            "que son": 4,
            "quế sơn": 4,
            "huyen que son": 4,
            "huyện quế sơn": 4,
            
            # Điện Bàn
            "dien ban": 5,
            "điện bàn": 5,
            "huyen dien ban": 5,
            "huyện điện bàn": 5,        }
        
        try:
            # Gọi API reverse geocoding nội bộ
            reverse_request = type('obj', (object,), {'data': {'lat': lat, 'lon': lon}})
            reverse_response = self.reverse_geocode_nominatim(reverse_request)
            
            if reverse_response.status_code != 200:
                return reverse_response
                
            data = reverse_response.data
            
            # Lấy thông tin địa chỉ
            address = data.get('address', {})
            display_name = data.get('display_name', '').lower()
            
            # Danh sách các trường có thể chứa thông tin huyện/thành phố
            address_fields = [
                address.get('city', ''),
                address.get('town', ''),
                address.get('county', ''),
                address.get('state_district', ''),
                address.get('suburb', ''),
                address.get('municipality', ''),
                display_name
            ]
            
            # Thử match với mapping
            for field in address_fields:
                if field:
                    field_lower = field.lower()
                    for keyword, ma_huyen in huyen_mapping.items():
                        if keyword in field_lower:
                            from .models import Huyen
                            try:
                                huyen = Huyen.objects.get(mahuyen=ma_huyen)
                                return Response({
                                    "mahuyen": huyen.mahuyen,
                                    "tenhuyen": huyen.tenhuyen,
                                    "matched_field": field,
                                    "matched_keyword": keyword,
                                    "nominatim_data": data
                                })
                            except Huyen.DoesNotExist:
                                pass
            
            # Fallback: nếu không match được, kiểm tra tọa độ để guess huyện
            lat_float = float(lat)
            lon_float = float(lon)
            
            # Rough coordinate ranges for different areas
            if 16.0 <= lat_float <= 16.15 and 108.15 <= lon_float <= 108.3:
                # Likely Đà Nẵng area
                ma_huyen = 2
            elif 15.5 <= lat_float <= 15.7 and 108.4 <= lon_float <= 108.6:
                # Likely Tam Kỳ area
                ma_huyen = 1
            else:
                # Default fallback
                ma_huyen = 1
            
            from .models import Huyen
            try:
                huyen = Huyen.objects.get(mahuyen=ma_huyen)
                return Response({
                    "mahuyen": huyen.mahuyen,
                    "tenhuyen": huyen.tenhuyen,
                    "method": "coordinate_fallback",
                    "nominatim_data": data
                })
            except Huyen.DoesNotExist:
                return Response({
                    "error": "Không thể xác định huyện",
                    "nominatim_data": data                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({"error": f"Lỗi xử lý: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
    @extend_schema(**get_tuyen_duong_by_coordinates_schema())
    @action(detail=False, methods=['post'], url_path='get_tuyen_duong')
    def get_tuyen_duong(self, request):
        """Tìm tuyến đường từ 2 tọa độ"""
        serializer = GetTuyenDuongByCoordinatesInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        lat_don = serializer.validated_data['lat_don']
        lon_don = serializer.validated_data['lon_don']
        lat_tra = serializer.validated_data['lat_tra']
        lon_tra = serializer.validated_data['lon_tra']
        
        return self.find_route_by_coordinates(lat_don, lon_don, lat_tra, lon_tra)
        
    def find_route_by_coordinates(self, lat_don, lon_don, lat_tra, lon_tra):
        """Hàm chung để tìm tuyến đường từ tọa độ"""
        print(f"🔍 Bắt đầu tìm tuyến đường từ tọa độ: điểm đón ({lat_don}, {lon_don}) -> điểm trả ({lat_tra}, {lon_tra})")
        
        try:
            # Lấy mã huyện điểm đón
            print(f"📍 Đang tìm huyện cho điểm đón: lat={lat_don}, lon={lon_don}")
            huyen_don_request = type('obj', (object,), {'data': {'lat': lat_don, 'lon': lon_don}})
            huyen_don_response = self.get_huyen_from_coordinates(huyen_don_request)
            if huyen_don_response.status_code != 200:
                print(f"❌ Không thể xác định huyện điểm đón: {huyen_don_response.data}")
                return Response({
                    "success": False,
                    "message": "Không thể xác định huyện điểm đón",
                    "error_type": "no_pickup",
                    "details": huyen_don_response.data
                }, status=400)
            huyen_don_data = huyen_don_response.data
            print(f"✅ Tìm thấy huyện điểm đón: {huyen_don_data}")
            
            # Lấy mã huyện điểm trả
            print(f"📍 Đang tìm huyện cho điểm trả: lat={lat_tra}, lon={lon_tra}")
            huyen_tra_request = type('obj', (object,), {'data': {'lat': lat_tra, 'lon': lon_tra}})
            huyen_tra_response = self.get_huyen_from_coordinates(huyen_tra_request)
            if huyen_tra_response.status_code != 200:
                print(f"❌ Không thể xác định huyện điểm trả: {huyen_tra_response.data}")
                return Response({
                    "success": False,
                    "message": "Không thể xác định huyện điểm trả",
                    "error_type": "no_dropoff",
                    "details": huyen_tra_response.data
                }, status=400)
            huyen_tra_data = huyen_tra_response.data
            print(f"✅ Tìm thấy huyện điểm trả: {huyen_tra_data}")
              # Tìm tuyến đường trong DB
            ma_huyen_don = huyen_don_data['mahuyen']
            ma_huyen_tra = huyen_tra_data['mahuyen']
            print(f"🚍 Đang tìm tuyến đường từ huyện {ma_huyen_don} ({huyen_don_data.get('tenhuyen')}) đến huyện {ma_huyen_tra} ({huyen_tra_data.get('tenhuyen')})")
            
            try:
                tuyenduong = Tuyenduong.objects.get(
                    huyendon=ma_huyen_don,
                    huyentra=ma_huyen_tra
                )
                print(f"✅ Tìm thấy tuyến đường: {huyen_don_data.get('tenhuyen')} -> {huyen_tra_data.get('tenhuyen')} (ID: {tuyenduong.matuyenduong})")
                
                return Response({
                    "success": True,
                    "message": "Tìm thấy tuyến đường",
                    "tuyenduong": TuyenduongSerializer(tuyenduong).data,
                    "huyen_don": {
                        "mahuyen": huyen_don_data['mahuyen'],
                        "tenhuyen": huyen_don_data['tenhuyen']
                    },
                    "huyen_tra": {
                        "mahuyen": huyen_tra_data['mahuyen'],
                        "tenhuyen": huyen_tra_data['tenhuyen']
                    },
                    "coordinates": {
                        "pickup": {"lat": lat_don, "lon": lon_don},
                        "dropoff": {"lat": lat_tra, "lon": lon_tra}
                    }                })
                
            except Tuyenduong.DoesNotExist:
                print(f"❌ Không tìm thấy tuyến đường từ huyện {ma_huyen_don} ({huyen_don_data['tenhuyen']}) đến huyện {ma_huyen_tra} ({huyen_tra_data['tenhuyen']})")
                return Response({
                    "success": False,
                    "message": f"Không có tuyến đường từ {huyen_don_data['tenhuyen']} đến {huyen_tra_data['tenhuyen']}",
                    "error_type": "no_route",
                    "huyen_don": {
                        "mahuyen": huyen_don_data['mahuyen'],
                        "tenhuyen": huyen_don_data['tenhuyen']
                    },
                    "huyen_tra": {
                        "mahuyen": huyen_tra_data['mahuyen'],
                        "tenhuyen": huyen_tra_data['tenhuyen']
                    },
                    "coordinates": {
                        "pickup": {"lat": lat_don, "lon": lon_don},
                        "dropoff": {"lat": lat_tra, "lon": lon_tra}
                    }                }, status=404)
                
        except Exception as e:
            print(f"💥 Lỗi xử lý trong find_route_by_coordinates: {str(e)}")
            return Response({
                "success": False,
                "message": f"Lỗi xử lý: {str(e)}"
            }, status=500)

