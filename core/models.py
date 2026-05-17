from django.db import models
from django.contrib.auth.models import User


class NhanVien(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='nhanvien')
    ho_ten = models.CharField(max_length=100)
    so_dien_thoai = models.CharField(max_length=15)

    class Meta:
        verbose_name = 'Nhân Viên'
        verbose_name_plural = 'Nhân Viên'

    def __str__(self) -> str:
        return self.ho_ten


class QuanLy(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='quanly')
    ho_ten = models.CharField(max_length=100)
    so_dien_thoai = models.CharField(max_length=15)
    chuc_vu = models.CharField(max_length=50, default='Quản lý')

    class Meta:
        verbose_name = 'Quản Lý'
        verbose_name_plural = 'Quản Lý'

    def __str__(self) -> str:
        return self.ho_ten


class ChuyenMuc(models.Model):
    ten_cm = models.CharField(max_length=100)
    mo_ta = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fa-building')  # FontAwesome class
    quan_ly = models.ForeignKey(QuanLy, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Chuyên Mục'
        verbose_name_plural = 'Chuyên Mục'

    def __str__(self) -> str:
        return self.ten_cm

    @property
    def so_luong_sp(self) -> int:
        return self.canho_set.filter(trang_thai=CanHo.TrangThai.TRONG).count()


class CanHo(models.Model):
    class TrangThai(models.TextChoices):
        TRONG = 'TRONG', 'Còn trống'
        CHO_DUYET = 'CHO_DUYET', 'Chờ duyệt'
        DA_THUE = 'DA_THUE', 'Đã thuê'

    class LoaiPhong(models.TextChoices):
        BANCOL = 'BANCOL', 'Bancol'
        DUPLEX = 'DUPLEX', 'Duplex'
        THUONG = 'THUONG', 'Thường'

    ten_ch = models.CharField(max_length=200)
    gia = models.DecimalField(max_digits=12, decimal_places=0)
    mo_ta = models.TextField(blank=True)
    loai_phong = models.CharField(max_length=20, choices=LoaiPhong.choices, default=LoaiPhong.BANCOL)
    trang_thai = models.CharField(max_length=20, choices=TrangThai.choices, default=TrangThai.TRONG)
    chuyen_muc = models.ForeignKey(ChuyenMuc, on_delete=models.SET_NULL, null=True)
    dien_tich = models.FloatField(null=True, blank=True)
    ngay_tao = models.DateTimeField(auto_now_add=True)
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Căn Hộ / Phòng Trọ'
        verbose_name_plural = 'Căn Hộ / Phòng Trọ'
        ordering = ['-ngay_tao']

    def __str__(self) -> str:
        return self.ten_ch

    @property
    def gia_format(self) -> str:
        # Định dạng: 1.234.567 đ
        return f"{int(self.gia):,}".replace(',', '.') + " đ"

    @property
    def anh_chinh(self):
        return self.anh_set.first()


class Anh(models.Model):
    can_ho = models.ForeignKey(CanHo, on_delete=models.CASCADE, related_name='anh_set')
    link_anh = models.URLField(max_length=500)
    la_anh_chinh = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Ảnh'
        verbose_name_plural = 'Ảnh'

    def __str__(self) -> str:
        return f"Ảnh của {self.can_ho.ten_ch}"


class DiaChi(models.Model):
    can_ho = models.OneToOneField(CanHo, on_delete=models.CASCADE, related_name='dia_chi')
    tinh = models.CharField(max_length=100, default='TP Hồ Chí Minh')
    quan = models.CharField(max_length=100)
    dia_chi_cu_the = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = 'Địa Chỉ'
        verbose_name_plural = 'Địa Chỉ'

    def __str__(self) -> str:
        return f"{self.quan}, {self.tinh}"

    @property
    def dia_chi_day_du(self) -> str:
        parts = [p for p in [self.dia_chi_cu_the, self.quan, self.tinh] if p]
        return ', '.join(parts)


class KhachHang(models.Model):
    ho_ten = models.CharField(max_length=100)
    so_dien_thoai = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    nhan_vien = models.ForeignKey(NhanVien, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Khách Hàng'
        verbose_name_plural = 'Khách Hàng'

    def __str__(self) -> str:
        return f"{self.ho_ten} — {self.so_dien_thoai}"


class HopDong(models.Model):
    class TrangThai(models.TextChoices):
        CHO_DUYET = 'CHO_DUYET', 'Chờ duyệt'
        DA_DUYET = 'DA_DUYET', 'Đã duyệt'
        TU_CHOI = 'TU_CHOI', 'Từ chối'

    can_ho = models.ForeignKey(CanHo, on_delete=models.PROTECT, related_name='hop_dong_set')
    khach_hang = models.ForeignKey(KhachHang, on_delete=models.PROTECT)
    nhan_vien = models.ForeignKey(NhanVien, on_delete=models.SET_NULL, null=True, blank=True)
    ngay_lap = models.DateField()
    tong_tien_thu = models.DecimalField(max_digits=12, decimal_places=0)
    minh_chung = models.URLField(max_length=500, blank=True)
    trang_thai = models.CharField(max_length=20, choices=TrangThai.choices, default=TrangThai.CHO_DUYET)
    ghi_chu = models.TextField(blank=True)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Hợp Đồng'
        verbose_name_plural = 'Hợp Đồng'
        ordering = ['-ngay_tao']

    def __str__(self) -> str:
        return f"HĐ-{self.pk:04d} — {self.can_ho.ten_ch}"
