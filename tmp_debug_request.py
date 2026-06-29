import os
import django
import random
import string
import io

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from django.contrib.auth import get_user_model
from postulantes.models import Postulante, Postulacion
from modalidades.models import Modalidad, Etapa
from documentos.models import TipoDocumento, DocumentoPostulacion
from documentos.views import DocumentoPostulacionViewSet

User = get_user_model()
suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
student_user = User.objects.create_user(username=f'e2e_student_req_{suffix}', password='student')
admin = User.objects.create_user(username=f'e2e_admin_req_{suffix}', password='admin', is_superuser=True, is_staff=True)
postulante = Postulante.objects.create(usuario=student_user, nombre='E2E', apellido='Req', ci=f'E2E-RUN-REQ-{suffix}', telefono='000', codigo_estudiante=f'E2E-RUN-REQ-{suffix}')
modalidad = Modalidad.objects.create(nombre=f'E2E Modalidad req {suffix}')
etapa = Etapa.objects.create(nombre=f'E2E Etapa req {suffix}', orden=1, modalidad=modalidad)
postulacion = Postulacion.objects.create(postulante=postulante, modalidad=modalidad, titulo_trabajo='T', anio_academico=2026, semestre_academico=1, gestion=2026)
tipo = TipoDocumento.objects.create(nombre=f'E2E Tipo req {suffix}', etapa=etapa)

factory = APIRequestFactory()
file1 = io.BytesIO(b'v1')
file1.name = 'f1.pdf'
request1 = factory.post('/api/documentos/', {'postulacion': str(postulacion.id), 'tipo_documento': str(tipo.id), 'archivo': file1}, format='multipart')
request1.user = student_user
request1 = Request(request1)
print('req1 data', request1.data)
print('req1 files', request1.FILES)
view = DocumentoPostulacionViewSet.as_view({'post': 'create'})
res1 = view(request1)
print('res1', res1.status_code, getattr(res1, 'data', None))

# exact object check
print('existing count', DocumentoPostulacion.objects.filter(postulacion_id=postulacion.id, tipo_documento_id=tipo.id).count())
print('existing item', DocumentoPostulacion.objects.filter(postulacion_id=postulacion.id, tipo_documento_id=tipo.id).first())
