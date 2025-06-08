from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .models import NguoiDung, Datxe
from .serializers import UserSerializer, DatxeSerializer, SignupSerializer, LoginSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = NguoiDung.objects.all()
    serializer_class = UserSerializer

    

    def get_serializer_class(self):
        if self.action == 'signup':
            return SignupSerializer
        if self.action == 'login':
            return LoginSerializer
        if self.action == 'logout':
            class LogoutSerializer(serializers.Serializer):
                refresh = serializers.CharField()
            return LogoutSerializer
        return super().get_serializer_class()

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

