from rest_framework import serializers
from .models import NguoiDung, Cataixe, Chitietdatxe, Danhgia, Datxe, Nhanvien, Tuyenduong

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = NguoiDung
        fields = '__all__'
               
class DatxeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Datxe
        fields = '__all__'
        

