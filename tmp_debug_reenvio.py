import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from postulantes.models import Postulante, Postulacion
from modalidades.models import Modalidad, Etapa
from documentos.models import TipoDocumento, DocumentoPostulacion
from documentos.views import DocumentoPostulacionViewSet
import io

User = get_user_model()
student_user = User.objects.create_user(username='e2e_student_dbg', password='student')
admin = User.objects.create_user(username='e2e_admin_dbg', password='admin', is_superuser=True, is_staff=True)
postulante = Postulante.objects.create(usuario=student_user, nombre='E2E', apellido='Dbg', ci='E2E-RUN-DBG-EXT', telefono='000', codigo_estudiante='E2E-RUN-DBG-EXT')
modalidad = Modalidad.objects.create(nombre='E2E Modalidad dbg')
etapa = Etapa.objects.create(nombre='E2E Etapa dbg', orden=1, modalidad=modalidad)
postulacion = Postulacion.objects.create(postulante=postulante, modalidad=modalidad, titulo_trabajo='T', anio_academico=2026, semestre_academico=1, gestion=2026)
tipo = TipoDocumento.objects.create(nombre='E2E Tipo dbg', etapa=etapa)

# Instrument create method on the actual class
import documentos.views as views_module
orig_create = views_module.DocumentoPostulacionViewSet.create

def debug_create(self, request, *args, **kwargs):
    print('=== DEBUG_CREATE ENTER ===')
    print('user', getattr(request.user, 'username', None), 'auth', getattr(request.user, 'is_authenticated', None))
    try:
        print('request.data keys', list(request.data.keys()))
        print('request.data', {k: request.data.get(k) for k in ['postulacion', 'tipo_documento', 'archivo']})
    except Exception as e:
        print('request.data ERROR', e)
    try:
        print('request.FILES keys', list(request.FILES.keys()))
        print('request.FILES archivo', request.FILES.get('archivo'))
    except Exception as e:
        print('request.FILES ERROR', e)
    resp = orig_create(self, request, *args, **kwargs)
    print('response status', resp.status_code)
    print('response data', resp.data)
    print('=== DEBUG_CREATE EXIT ===')
    return resp

views_module.DocumentoPostulacionViewSet.create = debug_create

client = APIClient()
client.force_authenticate(user=student_user)
file1 = io.BytesIO(b'v1')
file1.name = 'f1.pdf'
resp1 = client.post('/api/documentos/', {'postulacion': postulacion.id, 'tipo_documento': tipo.id, 'archivo': file1}, format='multipart')
print('create1', resp1.status_code, resp1.data)

client.force_authenticate(user=admin)
resp2 = client.patch(f'/api/documentos/{resp1.data["id"]}/', {'estado': 'rechazado', 'comentario_revision': 'bad'}, format='json')
print('patch', resp2.status_code, resp2.data)

client.force_authenticate(user=student_user)
file2 = io.BytesIO(b'v2')
file2.name = 'f2.pdf'
resp3 = client.post('/api/documentos/', {'postulacion': postulacion.id, 'tipo_documento': tipo.id, 'archivo': file2}, format='multipart')
print('create2', resp3.status_code, resp3.data)
print('final count', DocumentoPostulacion.objects.filter(postulacion=postulacion, tipo_documento=tipo).count())
print('final docs', list(DocumentoPostulacion.objects.filter(postulacion=postulacion, tipo_documento=tipo).values('id','estado','comentario_revision','archivo')))
