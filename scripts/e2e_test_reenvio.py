import os
import django
import io
import sys
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from documentos.models import DocumentoPostulacion, TipoDocumento
from postulantes.models import Postulante, Postulacion
from modalidades.models import Modalidad, Etapa

User = get_user_model()

client = APIClient()

# Limpiar posibles datos previos (solo para entorno de pruebas local)
User.objects.filter(username__in=['e2e_student', 'e2e_admin']).delete()
Modalidad.objects.filter(nombre='E2E Modalidad').delete()
TipoDocumento.objects.filter(nombre='E2E Tipo').delete()

# Crear usuarios
admin = User.objects.create_user(username='e2e_admin', email='admin@example.com', password='admin', is_superuser=True, is_staff=True)
student_user = User.objects.create_user(username='e2e_student', email='student@example.com', password='student')

# Crear postulante y postulacion
postulante = Postulante.objects.create(usuario=student_user, nombre='Est', apellido='Ud', ci='E2E-001', telefono='000', codigo_estudiante='E2E-001')
modalidad = Modalidad.objects.create(nombre='E2E Modalidad')
etapa = Etapa.objects.create(nombre='E2E Etapa', orden=1, modalidad=modalidad)
postulacion = Postulacion.objects.create(postulante=postulante, modalidad=modalidad, titulo_trabajo='T', anio_academico=2026, semestre_academico=1, gestion=2026)

# Crear tipo documento
tipo = TipoDocumento.objects.create(nombre='E2E Tipo', etapa=etapa)

print('Setup completo')

# 1) Estudiante crea documento por primera vez
client.force_authenticate(user=student_user)
file1 = io.BytesIO(b'Test file content v1')
file1.name = 'doc_v1.pdf'
resp = client.post('/api/documentos/', {'postulacion': postulacion.id, 'tipo_documento': tipo.id, 'archivo': file1}, format='multipart')
print('POST estudiante status_code:', resp.status_code, 'data:', resp.data)
if resp.status_code not in (200,201):
    print('Fallo creación por estudiante')
    sys.exit(2)

doc_id = resp.data['id']
doc = DocumentoPostulacion.objects.get(id=doc_id)
assert doc.estado == 'pendiente', f"Esperado 'pendiente', got {doc.estado}"

# 2) Admin rechaza el documento
client.force_authenticate(user=admin)
resp2 = client.patch(f'/api/documentos/{doc_id}/', {'estado': 'rechazado', 'comentario_revision': 'No cumple formato'}, format='json')
print('PATCH admin status_code:', resp2.status_code, 'data:', resp2.data)
if resp2.status_code != 200:
    print('Fallo rechazo por admin')
    sys.exit(3)

doc.refresh_from_db()
assert doc.estado == 'rechazado', f"Esperado 'rechazado', got {doc.estado}"
assert doc.revisado_por is not None, 'revisado_por debe estar seteado'
assert doc.fecha_revision is not None, 'fecha_revision debe estar seteado'

# Guardar conteo antes del reenvío
count_before = DocumentoPostulacion.objects.count()

# 3) Estudiante reenvía documento del mismo tipo
client.force_authenticate(user=student_user)
file2 = io.BytesIO(b'Test file content v2')
file2.name = 'doc_v2.pdf'
resp3 = client.post('/api/documentos/', {'postulacion': postulacion.id, 'tipo_documento': tipo.id, 'archivo': file2}, format='multipart')
print('POST reenvío estudiante status_code:', resp3.status_code, 'data:', resp3.data)
if resp3.status_code not in (200,201):
    print('Fallo reenvío por estudiante')
    sys.exit(4)

new_doc_id = resp3.data['id']
# Verificar que es el mismo id (reutilizado)
if new_doc_id != doc_id:
    print('ERROR: Se creó un nuevo DocumentoPostulacion en lugar de reutilizar el existente', new_doc_id, doc_id)
    sys.exit(5)

# Verificar que no se aumentó el conteo
count_after = DocumentoPostulacion.objects.count()
if count_after != count_before:
    print('ERROR: Conteo de documentos cambió (se creó uno nuevo)')
    sys.exit(6)

# Verificar campos limpiados
doc.refresh_from_db()
assert doc.estado == 'pendiente', f"Esperado 'pendiente' tras reenvío, got {doc.estado}"
assert doc.revisado_por is None, 'revisado_por debe ser None tras reenvío'
assert doc.fecha_revision is None, 'fecha_revision debe ser None tras reenvío'
assert (doc.comentario_revision or '') == '', f"comentario_revision debe quedar vacío, actual: {doc.comentario_revision}"

print('E2E tests PASSED')
sys.exit(0)
