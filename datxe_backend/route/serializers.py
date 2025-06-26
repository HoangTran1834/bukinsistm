from rest_framework import serializers
from ..models import Diadiem, Tuyenduong, Huyen

class DiadiemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diadiem
        fields = ['madiadiem', 'tendiadiem', 'vido', 'kinhdo']

class CreateDiadiemSerializer(serializers.Serializer):
    """Serializer cho tạo địa điểm mới"""
    tendiadiem = serializers.CharField(max_length=255, help_text="Tên địa điểm")
    lat = serializers.FloatField(help_text="Vĩ độ (latitude)")
    lon = serializers.FloatField(help_text="Kinh độ (longitude)")
    
    def create(self, validated_data):
        # Lưu trực tiếp lat/lon dạng float
        diadiem = Diadiem.objects.create(
            tendiadiem=validated_data['tendiadiem'],
            vido=validated_data['lat'],
            kinhdo=validated_data['lon']
        )
        return diadiem

class HuyenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Huyen
        fields = ['mahuyen', 'tenhuyen']

class TuyenduongSerializer(serializers.ModelSerializer):
    huyendon = HuyenSerializer(read_only=True)
    huyentra = HuyenSerializer(read_only=True)
    class Meta:
        model = Tuyenduong
        fields = '__all__'

class GetDirectionInputSerializer(serializers.Serializer):
    diemdon = serializers.IntegerField()
    diemtra = serializers.IntegerField()

class GetDistrictInputSerializer(serializers.Serializer):
    madiadiem = serializers.IntegerField()

class GetTuyenDuongInputSerializer(serializers.Serializer):
    diachi_don = serializers.CharField(help_text="Địa chỉ điểm đón")
    diachi_tra = serializers.CharField(help_text="Địa chỉ điểm trả")

class GetTuyenDuongByCoordinatesInputSerializer(serializers.Serializer):
    lat_don = serializers.CharField(help_text="Vĩ độ điểm đón")
    lon_don = serializers.CharField(help_text="Kinh độ điểm đón")
    lat_tra = serializers.CharField(help_text="Vĩ độ điểm trả")
    lon_tra = serializers.CharField(help_text="Kinh độ điểm trả")

class GetPriceInputSerializer(serializers.Serializer):
    diachi_don = serializers.CharField(help_text="Địa chỉ điểm đón", required=False)
    diachi_tra = serializers.CharField(help_text="Địa chỉ điểm trả", required=False)
    lat_don = serializers.CharField(help_text="Vĩ độ điểm đón (nếu không dùng địa chỉ)", required=False)
    lon_don = serializers.CharField(help_text="Kinh độ điểm đón (nếu không dùng địa chỉ)", required=False)
    lat_tra = serializers.CharField(help_text="Vĩ độ điểm trả (nếu không dùng địa chỉ)", required=False)
    lon_tra = serializers.CharField(help_text="Kinh độ điểm trả (nếu không dùng địa chỉ)", required=False)

class GetHuyenInputSerializer(serializers.Serializer):
    lat = serializers.CharField(help_text="Vĩ độ")
    lon = serializers.CharField(help_text="Kinh độ")

class GetHuyenOutputSerializer(serializers.Serializer):
    mahuyen = serializers.IntegerField()
    tenhuyen = serializers.CharField()
    matched_field = serializers.CharField(required=False)
    matched_keyword = serializers.CharField(required=False)
    method = serializers.CharField(required=False)
    nominatim_data = serializers.JSONField(required=False)