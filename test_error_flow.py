#!/usr/bin/env python
"""
Script para probar el flujo de errores de validación en postulaciones.
Verifica que:
1. El backend retorna el mensaje específico del serializer
2. El exception_handler lo procesa correctamente
3. El mensaje se muestra al usuario
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from postulantes.models import Postulante, Postulacion
from modalidades.models import Modalidad, Etapa
from rest_framework.authtoken.models import Token

User = get_user_model()

def test_duplicate_postulacion_error():
    """Test que simula crear dos postulaciones duplicadas y verifica el error."""
    
    client = Client()
    
    # 1. Crear usuario y postulante
    print("1️⃣  Creando usuario de prueba...")
    user = User.objects.create_user(
        username='test_duplicate_user',
        email='test_dup@example.com',
        password='testpass123'
    )
    
    # 2. Crear postulante
    print("2️⃣  Creando postulante...")
    postulante = Postulante.objects.create(
        usuario=user,
        nombre='Test',
        apellido='Duplicate',
        ci='12345678',
        codigo_estudiante='TEST001'
    )
    
    # 3. Crear modalidad y etapa
    print("3️⃣  Creando modalidad y etapa...")
    modalidad = Modalidad.objects.create(
        nombre='Tesis',
        descripcion='Tesis test',
        activa=True
    )
    etapa = Etapa.objects.create(
        modalidad=modalidad,
        nombre='Defensa',
        orden=1,
        activo=True
    )
    
    # 4. Crear primera postulación
    print("4️⃣  Creando primera postulación (debe ser exitosa)...")
    first_post_data = {
        'postulante_id': postulante.id,
        'modalidad': modalidad.id,
        'titulo_trabajo': 'Primer Trabajo',
        'anio_academico': 2024,
        'semestre_academico': 1,
        'etapa_actual': etapa.id,
        'estado': 'borrador',
    }
    
    response1 = client.post(
        '/api/postulaciones/',
        data=json.dumps(first_post_data),
        content_type='application/json'
    )
    print(f"   Response 1 status: {response1.status_code}")
    print(f"   Response 1 content: {response1.json()}")
    
    # 5. Intentar crear segunda postulación duplicada
    print("\n5️⃣  Intentando crear postulación duplicada...")
    second_post_data = {
        'postulante_id': postulante.id,
        'modalidad': modalidad.id,
        'titulo_trabajo': 'Segundo Trabajo (duplicado)',
        'anio_academico': 2024,
        'semestre_academico': 1,  # Mismo año y semestre = duplicado
        'etapa_actual': etapa.id,
        'estado': 'borrador',
    }
    
    response2 = client.post(
        '/api/postulaciones/',
        data=json.dumps(second_post_data),
        content_type='application/json'
    )
    
    print(f"   Response 2 status: {response2.status_code}")
    response2_json = response2.json()
    print(f"   Response 2 content: {json.dumps(response2_json, indent=2, ensure_ascii=False)}")
    
    # 6. Verificar que el mensaje es correcto
    print("\n6️⃣  Verificando el mensaje de error...")
    if response2.status_code == 400:
        error_message = response2_json.get('error', '')
        expected_msg = 'El estudiante ya cuenta con una postulación'
        
        if expected_msg in error_message:
            print(f"   ✅ ÉXITO: El mensaje contiene el texto esperado")
            print(f"   Mensaje completo: {error_message}")
        else:
            print(f"   ❌ ERROR: El mensaje no contiene el texto esperado")
            print(f"   Esperado contener: {expected_msg}")
            print(f"   Recibido: {error_message}")
    else:
        print(f"   ❌ ERROR: El status code no es 400, es {response2.status_code}")
    
    # 7. Limpiar
    print("\n7️⃣  Limpiando datos de prueba...")
    postulante.delete()
    user.delete()
    modalidad.delete()
    
    print("\n✅ Test completado\n")

if __name__ == '__main__':
    test_duplicate_postulacion_error()
