from __future__ import annotations

from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView, PasswordChangeView as DjangoPasswordChangeView
import cloudinary
import cloudinary.uploader
from django.conf import settings
from django.db.models import Q, Sum, Count, Avg, Max, Min
from django.urls import reverse_lazy
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView
from django.contrib.auth.models import User

from .models import Anh, CanHo, ChuyenMuc, DiaChi, HopDong, KhachHang, NhanVien, NhanVienMKT, QuanLy

# Cloudinary Configuration
cloudinary.config(
    cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
    api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
    secure=True
)


# ─────────────────────────── Mixins ──────────────────────────────

class StaffRequiredMixin(LoginRequiredMixin):
    """Chỉ nhân viên hoặc quản lý mới được vào."""
    login_url = '/login/'

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class ManagerRequiredMixin(StaffRequiredMixin):
    """Chỉ quản lý mới được vào."""
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        result = super().dispatch(request, *args, **kwargs)
        if request.user.is_authenticated and not (hasattr(request.user, 'quanly') or request.user.is_superuser):
            messages.error(request, 'Bạn không có quyền truy cập trang này.')
            return redirect('dashboard')
        return result


def _base_context(request: HttpRequest) -> dict:
    """Context chung cho tất cả views."""
    return {'chuyen_muc_list': ChuyenMuc.objects.all()}


# ─────────────────────────── Auth ────────────────────────────────

class AlphaLoginView(DjangoLoginView):
    template_name = 'core/login.html'
    redirect_authenticated_user = True

    def get_success_url(self) -> str:
        return '/'


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect('login')


# ─────────────────────────── Dashboard ───────────────────────────

class DashboardView(StaffRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        can_ho_qs = CanHo.objects.all()
        ctx = _base_context(request)
        
        # Doanh thu
        revenue_personal = 0
        revenue_all = 0
        if not (hasattr(request.user, 'quanly') or request.user.is_superuser):
            # Nhân viên: Doanh thu cá nhân
            nv = getattr(request.user, 'nhanvien', None)
            if nv:
                revenue_personal = HopDong.objects.filter(
                    nhan_vien=nv,
                    trang_thai=HopDong.TrangThai.DA_DUYET
                ).aggregate(s=Sum('tong_tien_thu'))['s'] or 0
        else:
            # Quản lý: Doanh thu toàn bộ
            revenue_all = HopDong.objects.filter(
                trang_thai=HopDong.TrangThai.DA_DUYET
            ).aggregate(s=Sum('tong_tien_thu'))['s'] or 0

        ctx.update({
            'total_phong':      can_ho_qs.count(),
            'phong_trong':      can_ho_qs.filter(trang_thai=CanHo.TrangThai.TRONG).count(),
            'phong_cho_duyet':  can_ho_qs.filter(trang_thai=CanHo.TrangThai.CHO_DUYET).count(),
            'phong_da_thue':    can_ho_qs.filter(trang_thai=CanHo.TrangThai.DA_THUE).count(),
            'san_pham_moi':     can_ho_qs.select_related('dia_chi', 'chuyen_muc').prefetch_related('anh_set')[:8],
            'revenue_personal': int(revenue_personal),
            'revenue_all':      int(revenue_all),
        })
        return render(request, 'core/dashboard.html', ctx)


# ─────────────────────────── Product List ────────────────────────

class ProductListView(StaffRequiredMixin, View):
    paginate_by = 10
    GRID_PAGE_SIZE = 12
    LIST_PAGE_SIZE = 10

    def get(self, request: HttpRequest) -> HttpResponse:
        qs = CanHo.objects.select_related('dia_chi', 'chuyen_muc').prefetch_related('anh_set')

        # Managers see all; staff only see available rooms
        if not (hasattr(request.user, 'quanly') or request.user.is_superuser):
            qs = qs.filter(trang_thai=CanHo.TrangThai.TRONG)

        # Filters
        if cm := request.GET.get('cm'):
            qs = qs.filter(chuyen_muc__pk=cm)
        if loai := request.GET.get('loai'):
            qs = qs.filter(loai_phong=loai)
        if tt := request.GET.get('tt'):
            qs = qs.filter(trang_thai=tt)
        if quan := request.GET.get('quan'):
            qs = qs.filter(dia_chi__quan=quan)
        if q := request.GET.get('q'):
            qs = qs.filter(Q(ten_ch__icontains=q) | Q(dia_chi__quan__icontains=q))
        if gia := request.GET.get('gia'):
            lo, hi = (float(x) * 1_000_000 for x in gia.split('-'))
            qs = qs.filter(gia__gte=lo, gia__lte=hi)

        # Sorting
        sort = request.GET.get('sort', '-pk')
        if sort == 'gia_tang':
            qs = qs.order_by('gia')
        elif sort == 'gia_giam':
            qs = qs.order_by('-gia')
        elif sort == 'ten_az':
            qs = qs.order_by('ten_ch')
        elif sort == 'ten_za':
            qs = qs.order_by('-ten_ch')
        else:
            qs = qs.order_by('-pk')  # Mới nhất trước

        from django.core.paginator import Paginator
        # ps=12 → grid mode, ps=10 → list mode; fallback to default
        ps_param = request.GET.get('ps', '')
        page_size = self.GRID_PAGE_SIZE if ps_param == '12' else self.LIST_PAGE_SIZE
        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(request.GET.get('page', 1))

        ctx = _base_context(request)
        ctx['page_obj'] = page_obj
        # Lấy danh sách quận không trùng lặp (làm sạch khoảng trắng và lọc trùng trong Python)
        raw_quans = CanHo.objects.values_list('dia_chi__quan', flat=True).exclude(dia_chi__quan__isnull=True).exclude(dia_chi__quan='')
        ctx['quan_list'] = sorted(list(set(q.strip() for q in raw_quans if q.strip())))
        return render(request, 'core/product_list.html', ctx)


# ─────────────────────────── Product Detail ──────────────────────

class ProductDetailView(StaffRequiredMixin, View):
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        phong = get_object_or_404(CanHo, pk=pk)
        
        # Sản phẩm liên quan cùng quận
        related_phong = []
        if hasattr(phong, 'dia_chi') and phong.dia_chi.quan:
            qs_related = CanHo.objects.filter(
                dia_chi__quan=phong.dia_chi.quan,
                trang_thai=CanHo.TrangThai.TRONG
            ).exclude(pk=pk).select_related('dia_chi', 'chuyen_muc').prefetch_related('anh_set')
            
            # Nếu nhân viên thì chỉ xem phòng trống, quản lý có thể xem hết (ở đây related chỉ ưu tiên phòng trống)
            related_phong = qs_related[:4]

        ctx = _base_context(request)
        ctx.update({
            'phong':         phong,
            'anh_list':      phong.anh_set.all(),
            'hop_dong_list': phong.hop_dong_set.select_related('khach_hang', 'nhan_vien').all(),
            'related_phong': related_phong,
        })
        return render(request, 'core/product_detail.html', ctx)


# ─────────────────────────── Sale Form ───────────────────────────

class SaleFormView(StaffRequiredMixin, View):
    """Nhân viên chốt sale — tạo KH + HĐ, đổi phòng sang CHO_DUYET."""

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        phong = get_object_or_404(CanHo, pk=pk, trang_thai=CanHo.TrangThai.TRONG)
        ctx = _base_context(request)
        ctx['phong'] = phong
        return render(request, 'core/sale_form.html', ctx)

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        phong = get_object_or_404(CanHo, pk=pk, trang_thai=CanHo.TrangThai.TRONG)
        nhan_vien = getattr(request.user, 'nhanvien', None)
        is_manager = hasattr(request.user, 'quanly') or request.user.is_superuser

        if not nhan_vien and not is_manager:
            messages.error(request, 'Tài khoản của bạn không có quyền thực hiện thao tác này.')
            return redirect('product_detail', pk=pk)

        # Tạo khách hàng
        kh = KhachHang.objects.create(
            ho_ten=request.POST.get('ho_ten', '').strip(),
            so_dien_thoai=request.POST.get('so_dien_thoai', '').strip(),
            email=request.POST.get('email', '').strip(),
            nhan_vien=nhan_vien,
        )

        # Handle Proof Upload (Cloudinary)
        minh_chung_url = request.POST.get('minh_chung', '').strip()
        if request.FILES.get('minh_chung_file'):
            try:
                upload_result = cloudinary.uploader.upload(request.FILES['minh_chung_file'], folder="alphahome/contracts")
                minh_chung_url = upload_result.get('secure_url')
            except Exception as e:
                print(f"Cloudinary proof upload error: {e}")

        # Tạo hợp đồng
        hd = HopDong.objects.create(
            can_ho=phong,
            khach_hang=kh,
            nhan_vien=nhan_vien,
            ngay_lap=request.POST.get('ngay_lap') or timezone.now().date(),
            tong_tien_thu=request.POST.get('tong_tien_thu', 0),
            minh_chung=minh_chung_url,
            ghi_chu=request.POST.get('ghi_chu', '').strip(),
            trang_thai=HopDong.TrangThai.CHO_DUYET
        )

        # Đổi trạng thái phòng
        phong.trang_thai = CanHo.TrangThai.CHO_DUYET
        phong.save(update_fields=['trang_thai'])

        messages.success(request, f'Đã gửi yêu cầu chốt sale cho "{phong.ten_ch}". Chờ quản lý duyệt.')
        return redirect('dashboard')


# ─────────────────────────── Contract (Manager) ──────────────────

class ContractListView(StaffRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        qs = HopDong.objects.select_related('can_ho', 'khach_hang', 'nhan_vien').all()

        if not (hasattr(request.user, 'quanly') or request.user.is_superuser):
            if hasattr(request.user, 'nhanvien'):
                qs = qs.filter(nhan_vien=request.user.nhanvien)
            elif hasattr(request.user, 'khachhang'):
                qs = qs.filter(khach_hang=request.user.khachhang)
            else:
                qs = qs.none()

        if tt := request.GET.get('tt'):
            qs = qs.filter(trang_thai=tt)
        if nv := request.GET.get('nv'):
            qs = qs.filter(nhan_vien__pk=nv)
        if tu_ngay := request.GET.get('tu_ngay'):
            qs = qs.filter(ngay_lap__gte=tu_ngay)

        from django.core.paginator import Paginator
        paginator = Paginator(qs, 15)
        page_obj = paginator.get_page(request.GET.get('page', 1))

        ctx = _base_context(request)
        ctx.update({
            'page_obj':       page_obj,
            'nhan_vien_list': NhanVien.objects.all() if (hasattr(request.user, 'quanly') or request.user.is_superuser) else [],
            'cho_duyet':      HopDong.objects.filter(trang_thai=HopDong.TrangThai.CHO_DUYET).count() if (hasattr(request.user, 'quanly') or request.user.is_superuser) else HopDong.objects.filter(nhan_vien=getattr(request.user, 'nhanvien', None), trang_thai=HopDong.TrangThai.CHO_DUYET).count(),
            'da_duyet':       HopDong.objects.filter(trang_thai=HopDong.TrangThai.DA_DUYET).count() if (hasattr(request.user, 'quanly') or request.user.is_superuser) else HopDong.objects.filter(nhan_vien=getattr(request.user, 'nhanvien', None), trang_thai=HopDong.TrangThai.DA_DUYET).count(),
        })
        return render(request, 'core/contract_list.html', ctx)


class ContractDetailView(StaffRequiredMixin, View):
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        hd = get_object_or_404(HopDong.objects.select_related('can_ho', 'khach_hang', 'nhan_vien'), pk=pk)
        
        # Security: Staff can only see their own contracts
        if not (hasattr(request.user, 'quanly') or request.user.is_superuser):
            if hasattr(request.user, 'nhanvien') and hd.nhan_vien != request.user.nhanvien:
                messages.error(request, 'Bạn không có quyền xem hợp đồng này.')
                return redirect('contract_list')
            elif hasattr(request.user, 'khachhang') and hd.khach_hang != request.user.khachhang:
                messages.error(request, 'Bạn không có quyền xem hợp đồng này.')
                return redirect('contract_list')
            elif hasattr(request.user, 'nhanvienmkt'):
                messages.error(request, 'Bạn không có quyền xem hợp đồng này.')
                return redirect('contract_list')

        ctx = _base_context(request)
        ctx['hd'] = hd
        return render(request, 'core/contract_detail.html', ctx)


class ContractRejectView(ManagerRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        hd = get_object_or_404(HopDong, pk=pk)
        hd.trang_thai = HopDong.TrangThai.TU_CHOI
        hd.save(update_fields=['trang_thai'])
        
        # Revert room status to TRONG
        hd.can_ho.trang_thai = CanHo.TrangThai.TRONG
        hd.can_ho.save(update_fields=['trang_thai'])
        
        messages.warning(request, f'Đã từ chối hợp đồng HĐ-{hd.pk:04d}. Phòng đã được mở lại.')
        return redirect('contract_list')


class ContractApproveView(ManagerRequiredMixin, View):
    """Duyệt hợp đồng → phòng chuyển DA_THUE."""
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        hd = get_object_or_404(HopDong, pk=pk)
        hd.trang_thai = HopDong.TrangThai.DA_DUYET
        hd.save(update_fields=['trang_thai'])
        hd.can_ho.trang_thai = CanHo.TrangThai.DA_THUE
        hd.can_ho.save(update_fields=['trang_thai'])
        messages.success(request, f'Đã duyệt hợp đồng HĐ-{hd.pk:04d}.')
        return redirect('contract_list')


class ContractRejectView(ManagerRequiredMixin, View):
    """Từ chối hợp đồng -> phòng quay về TRONG."""
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        hd = get_object_or_404(HopDong, pk=pk)
        hd.trang_thai = HopDong.TrangThai.TU_CHOI
        hd.save(update_fields=['trang_thai'])
        hd.can_ho.trang_thai = CanHo.TrangThai.TRONG
        hd.can_ho.save(update_fields=['trang_thai'])
        messages.warning(request, f'Đã từ chối hợp đồng HĐ-{hd.pk:04d}. Phòng trở về trạng thái Còn trống.')
        return redirect('contract_list')


class ContractCancelApproveView(ManagerRequiredMixin, View):
    """Hủy duyệt hợp đồng đã duyệt -> đưa về trạng thái TU_CHOI và phòng thành TRONG."""
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        hd = get_object_or_404(HopDong, pk=pk, trang_thai=HopDong.TrangThai.DA_DUYET)
        hd.trang_thai = HopDong.TrangThai.TU_CHOI
        hd.save(update_fields=['trang_thai'])
        hd.can_ho.trang_thai = CanHo.TrangThai.TRONG
        hd.can_ho.save(update_fields=['trang_thai'])
        messages.success(request, f'Đã hủy duyệt hợp đồng HĐ-{hd.pk:04d}. Phòng đã trở lại trạng thái Còn trống.')
        return redirect('contract_list')


class ContractEditView(StaffRequiredMixin, View):
    """Nhân viên hoặc Quản lý sửa hợp đồng đang chờ duyệt."""
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        hd = get_object_or_404(HopDong, pk=pk, trang_thai=HopDong.TrangThai.CHO_DUYET)
        if not (hasattr(request.user, 'quanly') or request.user.is_superuser) and hd.nhan_vien != getattr(request.user, 'nhanvien', None):
            messages.error(request, 'Bạn không có quyền sửa hợp đồng này.')
            return redirect('contract_list')
        
        ctx = _base_context(request)
        ctx['hd'] = hd
        ctx['phong'] = hd.can_ho
        return render(request, 'core/contract_edit.html', ctx)

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        hd = get_object_or_404(HopDong, pk=pk, trang_thai=HopDong.TrangThai.CHO_DUYET)
        if not (hasattr(request.user, 'quanly') or request.user.is_superuser) and hd.nhan_vien != getattr(request.user, 'nhanvien', None):
            messages.error(request, 'Bạn không có quyền sửa hợp đồng này.')
            return redirect('contract_list')

        # Cập nhật khách hàng
        hd.khach_hang.ho_ten = request.POST.get('ho_ten', hd.khach_hang.ho_ten).strip()
        hd.khach_hang.so_dien_thoai = request.POST.get('so_dien_thoai', hd.khach_hang.so_dien_thoai).strip()
        hd.khach_hang.email = request.POST.get('email', hd.khach_hang.email).strip()
        hd.khach_hang.save()

        # Cập nhật hợp đồng
        hd.ngay_lap = request.POST.get('ngay_lap') or hd.ngay_lap
        hd.tong_tien_thu = request.POST.get('tong_tien_thu', hd.tong_tien_thu)
        hd.minh_chung = request.POST.get('minh_chung', hd.minh_chung).strip()
        hd.ghi_chu = request.POST.get('ghi_chu', hd.ghi_chu).strip()
        messages.success(request, f'Đã cập nhật hợp đồng HĐ-{hd.pk:04d}.')
        return redirect('contract_list')


class ContractDeleteView(ManagerRequiredMixin, View):
    """Quản lý xóa hợp đồng, khôi phục phòng về Còn trống nếu hợp đồng đang duyệt/chờ duyệt."""
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        hd = get_object_or_404(HopDong, pk=pk)
        if hd.trang_thai in [HopDong.TrangThai.DA_DUYET, HopDong.TrangThai.CHO_DUYET]:
            hd.can_ho.trang_thai = CanHo.TrangThai.TRONG
            hd.can_ho.save(update_fields=['trang_thai'])
        hd.delete()
        messages.success(request, f'Đã xóa hợp đồng HĐ-{pk:04d} thành công.')
        return redirect('contract_list')


class ContractBulkActionView(ManagerRequiredMixin, View):
    """Xử lý hành động hàng loạt trên Hợp đồng."""
    def post(self, request: HttpRequest) -> HttpResponse:
        selected_ids_str = request.POST.getlist('selected_ids')
        action = request.POST.get('action')
        
        if not selected_ids_str:
            messages.warning(request, 'Vui lòng chọn ít nhất một hợp đồng.')
            return redirect('contract_list')
            
        selected_ids = [int(i) for i in selected_ids_str if i.isdigit()]
        contracts = HopDong.objects.filter(pk__in=selected_ids)
        
        count = 0
        if action == 'approve':
            for hd in contracts:
                if hd.trang_thai != HopDong.TrangThai.DA_DUYET:
                    hd.trang_thai = HopDong.TrangThai.DA_DUYET
                    hd.save(update_fields=['trang_thai'])
                    hd.can_ho.trang_thai = CanHo.TrangThai.DA_THUE
                    hd.can_ho.save(update_fields=['trang_thai'])
                    count += 1
            messages.success(request, f'Đã duyệt thành công {count} hợp đồng.')
            
        elif action == 'reject':
            for hd in contracts:
                if hd.trang_thai != HopDong.TrangThai.TU_CHOI:
                    hd.trang_thai = HopDong.TrangThai.TU_CHOI
                    hd.save(update_fields=['trang_thai'])
                    hd.can_ho.trang_thai = CanHo.TrangThai.TRONG
                    hd.can_ho.save(update_fields=['trang_thai'])
                    count += 1
            messages.warning(request, f'Đã từ chối {count} hợp đồng.')
            
        elif action == 'delete':
            for hd in contracts:
                if hd.trang_thai in [HopDong.TrangThai.DA_DUYET, HopDong.TrangThai.CHO_DUYET]:
                    hd.can_ho.trang_thai = CanHo.TrangThai.TRONG
                    hd.can_ho.save(update_fields=['trang_thai'])
                hd.delete()
                count += 1
            messages.success(request, f'Đã xóa vĩnh viễn {count} hợp đồng.')
            
        return redirect('contract_list')


# ─────────────────────────── Product CRUD (Manager) ──────────────

class ProductManageView(ManagerRequiredMixin, View):
    """Thêm hoặc sửa phòng."""
    def get(self, request: HttpRequest, pk: int | None = None) -> HttpResponse:
        phong = get_object_or_404(CanHo, pk=pk) if pk else None
        ctx = _base_context(request)
        ctx['phong'] = phong
        return render(request, 'core/product_form.html', ctx)

    def post(self, request: HttpRequest, pk: int | None = None) -> HttpResponse:
        phong = get_object_or_404(CanHo, pk=pk) if pk else CanHo()

        phong.ten_ch       = request.POST.get('ten_ch', '').strip()
        phong.gia          = request.POST.get('gia', 0)
        phong.loai_phong   = request.POST.get('loai_phong', CanHo.LoaiPhong.THUONG)
        phong.trang_thai   = request.POST.get('trang_thai', CanHo.TrangThai.TRONG)
        phong.mo_ta        = request.POST.get('mo_ta', '').strip()
        phong.dien_tich    = request.POST.get('dien_tich') or None
        cm_pk              = request.POST.get('chuyen_muc')
        if cm_pk:
            phong.chuyen_muc = get_object_or_404(ChuyenMuc, pk=cm_pk)
        phong.save()

        # Upsert DiaChi
        DiaChi.objects.update_or_create(
            can_ho=phong,
            defaults={
                'tinh':            request.POST.get('tinh', 'TP Hồ Chí Minh'),
                'quan':            request.POST.get('quan', ''),
                'dia_chi_cu_the':  request.POST.get('dia_chi_cu_the', ''),
            }
        )

        # Handle Image URLs (Syncing)
        current_urls = request.POST.getlist('anh_url')
        current_urls = [u.strip() for u in current_urls if u.strip()]
        
        # Delete images that are no longer in the list (user removed them from UI)
        phong.anh_set.exclude(link_anh__in=current_urls).delete()
        
        # Add new URLs that aren't in DB yet
        for url in current_urls:
            Anh.objects.get_or_create(can_ho=phong, link_anh=url)
        
        # 2. Files from upload fields
        files = request.FILES.getlist('anh_files')
        if files:
            import cloudinary.uploader
            for f in files:
                try:
                    result = cloudinary.uploader.upload(f, folder="alphahome/products")
                    secure_url = result.get('secure_url')
                    if secure_url:
                        Anh.objects.create(can_ho=phong, link_anh=secure_url)
                except Exception as e:
                    messages.error(request, f'Lỗi upload ảnh lên Cloudinary: {e}')

        messages.success(request, f'Đã lưu phòng "{phong.ten_ch}" thành công.')
        return redirect('product_detail', pk=phong.pk)


class ProductDeleteView(ManagerRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        from django.db.models import ProtectedError
        phong = get_object_or_404(CanHo, pk=pk)
        ten = phong.ten_ch
        try:
            phong.delete()
            messages.success(request, f'Đã xóa phòng "{ten}".')
        except ProtectedError:
            messages.error(request, f'Không thể xóa phòng "{ten}" vì đang có Hợp đồng liên quan. Vui lòng xóa hợp đồng trước.')
        return redirect('product_list')


class ProductBulkActionView(ManagerRequiredMixin, View):
    """Xử lý hành động hàng loạt trên Căn hộ/Phòng trọ."""
    def post(self, request: HttpRequest) -> HttpResponse:
        selected_ids_str = request.POST.getlist('selected_ids')
        action = request.POST.get('action')
        
        if not selected_ids_str:
            messages.warning(request, 'Vui lòng chọn ít nhất một phòng trọ.')
            return redirect('product_list')
            
        selected_ids = [int(i) for i in selected_ids_str if i.isdigit()]
        rooms = CanHo.objects.filter(pk__in=selected_ids)
        
        if action == 'delete':
            from django.db.models import ProtectedError
            deleted_count = 0
            protected_count = 0
            for r in rooms:
                try:
                    r.delete()
                    deleted_count += 1
                except ProtectedError:
                    protected_count += 1
            if deleted_count > 0:
                messages.success(request, f'Đã xóa thành công {deleted_count} phòng.')
            if protected_count > 0:
                messages.error(request, f'Không thể xóa {protected_count} phòng do đang có hợp đồng ràng buộc.')
                
        elif action == 'status_trong':
            rooms.update(trang_thai=CanHo.TrangThai.TRONG)
            messages.success(request, f'Đã chuyển trạng thái {rooms.count()} phòng thành Còn trống.')
            
        elif action == 'status_dathue':
            rooms.update(trang_thai=CanHo.TrangThai.DA_THUE)
            messages.success(request, f'Đã chuyển trạng thái {rooms.count()} phòng thành Đã thuê.')
            
        return redirect('product_list')


# ─────────────────────────── Report (Manager) ────────────────────

class ReportView(ManagerRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        today = timezone.now().date()
        seven_days = [today - timedelta(days=i) for i in range(6, -1, -1)]

        chart_labels = [d.strftime('%d/%m') for d in seven_days]
        chart_data = [
            int(HopDong.objects.filter(
                ngay_lap=d,
                trang_thai=HopDong.TrangThai.DA_DUYET
            ).aggregate(s=Sum('tong_tien_thu'))['s'] or 0)
            for d in seven_days
        ]

        week_start = today - timedelta(days=today.weekday())
        tong_hop_dong = HopDong.objects.filter(ngay_lap__gte=week_start).count()
        doanh_thu_tuan = HopDong.objects.filter(
            ngay_lap__gte=week_start,
            trang_thai=HopDong.TrangThai.DA_DUYET
        ).aggregate(s=Sum('tong_tien_thu'))['s'] or 0

        # Doanh thu từng nhân viên
        staff_revenue = []
        for nv in NhanVien.objects.all():
            rev = HopDong.objects.filter(
                nhan_vien=nv,
                trang_thai=HopDong.TrangThai.DA_DUYET
            ).aggregate(s=Sum('tong_tien_thu'))['s'] or 0
            staff_revenue.append({
                'name': nv.ho_ten,
                'revenue': int(rev)
            })
        staff_revenue.sort(key=lambda x: x['revenue'], reverse=True)
        
        total_revenue_all = sum(item['revenue'] for item in staff_revenue)
        for item in staff_revenue:
            item['percentage'] = (item['revenue'] / total_revenue_all * 100) if total_revenue_all > 0 else 0

        can_ho_qs = CanHo.objects.all()
        ctx = _base_context(request)
        ctx.update({
            'chart_labels':      chart_labels,
            'chart_data':        chart_data,
            'tong_hop_dong':     tong_hop_dong,
            'doanh_thu_tuan':    int(doanh_thu_tuan),
            'phong_trong':       can_ho_qs.filter(trang_thai=CanHo.TrangThai.TRONG).count(),
            'phong_cho_duyet':   can_ho_qs.filter(trang_thai=CanHo.TrangThai.CHO_DUYET).count(),
            'phong_da_thue':     can_ho_qs.filter(trang_thai=CanHo.TrangThai.DA_THUE).count(),
            'staff_revenue':     staff_revenue,
            'total_revenue_all': total_revenue_all,
        })
        return render(request, 'core/report.html', ctx)


# ─────────────────────────── Map (Staff) ─────────────────────────

import random

class MapView(StaffRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        qs = CanHo.objects.filter(trang_thai=CanHo.TrangThai.TRONG).select_related('dia_chi').prefetch_related('anh_set')
        
        # Tọa độ giả định cho các quận ở TP.HCM
        coords = {
            'Quận 1': [10.7756, 106.7019],
            'Quận 2': [10.7876, 106.7452],
            'Quận 3': [10.7816, 106.6858],
            'Quận 4': [10.7588, 106.7025],
            'Quận 5': [10.7540, 106.6635],
            'Quận 6': [10.7480, 106.6353],
            'Quận 7': [10.7335, 106.7272],
            'Quận 8': [10.7241, 106.6286],
            'Quận 9': [10.8428, 106.8286],
            'Quận 10': [10.7744, 106.6669],
            'Quận 11': [10.7628, 106.6433],
            'Quận 12': [10.8672, 106.6414],
            'Quận Bình Thạnh': [10.8061, 106.7056],
            'Quận Phú Nhuận': [10.7992, 106.6789],
            'Quận Gò Vấp': [10.8386, 106.6662],
            'Quận Tân Bình': [10.8015, 106.6526],
            'Quận Tân Phú': [10.7909, 106.6283],
            'Quận Bình Tân': [10.7653, 106.6033],
            'TP Thủ Đức': [10.8494, 106.7537],
            'Huyện Bình Chánh': [10.6874, 106.5939],
            'Huyện Hóc Môn': [10.8841, 106.5939],
            'Huyện Củ Chi': [11.0067, 106.5056],
            'Huyện Nhà Bè': [10.6015, 106.7377],
            'Huyện Cần Giờ': [10.4082, 106.8830],
        }
        
        map_data = []
        for phong in qs:
            quan = phong.dia_chi.quan if hasattr(phong, 'dia_chi') else ''
            if quan and quan in coords:
                base_lat, base_lng = coords[quan]
                # Thêm độ lệch ngẫu nhiên để các marker không đè lên nhau (bán kính khoảng 1-2km)
                lat = base_lat + random.uniform(-0.015, 0.015)
                lng = base_lng + random.uniform(-0.015, 0.015)
                
                # Format URL an toàn
                from django.urls import reverse
                detail_url = reverse('product_detail', args=[phong.pk])
                
                # Lấy ảnh đầu tiên
                anh_first = phong.anh_set.first()
                anh_url = anh_first.link_anh if anh_first else ''
                
                map_data.append({
                    'id': phong.pk,
                    'ten': phong.ten_ch,
                    'gia': f"{phong.gia:,.0f} đ".replace(',', '.'),
                    'url': detail_url,
                    'anh_url': anh_url,
                    'lat': lat,
                    'lng': lng,
                    'trang_thai': phong.get_trang_thai_display(),
                })
                
        ctx = _base_context(request)
        import json
        ctx['map_data_json'] = json.dumps(map_data)
        return render(request, 'core/map.html', ctx)

# ─────────────────────────── Account Management (Manager) ─────────

class AccountListView(ManagerRequiredMixin, ListView):
    model = User
    template_name = 'core/account_list.html'
    context_object_name = 'users'
    paginate_by = 10
    
    def get_queryset(self):
        return User.objects.filter(is_superuser=False).select_related('nhanvien', 'quanly', 'nhanvienmkt', 'khachhang').order_by('-date_joined')
        
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(_base_context(self.request))
        return ctx

class AccountCreateView(ManagerRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        ctx = _base_context(request)
        return render(request, 'core/account_form.html', ctx)
        
    def post(self, request: HttpRequest) -> HttpResponse:
        username = request.POST.get('username')
        password = request.POST.get('password')
        ho_ten = request.POST.get('ho_ten')
        sdt = request.POST.get('sdt')
        vai_tro = request.POST.get('vai_tro')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại.')
            return redirect('account_create')
            
        user = User.objects.create_user(username=username, password=password)
        
        if vai_tro == 'QUAN_LY':
            user.is_staff = True
            user.save()
            QuanLy.objects.create(user=user, ho_ten=ho_ten, so_dien_thoai=sdt, chuc_vu='Quản lý')
        elif vai_tro == 'NHAN_VIEN_MKT':
            NhanVienMKT.objects.create(user=user, ho_ten=ho_ten, so_dien_thoai=sdt)
        elif vai_tro == 'KHACH_HANG':
            KhachHang.objects.create(user=user, ho_ten=ho_ten, so_dien_thoai=sdt)
        else:
            NhanVien.objects.create(user=user, ho_ten=ho_ten, so_dien_thoai=sdt)
            
        messages.success(request, f'Tạo tài khoản {username} thành công.')
        return redirect('account_list')

class AccountDeleteView(ManagerRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        user_to_delete = get_object_or_404(User, pk=pk, is_superuser=False)
        username = user_to_delete.username
        
        if user_to_delete == request.user:
            messages.error(request, 'Bạn không thể tự xóa tài khoản của chính mình.')
            return redirect('account_list')
            
        if hasattr(user_to_delete, 'quanly') and not request.user.is_superuser:
            messages.error(request, 'Bạn không có quyền xóa tài khoản Quản lý khác.')
            return redirect('account_list')
            
        user_to_delete.delete()
        messages.success(request, f'Đã xóa tài khoản {username} thành công.')
        return redirect('account_list')

class AccountEditView(ManagerRequiredMixin, View):
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        u = get_object_or_404(User, pk=pk, is_superuser=False)
        
        if hasattr(u, 'quanly') and not request.user.is_superuser:
            messages.error(request, 'Bạn không có quyền sửa tài khoản Quản lý khác.')
            return redirect('account_list')
            
        ctx = _base_context(request)
        ctx.update({
            'u': u,
            'is_edit': True,
        })
        return render(request, 'core/account_form.html', ctx)

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        u = get_object_or_404(User, pk=pk, is_superuser=False)
        
        if hasattr(u, 'quanly') and not request.user.is_superuser:
            messages.error(request, 'Bạn không có quyền sửa tài khoản Quản lý khác.')
            return redirect('account_list')
            
        username = request.POST.get('username').strip()
        password = request.POST.get('password')
        ho_ten = request.POST.get('ho_ten').strip()
        sdt = request.POST.get('sdt').strip()
        vai_tro = request.POST.get('vai_tro')

        if username != u.username and User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại.')
            ctx = _base_context(request)
            ctx.update({'u': u, 'is_edit': True})
            return render(request, 'core/account_form.html', ctx)

        u.username = username
        if password:
            u.set_password(password)
            
        if vai_tro == 'QUAN_LY':
            u.is_staff = True
            NhanVien.objects.filter(user=u).delete()
            NhanVienMKT.objects.filter(user=u).delete()
            KhachHang.objects.filter(user=u).update(user=None)
            quan_ly, created = QuanLy.objects.get_or_create(user=u)
            quan_ly.ho_ten = ho_ten
            quan_ly.so_dien_thoai = sdt
            quan_ly.chuc_vu = 'Quản lý'
            quan_ly.save()
        elif vai_tro == 'NHAN_VIEN_MKT':
            u.is_staff = False
            QuanLy.objects.filter(user=u).delete()
            NhanVien.objects.filter(user=u).delete()
            KhachHang.objects.filter(user=u).update(user=None)
            nhan_vien_mkt, created = NhanVienMKT.objects.get_or_create(user=u)
            nhan_vien_mkt.ho_ten = ho_ten
            nhan_vien_mkt.so_dien_thoai = sdt
            nhan_vien_mkt.save()
        elif vai_tro == 'KHACH_HANG':
            u.is_staff = False
            QuanLy.objects.filter(user=u).delete()
            NhanVien.objects.filter(user=u).delete()
            NhanVienMKT.objects.filter(user=u).delete()
            khach_hang, created = KhachHang.objects.get_or_create(user=u)
            khach_hang.ho_ten = ho_ten
            khach_hang.so_dien_thoai = sdt
            khach_hang.save()
        else:
            u.is_staff = False
            QuanLy.objects.filter(user=u).delete()
            NhanVienMKT.objects.filter(user=u).delete()
            KhachHang.objects.filter(user=u).update(user=None)
            nhan_vien, created = NhanVien.objects.get_or_create(user=u)
            nhan_vien.ho_ten = ho_ten
            nhan_vien.so_dien_thoai = sdt
            nhan_vien.save()

        u.save()
        messages.success(request, f'Cập nhật tài khoản {username} thành công.')
        return redirect('account_list')

# ─────────────────────────── Profile & Security ───────────────────

class ProfileView(StaffRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        ctx = _base_context(request)
        # Lấy thông tin mở rộng tùy vào vai trò
        profile_info = {}
        if hasattr(request.user, 'quanly'):
            profile_info = {
                'ho_ten': request.user.quanly.ho_ten,
                'sdt': request.user.quanly.so_dien_thoai,
                'vai_tro': 'Quản lý',
                'chuc_vu': request.user.quanly.chuc_vu
            }
        elif request.user.is_superuser:
            profile_info = {
                'ho_ten': request.user.username,
                'sdt': 'N/A',
                'vai_tro': 'Admin / Quản lý cấp cao nhất',
                'chuc_vu': 'Superuser'
            }
        elif hasattr(request.user, 'nhanvien'):
            profile_info = {
                'ho_ten': request.user.nhanvien.ho_ten,
                'sdt': request.user.nhanvien.so_dien_thoai,
                'vai_tro': 'Nhân viên Sale',
                'chuc_vu': 'Nhân viên kinh doanh' # NhanVien model doesn't have chuc_vu field
            }
            
        ctx['profile'] = profile_info
        return render(request, 'core/profile.html', ctx)

class AlphaPasswordChangeView(StaffRequiredMixin, DjangoPasswordChangeView):
    template_name = 'core/password_change.html'
    success_url = reverse_lazy('dashboard')
    
    def form_valid(self, form):
        messages.success(self.request, 'Đổi mật khẩu thành công!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(_base_context(self.request))
        return ctx


