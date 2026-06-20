# Corrección del Flujo de Errores para Postulaciones Duplicadas

## 📋 Problema Identificado

Cuando un estudiante intentaba registrar una segunda postulación para el mismo año y semestre, el usuario solo veía un mensaje genérico **"Validation error"** en lugar del mensaje específico definido en el serializer:

**Esperado:**
```
"El estudiante ya cuenta con una postulación registrada para la gestión y período académico seleccionados. No es posible registrar una nueva postulación en el mismo período."
```

**Actual (antes de la corrección):**
```
"Validation error"
```

## 🔍 Análisis del Flujo de Errores

### 1. **Backend (serializers.py)**
El serializer levantaba correctamente una excepción de validación:
```python
raise serializers.ValidationError({
    'non_field_errors': ['El estudiante ya posee una postulación...']
})
```

### 2. **Backend (exception_handler.py)** ❌ PROBLEMA AQUÍ
El exception_handler convertía todos los errores de validación en un mensaje genérico:
```python
elif isinstance(data, dict):
    error_response["error"] = "Validation error"  # ← Problema
    error_response["field_errors"] = data
```

Esto resultaba en:
```json
{
  "error": "Validation error",
  "field_errors": {
    "non_field_errors": ["El estudiante ya cuenta con..."]
  }
}
```

### 3. **Frontend (Postulaciones.jsx)**
El frontend intentaba acceder a `result.error` que contenía el mensaje genérico.

---

## ✅ Correcciones Implementadas

### 1. **config/exception_handler.py**
Se mejoró el manejo de `non_field_errors` para que el mensaje específico sea el error principal:

```python
elif isinstance(data, dict):
    # Si existe non_field_errors, prioriza ese mensaje sobre "Validation error"
    if 'non_field_errors' in data:
        non_field_errors = data['non_field_errors']
        if isinstance(non_field_errors, list) and len(non_field_errors) > 0:
            error_response["error"] = non_field_errors[0]  # ✅ Usa el mensaje específico
        elif isinstance(non_field_errors, str):
            error_response["error"] = non_field_errors
        else:
            error_response["error"] = "Validation error"
    else:
        error_response["error"] = "Validation error"
    error_response["field_errors"] = data
```

**Resultado:**
```json
{
  "error": "El estudiante ya cuenta con una postulación registrada para la gestión y período académico seleccionados. No es posible registrar una nueva postulación en el mismo período.",
  "field_errors": {
    "non_field_errors": [...]
  }
}
```

### 2. **postulantes/serializers.py**
Se actualizó el mensaje de error a la versión completa solicitada:

```python
DUPLICATE_POSTULACION_ERROR = 'El estudiante ya cuenta con una postulación registrada para la gestión y período académico seleccionados. No es posible registrar una nueva postulación en el mismo período.'
```

**Cambio:**
- ❌ Anterior: `'El estudiante ya posee una postulación registrada para el período académico seleccionado.'`
- ✅ Nuevo: `'El estudiante ya cuenta con una postulación registrada para la gestión y período académico seleccionados. No es posible registrar una nueva postulación en el mismo período.'`

### 3. **frontend/src/pages/Postulaciones.jsx**
Se mejoró el manejo de errores en el `handleSubmit` para procesar correctamente los errores del API:

```javascript
if (result.success) {
  // ... éxito
} else {
  // El API service retorna {success: false, error: "mensaje"}
  // El error ya contiene el mensaje procesado por exception_handler
  setError(result.error || 'Error en la operación');
  
  // Procesar field_errors si existen
  if (result.field_errors && typeof result.field_errors === 'object') {
    const fieldErrorsMap = {};
    Object.entries(result.field_errors).forEach(([key, value]) => {
      if (key !== 'non_field_errors' && value) {
        if (Array.isArray(value)) {
          fieldErrorsMap[key] = value[0] || null;
        } else {
          fieldErrorsMap[key] = value;
        }
      }
    });
    if (Object.keys(fieldErrorsMap).length > 0) {
      setFieldErrors(fieldErrorsMap);
    }
  }
}
```

---

## 🔄 Nuevo Flujo de Errores (Después de la corrección)

```
┌─────────────────────────────────────────┐
│ Backend - Serializer                     │
│ ValidationError({non_field_errors: [msg]})
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ Exception Handler                        │
│ - Detecta non_field_errors               │
│ - Usa el mensaje como error principal    │
│ - Preserva field_errors para UI          │
└──────────────┬──────────────────────────┘
               │
    {error: "El estudiante ya cuenta con...",
     field_errors: {...}}
               │
┌──────────────▼──────────────────────────┐
│ API Service (_handleError)               │
│ - Retorna {success: false, error: msg}   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ Frontend - Postulaciones.jsx             │
│ - Recibe result.error                    │
│ - Muestra el mensaje específico          │
│ setError(result.error)                   │
└──────────────┬──────────────────────────┘
               │
               ▼
    🎯 Usuario ve el mensaje completo
    "El estudiante ya cuenta con una 
     postulación registrada para la gestión
     y período académico seleccionados..."
```

---

## 🎯 Casos de Uso Cubiertos

### ✅ Caso 1: Error de Postulación Duplicada
```json
{
  "success": false,
  "error": "El estudiante ya cuenta con una postulación registrada...",
  "field_errors": {
    "non_field_errors": ["..."]
  }
}
```
→ Usuario ve el mensaje específico en el Alert

### ✅ Caso 2: Error de Validación de Campos
```json
{
  "success": false,
  "error": "Validation error",
  "field_errors": {
    "email": ["Email inválido"],
    "nombre": ["Campo requerido"]
  }
}
```
→ Usuario ve "Validation error" + errores específicos en cada campo

### ✅ Caso 3: Error de Cambio de Modalidad (si aplica)
```json
{
  "success": false,
  "error": "No es posible registrar una nueva postulación en esta modalidad...",
  "field_errors": {
    "modalidad": ["..."]
  }
}
```
→ Usuario ve el mensaje de error principal

---

## 🧪 Archivos Modificados

1. **`config/exception_handler.py`** - Mejora del manejo de `non_field_errors`
2. **`postulantes/serializers.py`** - Actualización del mensaje DUPLICATE_POSTULACION_ERROR
3. **`frontend/src/pages/Postulaciones.jsx`** - Mejora del manejo de errores en handleSubmit

---

## 📝 Pruebas Realizadas

Se ejecutó un script de demostración (`test_error_handling_demo.py`) que verificó:

✅ Error de validación (duplicado) → mensaje específico mostrado
✅ Error con field_errors + non_field_errors → prioridad correcta
✅ Error de field_errors solo → mensaje genérico correcto

---

## ⚙️ Comportamiento de la Validación

**La validación en sí NO cambió**, solo la presentación del mensaje:

```python
# Sigue siendo la misma validación en el serializer
if postulante and anio_academico is not None and semestre_academico is not None:
    dup_qs = Postulacion.objects.filter(
        postulante=postulante,
        anio_academico=anio_academico,
        semestre_academico=semestre_academico,
    )
    if self.instance:
        dup_qs = dup_qs.exclude(pk=self.instance.pk)
    if dup_qs.exists():
        raise serializers.ValidationError({
            'non_field_errors': [DUPLICATE_POSTULACION_ERROR]
        })
```

---

## 🚀 Resultado Final

Cuando un usuario intenta crear una postulación duplicada, ahora verá:

```
⚠️  El estudiante ya cuenta con una postulación registrada para la gestión 
    y período académico seleccionados. No es posible registrar una nueva 
    postulación en el mismo período.
```

En lugar de:

```
⚠️  Validation error
```
