from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from ..models import Datxe, Chitietdatxe, Chitietca, Diadiem, Ca
from .serializers import (
    BookingSerializer, CreateBookingSerializer, CreateStaffBookingSerializer,
    CheckSlotInputSerializer, DiadiemSerializer, CreateDiadiemSerializer,
    GetCaByDateInputSerializer, CaSerializer, UpdateChitietdatxeSerializer
)
from .schema import (
    create_booking_schema, create_staff_booking_schema, check_slot_schema,
    create_location_schema, get_locations_schema, get_ca_by_date_schema,
    update_chitietdatxe_schema
)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Datxe.objects.all()
    serializer_class = BookingSerializer

    def get_queryset(self):
        # Tạm thời chỉ allow tất cả xem được hết, các điều kiện còn lại comment lại
        return super().get_queryset()
        # user = self.request.user
        # # Nếu là tài xế (vaiTro=1) chỉ xem các booking có chi tiết ca tài xế thuộc về mình
        # if getattr(user, 'vaitro', None) == 1:
        #     return Datxe.objects.filter(machitietca__mataixe=user.pk).distinct()
        # # Nếu là admin hoặc nhân viên thì xem tất cả
        # if getattr(user, 'vaitro', None) in [0, 2]:
        #     return super().get_queryset()
        # # Hành khách chỉ xem booking của mình        
        # return Datxe.objects.filter(manguoidung_id=user.pk)    def get_serializer_class(self):
        if self.action == 'create':
            return CreateBookingSerializer
        return BookingSerializer
    
    @extend_schema(**create_booking_schema())
    def create(self, request, *args, **kwargs):
        # Logic tạo booking và tìm tuyến đường đã được chuyển vào CreateBookingSerializer
        # CreateBookingSerializer.create() cũng sẽ tự động gọi assign_driver_for_shift
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        
        # Trả về response với BookingSerializer để hiển thị đầy đủ thông tin
        response_serializer = BookingSerializer(booking)
        response_data = response_serializer.data
        
        # Thêm thông tin về auto-assign
        response_data['auto_assign_info'] = {
            'message': 'Hệ thống đã tự động phân bổ lại toàn bộ ca sau khi tạo booking',
            'ca_id': booking.maca.maca,            'note': 'Kiểm tra log để xem chi tiết quá trình auto-assign'
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @extend_schema(**create_staff_booking_schema())
    @action(detail=False, methods=['post'], url_path='staff', permission_classes=[IsAuthenticated])
    def create_staff_booking(self, request):
        """Nhân viên tạo booking cho khách hàng"""
        # Debug log để kiểm tra user và quyền
        print(f"🔐 [STAFF_BOOKING] User: {request.user.manguoidung if hasattr(request.user, 'manguoidung') else 'No ID'}")
        print(f"🔐 [STAFF_BOOKING] VaiTro: {request.user.vaitro if hasattr(request.user, 'vaitro') else 'No vaitro'}")
        print(f"🔐 [STAFF_BOOKING] User object: {request.user.__dict__ if hasattr(request.user, '__dict__') else 'No dict'}")
       
        data = request.data.copy()
        if 'ma_nhanvien' not in data or not data['ma_nhanvien']:
            data['ma_nhanvien'] = request.user.manguoidung
        
        serializer = CreateStaffBookingSerializer(data=data)
        if not serializer.is_valid():
            print(f"🚨 [STAFF_BOOKING] Validation errors: {serializer.errors}")
            return Response({
                'error': 'Dữ liệu không hợp lệ',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            booking = serializer.save()
            print(f"✅ [STAFF_BOOKING] Booking created successfully: {booking.madatxe}")
        except Exception as e:
            print(f"🚨 [STAFF_BOOKING] Error creating booking: {str(e)}")
            return Response({
                'error': 'Lỗi khi tạo booking',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Trả về response với BookingSerializer để hiển thị đầy đủ thông tin
        response_serializer = BookingSerializer(booking)
        response_data = response_serializer.data
        
        # Thêm thông tin về staff booking
        response_data['staff_booking_info'] = {
            'message': 'Booking được tạo bởi nhân viên',
            'ma_khach': data['ma_khach'],
            'ma_nhanvien': data['ma_nhanvien'],
            'auto_assign_info': {
                'message': 'Hệ thống đã tự động phân bổ lại toàn bộ ca sau khi tạo booking',
                'ca_id': booking.maca.maca,
                'note': 'Kiểm tra log để xem chi tiết quá trình auto-assign'            }
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @extend_schema(**check_slot_schema())
    @action(detail=False, methods=['post'], url_path='check_slot', permission_classes=[IsAuthenticated])
    def check_slot(self, request):
        machitietca = int(request.data.get('machitietca'))
        huong = int(request.data.get('huong'))
        if huong == 1:
            diemdon, diemtra = 1, 2
        else:
            diemdon, diemtra = 2, 1
        try:
            chitietca = Chitietca.objects.get(machitietca=machitietca)
            xe = getattr(chitietca, 'maxe', None)
            sochongoi = getattr(xe, 'sochongoi', 0) if xe else 0
            datxe_ids = Datxe.objects.filter(machitietca=chitietca).values_list('madatxe', flat=True)
            sokhach = Chitietdatxe.objects.filter(madatxe_id__in=datxe_ids, diemdon=diemdon, diemtra=diemtra).count()
            return Response({"sochongoi": sochongoi, "sokhach": sokhach, "conlai": sochongoi - sokhach})
        except Chitietca.DoesNotExist:            return Response({"error": "Không tìm thấy chi tiết ca."}, status=status.HTTP_404_NOT_FOUND)
    
    @extend_schema(**create_location_schema())
    @action(detail=False, methods=['post'], url_path='create_location')
    def create_location(self, request):
        """Tạo địa điểm mới"""
        serializer = CreateDiadiemSerializer(data=request.data)
        if serializer.is_valid():
            diadiem = serializer.save()
            result_serializer = DiadiemSerializer(diadiem)
            return Response({
                'message': 'Tạo địa điểm thành công',
                'madiadiem': diadiem.madiadiem,                'data': result_serializer.data            
                }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(**get_locations_schema())
    @action(detail=False, methods=['get'], url_path='locations')
    def get_locations(self, request):
        """Lấy danh sách tất cả địa điểm"""
        locations = Diadiem.objects.all()
        serializer = DiadiemSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(**get_ca_by_date_schema())
    @action(detail=False, methods=['post'], url_path='get_ca_by_date')
    def get_ca_by_date(self, request):
        """Lấy danh sách ca theo ngày"""
        serializer = GetCaByDateInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        ngay = serializer.validated_data['ngay']
        huyen_xuatphat = serializer.validated_data.get('huyen_xuatphat')
        
        print(f"🔍 [GET_CA] Tìm ca theo ngày: {ngay}")
        if huyen_xuatphat:
            print(f"🔍 [GET_CA] Lọc theo huyện xuất phát: {huyen_xuatphat}")
        
        # Query ca theo ngày
        queryset = Ca.objects.filter(ngayxuatphat=ngay)
        
        # Lọc theo huyện xuất phát nếu có
        if huyen_xuatphat:
            queryset = queryset.filter(mahuyenxuatphat=huyen_xuatphat)
        
        # Sắp xếp theo giờ xuất phát
        queryset = queryset.order_by('gioxuatphat')
        
        print(f"🔍 [GET_CA] Tìm thấy {queryset.count()} ca")
        
        ca_serializer = CaSerializer(queryset, many=True)
        return Response({
            'message': f'Tìm thấy {queryset.count()} ca trong ngày {ngay}',
            'ngay': ngay,
            'huyen_xuatphat': huyen_xuatphat,
            'data': ca_serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['put'], url_path='detail/(?P<chitiet_id>[^/.]+)')
    def update_booking_detail(self, request, chitiet_id=None):
        """
        Cập nhật thông tin chi tiết đặt xe
        Endpoint: PUT /api/booking/detail/{chitiet_id}/
        """
        try:
            chitiet = Chitietdatxe.objects.get(machitiet=chitiet_id)
        except Chitietdatxe.DoesNotExist:
            return Response({
                'error': 'Không tìm thấy chi tiết đặt xe'
            }, status=status.HTTP_404_NOT_FOUND)
                
        serializer = UpdateChitietdatxeSerializer(chitiet, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Cập nhật chi tiết đặt xe thành công',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)