from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import NguoiDung, Cataixe, Chitietdatxe, Danhgia, Datxe, Nhanvien, Tuyenduong, Xe, Taixe, Diadiem

class UserSerializer(serializers.ModelSerializer):
    vaitro = serializers.CharField(source='vaitro.tenvaitro', read_only=True)
    class Meta:
        model = NguoiDung
        fields = '__all__'

class XeSerializer(serializers.ModelSerializer):
    thongtin = serializers.SerializerMethodField()
    class Meta:
        model = Xe
        fields = '__all__'
    def get_thongtin(self, obj):
        return f"{obj.biensoxe} - {obj.sochongoi} chỗ"

class TaixeSerializer(serializers.ModelSerializer):
    hoten = serializers.CharField(source='mataixe.hoten', read_only=True)
    class Meta:
        model = Taixe
        fields = '__all__'

class DiadiemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diadiem
        fields = ['madiadiem', 'tendiadiem', 'vido', 'kinhdo']

class CataixeSerializer(serializers.ModelSerializer):
    maxe = XeSerializer(read_only=True)
    mataixe = TaixeSerializer(read_only=True)
    class Meta:
        model = Cataixe
        fields = '__all__'

class BookingDetailSerializer(serializers.ModelSerializer):
    diemdon = DiadiemSerializer(read_only=True)
    diemtra = DiadiemSerializer(read_only=True)
    matuyenduong = serializers.CharField(source='matuyenduong.diemdon', read_only=True)
    class Meta:
        model = Chitietdatxe
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    chitietdatxe = BookingDetailSerializer(many=True, read_only=True, source='chitietdatxe_set')
    diemdon = DiadiemSerializer(read_only=True)
    diemtra = DiadiemSerializer(read_only=True)
    maca = CataixeSerializer(read_only=True)
    manguoidung = UserSerializer(read_only=True)
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

class ShiftSerializer(serializers.ModelSerializer):
    maxe = XeSerializer(read_only=True)
    mataixe = TaixeSerializer(read_only=True)
    class Meta:
        model = Cataixe
        fields = '__all__'
