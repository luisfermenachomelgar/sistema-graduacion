#!/usr/bin/env python
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
import django
django.setup()
from reportes.services import dashboard_general

print("=== VERIFICANDO MÉTRICAS DE DASHBOARD ===")
data = dashboard_general()
print(f"✅ Finalizadas: {data.get('modalidades_finalizadas', 'MISSING')}")
print(f"✅ Total postulantes: {data.get('total_postulantes', 'MISSING')}")
print(f"✅ Total postulaciones: {data.get('total_postulaciones', 'MISSING')}")
print(f"✅ Primeras claves: {list(data.keys())[:10]}")
