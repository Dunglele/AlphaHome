import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alphahome.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import QuanLy

print("MANAGERS:")
for ql in QuanLy.objects.select_related('user'):
    safe_name = ql.ho_ten.encode('ascii', 'replace').decode()
    print(f"QL Name: {safe_name}, Username: {ql.user.username}")

print("\nSUPERUSERS:")
for u in User.objects.filter(is_superuser=True):
    print(f"Username: {u.username}")
