#!/usr/bin/env python
"""
Script para verificar el endpoint /api/reportes/dashboard-chart-data/
Comprueba si devuelve datos reales o solo está retornando estructura vacía.

USO:
    python test_chart_endpoint.py

RESULTADO:
    Mostrará la estructura JSON que el endpoint devuelve
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reportes.services import get_dashboard_chart_data
from postulantes.models import Postulacion
from documentos.models import DocumentoPostulacion
from datetime import datetime, timedelta

print("\n" + "="*60)
print("🔍 DEBUG: TEST DEL ENDPOINT /api/dashboard-chart-data/")
print("="*60)

# 1. Verificar datos en la BD
print("\n📊 1. ESTADO DE LA BASE DE DATOS:")
print("-" * 60)

total_postulaciones = Postulacion.objects.count()
total_documentos = DocumentoPostulacion.objects.count()
            
print(f"   Total Postulaciones: {total_postulaciones}")
print(f"   Total Documentos: {total_documentos}")

# Ver distribución por estado
print("\n   Postulaciones por estado:")
estados = Postulacion.objects.values('estado_general').annotate(
    count=__import__('django.db.models', fromlist=['Count']).Count('id')
).order_by('-count')
for estado_item in estados:
    print(f"      - {estado_item['estado_general']}: {estado_item['count']}")

# Ver postulaciones en los últimos 6 meses
print("\n   Postulaciones últimos 6 meses:")
fecha_inicio = datetime.now() - timedelta(days=180)
recientes = Postulacion.objects.filter(fecha_postulacion__gte=fecha_inicio).count()
print(f"      {recientes} postulaciones desde {fecha_inicio.date()}")

# 2. Probar la función get_dashboard_chart_data()
print("\n🔄 2. RESULTADO DE get_dashboard_chart_data():")
print("-" * 60)

result = get_dashboard_chart_data(meses=6)

print("\n✓ lineChartData:")
if result['lineChartData']:
    for item in result['lineChartData'][:2]:  # Mostrar primeros 2
        print(f"   {item}")
    if len(result['lineChartData']) > 2:
        print(f"   ... y {len(result['lineChartData']) - 2} más")
    print(f"   TOTAL: {len(result['lineChartData'])} ítems")
else:
    print("   ❌ VACÍO")

print("\n✓ barChartData:")
if result['barChartData']:
    for item in result['barChartData'][:2]:
        print(f"   {item}")
    if len(result['barChartData']) > 2:
        print(f"   ... y {len(result['barChartData']) - 2} más")
    print(f"   TOTAL: {len(result['barChartData'])} ítems")
else:
    print("   ❌ VACÍO")

print("\n✓ pieChartData:")
if result['pieChartData']:
    for item in result['pieChartData']:
        print(f"   {item}")
    print(f"   TOTAL: {len(result['pieChartData'])} ítems")
else:
    print("   ❌ VACÍO")

print("\n✓ error field:", result.get('error'))

# 3. Análisis
print("\n📈 3. ANÁLISIS:")
print("-" * 60)

total_line = len(result['lineChartData']) if result['lineChartData'] else 0
total_bar = len(result['barChartData']) if result['barChartData'] else 0
total_pie = len(result['pieChartData']) if result['pieChartData'] else 0

has_line_data = total_line > 0 and sum(item.get('graduados', 0) + item.get('pendientes', 0) + item.get('aprobados', 0) for item in result['lineChartData']) > 0
has_bar_data = total_bar > 0 and sum(item.get('postulantes', 0) + item.get('documentos', 0) for item in result['barChartData']) > 0
has_pie_data = total_pie > 0 and sum(item.get('value', 0) for item in result['pieChartData']) > 0

print(f"\n✅ lineChartData tiene datos REALES: {has_line_data}")
if has_line_data:
    total_graduados = sum(item.get('graduados', 0) for item in result['lineChartData'])
    total_pendientes = sum(item.get('pendientes', 0) for item in result['lineChartData'])
    print(f"   - Graduados: {total_graduados}")
    print(f"   - Pendientes: {total_pendientes}")

print(f"\n✅ barChartData tiene datos REALES: {has_bar_data}")
if has_bar_data:
    total_postulantes = sum(item.get('postulantes', 0) for item in result['barChartData'])
    total_docs = sum(item.get('documentos', 0) for item in result['barChartData'])
    print(f"   - Postulantes: {total_postulantes}")
    print(f"   - Documentos: {total_docs}")

print(f"\n✅ pieChartData tiene datos REALES: {has_pie_data}")
if has_pie_data:
    total_registros = sum(item.get('value', 0) for item in result['pieChartData'])
    print(f"   - Total de registros: {total_registros}")

# 4. Conclusión
print("\n🎯 4. CONCLUSIÓN:")
print("-" * 60)

if has_line_data and has_bar_data and has_pie_data:
    print("✅ EL BACKEND DEVUELVE DATOS REALES")
    print("\nEl frontend debe:")
    print("  1. Asegurarse que el token está en localStorage")
    print("  2. Que el fetch llega al endpoint")
    print("  3. Que el estado (useState) se actualiza correctamente")
elif total_postulaciones == 0 or total_documentos == 0:
    print("⚠️  NO HAY DATOS EN LA BASE DE DATOS")
    print("\nAcciones:")
    print("  1. Ir a /admin y crear Postulaciones/Documentos")
    print("  2. O ejecutar: python create_test_users.py")
    print("  3. O ejecutar: python setup_test_users.py")
else:
    print("⚠️  HAY DATOS EN BD PERO NO SE MUESTRAN EN EL ENDPOINT")
    print("\nVerifica:")
    print("  1. Los filtros de fecha en get_dashboard_chart_data()")
    print("  2. El mapeo de datos en las queries")

print("\n" + "="*60)
print("FIN DEL DEBUG")
print("="*60 + "\n")
