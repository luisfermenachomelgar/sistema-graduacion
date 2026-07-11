from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import CustomUser
from .serializers import CustomUserSerializer


class SelfServiceUserTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='estudiante1',
            email='estudiante@example.com',
            password='OldPassword123!',
            first_name='Ana',
            last_name='Pérez',
            role='estudiante',
            is_active=True,
        )

    def test_role_choices_exclude_administrativo(self):
        choices = dict(CustomUser.ROLE_CHOICES)
        self.assertEqual(set(choices.keys()), {'admin', 'estudiante'})
        self.assertNotIn('administ', choices)

    def test_serializer_rejects_administrativo_role(self):
        serializer = CustomUserSerializer(data={
            'username': 'nuevo_usuario',
            'email': 'nuevo@example.com',
            'password': 'Password123!',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'role': 'administ',
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('role', serializer.errors)

    def test_current_user_can_read_and_update_own_profile_via_user_detail_endpoint(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse('usuario-detail', kwargs={'pk': self.user.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'estudiante1')
        self.assertEqual(response.data['email'], 'estudiante@example.com')
        self.assertEqual(response.data['first_name'], 'Ana')
        self.assertEqual(response.data['last_name'], 'Pérez')

        patch_response = self.client.patch(
            reverse('usuario-detail', kwargs={'pk': self.user.pk}),
            {
                'username': 'estudiante2',
                'email': 'nuevo@example.com',
                'first_name': 'Ana María',
                'last_name': 'Pérez López',
            },
            format='json',
        )

        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'estudiante2')
        self.assertEqual(self.user.email, 'nuevo@example.com')
        self.assertEqual(self.user.first_name, 'Ana María')
        self.assertEqual(self.user.last_name, 'Pérez López')
