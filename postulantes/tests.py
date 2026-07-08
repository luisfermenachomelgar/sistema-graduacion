from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from documentos.models import DocumentoPostulacion, ModalidadTipoDocumento, TipoDocumento
from modalidades.models import Etapa, Modalidad
from postulantes.models import Postulante, Postulacion
from postulantes.services import EtapaIncompletaError, avanzar_postulacion


class AvanzarPostulacionTests(TestCase):
    def setUp(self):
        self.postulante = Postulante.objects.create(
            nombre='Ana',
            apellido='Pérez',
            ci='12345678',
            telefono='60000000',
            codigo_estudiante='EST-001',
        )

    def test_examen_grado_finaliza_cuando_acta_final_esta_aprobada(self):
        modalidad = Modalidad.objects.create(nombre='EXAMEN DE GRADO')
        etapa = Etapa.objects.create(modalidad=modalidad, nombre='Acta Final', orden=6, activo=True)
        tipo_documento = TipoDocumento.objects.create(
            nombre='Acta Final del Examen de Grado',
            obligatorio=True,
            activo=True,
        )
        ModalidadTipoDocumento.objects.create(
            modalidad=modalidad,
            tipo_documento=tipo_documento,
            etapa=etapa,
            obligatorio=True,
            activo=True,
            orden=1,
        )
        postulacion = Postulacion.objects.create(
            postulante=self.postulante,
            modalidad=modalidad,
            etapa_actual=etapa,
            titulo_trabajo='Trabajo de prueba',
            gestion=2026,
            estado_general='EN_PROCESO',
        )
        DocumentoPostulacion.objects.create(
            postulacion=postulacion,
            tipo_documento=tipo_documento,
            archivo=SimpleUploadedFile('acta.pdf', b'data', content_type='application/pdf'),
            estado='aprobado',
        )

        resultado = avanzar_postulacion(postulacion.id)

        self.assertEqual(resultado.estado_general, 'FINALIZADA')

    def test_examen_grado_finalizado_no_permite_avanzar(self):
        modalidad = Modalidad.objects.create(nombre='EXAMEN DE GRADO')
        etapa = Etapa.objects.create(modalidad=modalidad, nombre='Acta Final', orden=6, activo=True)
        postulacion = Postulacion.objects.create(
            postulante=self.postulante,
            modalidad=modalidad,
            etapa_actual=etapa,
            titulo_trabajo='Trabajo de prueba',
            gestion=2026,
            estado_general='FINALIZADA',
        )

        with self.assertRaisesMessage(
            EtapaIncompletaError,
            'La postulación ya finalizó el proceso de Examen de Grado.',
        ):
            avanzar_postulacion(postulacion.id)
