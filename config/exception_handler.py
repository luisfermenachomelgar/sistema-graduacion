from rest_framework.views import exception_handler as drf_exception_handler
from datetime import datetime, timezone


def custom_exception_handler(exc, context):
    """
    Custom exception handler que unifica SOLO errores.
    
    ✅ Preserva status_code original
    ✅ Field errors como objeto (nunca string)
    ✅ Detail movido a error
    ✅ Non-field errors (non_field_errors) manejados en field_errors
    ✅ Listas de validación soportadas
    ✅ Timezone-aware UTC con datetime.now(timezone.utc)
    ✅ No toca respuestas exitosas (200, 201, etc)
    
    Schema uniforme para errores:
    {
        "success": false,
        "error": "mensaje corto",
        "field_errors": {...} o null,
        "timestamp": "ISO8601Z"
    }
    """
    
    # Llamar handler default de DRF (aquí DRF procesa la excepción)
    response = drf_exception_handler(exc, context)
    
    # Si response es None = excepción no manejó DRF (ej: custom)
    if response is None:
        return None
    
    # Si es exitoso (esto nunca ocurre en exception_handler pero seguridad)
    if response.status_code < 400:
        return response
    
    # --- PROCESAR SOLO ERRORES (400+) ---
    
    error_response = {
        "success": False,
        "error": None,
        "field_errors": None,
        "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    
    data = response.data
    
    # CASO 1: Dict con "detail" (errores de permisos, auth, not found, etc)
    # Ej: {"detail": "Not found"} o {"detail": "Authentication failed"}
    if isinstance(data, dict) and 'detail' in data:
        error_response["error"] = str(data['detail'])
        # Si hay otros campos además de detail, son field_errors
        remaining_fields = {k: v for k, v in data.items() if k != 'detail'}
        if remaining_fields:
            error_response["field_errors"] = remaining_fields
    
    # CASO 2: Dict de validación (campos + posibles non_field_errors)
    # Ej: {"email": ["Invalid"], "non_field_errors": ["..."], "nombre": ["Required"]}
    # O: {"email": ["Invalid"]}
    # O: {"non_field_errors": ["..."] }
    elif isinstance(data, dict):
        if 'non_field_errors' in data:
            non_field_errors = data['non_field_errors']
            if isinstance(non_field_errors, list):
                error_response["error"] = non_field_errors[0] if non_field_errors else "Validation error"
            else:
                error_response["error"] = str(non_field_errors)
        else:
            error_response["error"] = "Validation error"
        error_response["field_errors"] = data  # Preserva non_field_errors si existe
    
    # CASO 3: Lista (raro pero DRF puede retornar lista en algunos casos)
    # Ej: ["This field is required", "..."]
    elif isinstance(data, list):
        error_response["error"] = "Validation error"
        error_response["field_errors"] = data
    
    # CASO 4: String u otro tipo primitivo
    # Ej: "Internal server error"
    else:
        error_response["error"] = str(data)
    
    # --- PRESERVAR STATUS CODE ORIGINAL ---
    response.data = error_response
    return response
