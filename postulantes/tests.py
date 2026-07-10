from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from documentos.models import DocumentoPostulacion, ModalidadTipoDocumento, TipoDocumento
from modalidades.models import Etapa, Modalidad
from postulantes.models import Postulante, Postulacion
from postulantes.serializers import PostulacionSerializer
from postulantes.services import EtapaIncompletaError, avanzar_postulacion, finalizar_postulacion_si_corresponde
from postulantes.views import PostulacionViewSet

User = get_user_model()


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

    def test_finaliza_postulacion_historica_cuando_documentos_y_actas_estan_aprobados(self):
        modalidad = Modalidad.objects.create(nombre='Modalidad Histórica')
        etapa = Etapa.objects.create(modalidad=modalidad, nombre='Registro', orden=1, activo=True)
        tipo_requisito = TipoDocumento.objects.create(nombre='Certificado Académico', obligatorio=True, activo=True)
        tipo_acta = TipoDocumento.objects.create(nombre='Acta de Defensa', obligatorio=True, activo=True)
        ModalidadTipoDocumento.objects.create(
            modalidad=modalidad,
            tipo_documento=tipo_requisito,
            etapa=etapa,
            obligatorio=True,
            activo=True,
            orden=1,
        )
        ModalidadTipoDocumento.objects.create(
            modalidad=modalidad,
            tipo_documento=tipo_acta,
            etapa=etapa,
            obligatorio=True,
            activo=True,
            orden=2,
        )
        postulacion = Postulacion.objects.create(
            postulante=self.postulante,
            modalidad=modalidad,
            etapa_actual=None,
            titulo_trabajo='Trabajo de prueba',
            gestion=2026,
            estado_general='EN_PROCESO',
        )
        DocumentoPostulacion.objects.create(
            postulacion=postulacion,
            tipo_documento=tipo_requisito,
            archivo=SimpleUploadedFile('requisito.pdf', b'data', content_type='application/pdf'),
            estado='aprobado',
        )
        DocumentoPostulacion.objects.create(
            postulacion=postulacion,
            tipo_documento=tipo_acta,
            archivo=SimpleUploadedFile('acta.pdf', b'data', content_type='application/pdf'),
            estado='aprobado',
        )

        resultado = finalizar_postulacion_si_corresponde(postulacion)

        self.assertEqual(resultado.estado_general, 'FINALIZADA')

    def test_perform_create_no_sobrescribe_etapa_actual_null_en_flujo_historico(self):
        modalidad = Modalidad.objects.create(nombre='EXAMEN DE GRADO')
        Etapa.objects.create(modalidad=modalidad, nombre='Registro', orden=1, activo=True)
        usuario = User.objects.create_user(username='tester', password='secret123')
        postulante = Postulante.objects.create(
            nombre='Luis',
            apellido='Martínez',
            ci='87654321',
            telefono='70000000',
            codigo_estudiante='EST-002',
            usuario=usuario,
        )

        view = PostulacionViewSet()
        serializer = view.get_serializer()
        serializer.is_valid(raise_exception=True)

        view.request = type('Request', (), {'user': usuario})()
        view.perform_create(serializer)
        postulacion = Postulacion.objects.latest('id')
        self.assertIsNone(postulacion.etapa_actual)

    def test_perform_create_asigna_registro_a_excelencia_academica(self):
        modalidad = Modalidad.objects.create(nombre='EXCELENCIA ACADÉMICA')
        etapa_registro = Etapa.objects.create(modalidad=modalidad, nombre='Registro', orden=1, activo=True)
        usuario = User.objects.create_user(username='tester2', password='secret123')
        postulante = Postulante.objects.create(
            nombre='María',
            apellido='López',
            ci='11223344',
            telefono='71111111',
            codigo_estudiante='EST-003',
            usuario=usuario,
        )

        view = PostulacionViewSet()
        serializer = view.get_serializer()
        serializer.is_valid(raise_exception=True)

        view.request = type('Request', (), {'user': usuario})()
        view.perform_create(serializer)
        postulacion = Postulacion.objects.latest('id')
        self.assertEqual(postulacion.etapa_actual_id, etapa_registro.id)
