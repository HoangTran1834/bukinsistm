# scripts/hash_user_password.py
"""
Script to hash all user passwords in the database.
Should only be called from Makefile build process.
"""
import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datxe_backend.settings')
django.setup()

from datxe_backend.models import NguoiDung

for user in NguoiDung.objects.all():
    user.set_password(user.password)
    user.save()
print("All user passwords have been hashed.")
