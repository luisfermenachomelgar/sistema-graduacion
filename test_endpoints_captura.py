"""
Script para capturar y demostrar qué endpoint se utiliza en la aplicación.
Simula peticiones HTTP desde el frontend y muestra las respuestas.
"""
import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost"
API_BASE = f"{BASE_URL}/api"

# Credenciales para testing
TEST_USER = "admin"
TEST_PASS = "admin"

def get_token():
    """Obtener token JWT"""
    response = requests.post(
        f"{API_BASE}/token/",
        json={"username": TEST_USER, "password": TEST_PASS},
        verify=False
    )
    if response.status_code == 200:
        return response.json()['access']
    print(f"Error obteniendo token: {response.text}")
    return None

def test_endpoints():
    """Prueba ambos endpoints para avanzar etapa"""
    
    token = get_token()
    if not token:
        print("❌ No se pudo obtener token de autenticación")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Buscar una postulación para usar en el test
    response = requests.get(
        f"{API_BASE}/postulaciones/",
        headers=headers,
        verify=False
    )
    
    if response.status_code != 200:
        print(f"❌ Error obteniendo postulaciones: {response.text}")
        return
    
    postulaciones = response.json()['results']
    if not postulaciones:
        print("⚠️  No hay postulaciones para probar")
        return
    
    postulacion = postulaciones[0]
    postulacion_id = postulacion['id']
    
    print("=" * 80)
    print(f"POSTULACIÓN SELECCIONADA: ID={postulacion_id}, Modalidad={postulacion.get('modalidad_nombre')}, Etapa={postulacion.get('etapa_nombre')}")
    print("=" * 80)
    print()
    
    # PRUEBA 1: POST /api/postulaciones/{id}/avanzar-etapa/ (Con validación)
    print("PRUEBA 1: POST /api/postulaciones/{id}/avanzar-etapa/")
    print("-" * 80)
    endpoint1 = f"{API_BASE}/postulaciones/{postulacion_id}/avanzar-etapa/"
    print(f"URL: {endpoint1}")
    print(f"Método: POST")
    print(f"Headers: Authorization: Bearer {token[:20]}...")
    print(f"Payload: (vacío - POST simple)")
    print()
    
    try:
        response1 = requests.post(
            endpoint1,
            headers=headers,
            verify=False,
            timeout=5
        )
        print(f"Status Code: {response1.status_code}")
        print(f"Response:")
        print(json.dumps(response1.json(), indent=2, default=str)[:500])
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
    
    # PRUEBA 2: PATCH /api/postulaciones/{id}/ (Sin validación)
    print("PRUEBA 2: PATCH /api/postulaciones/{id}/ (Edición manual)")
    print("-" * 80)
    endpoint2 = f"{API_BASE}/postulaciones/{postulacion_id}/"
    print(f"URL: {endpoint2}")
    print(f"Método: PATCH")
    print(f"Headers: Authorization: Bearer {token[:20]}...")
    print(f"Payload: {{'etapa_actual': <siguiente_etapa_id>}}")
    print()
    
    # Para PATCH, intentamos cambiar la etapa (sin documentos)
    payload = {
        "etapa_actual": postulacion.get('etapa_actual'),  # Intentamos mantener o cambiar
    }
    
    try:
        response2 = requests.patch(
            endpoint2,
            json=payload,
            headers=headers,
            verify=False,
            timeout=5
        )
        print(f"Status Code: {response2.status_code}")
        print(f"Response:")
        print(json.dumps(response2.json(), indent=2, default=str)[:500])
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
    
    print("=" * 80)
    print("ANÁLISIS")
    print("=" * 80)
    print()
    print("✅ Si PRUEBA 1 falla con 'documentos obligatorios' → endpoint valida")
    print("❌ Si PRUEBA 2 permite actualizar → endpoint tiene bypass")
    print()

if __name__ == "__main__":
    # Deshabilitar advertencias de SSL
    import urllib3
    urllib3.disable_warnings()
    
    test_endpoints()
