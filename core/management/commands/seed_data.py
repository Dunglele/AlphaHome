r"""
Seed data: tạo user admin/quanly/nhanvien + chuyên mục + 12 phòng mẫu.
Chạy: .\venv\Scripts\python.exe manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import NhanVien, QuanLy, ChuyenMuc, CanHo, Anh, DiaChi


SAMPLE_PHONG = [
    {
        'ten': 'Phòng trọ cao cấp full nội thất Quận Bình Thạnh',
        'gia': 4_500_000, 'loai': 'BANCOL', 'dien_tich': 25,
        'quan': 'Quận Bình Thạnh', 'dia_chi': '120 Đinh Bộ Lĩnh',
        'mo_ta': 'Phòng trọ cao cấp, đầy đủ nội thất, gần chợ, an ninh 24/7.',
        'anh': 'https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800&q=80',
    },
    {
        'ten': 'Căn hộ dịch vụ Quận 1 view sông Sài Gòn',
        'gia': 12_000_000, 'loai': 'DUPLEX', 'dien_tich': 45,
        'quan': 'Quận 1', 'dia_chi': '55 Bến Vân Đồn',
        'mo_ta': 'Căn hộ cao cấp tầng 15, view sông tuyệt đẹp, bể bơi, gym.',
        'anh': 'https://images.unsplash.com/photo-1502672260266-1c1de2d93688?w=800&q=80',
    },
    {
        'ten': 'Phòng trọ giá rẻ gần Đại học Bách Khoa Quận 10',
        'gia': 2_800_000, 'loai': 'BANCOL', 'dien_tich': 18,
        'quan': 'Quận 10', 'dia_chi': '45 Lý Thường Kiệt',
        'mo_ta': 'Gần Bách Khoa, Sư Phạm. Có wifi, máy lạnh, chỗ để xe.',
        'anh': 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&q=80',
    },
    {
        'ten': 'Căn hộ dịch vụ 2PN Vinhomes Grand Park Quận 9',
        'gia': 15_000_000, 'loai': 'DUPLEX', 'dien_tich': 65,
        'quan': 'TP Thủ Đức', 'dia_chi': 'Vinhomes Grand Park',
        'mo_ta': '2 phòng ngủ, 2WC, đầy đủ nội thất cao cấp. Bao phí quản lý.',
        'anh': 'https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800&q=80',
    },
    {
        'ten': 'Phòng trọ sạch sẽ yên tĩnh Quận 7 gần Phú Mỹ Hưng',
        'gia': 3_500_000, 'loai': 'BANCOL', 'dien_tich': 22,
        'quan': 'Quận 7', 'dia_chi': '88 Nguyễn Thị Thập',
        'mo_ta': 'Khu an ninh, sạch sẽ, gần siêu thị Big C, Lotte Mart.',
        'anh': 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&q=80',
    },
    {
        'ten': 'Căn hộ Studio Masteri Thảo Điền Quận 2',
        'gia': 9_500_000, 'loai': 'DUPLEX', 'dien_tich': 35,
        'quan': 'TP Thủ Đức', 'dia_chi': '159 Xa Lộ Hà Nội',
        'mo_ta': 'Studio cao cấp, full nội thất Châu Âu, hồ bơi vô cực.',
        'anh': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    },
    {
        'ten': 'Phòng trọ mới xây gần cầu Tham Lương Quận 12',
        'gia': 2_200_000, 'loai': 'BANCOL', 'dien_tich': 20,
        'quan': 'Quận 12', 'dia_chi': '200 Tô Ký',
        'mo_ta': 'Phòng mới, sàn gạch, có toilet riêng, WC khép kín.',
        'anh': 'https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800&q=80',
    },
    {
        'ten': 'Căn hộ dịch vụ cao cấp Midtown Phú Mỹ Hưng Quận 7',
        'gia': 22_000_000, 'loai': 'DUPLEX', 'dien_tich': 80,
        'quan': 'Quận 7', 'dia_chi': 'Midtown, Phú Mỹ Hưng',
        'mo_ta': 'Căn hộ hạng sang, 3PN, view công viên, trang bị đồ đẳng cấp.',
        'anh': 'https://images.unsplash.com/photo-1560185127-6ed189bf02f4?w=800&q=80',
    },
]


class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu cho hệ thống AlphaHome'

    def handle(self, *args, **kwargs):
        self.stdout.write('[+] Bat dau tao seed data...')

        # Quản lý
        ql_user, _ = User.objects.get_or_create(username='quanly', defaults={
            'first_name': 'Trần', 'last_name': 'Văn Quản',
            'email': 'quanly@alphahome.vn', 'is_staff': True,
        })
        ql_user.set_password('alphahome123')
        ql_user.save()
        ql, _ = QuanLy.objects.get_or_create(user=ql_user, defaults={
            'ho_ten': 'Trần Văn Quản', 'so_dien_thoai': '0901000001', 'chuc_vu': 'Quản lý trưởng',
        })
        self.stdout.write('  [v] Quan ly: quanly / alphahome123')

        # Nhân viên Sale
        nv_user, _ = User.objects.get_or_create(username='nhanvien', defaults={
            'first_name': 'Nguyễn', 'last_name': 'Thị Sale',
            'email': 'nhanvien@alphahome.vn',
        })
        nv_user.set_password('alphahome123')
        nv_user.save()
        nv, _ = NhanVien.objects.get_or_create(user=nv_user, defaults={
            'ho_ten': 'Nguyễn Thị Sale', 'so_dien_thoai': '0901000002',
        })
        self.stdout.write('  [v] Nhan vien: nhanvien / alphahome123')

        # Chuyên mục
        cm_data = [
            ('Phòng trọ', 'fa-bed', ql),
            ('Căn hộ dịch vụ', 'fa-building', ql),
            ('Dự án', 'fa-city', ql),
        ]
        chuyen_muc = {}
        for ten, icon, manager in cm_data:
            cm, _ = ChuyenMuc.objects.get_or_create(ten_cm=ten, defaults={'icon': icon, 'quan_ly': manager})
            chuyen_muc[ten] = cm
        self.stdout.write('  [v] 3 chuyen muc')

        # Phòng mẫu
        for i, data in enumerate(SAMPLE_PHONG):
            if CanHo.objects.filter(ten_ch=data['ten']).exists():
                continue
            cm_key = 'Căn hộ dịch vụ' if data['loai'] == 'DUPLEX' else 'Phòng trọ'
            phong = CanHo.objects.create(
                ten_ch=data['ten'],
                gia=data['gia'],
                loai_phong=data['loai'],
                dien_tich=data['dien_tich'],
                mo_ta=data['mo_ta'],
                chuyen_muc=chuyen_muc[cm_key],
                trang_thai=CanHo.TrangThai.TRONG,
            )
            DiaChi.objects.create(
                can_ho=phong,
                quan=data['quan'],
                dia_chi_cu_the=data['dia_chi'],
            )
            Anh.objects.create(can_ho=phong, link_anh=data['anh'], la_anh_chinh=True)

        self.stdout.write(f'  [v] {len(SAMPLE_PHONG)} phong mau')
        self.stdout.write(self.style.SUCCESS('\n[OK] Seed data hoan tat!'))
        self.stdout.write('\n  Dang nhap:')
        self.stdout.write('  Quan ly  -> quanly / alphahome123')
        self.stdout.write('  Nhan vien -> nhanvien / alphahome123')
