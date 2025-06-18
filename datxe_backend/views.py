from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError, AccessToken
from drf_spectacular.utils import extend_schema, OpenApiExample
from .models import NguoiDung, Datxe, Chitietdatxe, Danhgia, Nhanvien, Tuyenduong, Ca, Chitietca, Taixe, Xe, Diadiem
from .serializers import UserSerializer, SignupSerializer, LoginSerializer, BookingSerializer, CreateBookingSerializer, BookingDetailSerializer, CheckSlotInputSerializer, GetDirectionInputSerializer, GetDistrictInputSerializer, GetPriceInputSerializer, TuyenduongSerializer, HuyenSerializer, CaSerializer, CaCreateUpdateSerializer, ChitietcaSerializer, TaixeSerializer, XeSerializer, CreateShiftDetailSerializer, DiadiemSerializer, CreateDiadiemSerializer, GetHuyenInputSerializer, GetHuyenOutputSerializer, GetTuyenDuongInputSerializer, GetTuyenDuongByCoordinatesInputSerializer
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
        return BookingSerializer   
    
    @extend_schema(
        description="Tạo mới một booking (đặt xe). Tuyến đường sẽ được tự động tìm từ điểm đi và điểm đến.",
        request=CreateBookingSerializer,
        responses={201: BookingSerializer},        
        examples=[            
                  OpenApiExample(                
                                 'Đặt xe mẫu',                
                                 value={
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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        
        # Trả về response với BookingSerializer để hiển thị đầy đủ thông tin
        response_serializer = BookingSerializer(booking)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

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
            ),
        ],
    )
    
    @extend_schema(
        description="Kiểm tra số chỗ còn lại trong một chi tiết ca theo hướng và thời gian. Trả về tổng số chỗ, số khách đã đặt, số chỗ còn lại.",
        request=CheckSlotInputSerializer,
        responses={200: OpenApiExample('Kết quả', value={"sochongoi": 16, "sokhach": 10, "conlai": 6})},
        examples=[
            OpenApiExample(
                'Check slot mẫu',
                value={"machitietca": 1, "huong": 1},
                request_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['post'], url_path='check_slot', permission_classes=[IsAuthenticated])
    def check_slot(self, request):
        machitietca = int(request.data.get('machitietca'))
        huong = int(request.data.get('huong'))
        if huong == 1:
            diemdon, diemtra = 1, 2
        else:
            diemdon, diemtra = 2, 1
        try:
            chitietca = Chitietca.objects.get(machitietca=machitietca)
            xe = getattr(chitietca, 'maxe', None)
            sochongoi = getattr(xe, 'sochongoi', 0) if xe else 0
            datxe_ids = Datxe.objects.filter(machitietca=chitietca).values_list('madatxe', flat=True)
            sokhach = Chitietdatxe.objects.filter(madatxe_id__in=datxe_ids, diemdon=diemdon, diemtra=diemtra).count()
            return Response({"sochongoi": sochongoi, "sokhach": sokhach, "conlai": sochongoi - sokhach})
        except Chitietca.DoesNotExist:
            return Response({"error": "Không tìm thấy chi tiết ca."}, status=status.HTTP_404_NOT_FOUND)

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
        ],
    )
    @action(detail=False, methods=['get'], url_path='locations')
    def get_locations(self, request):
        """Lấy danh sách tất cả địa điểm"""
        locations = Diadiem.objects.all()
        serializer = DiadiemSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
        
        # Kiểm tra xem có đầy đủ thông tin tọa độ không
        lat_don = request.data.get('lat_don')
        lon_don = request.data.get('lon_don')
        lat_tra = request.data.get('lat_tra')
        lon_tra = request.data.get('lon_tra')
        
        # Kiểm tra xem có đầy đủ thông tin địa chỉ không
        diachi_don = request.data.get('diachi_don')
        diachi_tra = request.data.get('diachi_tra')
        
        # Trường hợp 1: Có đầy đủ tọa độ
        if all([lat_don, lon_don, lat_tra, lon_tra]):
            route_response = self.find_route_by_coordinates(lat_don, lon_don, lat_tra, lon_tra)
        
        # Trường hợp 2: Có đầy đủ địa chỉ
        elif all([diachi_don, diachi_tra]):
            # Tạo request giả lập để gọi API get_tuyen_duong
            temp_request = type('obj', (object,), {'data': {'diachi_don': diachi_don, 'diachi_tra': diachi_tra}})
              # Sử dụng hàm get_tuyen_duong để tìm tuyến đường từ địa chỉ
            route_response = self.get_tuyen_duong(temp_request)
        
        # Trường hợp 3: Không đủ thông tin
        else:
            return Response({
                "success": False,
                "message": "Không đủ thông tin để xác định tuyến đường. Cần cung cấp hoặc (1) cả 2 địa chỉ đón/trả hoặc (2) cả 4 tọa độ đón/trả.",
                "error_type": "missing_information"
            }, status=400)
            
        # Nếu không tìm thấy tuyến đường, trả về lỗi
        if route_response.status_code != 200:
            return route_response
            
        # Tìm thấy tuyến đường, tính giá
        try:
            route_data = route_response.data
            tuyenduong = route_data.get('tuyenduong')
            giacuoc = float(tuyenduong.get('giacuoc', 0))
            
            # Trả về kết quả với giá tiền và thông tin tuyến đường
            result = {
                "success": True,
                "giatien": giacuoc,
            }
            
            # Copy các thông tin khác từ route_response
            for key in route_data:
                if key != 'message':  # Không copy message để tránh nhầm lẫn
                    result[key] = route_data[key]
                    
            return Response(result)
            
        except Exception as e:
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
        description="Nhận ca_id, chia đều khách cho tài xế trong ca, cập nhật lại mã chi tiết ca cho từng chi tiết đặt xe.",
        request={
            "type": "object",
            "properties": {
                "ca_id": {"type": "integer", "description": "ID của ca tài xế"}
            },
            "required": ["ca_id"]
        },
        responses={200: OpenApiExample('Thành công', value={"result": {"taixe_1": {"machitietca": 1, "mataixe": 101, "maxe": 201, "khach": ["Nguyen Van B"]}}, "message": "Đã phân bổ khách cho tài xế thành công."})},
        examples=[
            OpenApiExample(
                'Phân bổ khách mẫu',
                value={"ca_id": 1},
                request_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['post'], url_path='assign_driver_for_shift', permission_classes=[IsAuthenticated])
    def assign_driver_for_shift(self, request):
        """
        API nhận vào ca_id, tự lấy danh sách tài xế (Chitietca) và danh sách chi tiết đặt xe (Chitietdatxe) của ca đó,
        chia đều khách cho tài xế, cập nhật lại mã chi tiết ca cho từng chi tiết đặt xe.
        """
        from django.db import transaction
        ca_id = request.data.get('ca_id')
        if not ca_id:
            return Response({'error': 'Thiếu ca_id'}, status=400)
        # Lấy danh sách chitietca (tài xế, xe) của ca này
        chitietca_list = list(Chitietca.objects.filter(maca=ca_id))
        if not chitietca_list:
            return Response({'error': 'Không có tài xế nào trong ca này'}, status=400)
        # Lấy tất cả chi tiết đặt xe chưa gán tài xế (hoặc đã gán nhưng muốn phân lại)
        chitietdatxe_list = list(Chitietdatxe.objects.filter(madatxe__machitietca__maca=ca_id))
        if not chitietdatxe_list:
            return Response({'error': 'Không có chi tiết đặt xe nào trong ca này'}, status=400)
        # Chia đều khách cho tài xế (round-robin)
        n_driver = len(chitietca_list)
        with transaction.atomic():
            for idx, chitiet in enumerate(chitietdatxe_list):
                chitiet.machitietca = chitietca_list[idx % n_driver]
                chitiet.save(update_fields=['machitietca'])
        # Trả về mapping tài xế - khách
        result = {}
        for i, chitietca in enumerate(chitietca_list):
            khach = [ct.tenkhach for ct in chitietdatxe_list if ct.machitietca_id == chitietca.machitietca]
            result[f'taixe_{i+1}'] = {
                'machitietca': chitietca.machitietca,
                'mataixe': chitietca.mataixe_id,
                'maxe': chitietca.maxe_id,                
                'khach': khach
            }
        return Response({'result': result, 'message': 'Đã phân bổ khách cho tài xế thành công.'})

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

