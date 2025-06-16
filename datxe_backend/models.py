from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class Huyen(models.Model):
    mahuyen = models.AutoField(db_column='maHuyen', primary_key=True)
    tenhuyen = models.CharField(db_column='tenHuyen', max_length=100)

    class Meta:
        managed = False
        db_table = 'Huyen'
    def __str__(self):
        return self.tenhuyen

class Vaitro(models.Model):
    mavaitro = models.IntegerField(db_column='maVaiTro', primary_key=True)
    tenvaitro = models.CharField(db_column='tenVaiTro', max_length=15)

    class Meta:
        managed = False
        db_table = 'VaiTro'
        
    def __str__(self):
        return self.tenvaitro

class NguoiDungManager(BaseUserManager):
    def create_user(self, sodienthoai, password=None, **extra_fields):
        from django.utils import timezone
        if not sodienthoai:
            raise ValueError('Phải cung cấp số điện thoại')
        if 'vaitro_id' not in extra_fields and 'vaitro' not in extra_fields:
            extra_fields['vaitro_id'] = 3  # (Hành khách)
        if 'date_joined' not in extra_fields and 'ngayTao' not in extra_fields:
            extra_fields['date_joined'] = timezone.now()
        user = self.model(sodienthoai=sodienthoai, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, sodienthoai, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(sodienthoai, password, **extra_fields)

class NguoiDung(AbstractBaseUser):
    manguoidung = models.AutoField(db_column='maNguoiDung', primary_key=True)
    hoten = models.CharField(db_column='hoTen', max_length=50)
    sodienthoai = models.CharField(db_column='soDienThoai', max_length=20, unique=True)
    password = models.CharField(db_column='matKhau', max_length=255)
    email = models.CharField(max_length=100, blank=True, null=True)
    vaitro = models.ForeignKey('Vaitro', models.DO_NOTHING, db_column='vaiTro')
    date_joined  = models.DateTimeField(db_column='ngayTao')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(blank=True, null=True)
    
    objects = NguoiDungManager()
    
    USERNAME_FIELD = 'sodienthoai'
    REQUIRED_FIELDS = ['hoten']
    
    def has_perm(self, perm, obj=None):
        return self.is_active and self.is_staff and self.vaitro_id == 0

    def has_module_perms(self, app_label):
        return self.is_active and self.is_staff and self.vaitro_id == 0
    
    class Meta:
        managed = False
        db_table = 'NguoiDung'
        
    def __str__(self):
        return self.hoten

class Nhanvien(models.Model):
    manhanvien = models.OneToOneField('NguoiDung', models.DO_NOTHING, db_column='maNhanVien', primary_key=True)
    ngayvaolam = models.DateField(db_column='ngayVaoLam')
    cccd = models.CharField(max_length=20, blank=True, null=True)
    trangthai = models.IntegerField(db_column='trangThai', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NhanVien'

class Taixe(models.Model):
    mataixe = models.OneToOneField('NguoiDung', models.DO_NOTHING, db_column='maTaiXe', primary_key=True)
    cccd = models.CharField(max_length=20, blank=True, null=True)
    trangthai = models.IntegerField(db_column='trangThai', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TaiXe'

class Xe(models.Model):
    maxe = models.AutoField(db_column='maXe', primary_key=True)
    biensoxe = models.CharField(db_column='bienSoXe', max_length=20)
    loaixe = models.CharField(db_column='loaiXe', max_length=50, blank=True, null=True)
    sochongoi = models.IntegerField(db_column='soChoNgoi')

    class Meta:
        managed = False
        db_table = 'Xe'

class Diadiem(models.Model):
    madiadiem = models.IntegerField(db_column='maDiaDiem', primary_key=True)
    tendiadiem = models.CharField(db_column='tenDiaDiem', max_length=100)
    vido = models.IntegerField(db_column='viDo')
    kinhdo = models.IntegerField(db_column='kinhDo')

    class Meta:
        managed = False
        db_table = 'DiaDiem'
        
    def __str__(self):
        return self.tendiadiem

class Tuyenduong(models.Model):
    matuyenduong = models.AutoField(db_column='maTuyenDuong', primary_key=True)
    huyendon = models.ForeignKey('Huyen', models.DO_NOTHING, db_column='huyenDon', related_name='tuyenduong_huyendon_set')
    huyentra = models.ForeignKey('Huyen', models.DO_NOTHING, db_column='huyenTra', related_name='tuyenduong_huyentra_set')
    giacuoc = models.DecimalField(db_column='giaCuoc', max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'TuyenDuong'

class Ca(models.Model):
    maca = models.AutoField(db_column='maCa', primary_key=True)
    gioxuatphat = models.TimeField(db_column='gioXuatPhat')
    ngayxuatphat = models.DateField(db_column='ngayXuatPhat')
    mahuyenxuatphat = models.ForeignKey('Huyen', models.DO_NOTHING, db_column='maHuyenXuatPhat')

    class Meta:
        managed = False
        db_table = 'Ca'

class Chitietca(models.Model):
    machitietca = models.AutoField(db_column='maChiTietCa', primary_key=True)
    maca = models.ForeignKey('Ca', models.DO_NOTHING, db_column='maCa')
    maxe = models.ForeignKey('Xe', models.DO_NOTHING, db_column='maXe')
    mataixe = models.ForeignKey('Taixe', models.DO_NOTHING, db_column='maTaiXe')

    class Meta:
        managed = False
        db_table = 'ChiTietCa'

class Datxe(models.Model):
    madatxe = models.AutoField(db_column='maDatXe', primary_key=True)
    manguoidung = models.ForeignKey('NguoiDung', models.DO_NOTHING, db_column='maNguoiDung')
    thoigiandat = models.DateTimeField(db_column='thoiGianDat')
    manhanvien = models.ForeignKey('Nhanvien', models.DO_NOTHING, db_column='maNhanVien', blank=True, null=True)
    machitietca = models.ForeignKey('Chitietca', models.DO_NOTHING, db_column='maChiTietCa')
    diemtra = models.ForeignKey('Diadiem', models.DO_NOTHING, db_column='diemTra')
    diemdon = models.ForeignKey('Diadiem', models.DO_NOTHING, db_column='diemDon', related_name='datxe_diemdon_set')
    matuyenduong = models.ForeignKey('Tuyenduong', models.DO_NOTHING, db_column='maTuyenDuong')
    trangthai = models.CharField(db_column='trangThai', max_length=50)
    ghichu = models.TextField(db_column='ghiChu', blank=True, null=True)
    yeucauchungxe = models.IntegerField(db_column='yeuCauChungXe')

    class Meta:
        managed = False
        db_table = 'DatXe'

class Chitietdatxe(models.Model):
    machitiet = models.AutoField(db_column='maChiTiet', primary_key=True)
    madatxe = models.ForeignKey('Datxe', models.DO_NOTHING, db_column='maDatXe')
    machitietca = models.ForeignKey('Chitietca', models.DO_NOTHING, db_column='maChiTietCa')
    tenkhach = models.CharField(db_column='tenKhach', max_length=50)
    sodienthoaikhach = models.CharField(db_column='soDienThoaiKhach', max_length=20)
    diemtra = models.ForeignKey('Diadiem', models.DO_NOTHING, db_column='diemTra')
    diemdon = models.ForeignKey('Diadiem', models.DO_NOTHING, db_column='diemDon', related_name='chitietdatxe_diemdon_set')
    matuyenduong = models.ForeignKey('Tuyenduong', models.DO_NOTHING, db_column='maTuyenDuong')
    trangthai = models.CharField(db_column='trangThai', max_length=50)
    ghichu = models.TextField(db_column='ghiChu', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ChiTietDatXe'

class Danhgia(models.Model):
    madatxe = models.OneToOneField('Datxe', models.DO_NOTHING, db_column='maDatXe', primary_key=True)
    diemso = models.IntegerField(db_column='diemSo')
    binhluan = models.TextField(db_column='binhLuan', blank=True, null=True)
    ngaydanhgia = models.DateField(db_column='ngayDanhGia')

    class Meta:
        managed = False
        db_table = 'DanhGia'
