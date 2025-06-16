from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from drf_spectacular.utils import extend_schema, OpenApiExample
from .models import NguoiDung, Datxe, Cataixe, Chitietdatxe, Danhgia, Nhanvien, Tuyenduong
from .serializers import UserSerializer, SignupSerializer, LoginSerializer, ShiftSerializer, BookingSerializer, BookingDetailSerializer

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
    queryset = Cataixe.objects.all()
    serializer_class = ShiftSerializer
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
        return Cataixe.objects.none()

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Datxe.objects.all()
    serializer_class = BookingSerializer

    def get_queryset(self):
        user = self.request.user
        # Nếu là tài xế (vaiTro=1) chỉ xem các booking có ca tài xế thuộc về mình
        if getattr(user, 'vaitro', None) == 1:
            return Datxe.objects.filter(cataixe__maTaiXe=user.pk).distinct()
        # Nếu là admin hoặc nhân viên thì xem tất cả
        if getattr(user, 'vaitro', None) in [0, 2]:
            return super().get_queryset()
        # Hành khách chỉ xem booking của mình
        return Datxe.objects.filter(manguoidung_id=user.pk)

    def get_serializer_class(self):
        # Luôn trả về BookingSerializer (đã có chitietdatxe trong fields)
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
                    "maca": 1,
                    "chitietdatxe": [
                        {"tenkhach": "Nguyen Van B", "sodienthoaikhach": "0987654321", "diemdon": 1, "diemtra": 2, "matuyenduong": 1, "trangthai": "Đã đặt"}
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
        booking = serializer.save(nguoidung=request.user)
        # Tạo các chi tiết đặt xe nếu có
        for chitiet in chitiet_data:
            chitiet['madatxe'] = booking.madatxe
            chitiet_serializer = BookingDetailSerializer(data=chitiet)
            chitiet_serializer.is_valid(raise_exception=True)
            chitiet_serializer.save()
        return Response(self.get_serializer(booking).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description="Tự động xếp hành khách vào ca tài xế còn chỗ. Chỉ cần cung cấp thông tin khách, hướng (1: Đà Nẵng đi Tam Kỳ, 2: Tam Kỳ đi Đà Nẵng), thời gian mong muốn. API sẽ tự xếp vào ca còn chỗ đầu tiên.",
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
        # Tìm ca còn chỗ
        from .models import Cataixe, Datxe, Chitietdatxe
        ca_list = Cataixe.objects.all().order_by('batdau')
        for ca in ca_list:
            xe = getattr(ca, 'maxe', None)
            sochongoi = getattr(xe, 'sochongoi', 0) if xe else 0
            # Đếm số khách đã đặt trong ca này, cùng hướng
            datxe_ids = Datxe.objects.filter(maca=ca.maca).values_list('madatxe', flat=True)
            sokhach = Chitietdatxe.objects.filter(madatxe_id__in=datxe_ids, diemdon=diemdon, diemtra=diemtra).count()
            if sochongoi > sokhach:
                # Tạo booking mới
                booking = Datxe.objects.create(manguoidung=request.user, diemdon=diemdon, diemtra=diemtra, maca=ca, matuyenduong=1)
                chitiet = Chitietdatxe.objects.create(madatxe=booking, tenkhach=tenkhach, sodienthoaikhach=sodienthoaikhach, diemdon=diemdon, diemtra=diemtra, matuyenduong=1, trangthai="Đã đặt")
                return Response(self.get_serializer(booking).data, status=status.HTTP_201_CREATED)
        return Response({"error": "Không còn ca nào còn chỗ phù hợp."}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Kiểm tra số chỗ còn lại trong một ca tài xế theo hướng và thời gian. Trả về tổng số chỗ, số khách đã đặt, số chỗ còn lại.",
        request={
            "type": "object",
            "properties": {
                "maca": {"type": "integer"},
                "huong": {"type": "integer", "description": "1: Đà Nẵng đi Tam Kỳ, 2: Tam Kỳ đi Đà Nẵng"}
            },
            "required": ["maca", "huong"]
        },
        responses={200: OpenApiExample('Kết quả', value={"sochongoi": 16, "sokhach": 10, "conlai": 6})},
        examples=[
            OpenApiExample(
                'Check slot mẫu',
                value={"maca": 1, "huong": 1},
                request_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['post'], url_path='check_slot', permission_classes=[IsAuthenticated])
    def check_slot(self, request):
        maca = int(request.data.get('maca'))
        huong = int(request.data.get('huong'))
        if huong == 1:
            diemdon, diemtra = 1, 2
        else:
            diemdon, diemtra = 2, 1
        from .models import Cataixe, Datxe, Chitietdatxe
        try:
            ca = Cataixe.objects.get(maca=maca)
            xe = getattr(ca, 'maxe', None)
            sochongoi = getattr(xe, 'sochongoi', 0) if xe else 0
            datxe_ids = Datxe.objects.filter(maca=ca.maca).values_list('madatxe', flat=True)
            sokhach = Chitietdatxe.objects.filter(madatxe_id__in=datxe_ids, diemdon=diemdon, diemtra=diemtra).count()
            return Response({"sochongoi": sochongoi, "sokhach": sokhach, "conlai": sochongoi - sokhach})
        except Cataixe.DoesNotExist:
            return Response({"error": "Không tìm thấy ca."}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        description="Tính hướng di chuyển giữa hai địa điểm (theo địa chỉ hoặc mã địa điểm). Hiện tại trả về mặc định 1 (Đà Nẵng đi Tam Kỳ).",
        request={
            "type": "object",
            "properties": {
                "diemdon": {"type": "integer", "description": "Mã địa điểm đón"},
                "diemtra": {"type": "integer", "description": "Mã địa điểm trả"}
            },
            "required": ["diemdon", "diemtra"]
        },
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
        request={
            "type": "object",
            "properties": {
                "madiadiem": {"type": "integer", "description": "Mã địa điểm"}
            },
            "required": ["madiadiem"]
        },
        responses={200: OpenApiExample('Kết quả', value={"huyen": "Tam Kỳ"})},
        examples=[
            OpenApiExample(
                'Tính huyện mẫu',
                value={"madiadiem": 1},
                request_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['post'], url_path='get_district', permission_classes=[IsAuthenticated])
    def get_district(self, request):
        madiadiem = int(request.data.get('madiadiem'))
        # Giả lập ánh xạ mã địa điểm sang huyện
        mapping = {1: "Tam Kỳ", 2: "Đà Nẵng", 3: "Thăng Bình", 4: "Quế Sơn", 5: "Điện Bàn"}
        huyen = mapping.get(madiadiem, "Không rõ")
        return Response({"huyen": huyen})

    @extend_schema(
        description="Tính giá tiền từ 2 địa điểm dựa vào huyện của từng địa điểm và bảng tuyến đường. Trả về giá nếu tìm thấy tuyến phù hợp.",
        request={
            "type": "object",
            "properties": {
                "diemdon": {"type": "integer", "description": "Mã địa điểm đón"},
                "diemtra": {"type": "integer", "description": "Mã địa điểm trả"}
            },
            "required": ["diemdon", "diemtra"]
        },
        responses={200: OpenApiExample('Kết quả', value={"giacuoc": 100000})},
        examples=[
            OpenApiExample(
                'Tính giá mẫu',
                value={"diemdon": 1, "diemtra": 2},
                request_only=True,
            ),
        ],
    )
    @action(detail=False, methods=['post'], url_path='get_price', permission_classes=[IsAuthenticated])
    def get_price(self, request):
        diemdon = int(request.data.get('diemdon'))
        diemtra = int(request.data.get('diemtra'))
        # Giả lập ánh xạ mã địa điểm sang huyện
        mapping = {1: "Tam Kỳ", 2: "Đà Nẵng", 3: "Thăng Bình", 4: "Quế Sơn", 5: "Điện Bàn"}
        huyen_don = mapping.get(diemdon, "")
        huyen_tra = mapping.get(diemtra, "")
        from .models import Tuyenduong
        tuyen = Tuyenduong.objects.filter(diemdon=huyen_don, diemtra=huyen_tra).first()
        if tuyen:
            return Response({"giacuoc": tuyen.giacuoc})
        return Response({"error": "Không tìm thấy tuyến phù hợp."}, status=status.HTTP_404_NOT_FOUND)



