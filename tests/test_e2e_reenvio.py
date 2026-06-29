import io
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from documentos.models import DocumentoPostulacion, TipoDocumento
from postulantes.models import Postulante, Postulacion
from modalidades.models import Modalidad, Etapa


class TestReenvio(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = APIClient()
        self.admin = User.objects.create_user(username='e2e_admin_test', password='admin', is_superuser=True, is_staff=True)
        self.student = User.objects.create_user(username='e2e_student_test', password='student')

        self.postulante = Postulante.objects.create(usuario=self.student, nombre='Est', apellido='Ud', ci='E2E-TEST-1', telefono='000', codigo_estudiante='E2E-TEST-1')
        self.modalidad = Modalidad.objects.create(nombre='E2E Modalidad Test')
        self.etapa = Etapa.objects.create(nombre='E2E Etapa Test', orden=1, modalidad=self.modalidad)
        self.postulacion = Postulacion.objects.create(postulante=self.postulante, modalidad=self.modalidad, titulo_trabajo='T', anio_academico=2026, semestre_academico=1, gestion=2026)
        self.tipo = TipoDocumento.objects.create(nombre='E2E Tipo Test', etapa=self.etapa)

    def test_reenvio_estudiante_rechazado(self):
        # 1) estudiante crea documento
        self.client.force_authenticate(user=self.student)
        f1 = io.BytesIO(b'v1')
        f1.name = 'f1.pdf'
        resp = self.client.post('/api/documentos/', {'postulacion': self.postulacion.id, 'tipo_documento': self.tipo.id, 'archivo': f1}, format='multipart')
        assert resp.status_code in (200, 201)
        doc_id = resp.data['id']

        doc = DocumentoPostulacion.objects.get(id=doc_id)
        assert doc.estado == 'pendiente'

        # 2) admin rechaza
        self.client.force_authenticate(user=self.admin)
        resp2 = self.client.patch(f'/api/documentos/{doc_id}/', {'estado': 'rechazado', 'comentario_revision': 'bad'}, format='json')
        assert resp2.status_code == 200
        doc.refresh_from_db()
        assert doc.estado == 'rechazado'
        assert doc.revisado_por is not None

        count_before = DocumentoPostulacion.objects.count()

        # 3) estudiante reenvía
        self.client.force_authenticate(user=self.student)
        f2 = io.BytesIO(b'v2')
        f2.name = 'f2.pdf'
        resp3 = self.client.post('/api/documentos/', {'postulacion': self.postulacion.id, 'tipo_documento': self.tipo.id, 'archivo': f2}, format='multipart')
        assert resp3.status_code in (200, 201)
        new_id = resp3.data['id']
        assert new_id == doc_id
        assert DocumentoPostulacion.objects.count() == count_before

        doc.refresh_from_db()
        assert doc.estado == 'pendiente'
        assert doc.revisado_por is None
        assert doc.fecha_revision is None
        assert (doc.comentario_revision or '') == ''
