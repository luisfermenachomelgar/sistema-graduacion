# Diagnóstico: Diferencia en Lógica de Validación entre Modalidades

## Problema
Usuario reporta: "Proyecto de Grado permite avanzar de etapa sin validar documentos obligatorios, pero Examen de Grado valida correctamente"

## Investigación Realizada

### 1. Código de Validación (Backend)

#### `postulantes/services.py:189` - `avanzar_postulacion()`
```python
missing_docs = required_documents_missing(postulacion)
if missing_docs:
    raise EtapaIncompletaError({
        'detail': 'Existen documentos obligatorios pendientes o no aprobados.',
        'faltantes': missing_names,
    })
```

**Hallazgo:** La lógica es **IDÉNTICA** para ambas modalidades. No hay condicionales.

#### `postulantes/services.py:114` - `required_documents_missing()`
```python
mtd_qs = ModalidadTipoDocumento.objects.filter(
    modalidad_id=postulacion.modalidad_id,
    obligatorio=True,
    activo=True,
).filter(Q(etapa_id=etapa.id) | Q(etapa__isnull=True))

if not mtd_qs.exists():
    return []  # Si no hay documentos configurados, permite avanzar
```

**Hallazgo:** La lógica es **IDÉNTICA** para ambas modalidades.

### 2. Endpoints Disponibles (Backend)

#### `postulantes/views.py:154` - `@action avanzar-etapa`
```python
@action(
    detail=True,
    methods=['post'],
    permission_classes=[PuedeAvanzarEtapaPermission],
    url_path='avanzar-etapa'
)
def avanzar_etapa(self, request, pk=None):
    postulacion = avanzar_postulacion(pk, actor=request.user)
    return Response(self.get_serializer(postulacion).data)
```

**Ruta:** `POST /api/postulaciones/{id}/avanzar-etapa/` ✅ Valida

#### `postulantes/views.py:78` - `PostulacionViewSet` (inherited update)
Sin `perform_update` personalizado, usa el método por defecto de ModelViewSet.

**Ruta:** `PATCH /api/postulaciones/{id}/` ⚠️ Actualiza sin validación

### 3. Configuración de Serializer (Backend)

#### `postulantes/serializers.py:130` - PostulacionDetailSerializer
```python
class Meta:
    model = Postulacion
    fields = [...]
    read_only_fields = ['id', 'fecha_postulacion', 'estado_general']
```

**Hallazgo:** `etapa_actual` NO está en `read_only_fields`

**Implicación:** `etapa_actual` es editable mediante PATCH/PUT sin validación.

---

## LA DIFERENCIA ENCONTRADA

### Caminos para Actualizar etapa_actual

| Operación | Endpoint | Método | Validación | Estado |
|-----------|----------|--------|------------|--------|
| Botón "Avanzar Etapa" | `/api/postulaciones/{id}/avanzar-etapa/` | POST | ✅ Valida con `required_documents_missing()` | Funciona |
| Editar Postulación (Modal) | `/api/postulaciones/{id}/` | PATCH | ❌ NO valida | **BYPASS** |

### Código Frontend

#### `frontend/src/pages/Postulaciones.jsx:225`
```javascript
const result = isEditMode
  ? await patch(endpoint, payload)  // ← PATCH sin validación
  : await create(payload);

if (result.success) {
  // Actualizar tabla
}
```

#### `frontend/src/pages/Postulaciones.jsx:277`
```javascript
const handleAvanzarEtapa = async (postulacion) => {
  const result = await api.create(API_CONFIG.ENDPOINTS.POSTULACION_AVANZAR_ETAPA(postulacion.id));
  // ← POST con validación
}
```

---

## Comportamiento Actual

### Examen de Grado
- ✅ Si usuario hace clic en "Avanzar Etapa" → valida documentos
- ✅ Botón siempre disponible
- ❌ Pero si usuario edita modal y cambia etapa_actual manualmente → BYPASS de validación

### Proyecto de Grado
- ✅ Si usuario hace clic en "Avanzar Etapa" → valida documentos (igual que Examen)
- ✅ Botón siempre disponible
- ❌ Pero si usuario edita modal y cambia etapa_actual manualmente → BYPASS de validación

**Conclusión:** Ambas modalidades tienen el MISMO comportamiento. Ambas permiten un BYPASS mediante PATCH manual.

---

## Problema Raíz

La lógica de validación es **correcta e idéntica** para ambas modalidades. El problema es:

**El campo `etapa_actual` es editable mediante PATCH, permitiendo un bypass de la validación en ambas modalidades.**

Cuando alguien hace:
```bash
PATCH /api/postulaciones/111/ {"etapa_actual": 24}
```

El serializer permite esta actualización sin llamar a `avanzar_postulacion()`, por lo tanto, sin validar documentos.

---

## Solución Correcta (sin cambiar reglas de negocio)

Marcar `etapa_actual` como **read-only** en el serializer:

```python
# postulantes/serializers.py - PostulacionDetailSerializer
class Meta:
    read_only_fields = ['id', 'fecha_postulacion', 'estado_general', 'etapa_actual']
```

Esto fuerza que CUALQUIER cambio de etapa pase por el endpoint `/avanzar-etapa/` que sí valida.

**Beneficio:** Proyecto de Grado y Examen de Grado usan **exactamente la misma lógica de validación**.

---

## Verificación

Para confirmar que ambas modalidades tienen el problema, se puede:

1. Crear postulación en Examen de Grado
2. Editar modal y cambiar `etapa_actual` directamente
3. Verificar que permite avanzar sin documentos
4. Repetir con Proyecto de Grado
5. Ambas permitirán el bypass

Por tanto, **el código ESTÁ reutilizando la misma lógica**. El problema es que hay un BYPASS que aplica a ambas.

La solución es eliminar ese bypass marcando `etapa_actual` como read-only.
