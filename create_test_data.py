#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from postulantes.models import Postulante, Postulacion
from modalidades.models import Modalidad
from usuarios.models import CustomUser

print("=" * 70)
print("CREANDO ESTRUCTURA DE DATOS DE PRUEBA PARA DOCUMENTOS")
print("=" * 70)

# 1. Obtener o crear usuario test_user
user, _ = CustomUser.objects.get_or_create(
    username='test_user',
    defaults={'email': 'test@example.com'}
)
print(f"\n✓ Usuario: {user.username}")

# 2. Crear un Postulante y asociarlo a test_user
postulante, created = Postulante.objects.get_or_create(
    usuario=user,
    defaults={
        'nombre': 'Juan',
        'apellido': 'Pérez',
        'ci': '12345678',
        'telefono': '79123456',
        'codigo_estudiante': 'EST-001',
    }
)
status = "CREADO" if created else "EXISTENTE"
print(f"✓ Postulante: {postulante.nombre} {postulante.apellido} ({status})")

# 3. Obtener una modalidad existente
modalidad = Modalidad.objects.first()
if not modalidad:
    print("✗ No hay modalidades disponibles")
    exit(1)
print(f"✓ Modalidad: {modalidad.nombre}")

# 4. Crear una Postulación
postulacion, created = Postulacion.objects.get_or_create(
    postulante=postulante,
    modalidad=modalidad,
    anio_academico=2026,
    semestre_academico=1,
    defaults={
        'titulo_trabajo': 'Mi Proyecto de Prueba',
        'gestion': 2026,
        'estado': 'borrador',
    }
)
status = "CREADA" if created else "EXISTENTE"
print(f"✓ Postulación: {postulacion.titulo_trabajo} ({status})")
print(f"  - Estado: {postulacion.estado}")
print(f"  - Modalidad: {postulacion.modalidad.nombre}")

print("\n" + "=" * 70)
print("✅ ESTRUCTURA LISTA PARA PRUEBAS")
print("=" * 70)
print(f"\nUsuario: {user.username}")
print(f"Postulante: {postulante.nombre} {postulante.apellido}")
print(f"Postulación ID: {postulacion.id}")
print(f"Modalidad: {postulacion.modalidad.nombre}")
