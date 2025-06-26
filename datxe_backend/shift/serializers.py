from rest_framework import serializers
from ..models import Ca, Chitietca, Taixe, NguoiDung, Xe, Huyen

class TaixeSerializer(serializers.ModelSerializer):
    # Thêm thông tin chi tiết từ NguoiDung
    hoten = serializers.CharField(source='mataixe.hoten', read_only=True)
    sodienthoai = serializers.CharField(source='mataixe.sodienthoai', read_only=True)
    
    class Meta:
        model = Taixe
        fields = ['mataixe', 'hoten', 'sodienthoai', 'cccd', 'trangthai']

class XeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Xe
        fields = ['maxe', 'biensoxe', 'loaixe', 'sochongoi']

class HuyenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Huyen
        fields = ['mahuyen', 'tenhuyen']

class CaSerializer(serializers.ModelSerializer):
    mahuyenxuatphat = HuyenSerializer(read_only=True)
    class Meta:
        model = Ca
        fields = '__all__'

class CaCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer cho tạo/cập nhật ca với mahuyenxuatphat có thể ghi"""
    
    mahuyenxuatphat_id = serializers.IntegerField(
        write_only=True, 
        help_text="Mã huyện xuất phát: 1=Tam Kỳ, 2=Đà Nẵng"
    )    
    class Meta:
        model = Ca
        fields = ['maca', 'gioxuatphat', 'ngayxuatphat', 'mahuyenxuatphat_id']
        read_only_fields = ['maca']
    
    def create(self, validated_data):
        mahuyenxuatphat_id = validated_data.pop('mahuyenxuatphat_id')
        ca = Ca.objects.create(
            mahuyenxuatphat_id=mahuyenxuatphat_id,
            **validated_data
        )
        return ca
    
    def update(self, instance, validated_data):
        if 'mahuyenxuatphat_id' in validated_data:
            instance.mahuyenxuatphat_id = validated_data.pop('mahuyenxuatphat_id')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class CreateShiftDetailSerializer(serializers.Serializer):
    """Serializer cho tạo chi tiết ca - input"""
    maxe = serializers.IntegerField(help_text="Mã xe")
    mataixe = serializers.IntegerField(help_text="Mã tài xế")

class ChitietcaSerializer(serializers.ModelSerializer):
    maca = CaSerializer(read_only=True)
    maxe = XeSerializer(read_only=True)
    mataixe = TaixeSerializer(read_only=True)
    class Meta:
        model = Chitietca
        fields = '__all__'

class CheckSlotInputSerializer(serializers.Serializer):
    maca = serializers.IntegerField()
    huong = serializers.IntegerField(help_text="1: Đà Nẵng đi Tam Kỳ, 2: Tam Kỳ đi Đà Nẵng")

class GetCaByDateInputSerializer(serializers.Serializer):
    """Serializer cho input API lấy ca theo ngày"""
    ngay = serializers.DateField(help_text="Ngày cần tìm ca (format: YYYY-MM-DD)")
    huyen_xuatphat = serializers.IntegerField(
        required=False, 
        help_text="Mã huyện xuất phát (1=Tam Kỳ, 2=Đà Nẵng). Bỏ trống để lấy tất cả"
    )

class AssignDriverInputSerializer(serializers.Serializer):
    """Serializer cho input API phân bổ tài xế cho ca"""
    ca_id = serializers.IntegerField(help_text="Mã ca cần phân bổ tài xế")