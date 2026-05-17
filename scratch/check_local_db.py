import os
import sys
import django
from pathlib import Path

# Setup Django environment
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alphahome.settings")
django.setup()

from django.db import connections
from django.conf import settings
from core.models import CanHo, NhanVien, HopDong, ChuyenMuc

def main():
    # Save postgres config
    postgres_db = settings.DATABASES['default']
    
    # Swap to SQLite
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': Path(settings.BASE_DIR) / 'db.sqlite3',
    }
    connections['default'].close()
    
    print("=== LOCAL SQLITE RECORD COUNTS ===")
    print(f"CanHo count: {CanHo.objects.count()}")
    print(f"NhanVien count: {NhanVien.objects.count()}")
    print(f"HopDong count: {HopDong.objects.count()}")
    print(f"ChuyenMuc count: {ChuyenMuc.objects.count()}")

if __name__ == "__main__":
    main()
