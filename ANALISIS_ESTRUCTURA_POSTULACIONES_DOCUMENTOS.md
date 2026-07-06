# 📊 Análisis Completo: Estructura de Postulaciones y Documentos

**Generado:** 2026-07-05  
**Archivos Analizados:** 10 archivos (backend + frontend)

---

## 📋 Tabla de Contenidos
1. [Modelos Backend](#modelos-backend)
2. [Relaciones de Datos](#relaciones-de-datos)
3. [Visualización Frontend](#visualización-frontend)
4. [Flujos de Usuario](#flujos-de-usuario)
5. [Inconsistencias Encontradas](#-inconsistencias-encontradas)
6. [Recomendaciones](#recomendaciones)

---

## Modelos Backend

### 1️⃣ Definición de Etapas

**Archivo:** [`modalidades/models.py`](modalidades/models.py)

```python
class Etapa(models.Model):
    nombre = CharField(max_length=100)
    orden = PositiveIntegerField()
    modalidad = ForeignKey(Modalidad, on_delete=CASCADE)  # ← CLAVE
    activo = BooleanField(default=True)
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=['modalidad', 'orden'])
        ]
```

**Características:**
- ✅ Cada etapa **PERTENECE a una modalidad**
- ✅ El orden es **ÚNICO por modalidad**
- ✅ Ejemplo: Modalidad "Tesis" → Etapas: 1. Perfil, 2. Defensa, 3. Titulación

---

### 2️⃣ Postulación con Etapa Actual

**Archivo:** [`postulantes/models.py`](postulantes/models.py)

```python
class Postulacion(models.Model):
    postulante = ForeignKey(Postulante, ...)
    modalidad = ForeignKey('modalidades.Modalidad', ...)  # REQUERIDO
    etapa_actual = ForeignKey(
        'modalidades.Etapa',
        on_delete=SET_NULL,
        null=True, blank=True  # ⚠️ NULLABLE
    )
    titulo_trabajo = CharField(...)
    estado = CharField(choices=[...])  # borrador, en_revision, aprobada, rechazada
    estado_general = CharField(...)    # EN_PROCESO, PERFIL_APROBADO, etc.
```

**Validación en Serializer:**
```python
if modalidad and etapa_actual and etapa_actual.modalidad_id != modalidad.id:
    raise ValidationError('La etapa debe pertenecer a la modalidad')
```

✅ **El sistema valida que la etapa pertenezca a la modalidad seleccionada**

---

### 3️⃣ Tipos de Documento y Modalidades

**Archivo:** [`documentos/models.py`](documentos/models.py)

#### Modelo: `TipoDocumento`
```python
class TipoDocumento(models.Model):
    nombre = CharField(max_length=100)
    etapa = ForeignKey('modalidades.Etapa', null=True, blank=True)  # ⚠️
    descripcion = TextField(blank=True)
    obligatorio = BooleanField(default=True)
```

#### Modelo: `ModalidadTipoDocumento` (M2M Relación)
```python
class ModalidadTipoDocumento(models.Model):
    modalidad = ForeignKey(Modalidad, ...)
    tipo_documento = ForeignKey(TipoDocumento, ...)
    etapa = ForeignKey(Etapa, null=True, blank=True)  # ← FILTRO PRINCIPAL
    obligatorio = BooleanField()
    orden = PositiveIntegerField()
    
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['modalidad', 'tipo_documento', 'etapa'],
                name='unique_modalidad_documento_etapa'
            )
        ]
```

**Propósito:** Define qué documentos son **obligatorios en cada etapa de cada modalidad**

#### Modelo: `DocumentoPostulacion`
```python
class DocumentoPostulacion(models.Model):
    postulacion = ForeignKey(Postulacion, ...)
    tipo_documento = ForeignKey(TipoDocumento, ...)
    archivo = FileField(upload_to='documentos/postulaciones/')
    estado = CharField(choices=[
        'pendiente', 'aprobado', 'rechazado'
    ])
```

---

## Relaciones de Datos

### Diagrama de Relaciones

```
┌─────────────────────────────────────────────────────────────┐
│                    MODALIDAD                                │
│  (Tesis, Trabajo Dirigido, Proyecto de Grado, etc.)         │
└────────────────────────┬────────────────────────────────────┘
                         │
                ┌────────┴────────────┬──────────────┐
                │                    │              │
        ┌───────▼────────┐   ┌──────▼──────┐  ┌──▼─────────────┐
        │     ETAPA       │   │ REQUISITO   │  │ MODALIDAD TIPO │
        │  (orden: 1,2,3) │   │             │  │  DOCUMENTO     │
        │  ej: Perfil     │   └─────────────┘  │ (documento +   │
        │  ej: Defensa    │                    │  etapa +       │
        │  ej: Titulación │                    │  obligatorio)  │
        └───────┬────────┘                     └──┬────────┬────┘
                │                                  │        │
                │                   ┌──────────────┘        │
                │                   │                       │
        ┌───────▼────────────────────▼──────────┐   ┌──────▼──────────┐
        │      TIPO DOCUMENTO                   │   │    POSTULACION  │
        │  (Currículum, Anteproyecto,etc.)     │   │  + etapa_actual │
        │                                       │   │  + modalidad    │
        └───────┬────────────────────────────────┘   └──┬─────────────┘
                │                                       │
                │                       ┌───────────────┘
                │                       │
        ┌───────▼───────────────────────▼───┐
        │    DOCUMENTO POSTULACION           │
        │ (Archivo subido por estudiante)    │
        │ estado: pendiente/aprobado/rechazado
        └───────────────────────────────────┘
```

### Tabla de Relaciones

| Tabla A | FK a B | Tabla B | Descripción |
|---------|--------|---------|------------|
| `Etapa` | `modalidad` | `Modalidad` | Etapa pertenece a una modalidad |
| `Postulacion` | `etapa_actual` | `Etapa` | Postulación en etapa actual |
| `Postulacion` | `modalidad` | `Modalidad` | Postulación bajo una modalidad |
| `TipoDocumento` | `etapa` | `Etapa` | ⚠️ Nullable, relación débil |
| `ModalidadTipoDocumento` | `modalidad` | `Modalidad` | Define documentos por modalidad |
| `ModalidadTipoDocumento` | `tipo_documento` | `TipoDocumento` | Documento asociado |
| `ModalidadTipoDocumento` | `etapa` | `Etapa` | Documento en esta etapa |
| `DocumentoPostulacion` | `postulacion` | `Postulacion` | Documento asociado a postulación |
| `DocumentoPostulacion` | `tipo_documento` | `TipoDocumento` | Tipo de documento |

---

## Visualización Frontend

### 1️⃣ Página: "Nueva Postulación" (Postulaciones.jsx)

**Ubicación:** [`frontend/src/pages/Postulaciones.jsx`](frontend/src/pages/Postulaciones.jsx)

#### Cargas Iniciales de Datos (líneas 75-88)

```javascript
// ✅ CORRECTO: Carga modalidades para el dropdown
if (modResult.success) {
  setModalidades(modsData);
}

// ❌ PROBLEMA: Carga TODAS las etapas SIN filtrar
if (etapaResult.success) {
  const etapasData = Array.isArray(etapaResult.data) 
    ? etapaResult.data 
    : etapaResult.data.results || [];
  setEtapas(etapasData);  // ← SIN FILTRO POR MODALIDAD
}
```

#### Formulario Modal

```javascript
{
  postulante_id: '',
  modalidad: '',            // Dropdown: todas las modalidades
  titulo_trabajo: '',
  anio_academico: 2026,
  semestre_academico: '',
  estado: 'en_revision',
  estado_general: 'EN_PROCESO',
  etapa_actual: null,       // ⚠️ NO hay dropdown visible en el código mostrado
  tutor: '',
  observaciones: '',
}
```

#### Envío de Datos

```javascript
const payload = {
  postulante_id: formData.postulante_id,
  titulo_trabajo: formData.titulo_trabajo,
  anio_academico: formData.anio_academico,
  semestre_academico: formData.semestre_academico,
  estado: formData.estado,
  modalidad: formData.modalidad,
  etapa_actual: formData.etapa_actual || null,  // ← Nullable, puede ser null
  tutor: formData.tutor,
  observaciones: formData.observaciones,
};
```

**Conclusión:**
- ✅ Se valida que etapa pertenezca a modalidad en backend
- ⚠️ Si hay selector de etapa en UI, mostraría TODAS sin filtro
- ❌ No hay reagrupación dinámica de etapas cuando seleccionas modalidad

---

### 2️⃣ Página: "Subir Documentos" (Documentos.jsx)

**Ubicación:** [`frontend/src/pages/Documentos.jsx`](frontend/src/pages/Documentos.jsx)

#### Flujo: Seleccionar Postulación → Documentos Filtrados

**Paso 1:** Usuario selecciona postulación (línea ~155-165)

```javascript
<FormField
  label="Postulación *"
  name="postulacion"
  type="select"
  value={formData.postulacion}
  onChange={handleInputChange}
  options={postulaciones.map(p => ({
    id: p.id,
    label: getPostulacionLabel(p),
  }))}
/>
```

**Paso 2:** Al cambiar postulación, se filtran documentos (línea ~130-145)

```javascript
const handleInputChange = async (e) => {
  // ...
  if (name === 'postulacion' && newValue) {
    const selectedPostulacion = postulaciones.find(p => p.id === newValue);
    const modalidadId = selectedPostulacion?.modalidad?.id;
    const etapaId = selectedPostulacion?.etapa_actual;  // ← Obtiene etapa actual

    if (modalidadId) {
      // Carga documentos para esta modalidad + etapa
      await getTiposDocumentoFiltrados(modalidadId, etapaId);
    }
  }
};
```

**Paso 3:** Método `getTiposDocumentoFiltrados` (línea ~104-125)

```javascript
const getTiposDocumentoFiltrados = async (modalidadId, etapaId = null) => {
  const cacheKey = `${modalidadId}:${etapaId || 'null'}`;
  
  // Consulta al backend
  const url = API_CONFIG.ENDPOINTS.MODALIDAD_TIPOS_DOCUMENTO(modalidadId);
  const params = etapaId ? { etapa: etapaId } : {};
  const result = await api.getAll(url, params);
  
  // Procesa resultados
  const filtered = deduplicated.map(item => ({
    id: item.tipo_documento.id,
    label: item.tipo_documento.nombre,
    obligatorio: item.obligatorio,
  }));
  
  setTiposDocumentoFiltrados(filtered);
};
```

**Paso 4:** Dropdown de Tipo Documento (línea ~169-177)

```javascript
<FormField
  label="Tipo de Documento *"
  name="tipo_documento"
  type="select"
  value={formData.tipo_documento}
  onChange={handleInputChange}
  options={(formData.postulacion ? tiposDocumentoFiltrados : [])
    .map(t => ({
      id: t.id,
      label: t.label,
    }))}
/>
```

**Conclusión:**
- ✅ Los documentos **SE FILTRAN automáticamente por modalidad + etapa**
- ✅ Solo muestra documentos relevantes para esa postulación
- ✅ El filtrado es **implícito** (ocurre cuando seleccionas postulación)

---

### 3️⃣ Backend: Endpoint de Filtrado

**Ubicación:** [`modalidades/views.py`](modalidades/views.py#L108-L124)

```python
@action(detail=True, methods=['get'], url_path='tipos-documento')
def tipos_documento(self, request, pk=None):
    modalidad = self.get_object()
    queryset = ModalidadTipoDocumento.objects.select_related(
        'tipo_documento', 'etapa'
    ).filter(
        modalidad=modalidad,
        activo=True,
        tipo_documento__activo=True,
    )

    # Filtrado OPCIONAL por etapa
    etapa_id = request.query_params.get('etapa')
    if etapa_id:
        queryset = queryset.filter(etapa_id=etapa_id)

    serializer = ModalidadTipoDocumentoSerializer(queryset, many=True)
    return Response(serializer.data)
```

**Endpoint:** `GET /api/modalidades/{id}/tipos-documento/?etapa={etapa_id}`

**Parámetros:**
- `id` (path): ID de la modalidad ✅
- `etapa` (query): ID de la etapa (opcional) ✅

---

## Flujos de Usuario

### 📌 Flujo 1: Crear Nueva Postulación

```
┌─────────────────────┐
│ 1. Abrir Modal      │
│    "Postulación"    │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────────┐
│ 2. Seleccionar:              │
│    - Postulante              │
│    - Modalidad (Tesis)        │
│    - Año/Semestre            │
│    - Título Trabajo          │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ 3. [OPCIONAL] Seleccionar Etapa      │
│    (todas las etapas se cargan)      │
│    ⚠️ SIN FILTRAR POR MODALIDAD     │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ 4. Enviar: POST /api/postulaciones/  │
│    {                                 │
│      postulante_id: 5,               │
│      modalidad: 3,                   │
│      etapa_actual: null,             │
│      ...                             │
│    }                                 │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ 5. Backend Valida:                   │
│    ✅ etapa.modalidad == modalidad   │
│    ✅ año/semestre único             │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ 6. Crear Postulacion                 │
│    estado: "borrador"                │
│    estado_general: "EN_PROCESO"      │
└──────────────────────────────────────┘
```

**Puntos Clave:**
1. ✅ Modalidad es REQUERIDO
2. ⚠️ Etapa actual es OPCIONAL (puede ser null)
3. ⚠️ Si etapa se selecciona, debe pertenecer a la modalidad
4. ✅ Validación ocurre en backend (serializers)

---

### 📌 Flujo 2: Subir Documentos

```
┌─────────────────────────────────┐
│ 1. Abrir Modal "Nuevo Documento"│
└──────────┬──────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ 2. Seleccionar Postulación           │
│    (dropdown con todas)              │
└──────────┬───────────────────────────┘
           │
           ▼
┌────────────────────────────────────────────┐
│ 3. Extracto AUTOMÁTICO:                    │
│    - postulacion.modalidad = "Tesis"       │
│    - postulacion.etapa_actual = 2 (Defensa)
└──────────┬─────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│ 4. Consulta:                             │
│    GET /api/modalidades/3/tipos-documento/
│        ?etapa=2                          │
└──────────┬───────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│ 5. Backend Retorna:                      │
│    ModalidadTipoDocumento.objects.filter(│
│      modalidad=3,                        │
│      etapa=2,                            │
│      activo=True                         │
│    )                                     │
│    Resultado:                            │
│    - Defensa (obligatorio)               │
│    - Correcciones (opcional)             │
└──────────┬───────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│ 6. Dropdown "Tipo Documento":            │
│    - ✅ Defensa                          │
│    - ✅ Correcciones                     │
│    (Solo estos, no otros)                │
└──────────┬───────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│ 7. Seleccionar Documento + Archivo       │
│    - Tipo: "Defensa"                     │
│    - Archivo: video.mp4 (50MB)           │
└──────────┬───────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│ 8. POST /api/documentos/                 │
│    {                                     │
│      postulacion: 42,                    │
│      tipo_documento: 15,                 │
│      archivo: <file>,                    │
│      estado: "pendiente"                 │
│    }                                     │
└──────────┬───────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│ 9. Crear DocumentoPostulacion            │
│    estado: "pendiente"                   │
│    (Admin después aprueba/rechaza)       │
└──────────────────────────────────────────┘
```

**Puntos Clave:**
1. ✅ Documentos se filtran automáticamente
2. ✅ Filtrado por modalidad + etapa actual
3. ✅ Solo muestra documentos obligatorios/permitidos
4. ✅ Validación de archivo (extensión, tamaño)

---

## 🚨 Inconsistencias Encontradas

### 1. ⚠️ Carga de TODAS las etapas sin filtro

**Severidad:** 🟡 **MEDIA**

**Ubicación:** [`Postulaciones.jsx`](frontend/src/pages/Postulaciones.jsx#L75-L88)

```javascript
// ❌ ACTUAL
if (etapaResult.success) {
  const etapasData = Array.isArray(etapaResult.data) 
    ? etapaResult.data 
    : etapaResult.data.results || [];
  setEtapas(etapasData);  // TODAS las etapas
}
```

**Problema:**
- Se cargan etapas de TODAS las modalidades
- Si hay selector UI para `etapa_actual`, mostraría etapas de modalidades que no coinciden
- Potencial para que un usuario seleccione una etapa de otra modalidad (aunque backend lo rechaza)

**Impacto:**
- UX confusa (usuario ve etapas irrelevantes)
- Consumo innecesario de datos (carga TODAS cuando podría cargar por demanda)

**Solución:**
```javascript
// ✅ MEJOR
const handleModalidadChange = async (modalidadId) => {
  // Cargar etapas solo para esta modalidad
  const etapasResult = await api.getAll(
    API_CONFIG.ENDPOINTS.ETAPAS,
    { modalidad: modalidadId },
    { skipGlobalLoader: true }
  );
  if (etapasResult.success) {
    setEtapas(etapasResult.data);
  }
};
```

**Validación que existe:** ✅ Backend valida en [`postulantes/serializers.py`](postulantes/serializers.py#L135-140)

---

### 2. ❌ Import de `EtapaSerializer` que no existe

**Severidad:** 🔴 **CRÍTICA**

**Ubicación:** [`postulantes/views.py`](postulantes/views.py#L13)

```python
from .serializers import (
    # ...
    EtapaSerializer,  # ❌ NO EXISTE en postulantes/serializers.py
    # ...
)
```

**Problema:**
- `EtapaSerializer` se importa pero no está definido
- Debería estar en [`modalidades/serializers.py`](modalidades/serializers.py)
- El import incorrecto causaría `ImportError` en runtime

**Solución:**
```python
# En postulantes/views.py
# CAMBIAR
from .serializers import EtapaSerializer

# POR
from modalidades.serializers import EtapaSerializer
```

---

### 3. ⚠️ `etapa_actual` nullable pero con validación

**Severidad:** 🟡 **MEDIA**

**Ubicación:** [`postulantes/models.py`](postulantes/models.py#L71-75)

```python
class Postulacion(models.Model):
    etapa_actual = models.ForeignKey(
        'modalidades.Etapa',
        on_delete=models.SET_NULL,
        null=True,        # ← Puede ser NULL
        blank=True,
        related_name='postulaciones_actuales',
    )
```

**Pero en serializer valida:** [`postulantes/serializers.py`](postulantes/serializers.py#L135-140)

```python
if modalidad and etapa_actual and etapa_actual.modalidad_id != modalidad.id:
    raise ValidationError(...)
```

**Problema:**
- Campo es nullable (puede ser null)
- Pero hay validación que asume que si existe, debe pertenecer a la modalidad
- **Inconsistencia:** ¿Es realmente opcional o debería ser requerido?

**Preguntas:**
- ¿Puede una postulación existir sin etapa?
- ¿Se inicializa automáticamente en la primera etapa?
- ¿El usuario puede cambiarla?

---

### 4. ⚠️ Dos relaciones a Etapa: `TipoDocumento.etapa` + `ModalidadTipoDocumento.etapa`

**Severidad:** 🟡 **MEDIA**

**Ubicación:** [`documentos/models.py`](documentos/models.py#L8-14) vs línea #52

```python
# TipoDocumento tiene relación directa a Etapa
class TipoDocumento(models.Model):
    etapa = models.ForeignKey(
        'modalidades.Etapa',
        on_delete=models.PROTECT,
        related_name='tipos_documento',
        null=True, blank=True,  # ← NULLABLE
    )

# Pero ModalidadTipoDocumento TAMBIÉN tiene
class ModalidadTipoDocumento(models.Model):
    etapa = models.ForeignKey(
        'modalidades.Etapa',
        on_delete=models.CASCADE,
        related_name='documentos_requeridos',
        null=True, blank=True,  # ← NULLABLE
    )
```

**Problema:**
- Hay **dos formas** de especificar la etapa de un documento
- Causa confusión sobre cuál es la "fuente de verdad"
- Si `TipoDocumento.etapa` y `ModalidadTipoDocumento.etapa` difieren, ¿cuál prevalece?

**Ejemplo de Inconsistencia:**
```
TipoDocumento: "Currículum"
  - etapa = Etapa 1 (Perfil)

ModalidadTipoDocumento: "Currículum" para Modalidad "Tesis"
  - etapa = Etapa 2 (Defensa)

¿Cuál es correcta?
```

---

### 5. ⚠️ Documentos filtrados por `postulacion.etapa_actual`

**Severidad:** 🟡 **MEDIA**

**Ubicación:** [`Documentos.jsx`](frontend/src/pages/Documentos.jsx#L130-145)

```javascript
// Cuando seleccionas postulación, se extrae su etapa_actual
const etapaId = selectedPostulacion?.etapa_actual;
// Y se consulta: MODALIDAD_TIPOS_DOCUMENTO(modalidad)?etapa=etapa
```

**Problema:**
- El filtrado es **implícito y automático**
- Si cambias `postulacion.etapa_actual` en admin, los documentos visibles **CAMBIAN**
- Usuario no tiene opción de ver documentos de otras etapas
- ¿Qué pasa si necesita subir documento de una etapa anterior que no completó?

**Preguntas:**
- ¿Debería haber opción de filtrar por etapa manualmente?
- ¿Debería mostrar documentos de todas las etapas?
- ¿Debería ser en cascada según el avance de etapas?

---

### 6. ⚠️ Falta de endpoint para filtrar Etapas por Modalidad

**Severidad:** 🟡 **MEDIA**

**Ubicación:** [`modalidades/views.py`](modalidades/views.py) - `EtapaViewSet`

```python
class EtapaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Etapa.objects.select_related('modalidad').all()
    # ...
    # NO hay filtro por modalidad en el ViewSet
```

**Actual:**
```
GET /api/etapas/
Response: TODAS las etapas de todas las modalidades
```

**Debería ser:**
```
GET /api/etapas/?modalidad=3
Response: Solo etapas de modalidad 3
```

**Solución sugerida:**
```python
# En modalidades/views.py
class EtapaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Etapa.objects.select_related('modalidad').all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['modalidad']  # ← AGREGAR
```

---

## 📊 Matriz de Filtrado

| Página | Elemento | Filtrado Por | ¿Funciona? | ¿Dinámico? |
|--------|----------|-------------|----------|-----------|
| **Postulaciones** | Etapas | Nada | ❌ | ❌ |
| **Postulaciones** | Modalidades | Nada | ✅ | ✅ |
| **Documentos** | Tipos Documento | Modalidad + Etapa | ✅ | ✅ |
| **Documentos** | Postulaciones | Nada | ✅ | ✅ |

---

## Recomendaciones

### 🔴 CRÍTICAS (Implementar ASAP)

1. **Corregir import de `EtapaSerializer`**
   - Archivo: [`postulantes/views.py`](postulantes/views.py#L13)
   - Cambiar: `from .serializers import EtapaSerializer`
   - Cambiar a: `from modalidades.serializers import EtapaSerializer`
   - Severidad: 🔴 Causa error en runtime

2. **Resolver redundancia en relaciones de Etapa**
   - Decidir si `TipoDocumento.etapa` es necesario
   - O si usar solo `ModalidadTipoDocumento.etapa`
   - Crear migración para limpiar datos

### 🟡 MEJORAS (Implementar pronto)

3. **Agregar filtro dinámico de Etapas**
   - En [`Postulaciones.jsx`](frontend/src/pages/Postulaciones.jsx)
   - Cuando selecciona modalidad, cargar solo sus etapas
   - Beneficio: Mejor UX, menos datos transferidos

4. **Agregar filtro de Etapas en API**
   - En [`modalidades/views.py`](modalidades/views.py)
   - Permitir: `GET /api/etapas/?modalidad=3`
   - Beneficio: Reutilizable por otras páginas

5. **Aclarar si `etapa_actual` es obligatorio**
   - Revisar lógica de negocio
   - Si es obligatorio: `null=False, blank=False`
   - Si es opcional: Documenter cuándo es null

### 🟢 MEJORAS FUTURAS

6. **Evaluar componente de filtrado de Documentos**
   - ¿Mostrar solo documentos de la etapa actual?
   - ¿O todas las etapas completadas?
   - ¿O permitir selección manual?

7. **Crear vista de Documentos por Etapa**
   - Mostrar cronológicamente
   - Ver requisitos completados vs pendientes

---

## Resumen Técnico

```yaml
Estructura:
  - Etapa: Pertenece a Modalidad (1:N)
  - Postulacion: Tiene etapa_actual (1:1 nullable)
  - Documento: Asociado a TipoDocumento
  - TipoDocumento: Relación débil a Etapa
  - ModalidadTipoDocumento: Relación fuerte (Modalidad + Etapa + Documento)

Validaciones:
  - ✅ etapa_actual.modalidad == postulacion.modalidad (backend)
  - ✅ Unicidad: (postulante, año, semestre)
  - ✅ Unicidad: (modalidad, tipo_documento, etapa)
  - ⚠️ No hay filtro en frontend al cargar etapas

Flujos:
  - Nueva Postulación: Crea Postulacion con etapa_actual nullable
  - Subir Documentos: Filtra por modalidad + etapa_actual
  - Cambiar Etapa: Endpoint `/avanzar-etapa/` disponible

Inconsistencias Críticas:
  - Import incorrecto de EtapaSerializer
  - Carga de TODAS las etapas sin filtro
  - Redundancia en relaciones a Etapa
```

---

## 📁 Archivos Afectados

### Backend
- [`postulantes/models.py`](postulantes/models.py) - Define Postulacion
- [`postulantes/serializers.py`](postulantes/serializers.py) - Valida etapa
- [`postulantes/views.py`](postulantes/views.py) - ❌ Import incorrecto
- [`modalidades/models.py`](modalidades/models.py) - Define Etapa
- [`modalidades/views.py`](modalidades/views.py) - Endpoint tipos-documento
- [`documentos/models.py`](documentos/models.py) - Define ModalidadTipoDocumento

### Frontend
- [`frontend/src/pages/Postulaciones.jsx`](frontend/src/pages/Postulaciones.jsx) - ⚠️ Carga sin filtro
- [`frontend/src/pages/Documentos.jsx`](frontend/src/pages/Documentos.jsx) - ✅ Filtrado correcto
- [`frontend/src/constants/api.js`](frontend/src/constants/api.js) - Endpoints

---

**Análisis completado:** 2026-07-05  
**Archivos totales analizados:** 10  
**Inconsistencias encontradas:** 6  
**Críticas:** 1 | Medianas: 5
