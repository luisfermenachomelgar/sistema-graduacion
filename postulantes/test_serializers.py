from django.test import TestCase

from modalidades.models import Etapa, Modalidad
from postulantes.models import Postulante, Postulacion
from postulantes.serializers import PostulacionListSerializer
from postulantes.views import PostulacionViewSet


class TestPostulacionListSerializer(TestCase):
    def setUp(self):
        self.modalidad = Modalidad.objects.create(nombre='EXAMEN DE GRADO', descripcion='Modalidad de prueba')
        self.etapa = Etapa.objects.create(modalidad=self.modalidad, nombre='Registro', orden=1, activo=True)
        self.postulante = Postulante.objects.create(
            nombre='Ana',
            apellido='Pérez',
            ci='1234567',
            telefono='1234567',
            carrera='Ingeniería',
            facultad='Facultad',
            codigo_estudiante='COD-001',
        )
        self.postulacion = Postulacion.objects.create(
            postulante=self.postulante,
            modalidad=self.modalidad,
            etapa_actual=self.etapa,
            titulo_trabajo='Tesis de prueba',
            anio_academico=2026,
            semestre_academico=1,
            gestion=2026,
        )

    def test_serializer_includes_etapa_actual_id_for_frontend_filtering(self):
        serializer = PostulacionListSerializer(self.postulacion)

        self.assertEqual(serializer.data['etapa_actual'], self.etapa.id)
        self.assertEqual(serializer.data['etapa_nombre'], self.etapa.nombre)

    def test_serializer_includes_ru_with_fallback_dash(self):
        serializer = PostulacionListSerializer(self.postulacion)

        self.assertEqual(serializer.data['ru'], 'COD-001')

        self.postulante.codigo_estudiante = ''
        self.postulante.save(update_fields=['codigo_estudiante'])
        serializer = PostulacionListSerializer(self.postulacion)

        self.assertEqual(serializer.data['ru'], '-')

    def test_viewset_uses_list_serializer_for_listing_action(self):
        viewset = PostulacionViewSet()
        viewset.action = 'list'

        self.assertIs(viewset.get_serializer_class(), PostulacionListSerializer)
