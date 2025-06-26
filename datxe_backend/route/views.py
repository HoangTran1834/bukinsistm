from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample
from ..models import Tuyenduong, Ca, Chitietca, Datxe, Chitietdatxe
from .serializers import (
    TuyenduongSerializer, GetDirectionInputSerializer, AssignDriverInputSerializer,
    GetHuyenInputSerializer, GetHuyenOutputSerializer, GetTuyenDuongByCoordinatesInputSerializer
)
from .schema import (
    get_price_schema, get_tuyen_duong_by_coordinates_schema, SearchAddressInputSerializer, 
    ReverseGeocodeInputSerializer, list_routes_schema, search_address_schema, 
    reverse_geocode_schema, get_huyen_schema, get_direction_schema, assign_driver_for_shift_schema
)
import requests
import math
import json

class RouteViewSet(viewsets.ViewSet):    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(**list_routes_schema())
    @action(detail=False, methods=['get'], url_path='routes')
    def list_routes(self, request):
        if request.user.vaitro != 0:
            return Response({"error": "Chỉ admin mới có quyền truy cập."}, status=status.HTTP_403_FORBIDDEN)
        routes = Tuyenduong.objects.all()
        serializer = TuyenduongSerializer(routes, many=True)
        return Response(serializer.data)

    @extend_schema(**get_price_schema())
    @action(detail=False, methods=['post'], url_path='get_price')
    def get_price(self, request):
        """Tính giá tiền cho chuyến đi"""
        
        # Kiểm tra xem có đầy đủ thông tin tọa độ không
        lat_don = request.data.get('lat_don')
        lon_don = request.data.get('lon_don')
        lat_tra = request.data.get('lat_tra')
        lon_tra = request.data.get('lon_tra')
        
        # Kiểm tra xem có đầy đủ thông tin địa chỉ không
        diachi_don = request.data.get('diachi_don')
        diachi_tra = request.data.get('diachi_tra')
        
        # Trường hợp 1: Có đầy đủ tọa độ
        if all([lat_don, lon_don, lat_tra, lon_tra]):
            route_response = self.find_route_by_coordinates(lat_don, lon_don, lat_tra, lon_tra)
        
        # Trường hợp 2: Có đầy đủ địa chỉ
        elif all([diachi_don, diachi_tra]):
            # Tạo request giả lập để gọi API get_tuyen_duong
            temp_request = type('obj', (object,), {'data': {'diachi_don': diachi_don, 'diachi_tra': diachi_tra}})
            # Sử dụng hàm get_tuyen_duong để tìm tuyến đường từ địa chỉ
            route_response = self.get_tuyen_duong(temp_request)
        
        # Trường hợp 3: Không đủ thông tin
        else:
            return Response({
                "success": False,
                "message": "Không đủ thông tin để xác định tuyến đường. Cần cung cấp hoặc (1) cả 2 địa chỉ đón/trả hoặc (2) cả 4 tọa độ đón/trả.",
                "error_type": "missing_information"
            }, status=400)
            
        # Nếu không tìm thấy tuyến đường, trả về lỗi
        if route_response.status_code != 200:
            return route_response
            
        # Tìm thấy tuyến đường, tính giá
        try:
            route_data = route_response.data
            tuyenduong = route_data.get('tuyenduong')
            giacuoc = float(tuyenduong.get('giacuoc', 0))
            
            # Trả về kết quả với giá tiền và thông tin tuyến đường
            result = {
                "success": True,
                "giatien": giacuoc,
            }
            
            # Copy các thông tin khác từ route_response
            for key in route_data:
                if key != 'message':  # Không copy message để tránh nhầm lẫn
                    result[key] = route_data[key]
                    
            return Response(result)
            
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Lỗi khi tính giá: {str(e)}",
                "error_type": "calculation_error"            }, status=500)
    
    @extend_schema(**get_direction_schema())
    @action(detail=False, methods=['post'], url_path='get_direction')
    def get_direction(self, request):        return Response({"huong": 1})
    
    @extend_schema(**search_address_schema())
    @action(detail=False, methods=['post'], url_path='search_address')
    def search_address_nominatim(self, request):
        NOMINATIM_BASE_URL = "http://localhost:8080"
        query = request.data.get('query')
        if not query:
            return Response({"error": "Thiếu tham số query"}, status=status.HTTP_400_BAD_REQUEST)
        endpoint = f"{NOMINATIM_BASE_URL}/search"
        params = {
            "q": query,
            "format": "json"
        }
        try:
            response = requests.get(endpoint, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            return Response(data)
        except requests.exceptions.RequestException as e:            return Response({"error": f"Lỗi khi gọi API Geocoding: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)
    
    @extend_schema(**reverse_geocode_schema())
    @action(detail=False, methods=['post'], url_path='reverse_geocode')
    def reverse_geocode_nominatim(self, request):
        NOMINATIM_BASE_URL = "http://localhost:8080"
        lat = request.data.get('lat')
        lon = request.data.get('lon')
        if not lat or not lon:
            return Response({"error": "Thiếu tham số lat hoặc lon"}, status=status.HTTP_400_BAD_REQUEST)
        endpoint = f"{NOMINATIM_BASE_URL}/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json"
        }
        try:
            response = requests.get(endpoint, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            return Response(data)
        except requests.exceptions.RequestException as e:            return Response({"error": f"Lỗi khi gọi API Reverse Geocoding: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)
    
    @extend_schema(**assign_driver_for_shift_schema())
    @action(detail=False, methods=['post'], url_path='assign_driver_for_shift', permission_classes=[IsAuthenticated])
    def assign_driver_for_shift(self, request):
        """
        API nhận vào ca_id, tự lấy danh sách tài xế (Chitietca) và danh sách đặt xe + chi tiết đặt xe có mã ca trùng,
        tính tổng số ghế cần thiết, chia đều khách cho tài xế theo capacity xe.
        """
        from django.db import transaction
        
        ca_id = request.data.get('ca_id')
        if not ca_id:
            return Response({'error': 'Thiếu ca_id'}, status=400)
        
        print(f"🚌 [ASSIGN] Bắt đầu phân bổ tài xế cho ca {ca_id}")
        
        try:
            # 1. Lấy thông tin ca
            ca = Ca.objects.get(maca=ca_id)
            print(f"🚌 [ASSIGN] Ca: {ca.gioxuatphat} ngày {ca.ngayxuatphat}, xuất phát từ huyện {ca.mahuyenxuatphat_id}")
            
            # 2. Lấy danh sách chi tiết ca (tài xế + xe) của ca này
            chitietca_list = list(Chitietca.objects.select_related('maxe', 'mataixe').filter(maca=ca_id))
            if not chitietca_list:
                return Response({'error': 'Không có tài xế nào trong ca này'}, status=400)
            
            print(f"🚌 [ASSIGN] Tìm thấy {len(chitietca_list)} tài xế trong ca")
            
            # 3. Lấy tất cả đặt xe có maca = ca_id và chưa được assign (machitietca = null)
            datxe_list = list(Datxe.objects.select_related('manguoidung', 'diemdon', 'diemtra').filter(
                maca=ca_id
            ))
            print(f"🚌 [ASSIGN] Tìm thấy {len(datxe_list)} đặt xe chính với mã ca {ca_id}")
            
            # 4. Lấy tất cả chi tiết đặt xe thuộc về các đặt xe trên và chưa được assign
            chitietdatxe_list = list(Chitietdatxe.objects.select_related('madatxe', 'diemdon', 'diemtra').filter(
                madatxe__maca=ca_id
            ))
            print(f"🚌 [ASSIGN] Tìm thấy {len(chitietdatxe_list)} chi tiết đặt xe")
            
            # 5. Tạo danh sách hành khách (bao gồm cả đặt xe chính và chi tiết)
            passengers = []
            
            # Thêm đặt xe chính vào danh sách hành khách
            print(f"🚌 [ASSIGN] Xử lý {len(datxe_list)} đặt xe chính:")
            for datxe in datxe_list:
                passenger_info = {
                    'type': 'datxe',
                    'id': datxe.madatxe,
                    'ten': datxe.manguoidung.hoten,
                    'sdt': datxe.manguoidung.sodienthoai,
                    'soghe': datxe.soghe,
                    'diemdon': datxe.diemdon.tendiadiem,
                    'diemtra': datxe.diemtra.tendiadiem,
                    'ghichu': datxe.ghichu or '',
                    'object': datxe
                }
                passengers.append(passenger_info)
                print(f"  + Đặt xe {datxe.madatxe}: {passenger_info['ten']} ({passenger_info['soghe']} ghế) - {passenger_info['diemdon']} → {passenger_info['diemtra']}")
            
            # Thêm chi tiết đặt xe vào danh sách hành khách 
            print(f"🚌 [ASSIGN] Xử lý {len(chitietdatxe_list)} chi tiết đặt xe:")
            for chitiet in chitietdatxe_list:
                # Nếu chi tiết thiếu thông tin, lấy từ đặt xe chính
                soghe = getattr(chitiet, 'soghe', None) or chitiet.madatxe.soghe
                diemdon = chitiet.diemdon.tendiadiem if chitiet.diemdon else chitiet.madatxe.diemdon.tendiadiem
                diemtra = chitiet.diemtra.tendiadiem if chitiet.diemtra else chitiet.madatxe.diemtra.tendiadiem
                ghichu = chitiet.ghichu if chitiet.ghichu else chitiet.madatxe.ghichu or ''
                
                passenger_info = {
                    'type': 'chitietdatxe',
                    'id': chitiet.machitiet,
                    'ten': chitiet.tenkhach,
                    'sdt': chitiet.sodienthoaikhach,
                    'soghe': soghe,
                    'diemdon': diemdon,
                    'diemtra': diemtra,
                    'ghichu': ghichu,
                    'object': chitiet
                }
                passengers.append(passenger_info)
                print(f"  + Chi tiết {chitiet.machitiet}: {passenger_info['ten']} ({passenger_info['soghe']} ghế) - {passenger_info['diemdon']} → {passenger_info['diemtra']} [thuộc đặt xe {chitiet.madatxe.madatxe}]")
            
            total_seats_needed = sum(p['soghe'] for p in passengers)
            print(f"🚌 [ASSIGN] Tổng số ghế cần: {total_seats_needed}")
            print(f"🚌 [ASSIGN] Tổng số hành khách: {len(passengers)} (gồm {len(datxe_list)} đặt xe chính + {len(chitietdatxe_list)} chi tiết)")
            
            # 6. Tính capacity tổng của các xe
            total_capacity = sum(cc.maxe.sochongoi for cc in chitietca_list)
            print(f"🚌 [ASSIGN] Tổng capacity xe: {total_capacity} chỗ")
            
            if total_seats_needed > total_capacity:
                return Response({
                    'error': f'Không đủ chỗ! Cần {total_seats_needed} ghế nhưng chỉ có {total_capacity} chỗ'
                }, status=400)
            
            # 7. Sử dụng VRP algorithm để tối ưu assignment
            assignments = self.assign_passengers_with_vrp(passengers, chitietca_list)
            
            if not assignments:
                return Response({
                    'error': 'Không thể tối ưu hóa việc phân bổ hành khách'
                }, status=400)
                
            # 8. Cập nhật database - gán machitietca cho đặt xe và chi tiết đặt xe
            print(f"🚌 [ASSIGN] Bắt đầu cập nhật database...")
            with transaction.atomic():
                total_updated_datxe = 0
                total_updated_chitiet = 0
                
                for machitietca, assignment in assignments.items():
                    chitietca_obj = next(cc for cc in chitietca_list if cc.machitietca == machitietca)
                    print(f"🚌 [ASSIGN] Cập nhật cho chi tiết ca {machitietca} (Tài xế: {chitietca_obj.mataixe.mataixe.hoten}, Xe: {chitietca_obj.maxe.biensoxe})")
                    print(f"         → {len(assignment['passengers'])} hành khách, {assignment['seats_used']}/{assignment['capacity']} ghế")
                    
                    for i, passenger in enumerate(assignment['passengers'], 1):
                        if passenger['type'] == 'datxe':
                            datxe_obj = passenger['object']
                            old_machitietca = datxe_obj.machitietca_id
                            datxe_obj.machitietca_id = machitietca
                            datxe_obj.save(update_fields=['machitietca'])
                            total_updated_datxe += 1
                            print(f"  {i:2d}. ✅ ĐẶT XE {datxe_obj.madatxe}: {passenger['ten']} (SĐT: {passenger['sdt']}, {passenger['soghe']} ghế)")
                            print(f"       🔄 machitietca: {old_machitietca} → {machitietca}")
                            print(f"       📍 {passenger['diemdon']} → {passenger['diemtra']}")
                            
                        elif passenger['type'] == 'chitietdatxe':
                            chitiet_obj = passenger['object']
                            old_machitietca = chitiet_obj.machitietca_id
                            chitiet_obj.machitietca_id = machitietca
                            chitiet_obj.save(update_fields=['machitietca'])
                            total_updated_chitiet += 1
                            print(f"  {i:2d}. ✅ CHI TIẾT {chitiet_obj.machitiet}: {passenger['ten']} (SĐT: {passenger['sdt']}, {passenger['soghe']} ghế)")
                            print(f"       🔄 machitietca: {old_machitietca} → {machitietca}")
                            print(f"       📍 {passenger['diemdon']} → {passenger['diemtra']}")
                            print(f"       🔗 Thuộc đặt xe: {chitiet_obj.madatxe.madatxe}")
                    
                    print(f"")  # Dòng trống giữa các xe
                
                print(f"🚌 [ASSIGN] ✅ HOÀN THÀNH CẬP NHẬT:")
                print(f"         - Đặt xe chính: {total_updated_datxe}")
                print(f"         - Chi tiết đặt xe: {total_updated_chitiet}")
                print(f"         - Tổng cộng: {total_updated_datxe + total_updated_chitiet} bản ghi")
            
            # 9. Tạo kết quả trả về
            result = {}
            for machitietca, assignment in assignments.items():
                # Tìm chitietca object
                cc = next(cc for cc in chitietca_list if cc.machitietca == machitietca)
                result[f'chitietca_{machitietca}'] = {
                    'machitietca': machitietca,
                    'mataixe': cc.mataixe_id,
                    'tentaixe': cc.mataixe.mataixe.hoten,
                    'maxe': cc.maxe_id,
                    'biensoxe': cc.maxe.biensoxe,
                    'capacity': cc.maxe.sochongoi,
                    'seats_used': assignment['seats_used'],
                    'seats_available': assignment['capacity'] - assignment['seats_used'],
                    'route': assignment.get('route', []),
                    'passengers': [
                        {
                            'type': p['type'],
                            'id': p['id'],
                            'ten': p['ten'],
                            'sdt': p['sdt'],
                            'soghe': p['soghe'],
                            'diemdon': p['diemdon'],
                            'diemtra': p['diemtra'],
                            'ghichu': p['ghichu']
                        } for p in assignment['passengers']
                    ]
                }
            
            print(f"🚌 [ASSIGN] Hoàn thành phân bổ cho {len(assignments)} xe")
            
            return Response({
                'success': True,
                'message': f'Đã phân bổ {len(passengers)} hành khách cho {len(assignments)} tài xế',
                'ca_id': ca_id,
                'total_passengers': len(passengers),
                'total_seats_needed': total_seats_needed,
                'total_capacity': total_capacity,
                'assignments': result
            })
            
        except Ca.DoesNotExist:
            return Response({'error': f'Không tìm thấy ca với ID {ca_id}'}, status=404)
        except Exception as e:
            print(f"🚌 [ASSIGN] Lỗi: {str(e)}")
            return Response({'error': f'Lỗi hệ thống: {str(e)}'}, status=500)
    
    def assign_passengers_with_vrp(self, passengers, chitietca_list):
        """Phân bổ đều hành khách cho tất cả xe hoạt động (không dùng VRP)"""
        print("🚌 [ASSIGN] Sử dụng thuật toán phân bổ đều cho taxi")
        
        # Khởi tạo assignments cho tất cả xe
        assignments = {}
        for cc in chitietca_list:
            assignments[cc.machitietca] = {
                'passengers': [],
                'seats_used': 0,
                'capacity': cc.maxe.sochongoi,
                'route': []
            }
        
        # Tính toán phân bổ đều
        total_passengers = len(passengers)
        num_vehicles = len(chitietca_list)
        
        print(f"🚌 [ASSIGN] Phân bổ {total_passengers} hành khách cho {num_vehicles} xe")
        
        # Sắp xếp hành khách theo số ghế giảm dần để ưu tiên gán những nhóm lớn trước
        passengers_sorted = sorted(passengers, key=lambda x: x['soghe'], reverse=True)
        
        # Sắp xếp xe theo capacity tăng dần để ưu tiên dùng xe nhỏ trước
        chitietca_sorted = sorted(chitietca_list, key=lambda x: x.maxe.sochongoi)
        
        # Phân bổ bằng Round Robin với cân bằng tải
        passenger_index = 0
        
        while passenger_index < len(passengers_sorted):
            assigned_this_round = False
            
            # Lần lượt thử gán cho từng xe theo thứ tự capacity
            for cc in chitietca_sorted:
                if passenger_index >= len(passengers_sorted):
                    break
                    
                assignment = assignments[cc.machitietca]
                passenger = passengers_sorted[passenger_index]
                
                # Kiểm tra xe có đủ chỗ không
                if assignment['seats_used'] + passenger['soghe'] <= assignment['capacity']:
                    assignment['passengers'].append(passenger)
                    assignment['seats_used'] += passenger['soghe']
                    
                    print(f"🚌 [ASSIGN] Gán {passenger['ten']} ({passenger['soghe']} ghế) vào xe {cc.maxe.biensoxe}")
                    print(f"         → Xe hiện tại: {assignment['seats_used']}/{assignment['capacity']} ghế ({assignment['seats_used']/assignment['capacity']*100:.1f}%)")
                    
                    passenger_index += 1
                    assigned_this_round = True
            
            # Nếu không gán được ai trong lượt này, có thể do hết chỗ
            if not assigned_this_round:
                # Thử tìm xe có capacity lớn nhất còn chỗ
                remaining_passenger = passengers_sorted[passenger_index]
                best_cc = None
                max_remaining_capacity = 0
                
                for cc in chitietca_list:
                    assignment = assignments[cc.machitietca]
                    remaining_capacity = assignment['capacity'] - assignment['seats_used']
                    
                    if (remaining_capacity >= remaining_passenger['soghe'] and 
                        remaining_capacity > max_remaining_capacity):
                        max_remaining_capacity = remaining_capacity
                        best_cc = cc
                
                if best_cc:
                    assignment = assignments[best_cc.machitietca]
                    assignment['passengers'].append(remaining_passenger)
                    assignment['seats_used'] += remaining_passenger['soghe']
                    
                    print(f"🚌 [ASSIGN] Gán đặc biệt {remaining_passenger['ten']} ({remaining_passenger['soghe']} ghế) vào xe {best_cc.maxe.biensoxe}")
                    passenger_index += 1
                else:
                    print(f"🚌 [ASSIGN] ❌ Không thể gán {remaining_passenger['ten']} ({remaining_passenger['soghe']} ghế) - Không đủ chỗ")
                    break
        
        # Kiểm tra tất cả hành khách đã được gán chưa
        total_assigned = sum(len(assignment['passengers']) for assignment in assignments.values())
        if total_assigned < total_passengers:
            print(f"🚌 [ASSIGN] ⚠️ Chỉ gán được {total_assigned}/{total_passengers} hành khách")
            return None
        
        # In thống kê phân bổ
        print(f"🚌 [ASSIGN] === KẾT QUẢ PHÂN BỔ ===")
        for cc in chitietca_list:
            assignment = assignments[cc.machitietca]
            if assignment['passengers']:
                usage_percent = (assignment['seats_used'] / assignment['capacity'] * 100)
                print(f"🚌 [ASSIGN] Xe {cc.maxe.biensoxe}: {len(assignment['passengers'])} hành khách, {assignment['seats_used']}/{assignment['capacity']} ghế ({usage_percent:.1f}%)")
            else:                print(f"🚌 [ASSIGN] Xe {cc.maxe.biensoxe}: không có hành khách (dự phòng)")
        
        return assignments
    
    @extend_schema(**get_huyen_schema())
    @action(detail=False, methods=['post'], url_path='get_huyen')
    def get_huyen_from_coordinates(self, request):
        """
        Lấy mã huyện từ tọa độ với mapping thông minh cho vùng Đà Nẵng - Quảng Nam
        """
        # Validate input bằng serializer
        serializer = GetHuyenInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        lat = serializer.validated_data['lat']
        lon = serializer.validated_data['lon']
        
        # Mapping keywords để nhận diện huyện/thành phố
        huyen_mapping = {
            # Đà Nẵng
            "đà nẵng": 2,
            "da nang": 2,
            "thanh pho da nang": 2,
            "thành phố đà nẵng": 2,
            "hai chau": 2,
            "hải châu": 2,
            "cam le": 2,
            "cẩm lệ": 2,
            "lien chieu": 2,
            "liên chiểu": 2,
            "ngu hanh son": 2,
            "ngũ hành sơn": 2,
            "son tra": 2,
            "sơn trà": 2,
            "hoa vang": 2,
            "hòa vang": 2,
            
            # Tam Kỳ
            "tam ky": 1,
            "tam kỳ": 1,
            "thanh pho tam ky": 1,
            "thành phố tam kỳ": 1,
            
            # Thăng Bình
            "thang binh": 3,
            "thăng bình": 3,
            "huyen thang binh": 3,
            "huyện thăng bình": 3,
            
            # Quế Sơn
            "que son": 4,
            "quế sơn": 4,
            "huyen que son": 4,
            "huyện quế sơn": 4,
            
            # Điện Bàn
            "dien ban": 5,
            "điện bàn": 5,
            "huyen dien ban": 5,
            "huyện điện bàn": 5,
        }
        
        try:
            # Gọi API reverse geocoding nội bộ
            reverse_request = type('obj', (object,), {'data': {'lat': lat, 'lon': lon}})
            reverse_response = self.reverse_geocode_nominatim(reverse_request)
            
            if reverse_response.status_code != 200:
                return reverse_response
                
            data = reverse_response.data
            
            # Lấy thông tin địa chỉ
            address = data.get('address', {})
            display_name = data.get('display_name', '').lower()
            
            # Danh sách các trường có thể chứa thông tin huyện/thành phố
            address_fields = [
                address.get('city', ''),
                address.get('town', ''),
                address.get('county', ''),
                address.get('state_district', ''),
                address.get('suburb', ''),
                address.get('municipality', ''),
                display_name
            ]
            
            # Thử match với mapping
            for field in address_fields:
                if field:
                    field_lower = field.lower()
                    for keyword, ma_huyen in huyen_mapping.items():
                        if keyword in field_lower:
                            from ..models import Huyen
                            try:
                                huyen = Huyen.objects.get(mahuyen=ma_huyen)
                                return Response({
                                    "mahuyen": huyen.mahuyen,
                                    "tenhuyen": huyen.tenhuyen,
                                    "matched_field": field,
                                    "matched_keyword": keyword,
                                    "nominatim_data": data
                                })
                            except Huyen.DoesNotExist:
                                pass
            
            # Fallback: nếu không match được, kiểm tra tọa độ để guess huyện
            lat_float = float(lat)
            lon_float = float(lon)
            
            # Rough coordinate ranges for different areas
            if 16.0 <= lat_float <= 16.15 and 108.15 <= lon_float <= 108.3:
                # Likely Đà Nẵng area
                ma_huyen = 2
            elif 15.5 <= lat_float <= 15.7 and 108.4 <= lon_float <= 108.6:
                # Likely Tam Kỳ area
                ma_huyen = 1
            else:
                # Default fallback
                ma_huyen = 1
            
            from ..models import Huyen
            try:
                huyen = Huyen.objects.get(mahuyen=ma_huyen)
                return Response({
                    "mahuyen": huyen.mahuyen,
                    "tenhuyen": huyen.tenhuyen,
                    "method": "coordinate_fallback",
                    "nominatim_data": data
                })
            except Huyen.DoesNotExist:
                return Response({
                    "error": "Không thể xác định huyện",
                    "nominatim_data": data                
                }, status=404)
                
        except Exception as e:
            return Response({"error": f"Lỗi xử lý: {str(e)}"}, status=500)
   
    @extend_schema(**get_tuyen_duong_by_coordinates_schema())
    @action(detail=False, methods=['post'], url_path='get_tuyen_duong')
    def get_tuyen_duong(self, request):
        """Tìm tuyến đường từ 2 tọa độ"""
        serializer = GetTuyenDuongByCoordinatesInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        lat_don = serializer.validated_data['lat_don']
        lon_don = serializer.validated_data['lon_don']
        lat_tra = serializer.validated_data['lat_tra']
        lon_tra = serializer.validated_data['lon_tra']
        
        return self.find_route_by_coordinates(lat_don, lon_don, lat_tra, lon_tra)
        
    def find_route_by_coordinates(self, lat_don, lon_don, lat_tra, lon_tra):
        """Hàm chung để tìm tuyến đường từ tọa độ"""
        print(f"🔍 Bắt đầu tìm tuyến đường từ tọa độ: điểm đón ({lat_don}, {lon_don}) -> điểm trả ({lat_tra}, {lon_tra})")
        
        try:
            # Lấy mã huyện điểm đón
            print(f"📍 Đang tìm huyện cho điểm đón: lat={lat_don}, lon={lon_don}")
            huyen_don_request = type('obj', (object,), {'data': {'lat': lat_don, 'lon': lon_don}})
            huyen_don_response = self.get_huyen_from_coordinates(huyen_don_request)
            if huyen_don_response.status_code != 200:
                print(f"❌ Không thể xác định huyện điểm đón: {huyen_don_response.data}")
                return Response({
                    "success": False,
                    "message": "Không thể xác định huyện điểm đón",
                    "error_type": "no_pickup",
                    "details": huyen_don_response.data
                }, status=400)
            huyen_don_data = huyen_don_response.data
            print(f"✅ Tìm thấy huyện điểm đón: {huyen_don_data}")
            
            # Lấy mã huyện điểm trả
            print(f"📍 Đang tìm huyện cho điểm trả: lat={lat_tra}, lon={lon_tra}")
            huyen_tra_request = type('obj', (object,), {'data': {'lat': lat_tra, 'lon': lon_tra}})
            huyen_tra_response = self.get_huyen_from_coordinates(huyen_tra_request)
            if huyen_tra_response.status_code != 200:
                print(f"❌ Không thể xác định huyện điểm trả: {huyen_tra_response.data}")
                return Response({
                    "success": False,
                    "message": "Không thể xác định huyện điểm trả",
                    "error_type": "no_dropoff",
                    "details": huyen_tra_response.data
                }, status=400)
            huyen_tra_data = huyen_tra_response.data
            print(f"✅ Tìm thấy huyện điểm trả: {huyen_tra_data}")
            
            # Tìm tuyến đường trong DB
            ma_huyen_don = huyen_don_data['mahuyen']
            ma_huyen_tra = huyen_tra_data['mahuyen']
            print(f"🚍 Đang tìm tuyến đường từ huyện {ma_huyen_don} ({huyen_don_data.get('tenhuyen')}) đến huyện {ma_huyen_tra} ({huyen_tra_data.get('tenhuyen')})")
            
            try:
                tuyenduong = Tuyenduong.objects.get(
                    huyendon=ma_huyen_don,
                    huyentra=ma_huyen_tra
                )
                print(f"✅ Tìm thấy tuyến đường: {huyen_don_data.get('tenhuyen')} -> {huyen_tra_data.get('tenhuyen')} (ID: {tuyenduong.matuyenduong})")
                
                return Response({
                    "success": True,
                    "message": "Tìm thấy tuyến đường",
                    "tuyenduong": TuyenduongSerializer(tuyenduong).data,
                    "huyen_don": {
                        "mahuyen": huyen_don_data['mahuyen'],
                        "tenhuyen": huyen_don_data['tenhuyen']
                    },
                    "huyen_tra": {
                        "mahuyen": huyen_tra_data['mahuyen'],
                        "tenhuyen": huyen_tra_data['tenhuyen']
                    },
                    "coordinates": {
                        "pickup": {"lat": lat_don, "lon": lon_don},
                        "dropoff": {"lat": lat_tra, "lon": lon_tra}
                    }                })
                
            except Tuyenduong.DoesNotExist:
                print(f"❌ Không tìm thấy tuyến đường từ huyện {ma_huyen_don} ({huyen_don_data['tenhuyen']}) đến huyện {ma_huyen_tra} ({huyen_tra_data['tenhuyen']})")
                return Response({
                    "success": False,
                    "message": f"Không có tuyến đường từ {huyen_don_data['tenhuyen']} đến {huyen_tra_data['tenhuyen']}",
                    "error_type": "no_route",
                    "huyen_don": {
                        "mahuyen": huyen_don_data['mahuyen'],
                        "tenhuyen": huyen_don_data['tenhuyen']
                    },
                    "huyen_tra": {
                        "mahuyen": huyen_tra_data['mahuyen'],
                        "tenhuyen": huyen_tra_data['tenhuyen']
                    },
                    "coordinates": {
                        "pickup": {"lat": lat_don, "lon": lon_don},
                        "dropoff": {"lat": lat_tra, "lon": lon_tra}
                    }
                }, status=404)
                
        except Exception as e:
            print(f"💥 Lỗi xử lý trong find_route_by_coordinates: {str(e)}")
            return Response({
                "success": False,
                "message": f"Lỗi xử lý: {str(e)}"
            }, status=500)