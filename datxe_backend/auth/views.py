from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError, AccessToken
from drf_spectacular.utils import extend_schema, OpenApiExample
from ..models_access_blacklist import BlacklistedAccessToken
from ..models import NguoiDung
from .serializers import (
    SignupSerializer, LoginSerializer, 
    OTPRequestSerializer, OTPVerifySerializer, ResetPasswordSerializer,
    UserProfileSerializer, UserSearchSerializer, UserUpdateSerializer
)
from .schema import (
    signup_schema, login_schema, logout_schema, reset_password_schema,
    sms_signup_verify_schema,
    get_profile_schema, search_user_schema, update_profile_schema
)
from .sms_service import SMSOTPService

def is_staff_user(request):
    """Helper function to check if user is staff by parsing token manually"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return False
    
    try:
        token_str = auth_header.replace('Bearer ', '')
        token = AccessToken(token_str)
        user_id = token['user_id']
        user = NguoiDung.objects.get(pk=user_id)
        return user.vaitro_id in [0, 2]  # Admin hoặc nhân viên
    except Exception:
        return False

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    @extend_schema(**signup_schema())
    @action(detail=False, methods=['post'], url_path='signup')
    def signup(self, request):
        # Kiểm tra xem có phải staff đang gọi không
        if is_staff_user(request):
            # Staff tạo tài khoản trực tiếp (không cần SMS)
            serializer = SignupSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    user = serializer.save()
                    return Response({
                        'message': 'Tạo tài khoản thành công',
                        'user': {
                            'id': user.manguoidung,
                            'hoten': user.hoten,
                            'sodienthoai': user.sodienthoai,
                            'vaitro': user.vaitro_id
                        }
                    }, status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response({
                        'error': f'Lỗi tạo tài khoản: {str(e)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # User thường - yêu cầu SMS OTP
            serializer = OTPRequestSerializer(data=request.data)
            if serializer.is_valid():
                phone = serializer.validated_data['sodienthoai']
                
                # Lưu toàn bộ request data để xử lý sau khi verify OTP
                request_data = {
                    'hoten': request.data.get('hoten', ''),
                    'email': request.data.get('email', ''),
                    'password': request.data.get('password', '')
                }
                
                result = SMSOTPService.send_otp(phone, 'signup', request_data)
                if result['success']:
                    return Response({
                        'message': 'OTP đã được gửi đến số điện thoại của bạn',
                        'phone': phone,
                        'expires_in': result.get('expires_in', 300),
                        'requires_otp': True
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'error': result['message']
                    }, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @extend_schema(**login_schema())
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        # Kiểm tra xem có password không
        password = request.data.get('password')
        if password:
            # Traditional password login
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
            return Response({
                "error": "Thông tin đăng nhập không hợp lệ",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # SMS OTP login
            serializer = OTPRequestSerializer(data=request.data)
            if serializer.is_valid():
                phone = serializer.validated_data['sodienthoai']
                # Kiểm tra phone phải tồn tại để login
                if not NguoiDung.objects.filter(sodienthoai=phone).exists():
                    return Response({
                        'error': 'Số điện thoại chưa được đăng ký'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Lưu request data cho login (chỉ cần phone)
                request_data = {'sodienthoai': phone}
                
                result = SMSOTPService.send_otp(phone, 'login', request_data)
                if result['success']:
                    return Response({
                        'message': 'OTP đã được gửi đến số điện thoại của bạn',
                        'phone': phone,
                        'expires_in': result.get('expires_in', 300),
                        'requires_otp': True
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'error': result['message']
                    }, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            return Response({"detail": "Đăng xuất thành công."}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({"error": "Token không hợp lệ hoặc đã bị thu hồi."}, status=status.HTTP_400_BAD_REQUEST)


    @extend_schema(**reset_password_schema())
    @action(detail=False, methods=['post'], url_path='reset_pw')
    def reset_pw(self, request):
        """Reset password - yêu cầu SMS OTP với password mới"""
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['sodienthoai']
            password = serializer.validated_data['password']
            
            # Lưu request data cho reset password (bao gồm password mới)
            request_data = {
                'sodienthoai': phone,
                'password': password
            }
            
            result = SMSOTPService.send_otp(phone, 'reset_password', request_data)
            if result['success']:
                return Response({
                    'message': 'OTP đã được gửi đến số điện thoại của bạn',
                    'phone': phone,
                    'expires_in': result.get('expires_in', 300),
                    'requires_otp': True
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': result['message']
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @extend_schema(**sms_signup_verify_schema())
    @action(detail=False, methods=['post'], url_path='verify')
    def verify(self, request):
        """Xác thực OTP và kích hoạt dữ liệu đã lưu"""
        phone = request.data.get('sodienthoai')
        otp = request.data.get('otp')
        
        if not phone or not otp:
            return Response({
                'error': 'Thiếu thông tin số điện thoại hoặc OTP'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Xác thực OTP và lấy dữ liệu đã lưu
        verify_result = SMSOTPService.verify_otp(phone, otp)
        
        if not verify_result['success']:
            return Response({
                'error': verify_result['message']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        action_type = verify_result['action_type']
        request_data = verify_result['request_data']
        
        # Xử lý theo loại action
        if action_type == 'signup':
            # Tạo user mới với dữ liệu đã lưu
            # Thêm password từ verify request nếu cần
            password = request.data.get('password') or request_data.get('password')
            hoten = request.data.get('hoten') or request_data.get('hoten')
            email = request.data.get('email') or request_data.get('email')
            
            if not password or not hoten:
                return Response({
                    'error': 'Thiếu thông tin bắt buộc: họ tên và mật khẩu'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                user = NguoiDung.objects.create_user(
                    sodienthoai=phone,
                    hoten=hoten,
                    password=password,
                    email=email or ''
                )
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'Đăng ký thành công',
                    'user': {
                        'id': user.manguoidung,
                        'hoten': user.hoten,
                        'sodienthoai': user.sodienthoai,
                        'vaitro': user.vaitro_id
                    },
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'error': f'Lỗi tạo tài khoản: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        elif action_type == 'login':
            # Đăng nhập user hiện tại
            try:
                user = NguoiDung.objects.get(sodienthoai=phone)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'Đăng nhập thành công',
                    'user': {
                        'id': user.manguoidung,
                        'hoten': user.hoten,
                        'sodienthoai': user.sodienthoai,
                        'vaitro': user.vaitro_id
                    },
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                }, status=status.HTTP_200_OK)
            except NguoiDung.DoesNotExist:
                return Response({
                    'error': 'Số điện thoại không tồn tại'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        elif action_type == 'reset_password':
            # Đặt lại mật khẩu với password đã lưu
            new_password = request_data.get('password')
            if not new_password:
                return Response({
                    'error': 'Dữ liệu mật khẩu mới bị thiếu'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                user = NguoiDung.objects.get(sodienthoai=phone)
                user.set_password(new_password)
                user.save()
                return Response({
                    'message': 'Đặt lại mật khẩu thành công'
                }, status=status.HTTP_200_OK)
            except NguoiDung.DoesNotExist:
                return Response({
                    'error': 'Số điện thoại không tồn tại'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response({
                'error': 'Loại yêu cầu không hợp lệ'
            }, status=status.HTTP_400_BAD_REQUEST)

    # Profile Management Endpoints
    @extend_schema(**get_profile_schema())
    @action(detail=False, methods=['get'], url_path='profile', permission_classes=[IsAuthenticated])
    def get_profile(self, request):
        """Lấy thông tin profile của user hiện tại"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(**search_user_schema())
    @action(detail=False, methods=['post'], url_path='search-user', permission_classes=[IsAuthenticated])
    def search_user(self, request):
        """Tìm kiếm user theo ID hoặc số điện thoại"""
        serializer = UserSearchSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data.get('manguoidung')
            phone = serializer.validated_data.get('sodienthoai')
            
            try:
                if user_id:
                    user = NguoiDung.objects.get(manguoidung=user_id)
                else:
                    user = NguoiDung.objects.get(sodienthoai=phone)
                
                # Ẩn email nếu không phải bản thân
                user_data = UserProfileSerializer(user).data
                if request.user.manguoidung != user.manguoidung:
                    user_data.pop('email', None)
                
                return Response(user_data, status=status.HTTP_200_OK)
                
            except NguoiDung.DoesNotExist:
                return Response({
                    'error': 'Không tìm thấy người dùng'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(**update_profile_schema())
    @action(detail=False, methods=['put', 'patch'], url_path='update-profile', permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """Cập nhật thông tin cá nhân"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Trả về thông tin đầy đủ sau khi update
            profile_data = UserProfileSerializer(request.user).data
            return Response({
                'message': 'Cập nhật thông tin thành công',
                'user': profile_data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)