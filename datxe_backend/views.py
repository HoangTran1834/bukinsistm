from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from drf_spectacular.utils import extend_schema, OpenApiExample
from .models import NguoiDung, Datxe, Chitietdatxe, Danhgia, Nhanvien, Tuyenduong, Ca, Chitietca
from .serializers import UserSerializer, SignupSerializer, LoginSerializer, BookingSerializer, BookingDetailSerializer, CheckSlotInputSerializer, GetDirectionInputSerializer, GetDistrictInputSerializer, GetPriceInputSerializer, TuyenduongSerializer, HuyenSerializer, CaSerializer, ChitietcaSerializer

"""
API ViewSets cho hệ thống đặt xe taxi:
- AuthViewSet: Đăng ký, đăng nhập, đăng xuất, sử dụng JWT, có ví dụ mẫu cho Swagger UI.
- UserViewSet: Xem/sửa thông tin tài khoản, cho phép tất cả user xem thông tin nhau, chỉ cho phép tự sửa thông tin cá nhân.
- ShiftViewSet: Quản lý ca tài xế, chỉ nhân viên/admin được chỉnh sửa, tài xế/nhân viên được xem.
- BookingViewSet: Đặt xe, xem danh sách booking, trả về đầy đủ chi tiết liên quan, hỗ trợ đặt nhiều khách/lượt.

Các API đều có mô tả chi tiết, ví dụ mẫu, hỗ trợ tốt cho thử nghiệm trên Swagger UI (drf-spectacular).
"""

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @extend_schema(
        description="Đăng ký tài khoản mới. Nhập họ tên, số điện thoại, mật khẩu và (tùy chọn) email.",
        request=SignupSerializer,
        responses={201: OpenApiExample('Đăng ký thành công', value={"message": "Đăng ký thành công"})},
        examples=[
            OpenApiExample(
                'Đăng ký mẫu',
                value={"hoten": "Nguyen Van A", "sodienthoai": "0123456789", "password": "matkhau123", "email": "a@gmail.com"},
                request_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['post'], url_path='signup')
    def signup(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Đăng ký thành công'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Đăng nhập bằng số điện thoại và mật khẩu để nhận access/refresh token.",
        request=LoginSerializer,
        responses={200: LoginSerializer},
        examples=[
            OpenApiExample(
                'Đăng nhập mẫu',
                value={"sodienthoai": "0123456789", "password": "matkhau123"},
                request_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Đăng xuất khỏi hệ thống, thu hồi refresh token.",
        request=None,
        responses={205: OpenApiExample('Đăng xuất thành công', value={"detail": "Đăng xuất thành công."})},
        examples=[
            OpenApiExample(
                'Đăng xuất mẫu',
                value={"refresh": "<refresh_token>"},
                request_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['post'], url_path='logout', permission_classes=[IsAuthenticated])
    def logout(self, request):
        refresh_token = request.data.get("refresh")
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

    def get_permissions(self):
        # Nhân viên được phép chỉnh sửa, tài xế/nhân viên đều được xem
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsNhanVien()]
        return [IsAuthenticated()]

    def get_queryset(self):
        # Admin, tài xế và nhân viên mới được xem
        user = self.request.user
        if getattr(user, 'vaitro', None) in [0, 1, 2]:
            return super().get_queryset()
        return Ca.objects.none()

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
        return BookingSerializer

    @extend_schema(
        description="Tạo mới một booking (đặt xe) kèm nhiều chi tiết đặt xe.",
        request=BookingSerializer,
        responses={201: BookingSerializer},
        examples=[
            OpenApiExample(
                'Đặt xe mẫu',
                value={
                    "diemdon": 1,
                    "diemtra": 2,
                    "matuyenduong": 1,
                    "machitietca": 1,
                    "chitietdatxe": [
                        {"tenkhach": "Nguyen Van B", "sodienthoaikhach": "0987654321", "diemdon": 1, "diemtra": 2, "matuyenduong": 1, "trangthai": "Đã đặt", "machitietca": 1}
                    ]
                },
                request_only=True,
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        chitiet_data = request.data.pop('chitietdatxe', [])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save(manguoidung=request.user)
        # Tạo các chi tiết đặt xe nếu có
        for chitiet in chitiet_data:
            chitiet['madatxe'] = booking.madatxe
            if 'machitietca' not in chitiet:
                chitiet['machitietca'] = booking.machitietca_id
            chitiet_serializer = BookingDetailSerializer(data=chitiet)
            chitiet_serializer.is_valid(raise_exception=True)
            chitiet_serializer.save()
        return Response(self.get_serializer(booking).data, status=status.HTTP_201_CREATED)

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
    @action(detail=False, methods=['post'], url_path='auto_assign', permission_classes=[IsAuthenticated])
    def auto_assign(self, request):
        from django.utils import timezone
        from django.db.models import F, Sum
        tenkhach = request.data.get('tenkhach')
        sodienthoaikhach = request.data.get('sodienthoaikhach')
        huong = int(request.data.get('huong'))
        thoigian = request.data.get('thoigian')
        # Giả sử huong=1: ĐN->TK, huong=2: TK->ĐN, mã địa điểm cố định
        if huong == 1:
            diemdon, diemtra = 1, 2
        else:
            diemdon, diemtra = 2, 1
        # Tìm chi tiết ca còn chỗ
        chitietca_list = Chitietca.objects.all().order_by('maca__gioxuatphat')
        for chitietca in chitietca_list:
            xe = getattr(chitietca, 'maxe', None)
            sochongoi = getattr(xe, 'sochongoi', 0) if xe else 0
            datxe_ids = Datxe.objects.filter(machitietca=chitietca).values_list('madatxe', flat=True)
            sokhach = Chitietdatxe.objects.filter(madatxe_id__in=datxe_ids, diemdon=diemdon, diemtra=diemtra).count()
            if sochongoi > sokhach:
                # Tạo booking mới
                booking = Datxe.objects.create(manguoidung=request.user, diemdon=diemdon, diemtra=diemtra, machitietca=chitietca, matuyenduong=1, trangthai="Đã đặt", thoigiandat=timezone.now(), yeucauchungxe=0)
                chitiet = Chitietdatxe.objects.create(madatxe=booking, tenkhach=tenkhach, sodienthoaikhach=sodienthoaikhach, diemdon=diemdon, diemtra=diemtra, matuyenduong=1, trangthai="Đã đặt", machitietca=chitietca)
                return Response(self.get_serializer(booking).data, status=status.HTTP_201_CREATED)
        return Response({"error": "Không còn chi tiết ca nào còn chỗ phù hợp."}, status=status.HTTP_400_BAD_REQUEST)

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
    @action(detail=False, methods=['post'], url_path='get_direction', permission_classes=[IsAuthenticated])
    def get_direction(self, request):
        # Giả sử luôn trả về hướng 1 (Đà Nẵng đi Tam Kỳ)
        return Response({"huong": 1})

    @extend_schema(
        description="Tính huyện của một địa chỉ (mã địa điểm). Hiện tại trả về tên huyện mẫu dựa trên mã địa điểm (1: Tam Kỳ, 2: Đà Nẵng, ...)",
        request=GetDistrictInputSerializer,
        responses={200: OpenApiExample('Kết quả', value={"huyen": "Tam Kỳ"})},
        examples=[
            OpenApiExample(
                'Tính huyện mẫu',
                value={"diemdon": 1},
                request_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['post'], url_path='get_district', permission_classes=[IsAuthenticated])
    def get_district(self, request):
        # Giả sử luôn trả về huyện Tam Kỳ (mã 1)
        return Response({"huyen": "Tam Kỳ"})

    @extend_schema(
        description="Tính giá dự kiến cho một lộ trình (đã có mã tuyến đường). Chỉ cần nhập mã tuyến đường, API sẽ trả về giá dự kiến.",
        request=GetPriceInputSerializer,
        responses={200: OpenApiExample('Kết quả', value={"giatien": 30000})},
        examples=[
            OpenApiExample(
                'Tính giá mẫu',
                value={"matuyenduong": 1},
                request_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['post'], url_path='get_price', permission_classes=[IsAuthenticated])
    def get_price(self, request):
        matuyenduong = request.data.get('matuyenduong')
        # Giả sử luôn trả về giá 30.000đ cho mã tuyến đường bất kỳ
        return Response({"giatien": 30000})

    @extend_schema(
        description="Lấy danh sách các tài xế đang trực (online) theo ca. Chỉ admin mới xem được danh sách này.",
        responses={200: UserSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Tài xế trực mẫu',
                value=[
                    {"maNguoiDung": 2, "hoTen": "Tran Thi B", "sodienthoai": "0987654321", "vaitro": "Tài xế", "trangthai": "Đang trực"}
                ],
                response_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['get'], url_path='drivers_online', permission_classes=[IsAuthenticated])
    def drivers_online(self, request):
        from django.utils import timezone
        from datetime import timedelta
        # Lấy thời gian hiện tại trừ đi 30 phút
        time_threshold = timezone.now() - timedelta(minutes=30)
        # Tìm các tài xế có trạng thái "Đang trực" và có ca trong vòng 30 phút qua
        online_drivers = NguoiDung.objects.filter(
            vaitro="Tài xế",
            trangthai="Đang trực",
            cataixe__batdau__gte=time_threshold
        ).distinct()
        serializer = self.get_serializer(online_drivers, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Lấy danh sách các ca tài xế theo ngày. Chỉ admin mới xem được danh sách này.",
        responses={200: CaSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Ca tài xế mẫu',
                value=[
                    {"maca": 1, "tenca": "Ca sáng", "batdau": "2023-10-01T06:00:00", "ketthuc": "2023-10-01T12:00:00", "trangthai": "Đang hoạt động"}
                ],
                response_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['get'], url_path='shifts_by_date', permission_classes=[IsAuthenticated])
    def shifts_by_date(self, request):
        from django.utils import timezone
        from datetime import timedelta
        today = timezone.now().date()
        shifts = Ca.objects.filter(ngayxuatphat=today).order_by('gioxuatphat')
        serializer = CaSerializer(shifts, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Lấy thống kê số lượng tài xế, hành khách, đặt xe theo thời gian (theo ngày).",
        responses={200: OpenApiExample('Kết quả', value={"ngay": "2023-10-01", "soluongtaixe": 10, "soluonghanhkhach": 50, "soluongdatxe": 30})},
        examples=[
            OpenApiExample(
                'Thống kê mẫu',
                value={"tu_ngay": "2023-10-01", "den_ngay": "2023-10-31"},
                request_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['post'], url_path='statistics', permission_classes=[IsAuthenticated])
    def statistics(self, request):
        from django.db.models import Count
        tu_ngay = request.data.get('tu_ngay')
        den_ngay = request.data.get('den_ngay')
        # Giả sử luôn trả về số liệu mẫu cho tháng 10 năm 2023
        if tu_ngay == "2023-10-01" and den_ngay == "2023-10-31":
            return Response({
                "ngay": "2023-10-01",
                "soluongtaixe": 10,
                "soluonghanhkhach": 50,
                "soluongdatxe": 30
            })
        # Nếu không phải khoảng thời gian mẫu, trả về rỗng
        return Response([])

    @extend_schema(
        description="Lấy danh sách các tuyến đường (đã có mã tuyến đường). Chỉ admin mới xem được danh sách này.",
        responses={200: TuyenduongSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Tuyến đường mẫu',
                value=[
                    {"matuyenduong": 1, "tentuyenduong": "Đà Nẵng - Tam Kỳ", "giatien": 30000}
                ],
                response_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['get'], url_path='routes', permission_classes=[IsAuthenticated])
    def routes(self, request):
        # Chỉ admin mới xem được danh sách này
        if request.user.vaitro != 0:
            return Response({"error": "Chỉ admin mới có quyền truy cập."}, status=status.HTTP_403_FORBIDDEN)
        routes = Tuyenduong.objects.all()
        serializer = self.get_serializer(routes, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Tạo mới một tuyến đường (chưa có mã tuyến đường). Chỉ admin mới có quyền này.",
        request=TuyenduongSerializer,
        responses={201: TuyenduongSerializer},
        examples=[
            OpenApiExample(
                'Thêm tuyến đường mẫu',
                value={"tentuyenduong": "Tam Kỳ - Hội An", "giatien": 40000},
                request_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['post'], url_path='routes', permission_classes=[IsAuthenticated])
    def create_route(self, request):
        # Chỉ admin mới có quyền thêm tuyến đường
        if request.user.vaitro != 0:
            return Response({"error": "Chỉ admin mới có quyền này."}, status=status.HTTP_403_FORBIDDEN)
        serializer = TuyenduongSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description="Cập nhật thông tin một tuyến đường (đã có mã tuyến đường). Chỉ admin mới có quyền này.",
        request=TuyenduongSerializer,
        responses={200: TuyenduongSerializer},
        examples=[
            OpenApiExample(
                'Cập nhật tuyến đường mẫu',
                value={"matuyenduong": 1, "tentuyenduong": "Đà Nẵng - Hội An", "giatien": 35000},
                request_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['put'], url_path='routes', permission_classes=[IsAuthenticated])
    def update_route(self, request):
        # Chỉ admin mới có quyền sửa tuyến đường
        if request.user.vaitro != 0:
            return Response({"error": "Chỉ admin mới có quyền này."}, status=status.HTTP_403_FORBIDDEN)
        instance = Tuyenduong.objects.get(matuyenduong=request.data.get("matuyenduong"))
        serializer = TuyenduongSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        description="Xóa một tuyến đường (đã có mã tuyến đường). Chỉ admin mới có quyền này.",
        responses={204: OpenApiExample('Xóa thành công', value={})},
        examples=[
            OpenApiExample(
                'Xóa tuyến đường mẫu',
                value={"matuyenduong": 1},
                request_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['delete'], url_path='routes', permission_classes=[IsAuthenticated])
    def delete_route(self, request):
        # Chỉ admin mới có quyền xóa tuyến đường
        if request.user.vaitro != 0:
            return Response({"error": "Chỉ admin mới có quyền này."}, status=status.HTTP_403_FORBIDDEN)
        instance = Tuyenduong.objects.get(matuyenduong=request.data.get("matuyenduong"))
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



