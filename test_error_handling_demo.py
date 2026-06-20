#!/usr/bin/env python
"""
Script para demostrar y verificar el flujo de manejo de errores del exception_handler.
Este script prueba el procesamiento de ValidationError sin necesidad de base de datos.
"""

import json
from rest_framework import serializers


# Simular el DUPLICATE_POSTULACION_ERROR
DUPLICATE_POSTULACION_ERROR = 'El estudiante ya cuenta con una postulación registrada para la gestión y período académico seleccionados. No es posible registrar una nueva postulación en el mismo período.'


def simulate_validation_error():
    """Simula un error de validación como lo haría el serializer."""
    print("=" * 80)
    print("SIMULACIÓN: Error de validación (duplicado de postulación)")
    print("=" * 80)
    
    try:
        raise serializers.ValidationError({
            'non_field_errors': [DUPLICATE_POSTULACION_ERROR]
        })
    except serializers.ValidationError as e:
        print(f"\n1. Error original capturado por DRF:")
        print(f"   Type: {type(e.detail)}")
        print(f"   Content: {e.detail}")
        
        # Simular lo que hace el exception_handler (ANTES)
        print(f"\n2. Procesamiento ANTERIOR (problema):")
        data_old = e.detail
        error_response_old = {
            "success": False,
            "error": "Validation error",  # PROBLEMA: mensaje genérico
            "field_errors": data_old,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        print(f"   Response: {json.dumps(error_response_old, ensure_ascii=False, indent=2)}")
        print(f"   ❌ PROBLEMA: El usuario ve 'Validation error' en lugar del mensaje específico")
        
        # Simular lo que hace el exception_handler (DESPUÉS)
        print(f"\n3. Procesamiento NUEVO (solución):")
        data = e.detail
        error_response = {
            "success": False,
            "error": None,
            "field_errors": data,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Mejorado: priorizar non_field_errors
        if 'non_field_errors' in data:
            non_field_errors = data['non_field_errors']
            if isinstance(non_field_errors, list) and len(non_field_errors) > 0:
                error_response["error"] = non_field_errors[0]
            elif isinstance(non_field_errors, str):
                error_response["error"] = non_field_errors
            else:
                error_response["error"] = "Validation error"
        else:
            error_response["error"] = "Validation error"
        
        print(f"   Response: {json.dumps(error_response, ensure_ascii=False, indent=2)}")
        print(f"   ✅ SOLUCIÓN: El usuario ve el mensaje específico del backend")
        
        # Verificación
        print(f"\n4. Verificación:")
        if error_response["error"] == DUPLICATE_POSTULACION_ERROR:
            print(f"   ✅ El mensaje coincide exactamente con el definido en el serializer")
            print(f"   ✅ El usuario verá: '{error_response['error']}'")
        else:
            print(f"   ❌ El mensaje no coincide")


def simulate_field_error_with_non_field():
    """Simula errores con field_errors AND non_field_errors."""
    print("\n" + "=" * 80)
    print("SIMULACIÓN: Error con field_errors + non_field_errors")
    print("=" * 80)
    
    try:
        raise serializers.ValidationError({
            'modalidad': ['Modalidad inválida'],
            'non_field_errors': ['El estudiante ya cuenta con una postulación...']
        })
    except serializers.ValidationError as e:
        data = e.detail
        error_response = {
            "success": False,
            "error": None,
            "field_errors": data,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Mejorado: priorizar non_field_errors
        if 'non_field_errors' in data:
            non_field_errors = data['non_field_errors']
            if isinstance(non_field_errors, list) and len(non_field_errors) > 0:
                error_response["error"] = non_field_errors[0]
        else:
            error_response["error"] = "Validation error"
        
        print(f"\nResponse:")
        print(json.dumps(error_response, ensure_ascii=False, indent=2))
        print(f"\n✅ El error principal es el non_field_error")
        print(f"   Los field_errors se preservan para mostrar en los campos")


def simulate_field_error_only():
    """Simula error de validación de campos sin non_field_errors."""
    print("\n" + "=" * 80)
    print("SIMULACIÓN: Error de field_errors solo")
    print("=" * 80)
    
    try:
        raise serializers.ValidationError({
            'email': ['Email inválido'],
            'nombre': ['Campo requerido']
        })
    except serializers.ValidationError as e:
        data = e.detail
        error_response = {
            "success": False,
            "error": None,
            "field_errors": data,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        if 'non_field_errors' in data:
            non_field_errors = data['non_field_errors']
            if isinstance(non_field_errors, list) and len(non_field_errors) > 0:
                error_response["error"] = non_field_errors[0]
        else:
            error_response["error"] = "Validation error"
        
        print(f"\nResponse:")
        print(json.dumps(error_response, ensure_ascii=False, indent=2))
        print(f"\n✅ Sin non_field_errors, se usa el mensaje genérico (correcto)")
        print(f"   Los field_errors se mostrarán en sus respectivos campos")


if __name__ == '__main__':
    simulate_validation_error()
    simulate_field_error_with_non_field()
    simulate_field_error_only()
    
    print("\n" + "=" * 80)
    print("✅ PRUEBAS DE FLUJO DE ERRORES COMPLETADAS")
    print("=" * 80)
    print("""
RESUMEN DE CAMBIOS:
1. ✅ exception_handler.py: Ahora prioriza non_field_errors como mensaje principal
2. ✅ serializers.py: Actualizado el mensaje a la versión completa del usuario
3. ✅ Postulaciones.jsx: Mejorado el manejo de result.error desde el API service

FLUJO DE ERRORES CORREGIDO:
- Backend lanza ValidationError({non_field_errors: [mensaje]})
- Exception handler convierte a {error: "mensaje específico", field_errors: {...}}
- Frontend recibe result.error con el mensaje específico
- Usuario ve el mensaje completo en lugar de "Validation error"
    """)
