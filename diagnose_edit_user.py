#!/usr/bin/env python
"""
Script de diagnóstico: Edición de usuario admin sin cambiar username
Reproduce el error: "A user with that username already exists."
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from usuarios.serializers import CustomUserSerializer
from usuarios.models import CustomUser

print("=" * 80)
print("DIAGNÓSTICO: Flujo de Edición de Usuarios")
print("=" * 80)

# 1. Verificar usuario admin
try:
    admin_user = CustomUser.objects.get(username='admin')
    print(f"\n✅ Usuario encontrado: {admin_user.username} (ID: {admin_user.id})")
    print(f"   Email: {admin_user.email}")
    print(f"   Role: {admin_user.role}")
except CustomUser.DoesNotExist:
    print("\n❌ Usuario admin no existe")
    exit(1)

# 2. Simular PATCH sin cambiar username
print("\n" + "-" * 80)
print("2. SIMULACIÓN: PATCH a /api/usuarios/{id}/ sin cambiar username")
print("-" * 80)

payload = {
    'username': 'admin',  # ← MISMO USERNAME
    'email': 'admin@admin.com',
    'first_name': 'Admin',
    'last_name': 'Sistema',
    'role': 'admin',
    'is_active': True,
}

print(f"\nPayload enviado:")
print(f"  {payload}")

# 3. PRUEBA 1: Sin pasar instance (INCORRECTO)
print("\n\n📋 PRUEBA 1: Serializer SIN instancia (problema esperado)")
print("-" * 80)

serializer = CustomUserSerializer(data=payload)
print(f"¿Es válido?: {serializer.is_valid()}")
if not serializer.is_valid():
    print(f"❌ ERRORES:")
    for field, errors in serializer.errors.items():
        print(f"   - {field}: {errors}")
else:
    print("✅ Serializer validó correctamente")

# 4. PRUEBA 2: Pasando instance (CORRECTO)
print("\n\n📋 PRUEBA 2: Serializer CON instancia (debería funcionar)")
print("-" * 80)

serializer = CustomUserSerializer(instance=admin_user, data=payload, partial=True)
print(f"¿Es válido?: {serializer.is_valid()}")
if not serializer.is_valid():
    print(f"❌ ERRORES:")
    for field, errors in serializer.errors.items():
        print(f"   - {field}: {errors}")
else:
    print("✅ Serializer validó correctamente")

# 5. Ver la llamada HTTP real (frontend)
print("\n\n" + "=" * 80)
print("3. VERIFICACIÓN: Llamada HTTP desde frontend")
print("=" * 80)

print("""
Línea 95 en frontend/src/pages/Usuarios.jsx:
    const result = isEditMode
        ? await patch(endpoint, payload)  ← PATCH HTTP
        ? await create(payload);

Endpoint construido: /api/usuarios/1/  (asumiendo ID=1)
Método HTTP: PATCH
Payload: {"username": "admin", "email": "...", ...}
""")

# 6. Ver el ViewSet backend
print("\n" + "=" * 80)
print("4. ANÁLISIS: ViewSet en usuarios/views.py")
print("=" * 80)

print("""
Línea 58-76 en usuarios/views.py:
    
    def update(self, request, *args, **kwargs):
        \"\"\"Actualizar usuario (PUT).\"\\"
        partial = kwargs.pop('partial', False)
        instance = self.get_object()  ← Obtiene la instancia actual
        
        # Manejo de contraseña...
        
        serializer = CustomUserSerializer(
            instance, data=data, partial=partial  ← PASA INSTANCE ✅
        )

ANÁLISIS: El ViewSet SÍ está pasando instance correctamente.
""")

# 7. Revisar el serializer
print("\n" + "=" * 80)
print("5. ANÁLISIS: CustomUserSerializer en usuarios/serializers.py")
print("=" * 80)

print("""
Línea 6-16 en usuarios/serializers.py:

class CustomUserSerializer(serializers.ModelSerializer):
    \"\"\"Serializer para CustomUser completo (lectura).\"\"\"
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']

ANÁLISIS: No hay validación personalizada. El modelo Django es quien valida.
El campo 'username' viene de AbstractUser con 'unique=True'.
""")

# 8. Verificar validación unique
print("\n" + "=" * 80)
print("6. VALIDACIÓN DE UNIQUE EN ABSTRACTUSER")
print("=" * 80)

from django.contrib.auth.models import AbstractUser
username_field = AbstractUser._meta.get_field('username')
print(f"\nCampo 'username' de AbstractUser:")
print(f"  unique: {username_field.unique}")
print(f"  max_length: {username_field.max_length}")
print(f"  validators: {username_field.validators}")

# Verificar el error_messages
if hasattr(username_field, 'error_messages'):
    print(f"  error_messages: {username_field.error_messages}")

print("\n" + "=" * 80)
print("CONCLUSIÓN")
print("=" * 80)

print("""
✅ CONFIRMED: El ViewSet SÍ está pasando 'instance' al serializer.

❌ PROBLEMA IDENTIFICADO:
   Aunque el serializer recibe la instancia, DRF debe excluir el username
   de la instancia actual al validar el 'unique=True'.
   
   Esto generalmente funciona automáticamente PERO puede fallar si:
   1. El serializer no tiene configurado validate_unique correctamente
   2. Hay una validación personalizada en el serializer que no excluye instance
   3. El campo no está siendo reconocido como 'unique' por DRF
   
RECOMENDACIÓN:
   Agregar un método validate_username() al serializer que explícitamente
   excluya la instancia actual al validar.
""")
