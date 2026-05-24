import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alphahome.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import QuanLy

# Delete if already exists
User.objects.filter(username='temp_agent_manager').delete()

user = User.objects.create_superuser('temp_agent_manager', 'temp@temp.com', 'TempPass123!')
QuanLy.objects.create(user=user, ho_ten='Temp Manager', so_dien_thoai='0123456789', chuc_vu='Quản lý')
print("Successfully created temporary manager user 'temp_agent_manager'.")
