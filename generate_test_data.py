#!/usr/bin/env python
"""
Script para crear datos de prueba con Postulaciones y Documentos
Esto permitirá que el endpoint /api/dashboard-chart-data/ devuelva datos reales

USO:
    python generate_test_data.py
"""

import os
import sys
import django
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from postulantes.models import Postulacion, Postulante
from documentos.models import DocumentoPostulacion, TipoDocumento
from modalidades.models import Modalidad, Etapa
from usuarios.models import CustomUser

print("\n" + "="*60)
print("🔧 GENERADOR DE DATOS DE PRUEBA")
print("="*60)

# 1. Crear o obtener tutor
print("\n1️⃣  Creando usuario tutor...")
tutor, _ = CustomUser.objects.get_or_create(
    username='tutor_test',
    defaults={
        'email': 'tutor@test.com',
        'role': 'tutor',
        'is_active': True
    }
)
if not tutor.has_usable_password():
    tutor.set_password('test123')
    tutor.save()
print(f"   ✅ Tutor: {tutor.username}")

# 2. Obtener o crear modalidad
print("\n2️⃣  Obteniendo modalidad...")
modalidad = Modalidad.objects.first()
if not modalidad:
    modalidad = Modalidad.objects.create(
        nombre='Profesional',
        descripcion='Modalidad Profesional de prueba',
        activa=True
    )
    print(f"   ✅ Modalidad creada: {modalidad.nombre}")
else:
    print(f"   ✅ Modalidad encontrada: {modalidad.nombre}")

# 3. Obtener tipos de documento
print("\n3️⃣  Obteniendo tipos de documento...")
tipos_doc = list(TipoDocumento.objects.all()[:3])
if not tipos_doc:
    tipos_doc = [
        TipoDocumento.objects.create(nombre='Cédula', obligatorio=True),
        TipoDocumento.objects.create(nombre='Foto', obligatorio=True),
        TipoDocumento.objects.create(nombre='Certificado', obligatorio=True),
    ]
print(f"   ✅ Tipos de documento: {len(tipos_doc)}")

# 4. Crear postulantes y postulaciones con datos distribuidos en los últimos 6 meses
print("\n4️⃣  Generando postulaciones y documentos...")
fecha_inicio = timezone.now() - timedelta(days=180)
estados = ['TITULADO', 'APROBADO', 'EN_PROCESO', 'RECHAZADO']
total_postulaciones = 0
total_documentos = 0

# Crear 100 postulaciones distribuidas en 6 meses
for i in range(100):
    # Fecha aleatoria en los últimos 6 meses
    dias_offset = random.randint(0, 180)
    fecha_postulacion = fecha_inicio + timedelta(days=dias_offset)
    
    # Crear usuario para el postulante (usar get_or_create)
    usuario, usuario_created = CustomUser.objects.get_or_create(
        username=f'post_test_{i+1}',
        defaults={
            'email': f'postulante{i+1}@testdata.com',
        }
    )
    if usuario_created:
        usuario.set_password('test123')
        usuario.save()
    
    # Crear postulante (usar get_or_create)
    postulante, _ = Postulante.objects.get_or_create(
        usuario=usuario,
        defaults={
            'nombre': f'Nombre {i+1}',
            'apellido': f'Apellido {i+1}',
            'ci': f'{100000000 + i}',
            'telefono': f'+5895551{i:04d}',
            'codigo_estudiante': f'EST{100000 + i}'
        }
    )
    
    # Crear postulación
    estado = random.choice(estados)
    postulacion = Postulacion.objects.create(
        postulante=postulante,
        modalidad=modalidad,
        titulo_trabajo=f'Trabajo de Grado #{i+1}',
        anio_academico=2026,
        semestre_academico=random.choice([1, 2]),
        estado='aprobada',
        estado_general=estado,
        observaciones=f'Postulación de prueba #{i+1}'
    )
    # Actualizar fecha_postulacion (normalmente es auto_now_add, pero lo haremos manualmente)
    postulacion.fecha_postulacion = fecha_postulacion
    postulacion.save()
    total_postulaciones += 1
    
    # Crear 2-3 documentos por postulación
    num_documentos = random.randint(2, 3)
    for j in range(num_documentos):
        tipo_doc = random.choice(tipos_doc)
        estado_doc = random.choice(['aprobado', 'pendiente', 'rechazado'])
        
        fecha_documento = fecha_postulacion + timedelta(days=random.randint(0, 30))
        
        doc = DocumentoPostulacion.objects.create(
            postulacion=postulacion,
            tipo_documento=tipo_doc,
            archivo='test.pdf',
            estado=estado_doc,
            fecha_subida=fecha_documento,
            fecha_revision=fecha_documento + timedelta(days=1) if estado_doc != 'pendiente' else None,
        )
        total_documentos += 1

print(f"   ✅ Total postulaciones creadas: {total_postulaciones}")
print(f"   ✅ Total documentos creados: {total_documentos}")

# 5. Resumen
print("\n📊 5️⃣  RESUMEN DE DATOS:")
print("-" * 60)

total_pos = Postulacion.objects.count()
total_doc = DocumentoPostulacion.objects.count()
pos_por_estado = Postulacion.objects.values('estado_general').annotate(
    count=__import__('django.db.models', fromlist=['Count']).Count('id')
).order_by('-count')

print(f"   Total postulaciones en BD: {total_pos}")
print(f"   Total documentos en BD: {total_doc}")
print("\n   Postulaciones por estado:")
for item in pos_por_estado:
    print(f"      - {item['estado_general']}: {item['count']}")

# 6. Verificar que el endpoint puede acceder a los datos
print("\n🔍 6️⃣  VERIFICANDO ENDPOINT:")
print("-" * 60)

from reportes.services import get_dashboard_chart_data

result = get_dashboard_chart_data(meses=6)

print(f"   lineChartData items: {len(result['lineChartData'])}")
sum_line = sum(
    (item.get('graduados', 0) + item.get('pendientes', 0) + item.get('aprobados', 0))
    for item in result['lineChartData']
)
print(f"   Total en lineChartData: {sum_line}")

print(f"\n   barChartData items: {len(result['barChartData'])}")
sum_bar = sum(
    (item.get('postulantes', 0) + item.get('documentos', 0))
    for item in result['barChartData']
)
print(f"   Total en barChartData: {sum_bar}")

print(f"\n   pieChartData items: {len(result['pieChartData'])}")
sum_pie = sum(item.get('value', 0) for item in result['pieChartData'])
print(f"   Total en pieChartData: {sum_pie}")

print(f"\n   error: {result.get('error')}")

print("\n" + "="*60)
print("✅ DATOS DE PRUEBA GENERADOS EXITOSAMENTE")
print("="*60)
print("\nAhora puedes:")
print("  1. Iniciar Django: python manage.py runserver")
print("  2. Abrir http://localhost:8000/api/reportes/dashboard-chart-data/?meses=6")
print("  3. Verificar que devuelve datos REALES (no mock)")
print("  4. El frontend mostrará los datos en los gráficos")
print("\n" + "="*60 + "\n")
