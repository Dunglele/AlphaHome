from django.contrib import admin
from .models import NhanVien, QuanLy, ChuyenMuc, CanHo, Anh, DiaChi, KhachHang, HopDong


class AnhInline(admin.TabularInline):
    model = Anh
    extra = 2


class DiaChiInline(admin.StackedInline):
    model = DiaChi
    max_num = 1


@admin.register(CanHo)
class CanHoAdmin(admin.ModelAdmin):
    list_display = ['ten_ch', 'loai_phong', 'gia', 'trang_thai', 'chuyen_muc', 'ngay_tao']
    list_filter = ['trang_thai', 'loai_phong', 'chuyen_muc']
    search_fields = ['ten_ch', 'mo_ta']
    list_editable = ['trang_thai']
    inlines = [AnhInline, DiaChiInline]


@admin.register(HopDong)
class HopDongAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'khach_hang', 'nhan_vien', 'ngay_lap', 'tong_tien_thu', 'trang_thai']
    list_filter = ['trang_thai', 'nhan_vien']
    search_fields = ['khach_hang__ho_ten', 'can_ho__ten_ch']
    readonly_fields = ['ngay_tao']


@admin.register(ChuyenMuc)
class ChuyenMucAdmin(admin.ModelAdmin):
    list_display = ['ten_cm', 'so_luong_sp', 'quan_ly']


admin.site.register(NhanVien)
admin.site.register(QuanLy)
admin.site.register(KhachHang)
