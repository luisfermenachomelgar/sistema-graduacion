import os
import random
import string
import io

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from postulantes.models import Postulante, Postulacion
from modalidades.models import Modalidad, Etapa
from documentos.models import TipoDocumento, DocumentoPostulacion
import documentos.views as views_module

User = get_user_model()
suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
student_username = f'e2e_student_dbg_full_{suffix}'
admin_username = f'e2e_admin_dbg_full_{suffix}'
student_user = User.objects.create_user(username=student_username, password='student')
admin = User.objects.create_user(username=admin_username, password='admin', is_superuser=True, is_staff=True)
postulante = Postulante.objects.create(usuario=student_user, nombre='E2E', apellido='Full', ci=f'E2E-RUN-FULL-{suffix}', telefono='000', codigo_estudiante=f'E2E-RUN-FULL-{suffix}')
modalidad = Modalidad.objects.create(nombre=f'E2E Modalidad full {suffix}')
etapa = Etapa.objects.create(nombre=f'E2E Etapa full {suffix}', orden=1, modalidad=modalidad)
postulacion = Postulacion.objects.create(postulante=postulante, modalidad=modalidad, titulo_trabajo='T', anio_academico=2026, semestre_academico=1, gestion=2026)
tipo = TipoDocumento.objects.create(nombre=f'E2E Tipo full {suffix}', etapa=etapa)

orig_create = views_module.DocumentoPostulacionViewSet.create

def debug_create(self, request, *args, **kwargs):
    print('=== INTERNAL CREATE START ===')
    print('class method', orig_create)
    print('user', getattr(request.user, 'username', None), 'authenticated', getattr(request.user, 'is_authenticated', None))
    print('request.data type', type(request.data))
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
    try:
        print('postulacion raw', request.data.get('postulacion'), 'tipo raw', request.data.get('tipo_documento'))
    except Exception as e:
        print('request.data.get error', e)
    resp = orig_create(self, request, *args, **kwargs)
    print('=== INTERNAL CREATE END ===', resp.status_code, resp.data)
    return resp

views_module.DocumentoPostulacionViewSet.create = debug_create
print('module file', views_module.__file__)
print('view create function', views_module.DocumentoPostulacionViewSet.create)
print('orig create', orig_create)
print('starting test')

client = APIClient()
client.force_authenticate(user=student_user)
file1 = io.BytesIO(b'v1'); file1.name = 'f1.pdf'
resp1 = client.post('/api/documentos/', {'postulacion': postulacion.id, 'tipo_documento': tipo.id, 'archivo': file1}, format='multipart')
print('create1 status', resp1.status_code)
print('create1 data', resp1.data)

print('count after create', DocumentoPostulacion.objects.filter(postulacion=postulacion, tipo_documento=tipo).count())
print('rows after create', list(DocumentoPostulacion.objects.filter(postulacion=postulacion, tipo_documento=tipo).values('id','estado','comentario_revision','archivo')))

client.force_authenticate(user=admin)
resp2 = client.patch(f'/api/documentos/{resp1.data["id"]}/', {'estado': 'rechazado', 'comentario_revision': 'bad'}, format='json')
print('patch status', resp2.status_code)
print('patch data', resp2.data)
print('count after patch', DocumentoPostulacion.objects.filter(postulacion=postulacion, tipo_documento=tipo).count())
print('rows after patch', list(DocumentoPostulacion.objects.filter(postulacion=postulacion, tipo_documento=tipo).values('id','estado','comentario_revision','archivo')))

client.force_authenticate(user=student_user)
file2 = io.BytesIO(b'v2'); file2.name = 'f2.pdf'
resp3 = client.post('/api/documentos/', {'postulacion': postulacion.id, 'tipo_documento': tipo.id, 'archivo': file2}, format='multipart')
print('resend status', resp3.status_code)
print('resend data', resp3.data)
print('count after resend', DocumentoPostulacion.objects.filter(postulacion=postulacion, tipo_documento=tipo).count())
print('rows after resend', list(DocumentoPostulacion.objects.filter(postulacion=postulacion, tipo_documento=tipo).values('id','estado','comentario_revision','archivo')))
