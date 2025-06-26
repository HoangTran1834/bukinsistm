from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from ..models import Ca, Chitietca, Datxe, Chitietdatxe, Taixe, Xe
from .serializers import CaSerializer, CaCreateUpdateSerializer, TaixeSerializer, XeSerializer
from .schema import create_shift_schema, list_shifts_schema, update_shift_schema, delete_shift_schema, create_shift_detail_schema

class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Ca.objects.all()
    serializer_class = CaSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        # Sử dụng serializer khác nhau cho create/update vs list/retrieve
        if self.action in ['create', 'update', 'partial_update']:
            return CaCreateUpdateSerializer
        return CaSerializer

    def get_queryset(self):
        # Tất cả user đã đăng nhập đều được xem        
        return super().get_queryset()
    
    @extend_schema(**create_shift_schema())
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ca_instance = serializer.save()
        
        # Sử dụng CaSerializer để trả về đầy đủ thông tin
        response_serializer = CaSerializer(ca_instance)
        return Response({
            "message": "Tạo ca thành công",
            "maca": ca_instance.maca,
            "data": response_serializer.data
        }, status=status.HTTP_201_CREATED)

    @extend_schema(**list_shifts_schema())
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(**update_shift_schema())
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(**update_shift_schema())
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)    
    
    @extend_schema(**delete_shift_schema())
    def destroy(self, request, *args, **kwargs):
        """Xóa ca (chỉ cho phép xóa ca chưa có chi tiết hoặc booking)"""
        ca = self.get_object()
        
        # Kiểm tra xem ca có chi tiết không
        chitiet_count = Chitietca.objects.filter(maca=ca).count()
        if chitiet_count > 0:
            return Response({
                'error': f'Không thể xóa ca này vì có {chitiet_count} chi tiết ca đang được sử dụng',
                'suggestion': 'Hãy xóa tất cả chi tiết ca trước khi xóa ca'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        ca_info = {
            'maca': ca.maca,
            'gioxuatphat': str(ca.gioxuatphat),
            'ngayxuatphat': str(ca.ngayxuatphat),
            'huyen': ca.mahuyenxuatphat.tenhuyen if ca.mahuyenxuatphat else None
        }
        
        ca.delete()
        
        return Response({
            'message': 'Xóa ca thành công',
            'deleted_ca': ca_info
        })

    @action(detail=False, methods=['get'], url_path='taixe')
    def get_drivers(self, request):
        """Lấy danh sách tài xế"""
        drivers = Taixe.objects.all()
        serializer = TaixeSerializer(drivers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='xe')
    def get_vehicles(self, request):
        """Lấy danh sách xe"""
        vehicles = Xe.objects.all()
        serializer = XeSerializer(vehicles, many=True)
        return Response(serializer.data)    
      
    @extend_schema(**create_shift_detail_schema())
    @action(detail=True, methods=['post', 'get', 'delete'], url_path='chitiet')
    def manage_shift_details(self, request, pk=None):
        """
        Quản lý chi tiết ca (gán tài xế và xe vào ca)
        - POST: Tạo chi tiết ca mới
        - GET: Lấy danh sách chi tiết ca
        - DELETE: Xóa chi tiết ca (cần chitietca_id trong body)
        """
        ca = self.get_object()
        
        if request.method == 'POST':
            return self._create_shift_detail(request, ca)
        elif request.method == 'GET':
            return self._get_shift_details(request, ca)
        elif request.method == 'DELETE':
            return self._delete_shift_detail(request, ca)
    
    def _create_shift_detail(self, request, ca):
        """Tạo chi tiết ca mới"""
        maxe = request.data.get('maxe')
        mataixe = request.data.get('mataixe')
        
        if not maxe or not mataixe:
            return Response({
                'error': 'Cần cung cấp cả maxe và mataixe'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Kiểm tra xe và tài xế có tồn tại không
        try:
            xe = Xe.objects.get(maxe=maxe)
            taixe = Taixe.objects.get(mataixe=mataixe)
        except Xe.DoesNotExist:
            return Response({'error': 'Xe không tồn tại'}, status=status.HTTP_400_BAD_REQUEST)
        except Taixe.DoesNotExist:
            return Response({'error': 'Tài xế không tồn tại'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Kiểm tra xe hoặc tài xế đã được gán cho ca này chưa
        existing_xe = Chitietca.objects.filter(maca=ca, maxe=xe).exists()
        existing_taixe = Chitietca.objects.filter(maca=ca, mataixe=taixe).exists()
        
        if existing_xe:
            return Response({
                'error': f'Xe {xe.biensoxe} đã được gán cho ca này'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if existing_taixe:
            return Response({
                'error': f'Tài xế {taixe.mataixe.hoten} đã được gán cho ca này'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Tạo chi tiết ca
        chitiet_ca = Chitietca.objects.create(
            maca=ca,
            maxe=xe,
            mataixe=taixe
        )
        
        # Trả về với thông tin chi tiết
        return Response({
            'message': 'Tạo chi tiết ca thành công',
            'data': {
                'machitietca': chitiet_ca.machitietca,
                'maca': chitiet_ca.maca.maca,
                'xe_info': {
                    'maxe': xe.maxe,
                    'biensoxe': xe.biensoxe,
                    'loaixe': xe.loaixe,
                    'sochongoi': xe.sochongoi,
                    'bienso_color': xe.mau if hasattr(xe, 'mau') else None
                },
                'taixe_info': {
                    'mataixe': taixe.mataixe_id,
                    'hoten': taixe.mataixe.hoten,
                    'sodienthoai': taixe.mataixe.sodienthoai,
                    'cccd': taixe.cccd,
                    'gplx': taixe.gplx,
                    'trangthai': taixe.trangthai
                }
            }
        }, status=status.HTTP_201_CREATED)
    
    def _get_shift_details(self, request, ca):
        """Lấy danh sách chi tiết ca với thông tin chi tiết tài xế và xe"""
        chitiet_ca_list = Chitietca.objects.filter(maca=ca).select_related('maxe', 'mataixe__mataixe')
        
        if not chitiet_ca_list.exists():
            return Response({
                'message': 'Ca này chưa có chi tiết nào',
                'ca_info': {
                    'maca': ca.maca,
                    'gioxuatphat': str(ca.gioxuatphat),
                    'ngayxuatphat': str(ca.ngayxuatphat)
                },
                'data': []
            })
        
        result = []
        for chitiet in chitiet_ca_list:
            xe = chitiet.maxe
            taixe = chitiet.mataixe
            
            result.append({
                'machitietca': chitiet.machitietca,
                'maca': chitiet.maca.maca,
                'xe_info': {
                    'maxe': xe.maxe,
                    'biensoxe': xe.biensoxe,
                    'loaixe': xe.loaixe,
                    'sochongoi': xe.sochongoi
                },                
                'taixe_info': {
                    'mataixe': taixe.mataixe_id,
                    'hoten': taixe.mataixe.hoten,
                    'sodienthoai': taixe.mataixe.sodienthoai,
                    'email': taixe.mataixe.email,
                    'cccd': taixe.cccd,
                    'trangthai': taixe.trangthai
                }
            })
        
        return Response({
            'message': f'Tìm thấy {len(result)} chi tiết ca',
            'ca_info': {
                'maca': ca.maca,
                'gioxuatphat': str(ca.gioxuatphat),
                'ngayxuatphat': str(ca.ngayxuatphat),
                'huyen_xuat_phat': ca.mahuyenxuatphat_id
            },
            'data': result
        })
    
    def _delete_shift_detail(self, request, ca):
        """Xóa chi tiết ca"""
        chitietca_id = request.data.get('chitietca_id')
        
        if not chitietca_id:
            return Response({
                'error': 'Cần cung cấp chitietca_id để xóa'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            chitiet_ca = Chitietca.objects.get(
                machitietca=chitietca_id,
                maca=ca
            )
            
            # Lưu thông tin trước khi xóa
            xe_info = {
                'biensoxe': chitiet_ca.maxe.biensoxe,
                'maxe': chitiet_ca.maxe.maxe
            }
            taixe_info = {
                'hoten': chitiet_ca.mataixe.mataixe.hoten,
                'mataixe': chitiet_ca.mataixe.mataixe_id
            }
            
            # Kiểm tra xem có booking nào đã được gán cho chi tiết ca này chưa
            bookings_count = Datxe.objects.filter(machitietca=chitiet_ca).count()
            booking_details_count = Chitietdatxe.objects.filter(machitietca=chitiet_ca).count()
            
            if bookings_count > 0 or booking_details_count > 0:
                return Response({
                    'error': f'Không thể xóa chi tiết ca này vì đã có {bookings_count} booking và {booking_details_count} chi tiết booking được gán',
                    'suggestion': 'Hãy chuyển các booking sang chi tiết ca khác trước khi xóa'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            chitiet_ca.delete()
            
            return Response({
                'message': 'Xóa chi tiết ca thành công',
                'deleted_info': {
                    'chitietca_id': chitietca_id,
                    'xe': xe_info,
                    'taixe': taixe_info
                }
            })
            
        except Chitietca.DoesNotExist:
            return Response({
                'error': f'Không tìm thấy chi tiết ca {chitietca_id} trong ca {ca.maca}'
            }, status=status.HTTP_404_NOT_FOUND)