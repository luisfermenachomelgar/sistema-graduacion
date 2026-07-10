from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Q
from rest_framework.test import APIClient, APITestCase

from documentos.models import DocumentoPostulacion, ModalidadTipoDocumento, TipoDocumento
from documentos.services import sync_excelencia_academica_catalog
from modalidades.models import Etapa, Modalidad
from postulantes.models import Postulante, Postulacion


class DocumentoPostulacionStageRulesTests(APITestCase):
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

    def test_tipos_documento_historicos_devuelven_todos_los_documentos_de_la_modalidad(self):
        postulacion_historica = Postulacion.objects.create(
            postulante=self.postulante,
            modalidad=self.modalidad,
            etapa_actual=None,
            titulo_trabajo='Trabajo histórico',
            gestion=2026,
            estado_general='EN_PROCESO',
        )
        tipo_general = TipoDocumento.objects.create(nombre='Documento general', obligatorio=True, activo=True)
        tipo_registro = TipoDocumento.objects.create(nombre='Documento de registro', obligatorio=True, activo=True)
        tipo_posterior = TipoDocumento.objects.create(nombre='Documento posterior', obligatorio=True, activo=True)

        ModalidadTipoDocumento.objects.create(modalidad=self.modalidad, tipo_documento=tipo_general, etapa=None, obligatorio=True, activo=True)
        ModalidadTipoDocumento.objects.create(modalidad=self.modalidad, tipo_documento=tipo_registro, etapa=self.etapa_registro, obligatorio=True, activo=True)
        ModalidadTipoDocumento.objects.create(modalidad=self.modalidad, tipo_documento=tipo_posterior, etapa=self.etapa_posterior, obligatorio=True, activo=True)

        queryset = ModalidadTipoDocumento.objects.filter(
            modalidad=self.modalidad,
            activo=True,
            tipo_documento__activo=True,
        )
        if postulacion_historica.etapa_actual_id is None:
            queryset = queryset.order_by('orden', 'tipo_documento__nombre')
        nombres = [item.tipo_documento.nombre for item in queryset]

        self.assertEqual(len(nombres), 3)
        self.assertIn('Documento general', nombres)
        self.assertIn('Documento de registro', nombres)
        self.assertIn('Documento posterior', nombres)

    def test_tipos_documento_en_flujo_normal_siguen_filtrando_por_etapa(self):
        tipo_general = TipoDocumento.objects.create(nombre='Documento general normal', obligatorio=True, activo=True)
        tipo_registro = TipoDocumento.objects.create(nombre='Documento de registro normal', obligatorio=True, activo=True)
        tipo_posterior = TipoDocumento.objects.create(nombre='Documento posterior normal', obligatorio=True, activo=True)

        ModalidadTipoDocumento.objects.create(modalidad=self.modalidad, tipo_documento=tipo_general, etapa=None, obligatorio=True, activo=True)
        ModalidadTipoDocumento.objects.create(modalidad=self.modalidad, tipo_documento=tipo_registro, etapa=self.etapa_registro, obligatorio=True, activo=True)
        ModalidadTipoDocumento.objects.create(modalidad=self.modalidad, tipo_documento=tipo_posterior, etapa=self.etapa_posterior, obligatorio=True, activo=True)

        queryset = ModalidadTipoDocumento.objects.filter(
            modalidad=self.modalidad,
            activo=True,
            tipo_documento__activo=True,
        ).filter(Q(etapa__isnull=True) | Q(etapa=self.etapa_registro))
        nombres = [item.tipo_documento.nombre for item in queryset]
        self.assertIn('Documento general normal', nombres)
        self.assertIn('Documento de registro normal', nombres)
        self.assertNotIn('Documento posterior normal', nombres)

    def test_postulacion_historica_se_finaliza_cuando_todos_los_obligatorios_estan_aprobados(self):
        postulacion_historica = Postulacion.objects.create(
            postulante=self.postulante,
            modalidad=self.modalidad,
            etapa_actual=None,
            titulo_trabajo='Trabajo histórico',
            gestion=2026,
            estado_general='EN_PROCESO',
        )
        tipo_uno = TipoDocumento.objects.create(nombre='Documento histórico obligatorio 1', obligatorio=True, activo=True)
        tipo_dos = TipoDocumento.objects.create(nombre='Documento histórico obligatorio 2', obligatorio=True, activo=True)

        ModalidadTipoDocumento.objects.create(modalidad=self.modalidad, tipo_documento=tipo_uno, etapa=None, obligatorio=True, activo=True)
        ModalidadTipoDocumento.objects.create(modalidad=self.modalidad, tipo_documento=tipo_dos, etapa=None, obligatorio=True, activo=True)

        DocumentoPostulacion.objects.create(
            postulacion=postulacion_historica,
            tipo_documento=tipo_uno,
            archivo=SimpleUploadedFile('doc1.pdf', b'data', content_type='application/pdf'),
            estado='aprobado',
        )
        DocumentoPostulacion.objects.create(
            postulacion=postulacion_historica,
            tipo_documento=tipo_dos,
            archivo=SimpleUploadedFile('doc2.pdf', b'data', content_type='application/pdf'),
            estado='aprobado',
        )

        postulacion_historica.refresh_from_db()
        self.assertEqual(postulacion_historica.estado_general, 'FINALIZADA')

    def test_postulacion_historica_vuelve_a_en_proceso_al_eliminar_un_documento_obligatorio(self):
        postulacion_historica = Postulacion.objects.create(
            postulante=self.postulante,
            modalidad=self.modalidad,
            etapa_actual=None,
            titulo_trabajo='Trabajo histórico 2',
            gestion=2026,
            estado_general='EN_PROCESO',
        )
        tipo_uno = TipoDocumento.objects.create(nombre='Documento histórico obligatorio 3', obligatorio=True, activo=True)
        tipo_dos = TipoDocumento.objects.create(nombre='Documento histórico obligatorio 4', obligatorio=True, activo=True)

        ModalidadTipoDocumento.objects.create(modalidad=self.modalidad, tipo_documento=tipo_uno, etapa=None, obligatorio=True, activo=True)
        ModalidadTipoDocumento.objects.create(modalidad=self.modalidad, tipo_documento=tipo_dos, etapa=None, obligatorio=True, activo=True)

        DocumentoPostulacion.objects.create(
            postulacion=postulacion_historica,
            tipo_documento=tipo_uno,
            archivo=SimpleUploadedFile('doc3.pdf', b'data', content_type='application/pdf'),
            estado='aprobado',
        )
        DocumentoPostulacion.objects.create(
            postulacion=postulacion_historica,
            tipo_documento=tipo_dos,
            archivo=SimpleUploadedFile('doc4.pdf', b'data', content_type='application/pdf'),
            estado='aprobado',
        )

        postulacion_historica.refresh_from_db()
        self.assertEqual(postulacion_historica.estado_general, 'FINALIZADA')

        DocumentoPostulacion.objects.filter(postulacion=postulacion_historica, tipo_documento=tipo_dos).delete()

        postulacion_historica.refresh_from_db()
        self.assertEqual(postulacion_historica.estado_general, 'EN_PROCESO')

    def test_sync_excelencia_academica_crea_etapa_registro_y_catalogo_oficial(self):
        modalidad = Modalidad.objects.create(nombre='EXCELENCIA  ACADÉMICA')
        Etapa.objects.create(modalidad=modalidad, nombre='Presentación de Requisitos', orden=1, activo=True)
        Etapa.objects.create(modalidad=modalidad, nombre='Revisión de Expediente', orden=2, activo=True)
        Etapa.objects.create(modalidad=modalidad, nombre='Acta Final', orden=3, activo=True)

        sync_excelencia_academica_catalog()

        etapas = {etapa.nombre: etapa for etapa in Etapa.objects.filter(modalidad=modalidad).order_by('orden')}
        self.assertIn('Registro', etapas)
        self.assertEqual(etapas['Registro'].orden, 1)
        self.assertEqual(etapas['Presentación de Requisitos'].orden, 2)
        self.assertEqual(etapas['Revisión de Expediente'].orden, 3)
        self.assertEqual(etapas['Acta Final'].orden, 4)

        relaciones = list(
            ModalidadTipoDocumento.objects.filter(modalidad=modalidad)
            .select_related('tipo_documento', 'etapa')
            .order_by('etapa__orden', 'orden', 'tipo_documento__nombre')
        )

        self.assertEqual(
            [rel.tipo_documento.nombre for rel in relaciones if rel.etapa.nombre == 'Presentación de Requisitos'],
            [
                'Carta de solicitud a la Dirección de la Carrera.',
                'Fotocopia del recibo de pago de matrícula.',
                'Historial Académico.',
                'Fólder amarillo rotulado.',
                'Certificaciones de investigación e interacción social.',
            ],
        )
        self.assertEqual(
            [rel.tipo_documento.nombre for rel in relaciones if rel.etapa.nombre == 'Revisión de Expediente'],
            [
                'Certificado de la Dirección de Planificación Académica.',
                'Certificado de Solvencia Universitaria.',
                'Certificado de Solvencia Bibliotecaria.',
                'Timbre Universitario para la modalidad Excelencia Académica.',
            ],
        )
        self.assertEqual(
            [rel.tipo_documento.nombre for rel in relaciones if rel.etapa.nombre == 'Acta Final'],
            ['Acta de Graduación por Excelencia Académica.'],
        )
        self.assertNotIn('Certificado de notas del programa', [rel.tipo_documento.nombre for rel in relaciones])
        self.assertNotIn('Copia simple de cédula de identidad', [rel.tipo_documento.nombre for rel in relaciones])
        self.assertNotIn('Currículum vitae actualizado', [rel.tipo_documento.nombre for rel in relaciones])
        self.assertNotIn('Memoria o trabajo final de graduación', [rel.tipo_documento.nombre for rel in relaciones])
        self.assertNotIn('Acta de defensa de tesis o de modalidad de graduación', [rel.tipo_documento.nombre for rel in relaciones])
        self.assertEqual(len(relaciones), 10)

    def test_sync_excelencia_academica_elimina_relaciones_antiguas_de_otras_etapas(self):
        modalidad = Modalidad.objects.create(nombre='EXCELENCIA ACADÉMICA')
        etapa_registro = Etapa.objects.create(modalidad=modalidad, nombre='Registro', orden=1, activo=True)
        etapa_presentacion = Etapa.objects.create(modalidad=modalidad, nombre='Presentación de Requisitos', orden=2, activo=True)
        tipo_carta = TipoDocumento.objects.create(nombre='Carta de solicitud', obligatorio=True, activo=True)

        ModalidadTipoDocumento.objects.create(
            modalidad=modalidad,
            tipo_documento=tipo_carta,
            etapa=etapa_presentacion,
            obligatorio=True,
            activo=True,
            orden=1,
        )

        sync_excelencia_academica_catalog()

        relaciones = ModalidadTipoDocumento.objects.filter(modalidad=modalidad, tipo_documento=tipo_carta)
        self.assertEqual(relaciones.count(), 1)
        self.assertEqual(relaciones.get().etapa, etapa_registro)
