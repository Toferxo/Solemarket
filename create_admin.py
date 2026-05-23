"""
Script para crear el superusuario inicial.
Corre una sola vez: python create_admin.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solemarket.settings')
django.setup()

from django.contrib.auth.models import User

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@solemarket.cl')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin2026!')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'✅ Superusuario "{username}" creado.')
else:
    print(f'ℹ️  El usuario "{username}" ya existe, no se creó.')
