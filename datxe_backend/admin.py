# datxe_backend/admin.py

from django.contrib import admin
from .models import (
    NguoiDung, Vaitro, Huyen, Nhanvien, Taixe, Xe, 
    Diadiem, Tuyenduong, Ca, Chitietca, Datxe, 
    Chitietdatxe, Danhgia
)

# Admin cho NguoiDung
class NguoiDungAdmin(admin.ModelAdmin):
    list_display = ['sodienthoai', 'hoten', 'vaitro', 'is_staff', 'is_active', 'date_joined']
    list_filter = ('is_staff', 'is_active', 'vaitro')
    search_fields = ('sodienthoai', 'hoten', 'email')
    ordering = ('sodienthoai',)
    fieldsets = (
        (None, {'fields': ('sodienthoai', 'password')}),
        ('Thông tin cá nhân', {'fields': ('hoten', 'email', 'vaitro')}),
        ('Quyền hạn', {'fields': ('is_staff', 'is_active')}),
        ('Khác', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('sodienthoai', 'hoten', 'password1', 'password2', 'is_staff', 'is_active', 'email', 'vaitro')}
        ),
    )

# Admin cho Vai trò
class VaitroAdmin(admin.ModelAdmin):
    list_display = ['mavaitro', 'tenvaitro']
    search_fields = ('tenvaitro',)

# Admin cho Huyện
class HuyenAdmin(admin.ModelAdmin):
    list_display = ['mahuyen', 'tenhuyen']
    search_fields = ('tenhuyen',)

# Admin cho Nhân viên
class NhanvienAdmin(admin.ModelAdmin):
    list_display = ['manhanvien', 'get_hoten', 'get_sodienthoai', 'ngayvaolam', 'trangthai']
    list_filter = ('trangthai', 'ngayvaolam')
    search_fields = ('manhanvien__hoten', 'manhanvien__sodienthoai', 'cccd')
    
    def get_hoten(self, obj):
        return obj.manhanvien.hoten
    get_hoten.short_description = 'Họ tên'
    
    def get_sodienthoai(self, obj):
        return obj.manhanvien.sodienthoai
    get_sodienthoai.short_description = 'SĐT'

# Admin cho Tài xế
class TaixeAdmin(admin.ModelAdmin):
    list_display = ['mataixe', 'get_hoten', 'get_sodienthoai', 'trangthai']
    list_filter = ('trangthai',)
    search_fields = ('mataixe__hoten', 'mataixe__sodienthoai', 'cccd')
    
    def get_hoten(self, obj):
        return obj.mataixe.hoten
    get_hoten.short_description = 'Họ tên'
    
    def get_sodienthoai(self, obj):
        return obj.mataixe.sodienthoai
    get_sodienthoai.short_description = 'SĐT'

# Admin cho Xe
class XeAdmin(admin.ModelAdmin):
    list_display = ['maxe', 'biensoxe', 'loaixe', 'sochongoi']
    list_filter = ('loaixe',)
    search_fields = ('biensoxe', 'loaixe')

# Admin cho Địa điểm
class DiadiemAdmin(admin.ModelAdmin):
    list_display = ['madiadiem', 'tendiadiem', 'vido', 'kinhdo']
    search_fields = ('tendiadiem',)

# Admin cho Tuyến đường
class TuyenduongAdmin(admin.ModelAdmin):
    list_display = ['matuyenduong', 'get_huyendon', 'get_huyentra', 'giacuoc', 'huongchay']
    list_filter = ('huyendon', 'huyentra', 'huongchay')
    search_fields = ('huyendon__tenhuyen', 'huyentra__tenhuyen')
    
    def get_huyendon(self, obj):
        return obj.huyendon.tenhuyen
    get_huyendon.short_description = 'Huyện đón'
    
    def get_huyentra(self, obj):
        return obj.huyentra.tenhuyen
    get_huyentra.short_description = 'Huyện trả'

# Admin cho Ca
class CaAdmin(admin.ModelAdmin):
    list_display = ['maca', 'gioxuatphat', 'ngayxuatphat', 'get_huyenxuatphat']
    list_filter = ('ngayxuatphat', 'mahuyenxuatphat')
    search_fields = ('maca', 'mahuyenxuatphat__tenhuyen')
    date_hierarchy = 'ngayxuatphat'
    
    def get_huyenxuatphat(self, obj):
        return obj.mahuyenxuatphat.tenhuyen
    get_huyenxuatphat.short_description = 'Huyện xuất phát'

# Admin cho Chi tiết ca
class ChitietcaAdmin(admin.ModelAdmin):
    list_display = ['machitietca', 'get_maca', 'get_xe', 'get_taixe']
    list_filter = ('maca__ngayxuatphat', 'maca__mahuyenxuatphat')
    search_fields = ('maxe__biensoxe', 'mataixe__mataixe__hoten')
    
    def get_maca(self, obj):
        return f"Ca {obj.maca.maca} - {obj.maca.gioxuatphat}"
    get_maca.short_description = 'Ca'
    
    def get_xe(self, obj):
        return obj.maxe.biensoxe
    get_xe.short_description = 'Xe'
    
    def get_taixe(self, obj):
        return obj.mataixe.mataixe.hoten
    get_taixe.short_description = 'Tài xế'

# Inline cho Chi tiết đặt xe
class ChitietdatxeInline(admin.TabularInline):
    model = Chitietdatxe
    extra = 1
    fields = ('tenkhach', 'sodienthoaikhach', 'diemdon', 'diemtra', 'soghe', 'trangthai')

# Admin cho Đặt xe
class DatxeAdmin(admin.ModelAdmin):
    list_display = ['madatxe', 'get_nguoidung', 'get_ca', 'thoigiandat', 'soghe', 'trangthai', 'get_chitietca']
    list_filter = ('trangthai', 'thoigiandat', 'maca__ngayxuatphat')
    search_fields = ('manguoidung__hoten', 'manguoidung__sodienthoai', 'madatxe')
    date_hierarchy = 'thoigiandat'
    inlines = [ChitietdatxeInline]
    
    def get_nguoidung(self, obj):
        return f"{obj.manguoidung.hoten} ({obj.manguoidung.sodienthoai})"
    get_nguoidung.short_description = 'Người dùng'
    
    def get_ca(self, obj):
        return f"Ca {obj.maca.maca} - {obj.maca.ngayxuatphat} {obj.maca.gioxuatphat}"
    get_ca.short_description = 'Ca'
    
    def get_chitietca(self, obj):
        if obj.machitietca:
            return f"{obj.machitietca.maxe.biensoxe} - {obj.machitietca.mataixe.mataixe.hoten}"
        return "Chưa phân bổ"
    get_chitietca.short_description = 'Xe được phân'

# Admin cho Chi tiết đặt xe
class ChitietdatxeAdmin(admin.ModelAdmin):
    list_display = ['machitiet', 'get_datxe', 'tenkhach', 'sodienthoaikhach', 'soghe', 'trangthai', 'get_chitietca']
    list_filter = ('trangthai', 'madatxe__thoigiandat')
    search_fields = ('tenkhach', 'sodienthoaikhach', 'madatxe__madatxe')
    
    def get_datxe(self, obj):
        return f"Đặt xe {obj.madatxe.madatxe}"
    get_datxe.short_description = 'Đặt xe'
    
    def get_chitietca(self, obj):
        if obj.machitietca:
            return f"{obj.machitietca.maxe.biensoxe} - {obj.machitietca.mataixe.mataixe.hoten}"
        return "Chưa phân bổ"
    get_chitietca.short_description = 'Xe được phân'

# Admin cho Đánh giá
class DanhgiaAdmin(admin.ModelAdmin):
    list_display = ['get_madatxe', 'diemso', 'ngaydanhgia', 'get_nguoidung']
    list_filter = ('diemso', 'ngaydanhgia')
    search_fields = ('madatxe__manguoidung__hoten', 'binhluan')
    date_hierarchy = 'ngaydanhgia'
    
    def get_madatxe(self, obj):
        return f"Đặt xe {obj.madatxe.madatxe}"
    get_madatxe.short_description = 'Đặt xe'
    
    def get_nguoidung(self, obj):
        return obj.madatxe.manguoidung.hoten
    get_nguoidung.short_description = 'Người đánh giá'

# Đăng ký tất cả admin classes với tên Việt hóa
admin.site.register(NguoiDung, NguoiDungAdmin)
admin.site.register(Vaitro, VaitroAdmin)
admin.site.register(Huyen, HuyenAdmin)
admin.site.register(Nhanvien, NhanvienAdmin)
admin.site.register(Taixe, TaixeAdmin)
admin.site.register(Xe, XeAdmin)
admin.site.register(Diadiem, DiadiemAdmin)
admin.site.register(Tuyenduong, TuyenduongAdmin)
admin.site.register(Ca, CaAdmin)
admin.site.register(Chitietca, ChitietcaAdmin)
admin.site.register(Datxe, DatxeAdmin)
admin.site.register(Chitietdatxe, ChitietdatxeAdmin)
admin.site.register(Danhgia, DanhgiaAdmin)

# Việt hóa tên hiển thị các model
NguoiDung._meta.verbose_name = "Người dùng"
NguoiDung._meta.verbose_name_plural = "👥 Quản lý Người dùng"

Vaitro._meta.verbose_name = "Vai trò"
Vaitro._meta.verbose_name_plural = "🎭 Quản lý Vai trò"

Huyen._meta.verbose_name = "Huyện"
Huyen._meta.verbose_name_plural = "🏢 Quản lý Huyện"

Nhanvien._meta.verbose_name = "Nhân viên"
Nhanvien._meta.verbose_name_plural = "👷 Quản lý Nhân viên"

Taixe._meta.verbose_name = "Tài xế"
Taixe._meta.verbose_name_plural = "🚗 Quản lý Tài xế"

Xe._meta.verbose_name = "Xe"
Xe._meta.verbose_name_plural = "🚐 Quản lý Xe"

Diadiem._meta.verbose_name = "Địa điểm"
Diadiem._meta.verbose_name_plural = "📍 Quản lý Địa điểm"

Tuyenduong._meta.verbose_name = "Tuyến đường"
Tuyenduong._meta.verbose_name_plural = "🛣️ Quản lý Tuyến đường"

Ca._meta.verbose_name = "Ca làm việc"
Ca._meta.verbose_name_plural = "⏰ Quản lý Ca làm việc"

Chitietca._meta.verbose_name = "Chi tiết ca"
Chitietca._meta.verbose_name_plural = "📋 Quản lý Chi tiết ca"

Datxe._meta.verbose_name = "Đặt xe"
Datxe._meta.verbose_name_plural = "🎫 Quản lý Đặt xe"

Chitietdatxe._meta.verbose_name = "Chi tiết đặt xe"
Chitietdatxe._meta.verbose_name_plural = "📝 Quản lý Chi tiết đặt xe"

Danhgia._meta.verbose_name = "Đánh giá"
Danhgia._meta.verbose_name_plural = "⭐ Quản lý Đánh giá"

# Tùy chỉnh admin site
admin.site.site_header = "Hệ thống Đặt Xe Taxi"
admin.site.site_title = "Admin Đặt Xe"
admin.site.index_title = "Quản trị hệ thống đặt xe taxi"
