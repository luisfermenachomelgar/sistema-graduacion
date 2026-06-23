#!/usr/bin/env python
import os
import sys
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from usuarios.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken

# Obtener admin user
admin = CustomUser.objects.first()
if not admin:
    print("❌ No admin user found")
    sys.exit(1)

# Generar token
refresh = RefreshToken.for_user(admin)
token = str(refresh.access_token)

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Llamar al endpoint
print("🔄 Calling: GET /api/reportes/estadisticas-tutores/exportar/")
response = requests.get('http://localhost:8000/api/reportes/estadisticas-tutores/exportar/', headers=headers)
print(f"Status: {response.status_code}")
print(f"Response:\n{response.text[:1000]}")

if response.status_code == 400:
    print("\n⚠️ Got 400 Bad Request - checking JSON:")
    try:
        data = response.json()
        print(f"Error details: {data}")
    except:
        print("Could not parse JSON response")
