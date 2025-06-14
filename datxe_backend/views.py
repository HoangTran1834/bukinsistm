from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .models import NguoiDung, Datxe, Cataixe, Chitietdatxe, Danhgia, Nhanvien, Tuyenduong
from .serializers import UserSerializer, SignupSerializer, LoginSerializer, ShiftSerializer, BookingSerializer, BookingDetailSerializer

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], url_path='signup')
    def signup(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Đăng ký thành công'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

class UserViewSet(viewsets.ModelViewSet):
    queryset = NguoiDung.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Chỉ cho phép user xem/sửa thông tin của chính mình
        return NguoiDung.objects.filter(pk=self.request.user.pk)

    @action(detail=False, methods=['get'], url_path='profile')
    def profile(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        # Luôn trả về user hiện tại
        instance = self.request.user
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        # Chỉ cho phép update user hiện tại
        instance = self.request.user
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

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

    def perform_create(self, serializer):
        serializer.save(nguoidung=self.request.user)



