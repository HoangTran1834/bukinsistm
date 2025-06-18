from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import NguoiDung, Ca, Chitietca, Chitietdatxe, Danhgia, Datxe, Nhanvien, Tuyenduong, Xe, Taixe, Diadiem, Huyen

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

class DiadiemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diadiem
        fields = ['madiadiem', 'tendiadiem', 'vido', 'kinhdo']

class CreateDiadiemSerializer(serializers.Serializer):
    """Serializer cho tạo địa điểm mới"""
    tendiadiem = serializers.CharField(max_length=100, help_text="Tên địa điểm")
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
        from .views import RouteViewSet
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
            raise serializers.ValidationError(f"Lỗi khi tìm tuyến đường: {str(e)}")        # Tạo booking với user hiện tại, tự động gán trạng thái "Đã đặt"
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
            from .views import RouteViewSet
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

class CheckSlotInputSerializer(serializers.Serializer):
    machitietca = serializers.IntegerField(help_text="Mã chi tiết ca cần kiểm tra")
    huong = serializers.IntegerField(help_text="1: Đà Nẵng đi Tam Kỳ, 2: Tam Kỳ đi Đà Nẵng")

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

class TuyenduongSerializer(serializers.ModelSerializer):
    huyendon = HuyenSerializer(read_only=True)
    huyentra = HuyenSerializer(read_only=True)
    class Meta:
        model = Tuyenduong
        fields = '__all__'
        
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
