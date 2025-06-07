from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import NguoiDung, Cataixe, Chitietdatxe, Danhgia, Datxe, Nhanvien, Tuyenduong

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = NguoiDung
        fields = '__all__'
               
class DatxeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Datxe
        fields = '__all__'
        
class SignupSerializer(serializers.Serializer):
    hoten = serializers.CharField(required=True)
    sodienthoai = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'}, required=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = NguoiDung
        fields = ['hoten', 'sodienthoai', 'password', 'email']
        
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

