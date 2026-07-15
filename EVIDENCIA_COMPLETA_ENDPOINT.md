# EVIDENCIA DEFINITIVA: ¿Qué Endpoint Usa el Botón "Avanzar Etapa"?

## 1. ANÁLISIS DEL CÓDIGO FRONTEND

### Paso 1: Búsqueda del Botón "Avanzar Etapa"

**Archivo:** `frontend/src/pages/Postulaciones.jsx`
**Líneas:** 428-434

```javascript
return (
  <button
    type="button"
    onClick={() => handleAvanzarEtapa(row)}
    className="px-3 py-1 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded hover:bg-indigo-200 dark:hover:bg-indigo-800 transition text-xs font-medium"
  >
    Avanzar Etapa
  </button>
);
```

**Conclusión:** El botón llama a `handleAvanzarEtapa(row)`

---

### Paso 2: Definición de `handleAvanzarEtapa`

**Archivo:** `frontend/src/pages/Postulaciones.jsx`
**Líneas:** 272-289

```javascript
const handleAvanzarEtapa = async (postulacion) => {
  setError('');
  setSuccess('');

  try {
    const result = await api.create(
      API_CONFIG.ENDPOINTS.POSTULACION_AVANZAR_ETAPA(postulacion.id)
    );
    if (result.success) {
      setSuccess('Postulación avanzada exitosamente');
      await refresh({
        errorMessage: 'Error al cargar postulaciones',
        exceptionMessage: 'Error loading postulaciones',
      });
    } else {
      setError(result.error || 'Error al avanzar la etapa');
    }
  } catch (err) {
    setError('Error al avanzar la etapa');
  }
};
```

**Conclusión:** Usa `api.create()` con endpoint `POSTULACION_AVANZAR_ETAPA`

---

### Paso 3: Definición del Endpoint

**Archivo:** `frontend/src/constants/api.js`
**Línea:** 53

```javascript
POSTULACION_AVANZAR_ETAPA: (id) => `/api/postulaciones/${id}/avanzar-etapa/`,
```

**Conclusión:** El endpoint es `/api/postulaciones/{id}/avanzar-etapa/`

---

### Paso 4: ¿Qué Método HTTP es `api.create()`?

En Axios (usado en la aplicación):
- `api.create(url)` = `POST url`

**Conclusión:** La petición es `POST /api/postulaciones/{id}/avanzar-etapa/`

---

## 2. ANÁLISIS DEL CÓDIGO BACKEND

### Paso 5: Definición del Endpoint

**Archivo:** `postulantes/views.py`
**Líneas:** 154-162

```python
@action(
    detail=True,
    methods=['post'],  # ← Solo POST
    permission_classes=[PuedeAvanzarEtapaPermission],
    url_path='avanzar-etapa'
)
def avanzar_etapa(self, request, pk=None):
    postulacion = avanzar_postulacion(pk, actor=request.user)
    return Response(self.get_serializer(postulacion).data)
```

**Conclusión:** El endpoint `avanzar-etapa` solo acepta `POST` y llama a `avanzar_postulacion(pk)`

---

### Paso 6: Función `avanzar_postulacion()`

**Archivo:** `postulantes/services.py`
**Líneas:** 189-240 (extracto crítico: 211-217)

```python
@transaction.atomic
def avanzar_postulacion(postulacion_id: int, *, actor=None) -> Postulacion:
    postulacion = (
        Postulacion.objects.select_for_update()
        .select_related('modalidad')
        .get(pk=postulacion_id)
    )
    # ... código previo ...
    
    # ← VALIDACIÓN CRÍTICA
    missing_docs = required_documents_missing(postulacion)
    if missing_docs:
        missing_names = [item['nombre'] for item in missing_docs]
        raise EtapaIncompletaError(
            {
                'detail': 'Existen documentos obligatorios pendientes o no aprobados.',
                'faltantes': missing_names,
            }
        )
    
    # Si hay documentos faltantes, levanta excepción aquí ↑
    # Si no hay faltantes, continúa ↓
    next_stage = (
        Etapa.objects.filter(
            modalidad_id=postulacion.modalidad_id,
            activo=True,
            orden__gt=postulacion.etapa_actual.orden,
        )
        .order_by('orden')
        .first()
    )
    
    if next_stage:
        postulacion.etapa_actual = next_stage
        # ... actualiza y guarda ...
```

**Conclusión:** Valida con `required_documents_missing()` antes de cambiar etapa

---

### Paso 7: Función `required_documents_missing()`

**Archivo:** `postulantes/services.py`
**Líneas:** 114-142

```python
def required_documents_missing(postulacion: Postulacion) -> list[dict]:
    etapa = postulacion.etapa_actual
    if not etapa:
        return []
    
    # Busca documentos obligatorios en ModalidadTipoDocumento
    mtd_qs = ModalidadTipoDocumento.objects.filter(
        modalidad_id=postulacion.modalidad_id,
        obligatorio=True,
        activo=True,
    ).filter(Q(etapa_id=etapa.id) | Q(etapa__isnull=True))

    if not mtd_qs.exists():
        return []  # ← AQUÍ: Si no hay documentos configurados, retorna lista vacía

    missing: list[dict] = []
    # Para cada tipo requerido, comprobar que exista un DocumentoPostulacion aprobado
    for mtd in mtd_qs.select_related('tipo_documento'):
        tipo = mtd.tipo_documento
        docs = DocumentoPostulacion.objects.filter(
            postulacion_id=postulacion.id, 
            tipo_documento_id=tipo.id
        )
        if not docs.exists():
            missing.append({
                'id': tipo.id, 
                'nombre': tipo.nombre, 
                'motivo': 'no_cargado'
            })
            continue
        # Hay al menos uno cargado; verificar que alguno esté aprobado
        aprobado = docs.filter(estado='aprobado').exists()
        if not aprobado:
            missing.append({
                'id': tipo.id, 
                'nombre': tipo.nombre, 
                'motivo': 'no_aprobado'
            })

    return missing
```

**Conclusión:** 
- NO tiene condicionales por modalidad
- Si no hay documentos configurados, retorna `[]` (lista vacía)
- Lista vacía = sin faltantes = permite avanzar

---

## 3. DIAGRAMA DE FLUJO

```
┌─ Frontend: Botón "Avanzar Etapa" (Postulaciones.jsx:430)
│
└─→ onClick: handleAvanzarEtapa(postulacion)
    │
    └─→ POST /api/postulaciones/{id}/avanzar-etapa/
        │
        └─→ Backend: PostulacionViewSet.avanzar_etapa()
            │
            └─→ avanzar_postulacion(pk, actor=request.user)
                │
                ├─→ required_documents_missing(postulacion)
                │   │
                │   └─→ ModalidadTipoDocumento.objects.filter(
                │       modalidad_id=postulacion.modalidad_id,
                │       obligatorio=True,
                │       etapa_id=etapa.id
                │   )
                │
                ├─→ if missing_docs:
                │   └─→ raise EtapaIncompletaError()  ✅ VALIDA
                │
                └─→ else:
                    └─→ postulacion.etapa_actual = next_stage  ✅ AVANZA
```

---

## 4. ANÁLISIS POR MODALIDAD

### Examen de Grado
```
Etapa 1 (Registro):         9 documentos obligatorios
Etapa 2 (Examen 1):         1 documento obligatorio
Etapa 3 (Examen 2):         1 documento obligatorio
Etapa 4 (Examen 3):         1 documento obligatorio
Etapa 5 (Examen 4):         1 documento obligatorio
Etapa 6 (Acta Final):       1 documento obligatorio

Cuando intenta avanzar desde cualquier etapa:
1. required_documents_missing() ENCUENTRA documentos obligatorios
2. Verifica que estén aprobados
3. Si NO están aprobados → retorna lista de faltantes
4. avanzar_postulacion() levanta EtapaIncompletaError ✅ FUNCIONA
```

### Proyecto de Grado
```
Etapa 1 (Registro):                 4 documentos obligatorios
Etapa 2 (Perfil):                   4 documentos obligatorios
Etapa 3 (Documento Final):          8 documentos obligatorios
Etapa 4 (Defensa Privada):          0 documentos ← VACÍA
Etapa 5 (Defensa Pública):          0 documentos ← VACÍA
Etapa 6 (Acta Final):               1 documento obligatorio

Cuando intenta avanzar FROM etapa 3 TO etapa 4:
1. required_documents_missing() busca documentos para etapa 4
2. NO ENCUENTRA documentos (están vacíos)
3. Retorna [] (lista vacía)
4. if missing_docs: → False (porque [] es falso)
5. avanzar_postulacion() NO levanta excepción
6. Avanza sin validar nada ❌ PROBLEMA
```

---

## 5. CONCLUSIÓN FINAL

### ✅ Lo que demuestra esta evidencia:

1. **El botón "Avanzar Etapa" SÍ usa el endpoint correcto:**
   - `POST /api/postulaciones/{id}/avanzar-etapa/`
   - Que SÍ valida documentos

2. **La lógica de validación es IDÉNTICA para ambas modalidades:**
   - `required_documents_missing()` NO tiene condicionales
   - `avanzar_postulacion()` NO tiene condicionales

3. **El problema SÍ es la configuración de datos:**
   - Etapas 4 y 5 de Proyecto de Grado NO tienen documentos configurados
   - Cuando no hay documentos, `required_documents_missing()` retorna `[]`
   - Lista vacía = permiso implícito para avanzar

4. **Esto afecta IGUAL a ambas modalidades:**
   - Si Examen de Grado tuviera etapas vacías, también permitiría avanzar
   - Proyecto de Grado permite porque SUS etapas 4 y 5 están vacías

---

## 6. El Usuario Podría Encontrar un Bypass (pero no es lo que pasa)

Existe un método alternativo para cambiar etapa (sin usar el botón):
- `PATCH /api/postulaciones/{id}/` puede editar `etapa_actual` directamente
- Esto SÍ tiene un bypass porque NO pasa por `avanzar_postulacion()`
- Pero el usuario reporta usar el botón "Avanzar Etapa", que SÍ valida

---

## RECOMENDACIÓN PARA PRÓXIMOS PASOS:

Para confirmar 100% que el usuario está viendo el comportamiento esperado:

1. **Opción A:** Agregar documentos obligatorios a etapas 4 y 5 de Proyecto de Grado
2. **Opción B:** Cerrar el bypass del PATCH (marcar etapa_actual como read_only)
3. **Opción C:** Ambas cosas para máxima seguridad

El usuario debería confirmar cuál es la regla de negocio correcta.
