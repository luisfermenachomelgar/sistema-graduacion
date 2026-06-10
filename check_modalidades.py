#!/usr/bin/env python
"""Script para diagnosticar origen de modalidades"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from modalidades.models import Modalidad
from django.db import connection

print("=" * 80)
print("MODALIDADES EN LA BD")
print("=" * 80)

for mod in Modalidad.objects.all():
    print(f"\nID: {mod.id}")
    print(f"  Nombre: {mod.nombre}")
    print(f"  Descripción: {mod.descripcion}")
    print(f"  Activa: {mod.activa}")
    print(f"  Creada: {mod.creada_en}")
    print(f"  Etapas: {mod.etapas.count()}")

# Ver logs de migrations
print("\n" + "=" * 80)
print("MIGRATIONS APLICADAS")
print("=" * 80)
with connection.cursor() as cursor:
    cursor.execute("SELECT app, name FROM django_migrations WHERE app = 'modalidades' ORDER BY id")
    for app, name in cursor.fetchall():
        print(f"  {name}")

print("\n" + "=" * 80)
