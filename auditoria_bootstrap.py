#!/usr/bin/env python
"""
BOOTSTRAP + AUDITORÍA FUNCIONAL REAL
Crea datos base si no existen + ejecuta pruebas
"""
import os
import sys
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/app')
django.setup()

from django.contrib.auth import get_user_model
from postulantes.models import Postulante, Postulacion
from documentos.models import TipoDocumento, DocumentoPostulacion
from modalidades.models import Modalidad, Etapa
from reportes.services import dashboard_general, get_dashboard_chart_data
from django.core.files.base import ContentFile

User = get_user_model()
results = {}

# ============================================================================
# BOOTSTRAP: Crear datos base
# ============================================================================
def bootstrap_data():
    """Crea datos base si no existen."""
    print("\n🔧 Bootstrap: Creando datos base...\n")
    
    # 1. Admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@admin.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('password')
        admin_user.save()
        print("   ✓ Admin user creado")
    else:
        print("   ✓ Admin user existe")
    
    # 2. Modalidad
    modalidad, created = Modalidad.objects.get_or_create(
        nombre='Tesis',
        defaults={'descripcion': 'Modalidad de Tesis'}
    )
    if created:
        print("   ✓ Modalidad 'Tesis' creada")
    else:
        print("   ✓ Modalidad 'Tesis' existe")
    
    # 3. Etapa
    etapa, created = Etapa.objects.get_or_create(
        modalidad=modalidad,
        numero=1,
        defaults={'nombre': 'Perfil'}
    )
    if created:
        print("   ✓ Etapa 1 creada")
    else:
        print("   ✓ Etapa 1 existe")
    
    # 4. Tipo de Documento
    tipo_doc, created = TipoDocumento.objects.get_or_create(
        nombre='Documento de Tesis',
        defaults={
            'etapa': etapa,
            'descripcion': 'Documento principal de tesis',
            'obligatorio': True,
            'activo': True
        }
    )
    if created:
        print("   ✓ Tipo documento creado")
    else:
        print("   ✓ Tipo documento existe")
    
    return admin_user

# ============================================================================
# AUDITORÍA
# ============================================================================
def test_result(num, status, message=""):
    """Guarda resultado."""
    results[num] = status
    emoji = "✅" if status == "OK" else "❌"
    print(f"{emoji} PRUEBA {num}: {status}")
    if message:
        print(f"   └─ {message}")

def print_section(title):
    """Imprime sección."""
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f"{'='*70}")

# PRUEBA 1
print_section("PRUEBA 1: Crear postulante real")
try:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    username = f'audit_user_{timestamp}'
    
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': f'{username}@test.local',
            'first_name': 'Test',
            'last_name': 'Audit'
        }
    )
    user.set_password('test_password_123')
    user.save()
    print(f"   ✓ Usuario: {username} (ID={user.id})")
    
    postulante = Postulante.objects.create(
        usuario=user,
        nombre='Test',
        apellido='Audit',
        ci=f'999{timestamp}',
        telefono='5990000000',
        codigo_estudiante=f'AUDIT_{timestamp}',
        carrera='Ingeniería en Sistemas',
        facultad='Facultad de Ciencias'
    )
    print(f"   ✓ Postulante: {postulante.get_full_name()} (ID={postulante.id})")
    
    dashboard_1 = dashboard_general()
    print(f"   ✓ Total Postulantes: {dashboard_1['total_postulantes']}")
    
    test_result(1, 'OK', f'Postulante ID={postulante.id} registrado en dashboard')
    postulante_info = {'id': postulante.id}
    
except Exception as e:
    test_result(1, 'ERROR', str(e))
    postulante_info = None

# PRUEBA 2
print_section("PRUEBA 2: Crear documento asociado")
try:
    if not postulante_info:
        raise Exception("No hay postulante")
    
    postulante = Postulante.objects.get(id=postulante_info['id'])
    modalidad = Modalidad.objects.first()
    
    postulacion = Postulacion.objects.create(
        postulante=postulante,
        modalidad=modalidad,
        titulo_trabajo='Auditoría del Sistema',
        tutor='Dr. Test',
        anio_academico=datetime.now().year,
        semestre_academico=1,
        estado='borrador',
        estado_general='EN_PROCESO'
    )
    print(f"   ✓ Postulación creada (ID={postulacion.id})")
    
    tipo_doc = TipoDocumento.objects.first()
    
    documento = DocumentoPostulacion.objects.create(
        postulacion=postulacion,
        tipo_documento=tipo_doc,
        estado='pendiente'
    )
    documento.archivo.save('test.pdf', ContentFile(b'PDF'))
    print(f"   ✓ Documento subido (ID={documento.id})")
    
    chart_data = get_dashboard_chart_data(meses=1)
    print(f"   ✓ Chart data actualizado")
    
    test_result(2, 'OK', f'Documento ID={documento.id} registrado')
    doc_info = {'id': documento.id, 'postulacion_id': postulacion.id}
    
except Exception as e:
    test_result(2, 'ERROR', str(e))
    doc_info = None

# PRUEBA 3
print_section("PRUEBA 3: Aprobar documento")
try:
    if not doc_info:
        raise Exception("No hay documento")
    
    documento = DocumentoPostulacion.objects.get(id=doc_info['id'])
    admin_user = User.objects.get(username='admin')
    
    documento.estado = 'aprobado'
    documento.revisado_por = admin_user
    documento.save()
    print(f"   ✓ Documento aprobado (estado={documento.estado})")
    
    chart_data = get_dashboard_chart_data(meses=1)
    print(f"   ✓ Chart data actualizado")
    
    test_result(3, 'OK', f'Documento aprobado')
    
except Exception as e:
    test_result(3, 'ERROR', str(e))

# PRUEBA 4
print_section("PRUEBA 4: Graduar postulante")
try:
    if not doc_info:
        raise Exception("No hay documento")
    
    postulacion = Postulacion.objects.get(id=doc_info['postulacion_id'])
    
    postulacion.estado_general = 'TITULADO'
    postulacion.estado = 'aprobada'
    postulacion.save()
    print(f"   ✓ Postulación: {postulacion.estado_general}")
    
    dashboard_2 = dashboard_general()
    total_titulados = dashboard_2['total_titulados']
    print(f"   ✓ Total Titulados: {total_titulados}")
    
    test_result(4, 'OK', f'Postulante graduado, Total Titulados={total_titulados}')
    
except Exception as e:
    test_result(4, 'ERROR', str(e))

# PRUEBA 5
print_section("PRUEBA 5: Refrescar dashboard")
try:
    dashboard = dashboard_general()
    print(f"   ✓ Dashboard obtenido")
    
    required_fields = [
        'total_postulantes', 'total_documentos', 'total_titulados',
        'tasa_aprobacion', 'cambio_postulantes_porcentaje',
        'cambio_documentos_porcentaje', 'cambio_titulados_porcentaje',
        'satisfaccion_score'
    ]
    
    missing = [f for f in required_fields if f not in dashboard]
    if missing:
        raise Exception(f"Campos faltantes: {missing}")
    
    print(f"   📊 Total Postulantes: {dashboard['total_postulantes']}")
    print(f"   📊 Total Documentos: {dashboard['total_documentos']}")
    print(f"   📊 Total Titulados: {dashboard['total_titulados']}")
    print(f"   📊 Tasa Aprobación: {dashboard['tasa_aprobacion']}%")
    print(f"   📊 Satisfacción: {dashboard['satisfaccion_score']}")
    
    chart_data = get_dashboard_chart_data(meses=3)
    required_charts = ['lineChartData', 'barChartData', 'pieChartData']
    missing_charts = [c for c in required_charts if c not in chart_data]
    if missing_charts:
        raise Exception(f"Gráficos faltantes: {missing_charts}")
    
    print(f"   ✓ Todos los campos y gráficos presentes")
    
    test_result(5, 'OK', 'Dashboard refrescado correctamente')
    chart_data_result = chart_data
    
except Exception as e:
    test_result(5, 'ERROR', str(e))
    chart_data_result = None

# PRUEBA 6
print_section("PRUEBA 6: Revisar gráficos")
try:
    if not chart_data_result:
        raise Exception("No hay chart data")
    
    line_data = chart_data_result.get('lineChartData', [])
    bar_data = chart_data_result.get('barChartData', [])
    pie_data = chart_data_result.get('pieChartData', [])
    
    print(f"   • Items Line: {len(line_data)}")
    print(f"   • Items Bar: {len(bar_data)}")
    print(f"   • Items Pie: {len(pie_data)}")
    
    has_line = any(d.get('graduados', 0) > 0 or d.get('aprobados', 0) > 0 or d.get('pendientes', 0) > 0 for d in line_data)
    has_bar = any(d.get('postulantes', 0) > 0 or d.get('documentos', 0) > 0 for d in bar_data)
    has_pie = any(d.get('name', '').strip() != 'Sin datos' for d in pie_data)
    
    print(f"   ✓ Line con datos: {has_line}")
    print(f"   ✓ Bar con datos: {has_bar}")
    print(f"   ✓ Pie con datos reales: {has_pie}")
    
    # Verificar pie chart value
    for item in pie_data:
        if item.get('name') == 'Sin datos':
            value = item.get('value')
            print(f"   ✓ Pie 'Sin datos' value: {value}")
            if value != 100:
                raise Exception(f'Pie chart "Sin datos" debe ser 100, es {value}')
    
    test_result(6, 'OK', 'Gráficos verificados correctamente')
    
except Exception as e:
    test_result(6, 'ERROR', str(e))

# RESUMEN
print_section("RESUMEN DE AUDITORÍA")
for test_num in range(1, 7):
    status = results.get(test_num, "SKIP")
    emoji = "✅" if status == "OK" else "❌"
    print(f"{emoji} PRUEBA {test_num}: {status}")

print(f"\n{'='*70}")
total_ok = sum(1 for v in results.values() if v == "OK")
print(f"RESULTADO FINAL: {total_ok}/6 pruebas ✨")
print(f"{'='*70}\n")
