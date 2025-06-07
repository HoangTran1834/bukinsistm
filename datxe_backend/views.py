from rest_framework import viewsets
from .models import NguoiDung, Datxe, Chitietdatxe
from .serializers import UserSerializer, DatxeSerializer, ChitietdatxeSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = NguoiDung.objects.all()
    serializer_class = UserSerializer
    
class DatXeViewSet(viewsets.ModelViewSet):
    queryset = Datxe.objects.all()
    serializer_class = DatxeSerializer
