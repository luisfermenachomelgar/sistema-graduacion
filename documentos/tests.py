from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from documentos.models import TipoDocumento
from modalidades.models import Etapa, Modalidad
from postulantes.models import Postulante, Postulacion


class DocumentoPostulacionStageRulesTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='estudiante',
            email='estudiante@example.com',
            password='password123',
        )
        self.postulante = Postulante.objects.create(
            usuario=self.user,
            nombre='Ana',
            apellido='Pérez',
            ci='12345678',
            telefono='60000000',
            codigo_estudiante='EST-001',
        )
        self.modalidad = Modalidad.objects.create(nombre='EXAMEN DE GRADO')
        self.etapa_registro = Etapa.objects.create(modalidad=self.modalidad, nombre='Registro', orden=1, activo=True)
        self.etapa_posterior = Etapa.objects.create(modalidad=self.modalidad, nombre='Examen 1', orden=2, activo=True)
        self.tipo_documento = TipoDocumento.objects.create(nombre='Documento de respaldo', obligatorio=True, activo=True)
        self.tipo_acta = TipoDocumento.objects.create(nombre='Acta Final del Examen de Grado', obligatorio=True, activo=True)

    def _create_postulacion(self, etapa):
        return Postulacion.objects.create(
            postulante=self.postulante,
            modalidad=self.modalidad,
            etapa_actual=etapa,
            titulo_trabajo='Trabajo de prueba',
            gestion=2026,
            estado_general='EN_PROCESO',
        )

    def _upload_document(self, postulacion, tipo_documento):
        self.client.force_authenticate(self.user)
        return self.client.post(
            '/api/documentos/',
            {
                'postulacion': postulacion.id,
                'tipo_documento': tipo_documento.id,
                'archivo': SimpleUploadedFile('doc.pdf', b'data', content_type='application/pdf'),
            },
            format='multipart',
        )

    def test_estudiante_puede_subir_documento_en_etapa_registro(self):
        postulacion = self._create_postulacion(self.etapa_registro)

        response = self._upload_document(postulacion, self.tipo_documento)

        self.assertEqual(response.status_code, 201)

    def test_estudiante_no_puede_subir_documento_fuera_de_registro(self):
        postulacion = self._create_postulacion(self.etapa_posterior)

        response = self._upload_document(postulacion, self.tipo_documento)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['detail'],
            'Solo es posible subir documentos durante la etapa de Registro. Las actas de evaluación son registradas por la administración de la Carrera.',
        )

    def test_estudiante_no_puede_subir_acta_de_evaluacion(self):
        postulacion = self._create_postulacion(self.etapa_registro)

        response = self._upload_document(postulacion, self.tipo_acta)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['detail'],
            'Solo es posible subir documentos durante la etapa de Registro. Las actas de evaluación son registradas por la administración de la Carrera.',
        )
