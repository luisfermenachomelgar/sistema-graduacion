import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from postulantes.models import Postulante
from postulantes.serializers import PostulanteSerializer
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
import traceback

User = get_user_model()

def diagnose():
    try:
        # 1. Estado de los modelos y usuario
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            user = User.objects.create_superuser('admin_test', 'admin@test.com', 'pass123')
            print(f"Usuario superusuario creado: {user.username}")
        else:
            print(f"Usuario usado: {user.username}")

        print("\n--- Estado del Modelo Postulante ---")
        for field in Postulante._meta.fields:
            print(f"Field: {field.name}, null={field.null}, blank={field.blank}")

        # 2. Reproducción del POST contra el serializer
        print("\n--- Intento de creación con Serializer (sin usuario en payload) ---")
        
        payload = {
            "nombre": "Test",
            "apellido": "User",
            "ci": "1234567-T",
            "codigo_estudiante": "20230001",
            "telefono": "77777777",
            "carrera": "Sistemas",
            "facultad": "Tecnologia"
        }
        
        factory = APIRequestFactory()
        request = factory.post('/api/postulantes/', payload, format='json')
        request.user = user

        serializer = PostulanteSerializer(data=payload, context={'request': request})
        
        is_valid = serializer.is_valid()
        print(f"Serializer is_valid: {is_valid}")
        if not is_valid:
            print(f"Errores del serializer: {serializer.errors}")
            return

        try:
            # Replicando perform_create del ViewSet
            instance = serializer.save(usuario=user)
            print(f"Postulante creado exitosamente: ID {instance.id}")
            instance.delete()
            print("Postulante de prueba eliminado.")
        except Exception:
            print("\n--- Traceback durante serializer.save() ---")
            traceback.print_exc()

    except Exception:
        traceback.print_exc()

if __name__ == '__main__':
    diagnose()
