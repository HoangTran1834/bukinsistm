# datxe_backend/admin.py

from django.contrib import admin
from .models import NguoiDung

class NguoiDungAdmin(admin.ModelAdmin):
    list_display = ['sodienthoai', 'hoten', 'is_staff', 'is_active']
    list_filter = ('is_staff', 'is_active')
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
    search_fields = ('sodienthoai', 'hoten', 'email')
    ordering = ('sodienthoai',)


admin.site.register(NguoiDung, NguoiDungAdmin)
