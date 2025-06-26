from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import NguoiDung

class SignupSerializer(serializers.Serializer):
    hoten = serializers.CharField(required=True)
    sodienthoai = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'}, required=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)

    def validate_sodienthoai(self, value):
        if NguoiDung.objects.filter(sodienthoai=value).exists():
            raise serializers.ValidationError("Số điện thoại này đã được đăng ký.")
        return value
        
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = NguoiDung.objects.create_user(password=password, **validated_data)
        return user
    
class LoginSerializer(serializers.Serializer):
    sodienthoai = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, data):
        user = authenticate(username=data['sodienthoai'], password=data['password'])
        
        if not user or not user.is_active:
            raise serializers.ValidationError("Sai thông tin đăng nhập")

        token = RefreshToken.for_user(user)
        return {
            'access': str(token.access_token),
            'refresh': str(token),
        }

class LogoutInputSerializer(serializers.Serializer):
    refresh = serializers.CharField(help_text="Refresh token cần thu hồi")

class ResetPasswordSerializer(serializers.Serializer):
    """Yêu cầu đặt lại mật khẩu"""
    sodienthoai = serializers.CharField(max_length=15, help_text="Số điện thoại đã đăng ký")
    password = serializers.CharField(min_length=6, write_only=True, style={'input_type': 'password'}, help_text="Mật khẩu mới")

    def validate_sodienthoai(self, value):
        if not NguoiDung.objects.filter(sodienthoai=value).exists():
            raise serializers.ValidationError("Số điện thoại này chưa được đăng ký.")
        return value

# SMS OTP Serializers
class OTPRequestSerializer(serializers.Serializer):
    """Yêu cầu OTP"""
    sodienthoai = serializers.CharField(max_length=15)

    def validate_sodienthoai(self, value):
        # Kiểm tra cho signup: số điện thoại chưa tồn tại
        # Kiểm tra cho login: số điện thoại đã tồn tại
        # Logic sẽ được xử lý trong view
        return value

class OTPVerifySerializer(serializers.Serializer):
    """Xác thực OTP"""
    sodienthoai = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6, min_length=6)

# Profile Serializers
class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer để hiển thị thông tin profile user"""
    vaitro = serializers.CharField(source='get_vaitro_display', read_only=True)
    
    class Meta:
        model = NguoiDung
        fields = ['manguoidung', 'hoten', 'sodienthoai', 'email', 'vaitro']
        read_only_fields = ['manguoidung', 'sodienthoai', 'vaitro']

class UserSearchSerializer(serializers.Serializer):
    """Serializer để tìm kiếm user theo ID hoặc phone"""
    manguoidung = serializers.IntegerField(required=False, help_text="ID người dùng")
    sodienthoai = serializers.CharField(max_length=15, required=False, help_text="Số điện thoại")
    
    def validate(self, data):
        if not data.get('manguoidung') and not data.get('sodienthoai'):
            raise serializers.ValidationError("Cần cung cấp ít nhất một trong hai: ID hoặc số điện thoại")
        return data

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer để cập nhật thông tin cá nhân"""
    
    class Meta:
        model = NguoiDung
        fields = ['hoten', 'email']