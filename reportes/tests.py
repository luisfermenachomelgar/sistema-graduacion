from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from postulantes.models import Postulacion, Postulante
from modalidades.models import Modalidad

User = get_user_model()


class ReporteGeneralPostulacionesTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass123',
        )
        self.client.force_authenticate(self.user)

        self.modalidad_a = Modalidad.objects.create(nombre='Modalidad A')
        self.modalidad_b = Modalidad.objects.create(nombre='Modalidad B')

        self.postulante_a = Postulante.objects.create(
            nombre='Ana',
            apellido='Perez',
            ci='11111111',
            telefono='12345678',
            codigo_estudiante='EST0001',
            carrera='Ingeniería'
        )
        self.postulante_b = Postulante.objects.create(
            nombre='Beto',
            apellido='Lopez',
            ci='22222222',
            telefono='87654321',
            codigo_estudiante='EST0002',
            carrera='Arquitectura'
        )

        Postulacion.objects.create(
            postulante=self.postulante_a,
            modalidad=self.modalidad_a,
            titulo_trabajo='Trabajo A',
            tutor='Tutor Uno',
            anio_academico=2025,
            semestre_academico=1,
            estado='aprobada',
            estado_general='TITULADO',
        )
        Postulacion.objects.create(
            postulante=self.postulante_b,
            modalidad=self.modalidad_b,
            titulo_trabajo='Trabajo B',
            tutor='Tutor Dos',
            anio_academico=2026,
            semestre_academico=2,
            estado='rechazada',
            estado_general='EN_PROCESO',
        )

    def test_reporte_postulaciones_includes_dynamic_filters(self):
        response = self.client.get('/api/reportes/postulaciones/')
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn('filters_available', data)
        filters = data['filters_available']
        self.assertIn('modalidades', filters)
        self.assertIn('gestiones', filters)
        self.assertIn('anio_academicos', filters)
        self.assertIn('semestres_academicos', filters)
        self.assertIn('estados', filters)
        self.assertIn('estado_generales', filters)
        self.assertIn('carreras', filters)
        self.assertIn('tutores', filters)

        self.assertIn({'value': 'Ingeniería', 'label': 'Ingeniería'}, filters['carreras'])
        self.assertIn({'value': 'Tutor Uno', 'label': 'Tutor Uno'}, filters['tutores'])
        self.assertTrue(any(item['value'] == 2025 for item in filters['anio_academicos']))
        self.assertTrue(any(item['value'] == 2026 for item in filters['anio_academicos']))

    def test_search_filter_filters_results(self):
        response = self.client.get('/api/reportes/postulaciones/?search=Trabajo+A')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('count'), 1)
        self.assertEqual(data['results'][0]['titulo_trabajo'], 'Trabajo A')

    def test_ordering_by_postulante_nombre(self):
        response = self.client.get('/api/reportes/postulaciones/?ordering=postulante_nombre')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        nombres = [item['postulante_nombre'] for item in data['results']]
        self.assertEqual(nombres, sorted(nombres))

    def test_filter_by_carrera(self):
        response = self.client.get('/api/reportes/postulaciones/?carrera=Arquitectura')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('count'), 1)
        self.assertEqual(data['results'][0]['postulante_carrera'], 'Arquitectura')
