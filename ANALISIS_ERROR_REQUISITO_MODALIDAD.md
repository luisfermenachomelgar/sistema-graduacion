# Análisis del Error: "modalidad: This field is required"

## 1. ENDPOINT EXACTO QUE RECIBE LA CREACIÓN

**URL:** `POST /api/modalidades/{id}/requisitos/`

**Ejemplo:** `POST /api/modalidades/5/requisitos/`

**Código Backend (views.py líneas 41-56):**
```python
@action(detail=True, methods=['get', 'post'], url_path='requisitos')
def requisitos(self, request, pk=None):
    modalidad = self.get_object()  # Obtiene la modalidad desde la URL (pk)
    
    if request.method == 'GET':
        requisitos = modalidad.requisitos.all()
        serializer = ModalidadRequisitoSerializer(requisitos, many=True, context={'request': request})
        return Response(serializer.data)
    
    if not self._can_manage_requisitos(request.user):
        raise PermissionDenied('No tienes permiso para administrar requisitos.')
    
    # AQUÍ ESTÁ EL PROBLEMA:
    serializer = ModalidadRequisitoSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)  # ← Valida ANTES de asignar modalidad
    serializer.save(modalidad=modalidad)       # ← Asigna modalidad DESPUÉS de validar
    return Response(serializer.data, status=status.HTTP_201_CREATED)
```

---

## 2. PAYLOAD JSON QUE ENVÍA EL FRONTEND

**Código Frontend (ModalidadDetalle.jsx líneas 288-309):**
```javascript
const payload = new FormData();
payload.append('nombre', formData.nombre);
payload.append('descripcion', formData.descripcion || '');
payload.append('categoria', formData.categoria || 'General');
payload.append('obligatorio', formData.obligatorio ? 'true' : 'false');
payload.append('version', formData.version || '1.0');
payload.append('observaciones', formData.observaciones || '');
payload.append('activo', formData.activo ? 'true' : 'false');

if (archivoFile) {
    payload.append('archivo', archivoFile);
}

// NO SE ENVÍA EL CAMPO 'modalidad' ← Esto es correcto, viene de la URL
```

**Payload real enviado:**
```
Content-Type: multipart/form-data

nombre: "Reglamento PDF"
descripcion: "Describe el alcance del requisito"
categoria: "General"
obligatorio: "true"
version: "1.0"
observaciones: "Notas administrativas"
activo: "true"
archivo: [binary file data]
```

**NOTA:** El campo `modalidad` NO se envía en el payload porque se obtiene de la URL.

---

## 3. SERIALIZER ACTUAL DE REQUISITO

**Código (serializers.py líneas 48-76):**
```python
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
            'modalidad',           # ← ESTE CAMPO ESTÁ EN fields
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
        read_only_fields = ['id', 'modalidad_nombre', 'archivo_url', 'archivo_nombre', 'archivo_tipo', 'archivo_tamano', 'created_at', 'updated_at']
        # ← 'modalidad' NO está en read_only_fields
```

**PROBLEMA IDENTIFICADO:**
- El campo `modalidad` está en `fields` pero NO en `read_only_fields`
- Esto significa que Django REST Framework espera que `modalidad` venga en el request.data
- Como no viene, la validación falla con: "modalidad: This field is required"

---

## 4. ¿MODALIDAD DESDE URL O DESDE BODY?

**RESPUESTA:** Debe obtenerse desde la URL (como está diseñado actualmente)

**Razón:**
- La URL es `/api/modalidades/{id}/requisitos/`
- El `{id}` identifica la modalidad padre
- Es un patrón RESTful estándar: recursos anidados
- El frontend ya está dentro del detalle de la modalidad específica

**Flujo correcto:**
1. Usuario abre modalidad con ID=5
2. Frontend hace: `POST /api/modalidades/5/requisitos/`
3. Backend extrae `pk=5` de la URL
4. Backend obtiene `modalidad = self.get_object()` (línea 43)
5. Backend asigna `serializer.save(modalidad=modalidad)` (línea 55)

---

## 5. ¿QUÉ CAMBIO PROVOCÓ EL ERROR?

### Análisis de Commits:

```bash
git log --oneline --all -- modalidades/serializers.py

3671f09 Vista previa en modalidades  ← COMMIT ACTUAL (HEAD)
688c98c Modalidades requisitos        ← COMMIT DONDE SE CREÓ LA FUNCIONALIDAD
ab57e50 style wix
ab68931 backup before frontend refactor
```

### Comparación de Código:

**ANTES (commit 688c98c):** El serializer probablemente tenía `modalidad` en `read_only_fields`

**AHORA (commit 3671f09):** El serializer tiene `modalidad` en `fields` pero NO en `read_only_fields`

### ¿Por qué funcionaba antes?

Hay dos posibilidades:

1. **Opción A:** En el commit 688c98c, `modalidad` estaba en `read_only_fields`:
   ```python
   read_only_fields = ['id', 'modalidad', 'modalidad_nombre', ...]
   ```

2. **Opción B:** El campo `modalidad` no estaba en `fields` en absoluto

### ¿Qué pasó en el commit 3671f09 "Vista previa en modalidades"?

Es probable que al agregar la funcionalidad de vista previa, se haya:
- Refactorizado el serializer
- Removido accidentalmente `modalidad` de `read_only_fields`
- O agregado `modalidad` a `fields` sin marcarlo como read-only

---

## CAUSA EXACTA DEL ERROR

### El Problema:

```python
# En views.py línea 53-55:
serializer = ModalidadRequisitoSerializer(data=request.data, context={'request': request})
serializer.is_valid(raise_exception=True)  # ← FALLA AQUÍ
serializer.save(modalidad=modalidad)
```

**Secuencia de eventos:**

1. `serializer.is_valid()` se ejecuta
2. Django REST Framework valida todos los campos en `fields`
3. Ve que `modalidad` está en `fields` pero NO en `read_only_fields`
4. Busca `modalidad` en `request.data`
5. No lo encuentra
6. Lanza error: **"modalidad: This field is required"**
7. Nunca llega a `serializer.save(modalidad=modalidad)` donde se asignaría

### Por qué `serializer.save(modalidad=modalidad)` no ayuda:

El método `save()` se ejecuta DESPUÉS de `is_valid()`. Si la validación falla, nunca se llega al `save()`.

---

## SOLUCIÓN

Agregar `modalidad` a `read_only_fields` en el serializer:

```python
class Meta:
    model = ModalidadRequisito
    fields = [
        'id',
        'modalidad',
        'modalidad_nombre',
        # ... resto de campos
    ]
    read_only_fields = [
        'id', 
        'modalidad',  # ← AGREGAR AQUÍ
        'modalidad_nombre', 
        'archivo_url', 
        'archivo_nombre', 
        'archivo_tipo', 
        'archivo_tamano', 
        'created_at', 
        'updated_at'
    ]
```

### ¿Por qué esta solución es correcta?

1. **Patrón RESTful:** La modalidad se identifica por la URL, no por el body
2. **Seguridad:** Evita que un usuario malicioso envíe un `modalidad` diferente
3. **Consistencia:** El campo `modalidad` se asigna en el backend via `save(modalidad=...)`
4. **Validación:** Django REST Framework no exigirá el campo durante `is_valid()`

---

## VERIFICACIÓN

### Antes del cambio:
```
POST /api/modalidades/5/requisitos/
Body: { nombre: "Test", archivo: file }
Error: "modalidad: This field is required"
```

### Después del cambio:
```
POST /api/modalidades/5/requisitos/
Body: { nombre: "Test", archivo: file }
Success: 201 Created
```

---

## RESUMEN EJECUTIVO

| Aspecto | Detalle |
|---------|---------|
| **Error** | "modalidad: This field is required" |
| **Causa** | Campo `modalidad` en `fields` pero no en `read_only_fields` |
| **Cuándo ocurre** | Al crear un nuevo requisito desde el detalle de modalidad |
| **Por qué falló** | La validación ocurre antes de asignar `modalidad` via `save()` |
| **Cambio reciente** | Commit "Vista previa en modalidades" modificó el serializer |
| **Solución** | Agregar `'modalidad'` a `read_only_fields` |
| **Impacto** | Bajo - Solo afecta creación de requisitos |
| **Tiempo estimado** | 1 línea de código, 30 segundos |
