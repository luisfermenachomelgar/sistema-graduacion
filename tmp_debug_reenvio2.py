import os
import random
import string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from postulantes.models import Postulante, Postulacion
from modalidades.models import Modalidad, Etapa
from documentos.models import TipoDocumento, DocumentoPostulacion
import documentos.views as views_module
import io

suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
User = get_user_model()
student_user = User.objects.create_user(username=f'e2e_student_dbg2_{suffix}', password='student')
admin = User.objects.create_user(username=f'e2e_admin_dbg2_{suffix}', password='admin', is_superuser=True, is_staff=True)
postulante = Postulante.objects.create(usuario=student_user, nombre='E2E', apellido='Dbg2', ci=f'E2E-RUN-DBG2-{suffix}', telefono='000', codigo_estudiante=f'E2E-RUN-DBG2-{suffix}')
modalidad = Modalidad.objects.create(nombre=f'E2E Modalidad dbg2 {suffix}')
etapa = Etapa.objects.create(nombre=f'E2E Etapa dbg2 {suffix}', orden=1, modalidad=modalidad)
postulacion = Postulacion.objects.create(postulante=postulante, modalidad=modalidad, titulo_trabajo='T', anio_academico=2026, semestre_academico=1, gestion=2026)
tipo = TipoDocumento.objects.create(nombre=f'E2E Tipo dbg2 {suffix}', etapa=etapa)

orig_create = views_module.DocumentoPostulacionViewSet.create

def debug_create(self, request, *args, **kwargs):
    print('=== DEBUG CREATE ENTER ===')
    print('user', getattr(request.user, 'username', None), 'authenticated', getattr(request.user, 'is_authenticated', None))
    try:
        print('request.data keys', list(request.data.keys()))
    except Exception as e:
        print('request.data keys error', e)
    try:
        print('request.data values', {k: request.data.get(k) for k in ['postulacion', 'tipo_documento', 'archivo']})
    except Exception as e:
        print('request.data values error', e)
    try:
        print('request.FILES keys', list(request.FILES.keys()))
    except Exception as e:
        print('request.FILES keys error', e)
    print('request.FILES archivo', request.FILES.get('archivo'))
    resp = orig_create(self, request, *args, **kwargs)
    print('=== DEBUG CREATE EXIT ===', resp.status_code, resp.data)
    return resp

views_module.DocumentoPostulacionViewSet.create = debug_create

client = APIClient()
client.force_authenticate(user=student_user)
file1 = io.BytesIO(b'v1')
file1.name = 'f1.pdf'
resp1 = client.post('/api/documentos/', {'postulacion': postulacion.id, 'tipo_documento': tipo.id, 'archivo': file1}, format='multipart')
print('create1 status', resp1.status_code)
print('create1 data', resp1.data)

client.force_authenticate(user=admin)
resp2 = client.patch(f'/api/documentos/{resp1.data["id"]}/', {'estado': 'rechazado', 'comentario_revision': 'bad'}, format='json')
print('patch status', resp2.status_code)
print('patch data', resp2.data)

client.force_authenticate(user=student_user)
file2 = io.BytesIO(b'v2')
file2.name = 'f2.pdf'
resp3 = client.post('/api/documentos/', {'postulacion': postulacion.id, 'tipo_documento': tipo.id, 'archivo': file2}, format='multipart')
print('resend status', resp3.status_code)
print('resend data', resp3.data)
print('final count', DocumentoPostulacion.objects.filter(postulacion=postulacion, tipo_documento=tipo).count())
print('final rows', list(DocumentoPostulacion.objects.filter(postulacion=postulacion, tipo_documento=tipo).values('id','estado','comentario_revision','archivo')))
