# Diff Propuesto para modalidades/serializers.py

## Cambio a Realizar

**Archivo:** `modalidades/serializers.py`  
**Línea:** 76  
**Tipo:** Modificación de `read_only_fields`

---

## ANTES (Línea 76):

```python
read_only_fields = ['id', 'modalidad_nombre', 'archivo_url', 'archivo_nombre', 'archivo_tipo', 'archivo_tamano', 'created_at', 'updated_at']
```

---

## DESPUÉS (Línea 76):

```python
read_only_fields = ['id', 'modalidad', 'modalidad_nombre', 'archivo_url', 'archivo_nombre', 'archivo_tipo', 'archivo_tamano', 'created_at', 'updated_at']
```

---

## Diff Visual:

```diff
class ModalidadRequisitoSerializer(serializers.ModelSerializer):
    modalidad_nombre = serializers.CharField(source='modalidad.nombre', read_only=True)
    archivo_url = serializers.SerializerMethodField()
    archivo_nombre = serializers.SerializerMethodField()
    archivo_tipo = serializers.SerializerMethodField()
    archivo_tamano = serializers.SerializerMethodField()

    class Meta:
        model = ModalidadRequisito
        fields = [
            'id',
            'modalidad',
            'modalidad_nombre',
            'nombre',
            'descripcion',
            'archivo',
            'archivo_url',
            'archivo_nombre',
            'archivo_tipo',
            'archivo_tamano',
            'categoria',
            'obligatorio',
            'version',
            'observaciones',
            'activo',
            'created_at',
            'updated_at',
        ]
-       read_only_fields = ['id', 'modalidad_nombre', 'archivo_url', 'archivo_nombre', 'archivo_tipo', 'archivo_tamano', 'created_at', 'updated_at']
+       read_only_fields = ['id', 'modalidad', 'modalidad_nombre', 'archivo_url', 'archivo_nombre', 'archivo_tipo', 'archivo_tamano', 'created_at', 'updated_at']
```

---

## Impacto del Cambio

### ✅ POST - Creación de Requisitos (ARREGLADO)

**Endpoint:** `POST /api/modalidades/{id}/requisitos/`

**Antes del cambio:**
```python
# views.py línea 53-55
serializer = ModalidadRequisitoSerializer(data=request.data, context={'request': request})
serializer.is_valid(raise_exception=True)  # ❌ FALLA: "modalidad: This field is required"
serializer.save(modalidad=modalidad)       # ← Nunca llega aquí
```

**Después del cambio:**
```python
# views.py línea 53-55
serializer = ModalidadRequisitoSerializer(data=request.data, context={'request': request})
serializer.is_valid(raise_exception=True)  # ✅ PASA: modalidad es read_only, no se valida
serializer.save(modalidad=modalidad)       # ✅ Se asigna correctamente desde la URL
```

**Resultado:**
- ✅ La validación pasa porque `modalidad` es read-only
- ✅ `serializer.save(modalidad=modalidad)` asigna la modalidad desde la URL
- ✅ El requisito se crea correctamente asociado a la modalidad

---

### ✅ PATCH/PUT - Edición de Requisitos (NO AFECTADO)

**Endpoint:** `PATCH /api/modalidades/{modalidadId}/requisitos/{requisitoId}/`

**Código actual (views.py líneas 73-81):**
```python
serializer = ModalidadRequisitoSerializer(
    requisito,
    data=request.data,
    partial=(request.method == 'PATCH'),
    context={'request': request},
)
serializer.is_valid(raise_exception=True)
serializer.save()  # ← NO pasa modalidad, usa la existente del requisito
```

**Comportamiento:**
- ✅ Al editar, el serializer recibe `requisito` (instancia existente)
- ✅ La modalidad ya está asignada en `requisito.modalidad`
- ✅ Como `modalidad` es read-only, no se puede modificar desde el request
- ✅ `serializer.save()` mantiene la modalidad original
- ✅ **SEGURIDAD:** Evita que un usuario cambie la modalidad de un requisito existente

---

### ✅ GET - Lectura de Requisitos (NO AFECTADO)

**Endpoint:** `GET /api/modalidades/{id}/requisitos/`

**Comportamiento:**
- ✅ El campo `modalidad` se serializa normalmente
- ✅ Se incluye en la respuesta JSON
- ✅ El frontend puede leer el ID de la modalidad

**Respuesta JSON:**
```json
{
  "id": 1,
  "modalidad": 5,           // ← Se incluye en la respuesta
  "modalidad_nombre": "Proyecto de Grado",
  "nombre": "Reglamento PDF",
  "descripcion": "...",
  "archivo_url": "...",
  // ... resto de campos
}
```

---

## Verificación de Seguridad

### ¿Puede un usuario malicioso cambiar la modalidad?

**Escenario de ataque:**
```javascript
// Usuario intenta crear un requisito para modalidad 5
// pero envía modalidad: 999 en el body
POST /api/modalidades/5/requisitos/
Body: {
  nombre: "Hack",
  modalidad: 999,  // ← Intento de cambiar modalidad
  archivo: file
}
```

**Resultado con el cambio:**
- ✅ El campo `modalidad: 999` en el body es **IGNORADO** (read-only)
- ✅ Se usa `modalidad = 5` de la URL (línea 43: `modalidad = self.get_object()`)
- ✅ El requisito se crea correctamente para modalidad 5, no 999
- ✅ **SEGURIDAD MEJORADA:** No se puede manipular la modalidad desde el request

---

## Casos de Prueba

### Caso 1: Crear requisito nuevo
```bash
POST /api/modalidades/5/requisitos/
Content-Type: multipart/form-data

nombre: "Test Requisito"
archivo: [file]
```
**Esperado:** ✅ Crea requisito con modalidad_id=5

---

### Caso 2: Editar requisito existente
```bash
PATCH /api/modalidades/5/requisitos/10/
Content-Type: multipart/form-data

nombre: "Test Requisito Editado"
```
**Esperado:** ✅ Actualiza nombre, mantiene modalidad_id=5

---

### Caso 3: Intentar cambiar modalidad en edición
```bash
PATCH /api/modalidades/5/requisitos/10/
Content-Type: application/json

{
  "nombre": "Test",
  "modalidad": 999
}
```
**Esperado:** ✅ Actualiza nombre, IGNORA modalidad=999, mantiene modalidad_id=5

---

## Conclusión

**Este cambio:**
- ✅ Arregla el error "modalidad: This field is required"
- ✅ Mantiene la funcionalidad de edición intacta
- ✅ Mejora la seguridad (no se puede manipular modalidad)
- ✅ Sigue el patrón RESTful de recursos anidados
- ✅ Es consistente con el diseño actual del sistema

**Riesgo:** Ninguno  
**Impacto:** Solo positivo  
**Líneas modificadas:** 1  
**Tiempo de aplicación:** 30 segundos
