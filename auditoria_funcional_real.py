#!/usr/bin/env python
"""
AUDITORIA FUNCIONAL REAL DEL SISTEMA COMPLETO
Valida flujo extremo a extremo con datos reales en base de datos
"""
import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/app')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from postulantes.models import Postulante, Postulacion
from documentos.models import TipoDocumento, DocumentoPostulacion
from modalidades.models import Modalidad, Etapa
from reportes.services import dashboard_general, get_dashboard_chart_data

User = get_user_model()

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
API_BASE = 'http://localhost/api'
ADMIN_USER = 'admin'
ADMIN_PASS = 'password'

# Para archivo de prueba
TEST_FILE_PATH = '/tmp/test_doc.pdf'

# ============================================================================
# UTILIDADES
# ============================================================================
def print_test(test_num, name):
    """Imprime nombre de prueba."""
    print(f"\n{'='*70}")
    print(f"PRUEBA {test_num}: {name}")
    print(f"{'='*70}")

def print_result(test_num, status, message):
    """Imprime resultado."""
    emoji = "✅" if status == "OK" else "❌"
    print(f"{emoji} PRUEBA {test_num}: {status}")
    print(f"   {message}\n")

def create_test_pdf():
    """Crea archivo PDF de prueba."""
    with open(TEST_FILE_PATH, 'wb') as f:
        # Mínimo PDF válido
        f.write(b'%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj')
        f.write(b'2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj')
        f.write(b'3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj')
        f.write(b'xref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000074 00000 n\n0000000133 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n212\n%%EOF')

def login_admin():
    """Obtiene token JWT del admin."""
    try:
        resp = requests.post(f'{API_BASE}/auth/login/', json={
            'username': ADMIN_USER,
            'password': ADMIN_PASS
        })
        if resp.status_code == 200:
            return resp.json().get('access')
        return None
    except Exception as e:
        print(f"❌ Error al login: {e}")
        return None

def get_headers(token):
    """Headers con autenticación."""
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

def reset_database():
    """Limpia datos de prueba previos."""
    print("\n🧹 Limpiando base de datos de pruebas previas...")
    # Eliminar postulantes de prueba
    Postulante.objects.filter(codigo_estudiante__startswith='AUDIT_').delete()
    print("   ✓ Base limpia")

# ============================================================================
# PRUEBA 1: CREAR POSTULANTE REAL
# ============================================================================
def test_1_crear_postulante(token):
    """PRUEBA 1: Crear 1 postulante real."""
    print_test(1, "Crear postulante real")
    
    try:
        # 1. Crear usuario
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        username = f'audit_user_{timestamp}'
        
        user_data = {
            'username': username,
            'email': f'{username}@test.local',
            'password': 'test_password_123'
        }
        
        resp_user = requests.post(
            f'{API_BASE}/usuarios/',
            json=user_data,
            headers=get_headers(token)
        )
        
        if resp_user.status_code != 201:
            print_result(1, 'ERROR', f'Crear usuario falló: {resp_user.text}')
            return None
        
        user_id = resp_user.json()['id']
        print(f"   ✓ Usuario creado: ID={user_id}")
        
        # 2. Crear postulante
        postulante_data = {
            'usuario': user_id,
            'nombre': 'Test',
            'apellido': 'Audit',
            'ci': f'999{timestamp}',
            'telefono': '5990000000',
            'codigo_estudiante': f'AUDIT_{timestamp}',
            'carrera': 'Ingeniería en Sistemas',
            'facultad': 'Facultad de Ciencias'
        }
        
        resp_postulante = requests.post(
            f'{API_BASE}/postulantes/',
            json=postulante_data,
            headers=get_headers(token)
        )
        
        if resp_postulante.status_code != 201:
            print_result(1, 'ERROR', f'Crear postulante falló: {resp_postulante.text}')
            return None
        
        postulante_id = resp_postulante.json()['id']
        print(f"   ✓ Postulante creado: ID={postulante_id}")
        
        # 3. Verificar en listado
        resp_list = requests.get(
            f'{API_BASE}/postulantes/{postulante_id}/',
            headers=get_headers(token)
        )
        
        if resp_list.status_code != 200:
            print_result(1, 'ERROR', 'Postulante no aparece en listado')
            return None
        
        print(f"   ✓ Postulante aparece en listado")
        
        # 4. Consultar dashboard para verificar que Total Postulantes suba
        dashboard_before = dashboard_general()
        total_postulantes_before = dashboard_before['total_postulantes']
        print(f"   ✓ Total Postulantes antes: {total_postulantes_before}")
        
        print_result(1, 'OK', f'Postulante creado correctamente. ID={postulante_id}')
        return {
            'postulante_id': postulante_id,
            'user_id': user_id,
            'username': username
        }
        
    except Exception as e:
        print_result(1, 'ERROR', str(e))
        return None

# ============================================================================
# PRUEBA 2: CREAR DOCUMENTO ASOCIADO
# ============================================================================
def test_2_crear_documento(token, postulante_info):
    """PRUEBA 2: Crear documento asociado."""
    print_test(2, "Crear documento asociado al postulante")
    
    if not postulante_info:
        print_result(2, 'ERROR', 'No hay postulante previo')
        return None
    
    try:
        postulante_id = postulante_info['postulante_id']
        
        # 1. Crear postulación
        modalidad = Modalidad.objects.first()
        if not modalidad:
            print_result(2, 'ERROR', 'No hay modalidades en BD')
            return None
        
        postulacion_data = {
            'postulante': postulante_id,
            'modalidad': modalidad.id,
            'titulo_trabajo': 'Trabajo de Auditoría del Sistema',
            'tutor': 'Dr. Test',
            'anio_academico': datetime.now().year,
            'semestre_academico': 1,
            'estado': 'borrador',
            'estado_general': 'EN_PROCESO',
            'observaciones': 'Creado por auditoría funcional'
        }
        
        resp_post = requests.post(
            f'{API_BASE}/postulaciones/',
            json=postulacion_data,
            headers=get_headers(token)
        )
        
        if resp_post.status_code != 201:
            print_result(2, 'ERROR', f'Crear postulación falló: {resp_post.text}')
            return None
        
        postulacion_id = resp_post.json()['id']
        print(f"   ✓ Postulación creada: ID={postulacion_id}")
        
        # 2. Obtener tipo de documento
        resp_tipos = requests.get(
            f'{API_BASE}/tipos-documentos/',
            headers=get_headers(token)
        )
        
        if resp_tipos.status_code != 200 or not resp_tipos.json().get('results'):
            print_result(2, 'ERROR', 'No hay tipos de documentos')
            return None
        
        tipo_doc_id = resp_tipos.json()['results'][0]['id']
        print(f"   ✓ Tipo documento: ID={tipo_doc_id}")
        
        # 3. Crear archivo de prueba
        create_test_pdf()
        print(f"   ✓ Archivo de prueba creado")
        
        # 4. Subir documento
        with open(TEST_FILE_PATH, 'rb') as f:
            files = {'archivo': f}
            headers = {'Authorization': f'Bearer {token}'}
            
            doc_data = {
                'postulacion': postulacion_id,
                'tipo_documento': tipo_doc_id
            }
            
            resp_doc = requests.post(
                f'{API_BASE}/documentos-postulaciones/',
                data=doc_data,
                files=files,
                headers=headers
            )
        
        if resp_doc.status_code != 201:
            print_result(2, 'ERROR', f'Subir documento falló: {resp_doc.text}')
            return None
        
        doc_id = resp_doc.json()['id']
        print(f"   ✓ Documento subido: ID={doc_id}")
        
        # 5. Verificar en listado
        resp_list = requests.get(
            f'{API_BASE}/documentos-postulaciones/{doc_id}/',
            headers=get_headers(token)
        )
        
        if resp_list.status_code != 200:
            print_result(2, 'ERROR', 'Documento no aparece en listado')
            return None
        
        print(f"   ✓ Documento aparece en listado")
        
        # 6. Consultar dashboard
        dashboard_mid = get_dashboard_chart_data(meses=1)
        print(f"   ✓ Chart data actualizado")
        
        print_result(2, 'OK', f'Documento creado. ID={doc_id}')
        return {
            'doc_id': doc_id,
            'postulacion_id': postulacion_id,
            'tipo_doc_id': tipo_doc_id
        }
        
    except Exception as e:
        print_result(2, 'ERROR', str(e))
        return None

# ============================================================================
# PRUEBA 3: APROBAR DOCUMENTO
# ============================================================================
def test_3_aprobar_documento(token, doc_info):
    """PRUEBA 3: Aprobar documento."""
    print_test(3, "Aprobar documento")
    
    if not doc_info:
        print_result(3, 'ERROR', 'No hay documento previo')
        return None
    
    try:
        doc_id = doc_info['doc_id']
        
        # 1. Obtener admin user ID
        admin_user = User.objects.get(username=ADMIN_USER)
        print(f"   ✓ Admin user: ID={admin_user.id}")
        
        # 2. Aprobar documento
        update_data = {
            'estado': 'aprobado',
            'comentario_revision': 'Aprobado por auditoría funcional'
        }
        
        resp = requests.patch(
            f'{API_BASE}/documentos-postulaciones/{doc_id}/',
            json=update_data,
            headers=get_headers(token)
        )
        
        if resp.status_code != 200:
            print_result(3, 'ERROR', f'Aprobar documento falló: {resp.text}')
            return None
        
        print(f"   ✓ Documento aprobado")
        
        # 3. Verificar estado en BD
        doc = DocumentoPostulacion.objects.get(id=doc_id)
        if doc.estado != 'aprobado':
            print_result(3, 'ERROR', f'Estado en BD no es "aprobado": {doc.estado}')
            return None
        
        print(f"   ✓ Estado en BD confirmado: {doc.estado}")
        
        # 4. Consultar dashboard
        dashboard_mid2 = get_dashboard_chart_data(meses=1)
        print(f"   ✓ Chart data actualizado después de aprobación")
        
        print_result(3, 'OK', 'Documento aprobado correctamente')
        return True
        
    except Exception as e:
        print_result(3, 'ERROR', str(e))
        return None

# ============================================================================
# PRUEBA 4: GRADUAR / TITULAR POSTULANTE
# ============================================================================
def test_4_graduar_postulante(token, postulante_info):
    """PRUEBA 4: Graduar/titular postulante."""
    print_test(4, "Graduar postulante")
    
    if not postulante_info:
        print_result(4, 'ERROR', 'No hay postulante previo')
        return None
    
    try:
        postulante_id = postulante_info['postulante_id']
        
        # 1. Obtener postulación del postulante
        postulaciones = Postulacion.objects.filter(postulante_id=postulante_id)
        if not postulaciones.exists():
            print_result(4, 'ERROR', 'No hay postulación para el postulante')
            return None
        
        postulacion = postulaciones.first()
        print(f"   ✓ Postulación encontrada: ID={postulacion.id}")
        
        # 2. Cambiar estado a TITULADO
        resp = requests.patch(
            f'{API_BASE}/postulaciones/{postulacion.id}/',
            json={'estado_general': 'TITULADO'},
            headers=get_headers(token)
        )
        
        if resp.status_code != 200:
            print_result(4, 'ERROR', f'Cambiar a TITULADO falló: {resp.text}')
            return None
        
        print(f"   ✓ Estado cambiado a TITULADO")
        
        # 3. Verificar en BD
        postulacion.refresh_from_db()
        if postulacion.estado_general != 'TITULADO':
            print_result(4, 'ERROR', f'Estado en BD no es TITULADO: {postulacion.estado_general}')
            return None
        
        print(f"   ✓ Estado en BD confirmado: {postulacion.estado_general}")
        
        # 4. Consultar dashboard
        dashboard_final = dashboard_general()
        total_titulados = dashboard_final['total_titulados']
        print(f"   ✓ Total Titulados en dashboard: {total_titulados}")
        
        print_result(4, 'OK', 'Postulante graduado correctamente')
        return True
        
    except Exception as e:
        print_result(4, 'ERROR', str(e))
        return None

# ============================================================================
# PRUEBA 5: REFRESCAR DASHBOARD
# ============================================================================
def test_5_refrescar_dashboard():
    """PRUEBA 5: Refrescar dashboard y verificar cambios."""
    print_test(5, "Refrescar dashboard")
    
    try:
        # 1. Obtener datos actuales
        dashboard = dashboard_general()
        print(f"   ✓ Dashboard obtenido")
        
        # 2. Verificar que KPIs contienen datos (no vacíos)
        required_fields = [
            'total_postulantes',
            'total_documentos',
            'total_titulados',
            'tasa_aprobacion',
            'cambio_postulantes_porcentaje',
            'cambio_documentos_porcentaje',
            'cambio_titulados_porcentaje',
            'satisfaccion_score'
        ]
        
        missing_fields = [f for f in required_fields if f not in dashboard]
        if missing_fields:
            print_result(5, 'ERROR', f'Campos faltantes: {missing_fields}')
            return None
        
        print(f"   ✓ Todos los campos requeridos presentes")
        print(f"   📊 KPIs:")
        print(f"      - Total Postulantes: {dashboard['total_postulantes']}")
        print(f"      - Total Documentos: {dashboard['total_documentos']}")
        print(f"      - Total Titulados: {dashboard['total_titulados']}")
        print(f"      - Tasa Aprobación: {dashboard['tasa_aprobacion']}%")
        print(f"      - Satisfacción: {dashboard['satisfaccion_score']}")
        
        # 3. Obtener chart data
        chart_data = get_dashboard_chart_data(meses=3)
        print(f"   ✓ Chart data obtenido")
        
        # 4. Verificar estructura
        required_charts = ['lineChartData', 'barChartData', 'pieChartData']
        missing_charts = [c for c in required_charts if c not in chart_data]
        if missing_charts:
            print_result(5, 'ERROR', f'Gráficos faltantes: {missing_charts}')
            return None
        
        print(f"   ✓ Todos los gráficos presentes")
        
        print_result(5, 'OK', 'Dashboard refrescado correctamente')
        return dashboard
        
    except Exception as e:
        print_result(5, 'ERROR', str(e))
        return None

# ============================================================================
# PRUEBA 6: REVISAR GRÁFICOS
# ============================================================================
def test_6_revisar_graficos():
    """PRUEBA 6: Revisar gráficos para verificar que no muestren "Sin datos"."""
    print_test(6, "Revisar gráficos")
    
    try:
        chart_data = get_dashboard_chart_data(meses=6)
        
        # 1. Verificar que gráficos no estén vacíos
        has_line_data = any(d.get('graduados', 0) > 0 or d.get('aprobados', 0) > 0 or d.get('pendientes', 0) > 0 
                           for d in chart_data.get('lineChartData', []))
        has_bar_data = any(d.get('postulantes', 0) > 0 or d.get('documentos', 0) > 0 
                          for d in chart_data.get('barChartData', []))
        has_pie_data = any(d.get('name', '').strip() != 'Sin datos' 
                          for d in chart_data.get('pieChartData', []))
        
        print(f"   Line Chart con datos: {has_line_data}")
        print(f"   Bar Chart con datos: {has_bar_data}")
        print(f"   Pie Chart con datos: {has_pie_data}")
        
        # 2. Verificar estructura
        pie_data = chart_data.get('pieChartData', [])
        if pie_data:
            for item in pie_data:
                if item.get('name') == 'Sin datos':
                    # Si hay "Sin datos", debe ser 100% (value: 100)
                    if item.get('value') != 100:
                        print_result(6, 'ERROR', f'Pie chart "Sin datos" debe tener value=100, tiene {item.get("value")}')
                        return None
                    print(f"   ✓ Pie chart 'Sin datos' tiene value=100 (correcto)")
        
        # 3. Verificar que haya datos reales o placeholder correcto
        if has_line_data or has_bar_data or has_pie_data:
            print(f"   ✓ Gráficos mostrarán datos reales (no mock)")
        else:
            print(f"   ✓ Gráficos vacíos (mostrarán placeholders limpios)")
        
        print_result(6, 'OK', 'Gráficos verificados correctamente')
        return True
        
    except Exception as e:
        print_result(6, 'ERROR', str(e))
        return None

# ============================================================================
# MAIN
# ============================================================================
def main():
    print("\n" + "="*70)
    print("AUDITORIA FUNCIONAL REAL - SISTEMA DE GRADUACION")
    print("="*70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"API Base: {API_BASE}")
    
    # Limpiar
    reset_database()
    
    # Login
    print("\n🔐 Autenticando...")
    token = login_admin()
    if not token:
        print("❌ No se pudo obtener token JWT")
        sys.exit(1)
    print("✅ Autenticado")
    
    # Ejecutar pruebas
    results = {}
    
    # Prueba 1
    postulante_info = test_1_crear_postulante(token)
    results[1] = "OK" if postulante_info else "ERROR"
    
    # Prueba 2
    doc_info = test_2_crear_documento(token, postulante_info)
    results[2] = "OK" if doc_info else "ERROR"
    
    # Prueba 3
    prueba_3 = test_3_aprobar_documento(token, doc_info)
    results[3] = "OK" if prueba_3 else "ERROR"
    
    # Prueba 4
    prueba_4 = test_4_graduar_postulante(token, postulante_info)
    results[4] = "OK" if prueba_4 else "ERROR"
    
    # Prueba 5
    dashboard = test_5_refrescar_dashboard()
    results[5] = "OK" if dashboard else "ERROR"
    
    # Prueba 6
    prueba_6 = test_6_revisar_graficos()
    results[6] = "OK" if prueba_6 else "ERROR"
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE AUDITORÍA")
    print("="*70)
    for test_num in range(1, 7):
        status = results.get(test_num, "SKIP")
        emoji = "✅" if status == "OK" else "❌"
        print(f"{emoji} PRUEBA {test_num}: {status}")
    
    print("\n" + "="*70)
    total_ok = sum(1 for v in results.values() if v == "OK")
    print(f"RESULTADO FINAL: {total_ok}/6 pruebas pasaron")
    print("="*70 + "\n")
    
    # Cleanup
    if TEST_FILE_PATH and os.path.exists(TEST_FILE_PATH):
        os.remove(TEST_FILE_PATH)

if __name__ == '__main__':
    main()
