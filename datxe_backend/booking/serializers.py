from rest_framework import serializers
from ..models import Chitietdatxe, Datxe, NguoiDung, Nhanvien, Diadiem, Tuyenduong, Ca, Chitietca, Taixe, Xe, Huyen

# Import các serializers cần thiết sẽ được định nghĩa lại tại đây để tránh circular import

# Tạm thời định nghĩa lại các serializers cần thiết để tránh circular import
class UserSerializer(serializers.ModelSerializer):
    vaitro = serializers.CharField(source='vaitro.tenvaitro', read_only=True)
    class Meta:
        model = NguoiDung
        fields = '__all__'

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

class TaixeSerializer(serializers.ModelSerializer):
    hoten = serializers.CharField(source='mataixe.hoten', read_only=True)
    sodienthoai = serializers.CharField(source='mataixe.sodienthoai', read_only=True)
    class Meta:
        model = Taixe
        fields = ['mataixe', 'hoten', 'sodienthoai', 'cccd', 'trangthai']

class XeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Xe
        fields = ['maxe', 'biensoxe', 'loaixe', 'sochongoi']

class CaSerializer(serializers.ModelSerializer):
    mahuyenxuatphat = HuyenSerializer(read_only=True)
    class Meta:
        model = Ca
        fields = '__all__'

class ChitietcaSerializer(serializers.ModelSerializer):
    maca = CaSerializer(read_only=True)
    maxe = XeSerializer(read_only=True)
    mataixe = TaixeSerializer(read_only=True)
    class Meta:
        model = Chitietca
        fields = '__all__'

# Serializers bổ sung cho booking
class CheckSlotInputSerializer(serializers.Serializer):
    machitietca = serializers.IntegerField()
    huong = serializers.IntegerField(help_text="1: Đà Nẵng đi Tam Kỳ, 2: Tam Kỳ đi Đà Nẵng")

class GetCaByDateInputSerializer(serializers.Serializer):
    """Serializer cho input API lấy ca theo ngày"""
    ngay = serializers.DateField(help_text="Ngày cần tìm ca (format: YYYY-MM-DD)")
    huyen_xuatphat = serializers.IntegerField(
        required=False, 
        help_text="Mã huyện xuất phát (1=Tam Kỳ, 2=Đà Nẵng). Bỏ trống để lấy tất cả"
    )

class ChitietdatxeInputSerializer(serializers.ModelSerializer):
    """Serializer cho input chi tiết đặt xe khi tạo booking - có thể có điểm đón/trả riêng"""
    class Meta:
        model = Chitietdatxe
        fields = ['tenkhach', 'sodienthoaikhach', 'diemdon', 'diemtra', 'soghe', 'ghichu']
        # Không bao gồm madatxe, machitietca, trangthai, matuyenduong - sẽ được tự động gán

class BookingDetailSerializer(serializers.ModelSerializer):
    diemdon = DiadiemSerializer(read_only=True)
    diemtra = DiadiemSerializer(read_only=True)
    matuyenduong = serializers.CharField(source='matuyenduong.huyendon', read_only=True)
    machitietca = ChitietcaSerializer(read_only=True)
    class Meta:
        model = Chitietdatxe
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    chitietdatxe = BookingDetailSerializer(many=True, read_only=True, source='chitietdatxe_set')
    diemdon = DiadiemSerializer(read_only=True)
    diemtra = DiadiemSerializer(read_only=True)
    maca = CaSerializer(read_only=True)  # thêm thông tin ca
    machitietca = ChitietcaSerializer(read_only=True)
    manguoidung = UserSerializer(read_only=True)
    manhanvien = serializers.SerializerMethodField()  # thêm thông tin nhân viên
    
    def get_manhanvien(self, obj):
        """Lấy thông tin nhân viên tạo booking"""
        if obj.manhanvien:
            return {
                'manhanvien': obj.manhanvien.manhanvien_id,
                'hoten': obj.manhanvien.manhanvien.hoten,
                'sodienthoai': obj.manhanvien.manhanvien.sodienthoai,
                'ngayvaolam': obj.manhanvien.ngayvaolam
            }
        return None
    
    class Meta:
        model = Datxe
        fields = '__all__'

class CreateBookingSerializer(serializers.ModelSerializer):
    """Serializer cho tạo booking mới - tự động tìm tuyến đường từ điểm đi và điểm đến"""
    chitietdatxe = ChitietdatxeInputSerializer(many=True, required=False)    
    class Meta:
        model = Datxe
        fields = ['madatxe', 'maca', 'diemdon', 'diemtra', 'soghe', 'ghichu', 'chitietdatxe']
        read_only_fields = ['madatxe']
        # Loại bỏ machitietca và matuyenduong - sẽ được tự động gán

    def create(self, validated_data):
        from ..views import RouteViewSet
        import requests
        
        print(f"🔧 [BOOKING] Bắt đầu tạo booking với data: {validated_data}")
        
        chitietdatxe_data = validated_data.pop('chitietdatxe', [])
        diemdon = validated_data['diemdon']
        diemtra = validated_data['diemtra']
        
        try:
            # Lấy tọa độ từ địa điểm đi và đến
            diemdon_obj = Diadiem.objects.get(pk=diemdon.madiadiem)
            diemtra_obj = Diadiem.objects.get(pk=diemtra.madiadiem)
            
            # Sử dụng trực tiếp vido, kinhdo (đã là float)
            lat_don = diemdon_obj.vido
            lon_don = diemdon_obj.kinhdo
            lat_tra = diemtra_obj.vido
            lon_tra = diemtra_obj.kinhdo            
            print(f"🔧 [BOOKING] Tọa độ điểm đón: ({lat_don}, {lon_don})")
            print(f"🔧 [BOOKING] Tọa độ điểm trả: ({lat_tra}, {lon_tra})")
            
            print(f"🔧 [BOOKING] Gọi RouteViewSet.find_route_by_coordinates trực tiếp với tọa độ: ({lat_don}, {lon_don}) -> ({lat_tra}, {lon_tra})")
            route_viewset = RouteViewSet()
            response = route_viewset.find_route_by_coordinates(lat_don, lon_don, lat_tra, lon_tra)
            print(f"🔧 [BOOKING] Response status: {response.status_code}")
            print(f"🔧 [BOOKING] Response data: {response.data}")
            
            if response.status_code == 200 and response.data.get('success'):
                tuyenduong_data = response.data.get('tuyenduong')
                if not tuyenduong_data:
                    raise serializers.ValidationError("Không tìm thấy tuyến đường phù hợp cho điểm đi và điểm đến này.")
                
                # Lấy object tuyến đường từ matuyenduong
                matuyenduong_id = tuyenduong_data.get('matuyenduong')
                matuyenduong = Tuyenduong.objects.get(pk=matuyenduong_id)
                validated_data['matuyenduong'] = matuyenduong
            else:
                raise serializers.ValidationError("Không tìm thấy tuyến đường phù hợp cho điểm đi và điểm đến này.")
        
        except Diadiem.DoesNotExist:
            raise serializers.ValidationError("Điểm đi hoặc điểm đến không tồn tại.")
        except Tuyenduong.DoesNotExist:
            raise serializers.ValidationError("Tuyến đường không tồn tại.")
        except Exception as e:
            print(f"🔧 [BOOKING] Lỗi trong quá trình tìm tuyến đường: {str(e)}")
            raise serializers.ValidationError(f"Lỗi khi tìm tuyến đường: {str(e)}")        
        
        # Tạo booking với user hiện tại, tự động gán trạng thái "Đã đặt"
        # thoigiandat tự động set khi tạo booking
        from django.utils import timezone
        booking = Datxe.objects.create(
            manguoidung=self.context['request'].user,
            trangthai="Đã đặt",
            thoigiandat=timezone.now(),
            **validated_data
        )
        
        print(f"🔧 [BOOKING] Đã tạo booking thành công với ID: {booking.madatxe}")
        
        # Tạo chi tiết đặt xe nếu có, tự động gán trạng thái "Đã đặt" và tìm tuyến đường cho từng chi tiết
        for chitiet_data in chitietdatxe_data:
            # Tìm tuyến đường cho chi tiết đặt xe này
            diemdon_ct = chitiet_data.get('diemdon')
            diemtra_ct = chitiet_data.get('diemtra')
            
            if diemdon_ct and diemtra_ct:
                try:                    
                    # Lấy tọa độ từ địa điểm đi và đến của chi tiết
                    diemdon_ct_obj = Diadiem.objects.get(pk=diemdon_ct.madiadiem)
                    diemtra_ct_obj = Diadiem.objects.get(pk=diemtra_ct.madiadiem)
                    
                    # Sử dụng trực tiếp vido, kinhdo (đã là float)
                    lat_don_ct = diemdon_ct_obj.vido
                    lon_don_ct = diemdon_ct_obj.kinhdo
                    lat_tra_ct = diemtra_ct_obj.vido
                    lon_tra_ct = diemtra_ct_obj.kinhdo
                    
                    # Gọi hàm find_route_by_coordinates trực tiếp
                    route_viewset = RouteViewSet()
                    response_ct = route_viewset.find_route_by_coordinates(lat_don_ct, lon_don_ct, lat_tra_ct, lon_tra_ct)
                    
                    if response_ct.status_code == 200 and response_ct.data.get('success'):
                        tuyenduong_ct_data = response_ct.data.get('tuyenduong')
                        if tuyenduong_ct_data:
                            matuyenduong_ct_id = tuyenduong_ct_data.get('matuyenduong')
                            matuyenduong_ct = Tuyenduong.objects.get(pk=matuyenduong_ct_id)
                            chitiet_data['matuyenduong'] = matuyenduong_ct
                except:
                    # Nếu không tìm được tuyến đường cho chi tiết, dùng tuyến đường của booking chính
                    chitiet_data['matuyenduong'] = validated_data.get('matuyenduong')
            
            Chitietdatxe.objects.create(
                madatxe=booking, 
                trangthai="Đã đặt",
                **chitiet_data
            )
        
        # Auto-assign: Tự động gọi assign_driver_for_shift cho ca chứa booking này
        print(f"🚌 [AUTO-ASSIGN] Booking {booking.madatxe} đã tạo thành công, bắt đầu auto-assign cho ca {booking.maca.maca}")
        try:
            from ..views import RouteViewSet
            route_viewset = RouteViewSet()
            
            # Tạo fake request để gọi assign_driver_for_shift
            class FakeRequest:
                def __init__(self, ca_id):
                    self.data = {'ca_id': ca_id}
            
            fake_request = FakeRequest(booking.maca.maca)
            assign_response = route_viewset.assign_driver_for_shift(fake_request)
            
            if assign_response.status_code == 200:
                print(f"🚌 [AUTO-ASSIGN] ✅ Thành công auto-assign cho ca {booking.maca.maca}")
                print(f"🚌 [AUTO-ASSIGN] {assign_response.data.get('message', '')}")
            else:
                print(f"🚌 [AUTO-ASSIGN] ⚠️ Không thể auto-assign cho ca {booking.maca.maca}: {assign_response.data}")
                
        except Exception as e:
            print(f"🚌 [AUTO-ASSIGN] ❌ Lỗi khi auto-assign cho ca {booking.maca.maca}: {str(e)}")
            # Không raise exception để không ảnh hưởng việc tạo booking
        
        return booking

class UpdateChitietdatxeSerializer(serializers.ModelSerializer):
    """Serializer cho việc cập nhật chi tiết đặt xe"""
    class Meta:
        model = Chitietdatxe
        fields = ['tenkhach', 'sodienthoaikhach', 'diemdon', 'diemtra', 'soghe', 'ghichu', 'trangthai']
        # Không cho phép sửa: machitiet, madatxe, machitietca, matuyenduong
    
    def update(self, instance, validated_data):
        """Cập nhật chi tiết đặt xe"""
        print(f"🔧 [UPDATE_CHITIET] Cập nhật chi tiết {instance.machitiet} với data: {validated_data}")
        
        # Cập nhật các trường được phép
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        print(f"✅ [UPDATE_CHITIET] Đã cập nhật chi tiết {instance.machitiet}")
        
        return instance

class CreateStaffBookingSerializer(serializers.ModelSerializer):
    """Serializer cho nhân viên tạo booking cho khách hàng"""
    chitietdatxe = ChitietdatxeInputSerializer(many=True, required=False)
    ma_khach = serializers.IntegerField(help_text="Mã khách hàng (maNguoiDung)")
    ma_nhanvien = serializers.IntegerField(help_text="Mã nhân viên tạo booking", required=False)
    
    class Meta:
        model = Datxe
        fields = ['madatxe', 'maca', 'diemdon', 'diemtra', 'soghe', 'ghichu', 'chitietdatxe', 'ma_khach', 'ma_nhanvien']
        read_only_fields = ['madatxe']

    def create(self, validated_data):
        from ..views import RouteViewSet
        import requests
        
        print(f"🔧 [STAFF_BOOKING] Bắt đầu tạo booking bởi nhân viên với data: {validated_data}")
        
        chitietdatxe_data = validated_data.pop('chitietdatxe', [])
        ma_khach = validated_data.pop('ma_khach')
        ma_nhanvien = validated_data.pop('ma_nhanvien', None)
        diemdon = validated_data['diemdon']
        diemtra = validated_data['diemtra']
        
        # Kiểm tra khách hàng tồn tại
        try:
            khach_hang = NguoiDung.objects.get(manguoidung=ma_khach)
            print(f"🔧 [STAFF_BOOKING] Khách hàng: {khach_hang.hoten} ({khach_hang.sodienthoai})")
        except NguoiDung.DoesNotExist:
            raise serializers.ValidationError(f"Không tìm thấy khách hàng với mã {ma_khach}")
        
        # Kiểm tra nhân viên (nếu có)
        nhan_vien = None
        if ma_nhanvien:
            try:
                nhan_vien = NguoiDung.objects.get(manguoidung=ma_nhanvien)
                if nhan_vien.vaitro_id not in [0, 2]:  # Không phải admin (0) hoặc nhân viên (2)
                    raise serializers.ValidationError(f"Người dùng {ma_nhanvien} không phải là nhân viên (vaitro_id: {nhan_vien.vaitro_id})")
                print(f"🔧 [STAFF_BOOKING] Nhân viên tạo: {nhan_vien.hoten} (vaitro_id: {nhan_vien.vaitro_id})")
            except NguoiDung.DoesNotExist:
                raise serializers.ValidationError(f"Không tìm thấy nhân viên với mã {ma_nhanvien}")
        
        try:
            # Lấy tọa độ từ địa điểm đi và đến (tương tự CreateBookingSerializer)
            diemdon_obj = Diadiem.objects.get(pk=diemdon.madiadiem)
            diemtra_obj = Diadiem.objects.get(pk=diemtra.madiadiem)
            
            lat_don = diemdon_obj.vido
            lon_don = diemdon_obj.kinhdo
            lat_tra = diemtra_obj.vido
            lon_tra = diemtra_obj.kinhdo
            print(f"🔧 [STAFF_BOOKING] Tọa độ điểm đón: ({lat_don}, {lon_don})")
            print(f"🔧 [STAFF_BOOKING] Tọa độ điểm trả: ({lat_tra}, {lon_tra})")
            
            # Tìm tuyến đường - sử dụng fallback đơn giản
            try:
                route_viewset = RouteViewSet()
                response = route_viewset.find_route_by_coordinates(lat_don, lon_don, lat_tra, lon_tra)
                
                if response.status_code == 200 and response.data.get('success'):
                    tuyenduong_data = response.data.get('tuyenduong')
                    if not tuyenduong_data:
                        raise Exception("Không tìm thấy tuyến đường phù hợp")
                    
                    matuyenduong_id = tuyenduong_data.get('matuyenduong')
                    matuyenduong = Tuyenduong.objects.get(pk=matuyenduong_id)
                    validated_data['matuyenduong'] = matuyenduong
                    print(f"🔧 [STAFF_BOOKING] Tìm thấy tuyến đường: {matuyenduong_id}")
                else:
                    raise Exception(f"API trả về lỗi: {response.data}")
                    
            except Exception as route_error:
                print(f"🔧 [STAFF_BOOKING] Lỗi tìm tuyến đường, sử dụng fallback: {str(route_error)}")
                
                # Fallback: Tìm tuyến đường mặc định (Đà Nẵng - Tam Kỳ)
                try:
                    # Giả sử ID 1 là tuyến Đà Nẵng - Tam Kỳ
                    default_route = Tuyenduong.objects.first()
                    if default_route:
                        validated_data['matuyenduong'] = default_route
                        print(f"🔧 [STAFF_BOOKING] Sử dụng tuyến đường mặc định: {default_route.matuyenduong}")
                    else:
                        raise serializers.ValidationError("Không có tuyến đường nào trong hệ thống")
                except Tuyenduong.DoesNotExist:
                    raise serializers.ValidationError("Không tìm thấy tuyến đường mặc định")
        
        except Diadiem.DoesNotExist:
            raise serializers.ValidationError("Điểm đi hoặc điểm đến không tồn tại.")
        except Tuyenduong.DoesNotExist:
            raise serializers.ValidationError("Tuyến đường không tồn tại.")
        except Exception as e:
            print(f"🔧 [STAFF_BOOKING] Lỗi trong quá trình tìm tuyến đường: {str(e)}")
            raise serializers.ValidationError(f"Lỗi khi tìm tuyến đường: {str(e)}")
          
        # Tạo booking với khách hàng được chỉ định
        from django.utils import timezone
        
        # Chuẩn bị data để tạo booking
        booking_data = {
            'manguoidung': khach_hang,  # Sử dụng khách hàng được chỉ định
            'trangthai': "Đã đặt",
            'thoigiandat': timezone.now(),
            **validated_data
        }
        
        # Thêm thông tin nhân viên nếu có
        if ma_nhanvien and nhan_vien:
            # Kiểm tra xem nhân viên có trong bảng Nhanvien không
            try:
                nhanvien_obj = Nhanvien.objects.get(manhanvien_id=ma_nhanvien)
                booking_data['manhanvien'] = nhanvien_obj
                print(f"🔧 [STAFF_BOOKING] Gán nhân viên vào booking: {nhan_vien.hoten}")
            except Nhanvien.DoesNotExist:
                print(f"🔧 [STAFF_BOOKING] ⚠️ Người dùng {ma_nhanvien} không có trong bảng Nhanvien, bỏ qua việc gán manhanvien")
        
        booking = Datxe.objects.create(**booking_data)
        
        print(f"🔧 [STAFF_BOOKING] Đã tạo booking thành công với ID: {booking.madatxe}")
        if nhan_vien:
            print(f"🔧 [STAFF_BOOKING] Được tạo bởi nhân viên: {nhan_vien.hoten}")
        
        # Tạo chi tiết đặt xe (tương tự CreateBookingSerializer)
        for chitiet_data in chitietdatxe_data:
            diemdon_ct = chitiet_data.get('diemdon')
            diemtra_ct = chitiet_data.get('diemtra')
            
            if diemdon_ct and diemtra_ct:
                try:
                    diemdon_ct_obj = Diadiem.objects.get(pk=diemdon_ct.madiadiem)
                    diemtra_ct_obj = Diadiem.objects.get(pk=diemtra_ct.madiadiem)
                    
                    lat_don_ct = diemdon_ct_obj.vido
                    lon_don_ct = diemdon_ct_obj.kinhdo
                    lat_tra_ct = diemtra_ct_obj.vido
                    lon_tra_ct = diemtra_ct_obj.kinhdo
                    
                    route_viewset = RouteViewSet()
                    response_ct = route_viewset.find_route_by_coordinates(lat_don_ct, lon_don_ct, lat_tra_ct, lon_tra_ct)
                    
                    if response_ct.status_code == 200 and response_ct.data.get('success'):
                        tuyenduong_ct_data = response_ct.data.get('tuyenduong')
                        if tuyenduong_ct_data:
                            matuyenduong_ct_id = tuyenduong_ct_data.get('matuyenduong')
                            matuyenduong_ct = Tuyenduong.objects.get(pk=matuyenduong_ct_id)
                            chitiet_data['matuyenduong'] = matuyenduong_ct
                except:
                    chitiet_data['matuyenduong'] = validated_data.get('matuyenduong')
            
            Chitietdatxe.objects.create(
                madatxe=booking, 
                trangthai="Đã đặt",
                **chitiet_data
            )
        
        # Auto-assign cho ca
        print(f"🚌 [AUTO-ASSIGN] Staff booking {booking.madatxe} đã tạo thành công, bắt đầu auto-assign cho ca {booking.maca.maca}")
        try:
            from ..views import RouteViewSet
            route_viewset = RouteViewSet()
            
            class FakeRequest:
                def __init__(self, ca_id):
                    self.data = {'ca_id': ca_id}
            
            fake_request = FakeRequest(booking.maca.maca)
            assign_response = route_viewset.assign_driver_for_shift(fake_request)
            
            if assign_response.status_code == 200:
                print(f"🚌 [AUTO-ASSIGN] ✅ Thành công auto-assign cho ca {booking.maca.maca}")
            else:
                print(f"🚌 [AUTO-ASSIGN] ⚠️ Không thể auto-assign cho ca {booking.maca.maca}: {assign_response.data}")
                
        except Exception as e:
            print(f"🚌 [AUTO-ASSIGN] ❌ Lỗi khi auto-assign cho ca {booking.maca.maca}: {str(e)}")
        
        return booking