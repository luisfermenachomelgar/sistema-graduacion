#!/usr/bin/env python
"""
Script simplificado para crear datos de prueba
Limpia y regenera datos desde cero
"""

import os
import sys
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from postulantes.models import Postulacion, Postulante
from documentos.models import DocumentoPostulacion, TipoDocumento
from modalidades.models import Modalidad
from usuarios.models import CustomUser
from django.utils import timezone
from datetime import datetime, timedelta
import random

print("\n" + "="*60)
print("🔧 LIMPIAR Y REGENERAR DATOS")
print("="*60)

# 1. Limpiar datos previos
print("\n🗑️  Limpiando datos previos...")
DocumentoPostulacion.objects.all().delete()
Postulacion.objects.all().delete()
Postulante.objects.all().delete()
# NO eliminar CustomUser

# 2. Crear tutor
print("\n👤 Creando tutor...")
tutor, _ = CustomUser.objects.get_or_create(
    username='tutor_data',
    defaults={'email': 'tutor.data@test.com', 'is_active': True}
)
if tutor.has_usable_password() is False:
    tutor.set_password('test123')
    tutor.save()

# 3. Obtener modalidad
print("\n📚 Obteniendo modalidad...")
modalidad = Modalidad.objects.filter(activa=True).first()
if not modalidad:
    modalidad = Modalidad.objects.create(nombre='Profesional', activa=True)

# 4. Obtener tipos de documento
print("\n📄 Obteniendo tipos de documento...")
tipos_doc = list(TipoDocumento.objects.all()[:3])
if not tipos_doc:
    tipos_doc = [
        TipoDocumento.objects.create(nombre='Cédula', obligatorio=True),
        TipoDocumento.objects.create(nombre='Foto', obligatorio=True),
        TipoDocumento.objects.create(nombre='Certificado', obligatorio=True),
    ]

# 5. Generar datos
print("\n✍️  Generando 50 postulaciones...")
fecha_inicio = timezone.now() - timedelta(days=180)
estados = ['TITULADO', 'APROBADO', 'EN_PROCESO', 'RECHAZADO']

for i in range(50):
    # Usuario único
    usuario, _ = CustomUser.objects.get_or_create(
        username=f'post_data_{i:03d}',
        defaults={'email': f'pdata{i:03d}@test.com'}
    )
    
    # Postulante
    ci_num = 10000000 + (i * 1000)  # CI único
    postulante = Postulante.objects.create(
        usuario=usuario,
        nombre=f'Estudiante {i+1}',
        apellido=f'Test Graduacion',
        ci=str(ci_num),
        telefono=f'+5895551{i:04d}',
        codigo_estudiante=f'ES{2026}{i:05d}'
    )
    
    # Postulación
    estado = random.choice(estados)
    dias_offset = random.randint(0, 180)
    fecha_post = fecha_inicio + timedelta(days=dias_offset)
    
    postulacion = Postulacion.objects.create(
        postulante=postulante,
        modalidad=modalidad,
        titulo_trabajo=f'Trabajo de Grado {i+1}',
        anio_academico=2026,
        semestre_academico=random.choice([1, 2]),
        estado='aprobada',
        estado_general=estado
    )
    postulacion.fecha_postulacion = fecha_post
    postulacion.save()
    
    # 2-3 documentos (evitar duplicados en (postulacion, tipo_documento))
    tipos_usados = set()
    num_docs = random.randint(2, min(3, len(tipos_doc)))
    for j in range(num_docs):
        # Seleccionar un tipo de documento que no se haya usado para esta postulación
        tipo_disponibles = [t for t in tipos_doc if t.id not in tipos_usados]
        if not tipo_disponibles:
            break
        tipo_doc_sel = random.choice(tipo_disponibles)
        tipos_usados.add(tipo_doc_sel.id)
        
        estado_doc = random.choice(['aprobado', 'pendiente', 'rechazado'])
        fecha_doc = fecha_post + timedelta(days=random.randint(1, 20))
        
        DocumentoPostulacion.objects.create(
            postulacion=postulacion,
            tipo_documento=tipo_doc_sel,
            archivo='prueba.pdf',
            estado=estado_doc,
            fecha_subida=fecha_doc
        )

print("\n" + "="*60)
print("✅ DATOS GENERADOS")
print("="*60)

# Verificar
from reportes.services import get_dashboard_chart_data

result = get_dashboard_chart_data(meses=6)
print(f"\n📊 Resultado del endpoint:")
print(f"   - lineChartData: {len(result['lineChartData'])} meses")
print(f"   - barChartData: {len(result['barChartData'])} semanas")
print(f"   - pieChartData: {len(result['pieChartData'])} estados")
print(f"   - error: {result.get('error')}")

print("\n✨ El endpoint ahora devuelve datos REALES")
print("   Reinicia Django y recarga el navegador")
print("="*60 + "\n")
