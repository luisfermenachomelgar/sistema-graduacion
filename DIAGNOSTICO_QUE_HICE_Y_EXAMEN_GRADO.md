# 🔍 Diagnóstico: Lo Que Hice y Cómo Extrapolarlo a Examen de Grado

**Fecha:** 2026-07-05  
**Objetivo:** Explicar la implementación de sincronización de etapas y cómo aplicarla a Examen de Grado

---

## 📋 PARTE 1: QUÉ HICE EN DOCUMENTOS.JSX

### El Problema Que Solucioné

**Situación Inicial:**
- Usuario entra en "Subir Documentos"
- Selecciona una postulación
- Sistema filtra documentos por etapa automáticamente
- **PERO:** El usuario NO VE QUÉ ETAPA TIENE ASIGNADA

```
Usuario selecciona postulación
    ↓ (procesamiento invisible)
Documentos filtrados
Usuario confundido: "¿Qué documentos necesito?"
```

### Cómo Solucioné: 5 Pasos Clave

#### **PASO 1: Cargar los Datos Necesarios**

```jsx
const [etapaActualNombre, setEtapaActualNombre] = useState('');
const [etapas, setEtapas] = useState([]);
```

**¿Qué?** Agregué dos variables de estado para almacenar:
- `etapaActualNombre` = nombre de la etapa (ej: "Defensa")
- `etapas` = lista completa de etapas desde el backend

**¿Por qué?** Necesitaba:
1. La lista de etapas para poder buscar el nombre por ID
2. Una variable para mostrar el nombre en el formulario

**Analogía:** Como tener un libro de códigos para traducir ID → Nombre

---

#### **PASO 2: Cargar las Etapas del Backend**

```jsx
const fetchDropdownData = async () => {
  const [tiposRes, postRes, etapaRes] = await Promise.all([
    // ... tipos documento ...
    // ... postulaciones ...
    api.getAll(API_CONFIG.ENDPOINTS.ETAPAS, {}, { skipGlobalLoader: true }),
  ]);
  
  if (etapaRes.success) {
    setEtapas(etapasData);  // Guardar lista de etapas
  }
};
```

**¿Qué?** Llamar al API para obtener todas las etapas disponibles

**¿Por qué?** Sin la lista de etapas, no puedo traducir `etapa_id=2` a `nombre="Defensa"`

**Analogía:** Descargar el diccionario antes de intentar una traducción

---

#### **PASO 3: Extraer la Etapa Actual (Momento Clave)**

```jsx
const handleInputChange = async (e) => {
  if (name === 'postulacion' && newValue) {
    const selectedPostulacion = postulaciones.find((p) => p.id === newValue);
    const etapaId = selectedPostulacion?.etapa_actual;  // ← EXTRAER ID
    
    // Buscar el nombre en la lista de etapas
    if (etapaId) {
      const etapaSeleccionada = etapas.find((e) => e.id === etapaId);
      setEtapaActualNombre(etapaSeleccionada?.nombre || '');  // ← GUARDAR NOMBRE
    }
  }
};
```

**¿Qué?** Cuando el usuario selecciona una postulación:
1. Extraigo su `etapa_actual` (es un ID)
2. Busco ese ID en la lista de etapas
3. Guardo el nombre

**Flujo:**
```
Postulación {id: 1, etapa_actual: 2}
    ↓
Extraer etapa_actual = 2
    ↓
Buscar en lista de etapas donde id = 2
    ↓
Encontrar {id: 2, nombre: "Defensa"}
    ↓
Guardar "Defensa" en etapaActualNombre
```

**Analogía:** Es como buscar en un diccionario: "Dame el significado de la palabra con ID 2"

---

#### **PASO 4: Mostrar la Etapa Visualmente**

```jsx
<FormField
  label="Etapa Actual"
  name="etapa_actual"
  type="text"
  value={etapaActualNombre}  // Mostrar el nombre
  readOnly={true}             // No se puede editar
  placeholder="Sincronizada automáticamente"
/>
```

**¿Qué?** Agregar un campo en el formulario que muestre la etapa

**¿Por qué?** 
- El usuario VE cuál es su etapa actual
- No puede editarla (solo lectura)
- Se actualiza automáticamente

**Resultado Visual:**
```
┌─────────────────────┐
│ Postulación [Juan]  │
│ Etapa Actual        │
│ [Defensa] ← Visible│
└─────────────────────┘
```

---

#### **PASO 5: Sincronizar en tiempo real (useEffect)**

```jsx
useEffect(() => {
  if (!formData.postulacion) {
    setTiposDocumentoFiltrados([]);
    setEtapaActualNombre('');
    return;
  }

  const selectedPostulacion = postulaciones.find((p) => p.id === formData.postulacion);
  const etapaId = selectedPostulacion?.etapa_actual;

  if (etapaId) {
    const etapaSeleccionada = etapas.find((e) => e.id === etapaId);
    setEtapaActualNombre(etapaSeleccionada?.nombre || '');
  }
}, [formData.postulacion, postulaciones, etapas]);
```

**¿Qué?** Un efecto que se ejecuta automáticamente cuando cambian:
- La postulación seleccionada
- La lista de postulaciones
- La lista de etapas

**¿Por qué?** Si la postulación cambia, la etapa debe actualizarse automáticamente

**Analogía:** Un reloj que se ajusta automáticamente al cambiar de zona horaria

---

#### **PASO 6 (Backend): Incluir etapa_nombre en respuestas**

```python
# documentos/serializers.py

class DocumentoPostulacionListSerializer(serializers.ModelSerializer):
    etapa_nombre = serializers.CharField(
        source='postulacion.etapa_actual.nombre',  # ← Obtener del objeto relacionado
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = DocumentoPostulacion
        fields = [..., 'etapa_nombre', ...]
```

**¿Qué?** Hacer que el backend envíe el nombre de la etapa en respuestas

**¿Por qué?** Para que la tabla pueda mostrar la etapa de cada documento

**Flujo de Datos:**
```
Backend GET /documentos/
    ↓
Para cada documento, obtener:
├── documento.postulacion.etapa_actual.id (el ID)
└── documento.postulacion.etapa_actual.nombre (el nombre)
    ↓
API retorna: {"etapa_nombre": "Defensa", ...}
    ↓
Frontend muestra en tabla: [Defensa] ✅
```

---

## 📊 Resumen Visual: Lo Que Hice

```
ANTES: Etapas Ocultas
┌──────────────────────┐
│ Postulación [Juan]   │
│ Tipo Doc [Propuesta] │
│ Etapa: [???]         │ ← Usuario confundido
└──────────────────────┘

DESPUÉS: Etapas Visibles y Sincronizadas
┌──────────────────────┐
│ Postulación [Juan]   │
│ Etapa [Defensa] ✅   │ ← VISIBLE
│ Tipo Doc [Propuesta] │ ← Filtrado por esa etapa
└──────────────────────┘
        ↓
┌──────────────────┐
│ Documentos:      │
├──────────────────┤
│ Doc 1 | Defensa  │ ← ETAPA VISIBLE
│ Doc 2 | Defensa  │ ← ETAPA VISIBLE
└──────────────────┘
```

---

---

## 🎯 PARTE 2: APLICAR ESTO A EXAMEN DE GRADO

### Pregunta: ¿Qué es "Examen de Grado" en tu Sistema?

Tengo dos escenarios:

#### **Escenario A: "Examen de Grado" es una Modalidad más**

Si "Examen de Grado" es solo otra modalidad como "Tesis" o "Trabajo Dirigido":

```
MODALIDADES EXISTENTES:
├── Tesis
├── Trabajo Dirigido
├── Seminario
└── Examen de Grado ← Nueva modalidad
```

En este caso, **YA FUNCIONA AUTOMÁTICAMENTE** porque:
1. Documentos.jsx ya sincroniza etapas de cualquier modalidad
2. Si creo una modalidad "Examen de Grado" con etapas
3. El sistema automáticamente las mostrará

---

#### **Escenario B: "Examen de Grado" es una Sección Separada**

Si "Examen de Grado" es una funcionalidad diferente a Documentos:

```
ESTRUCTURA PROPUESTA:
├── Postulaciones (Tesis, Trabajo Dirigido, etc.)
├── Documentos (archivos de postulaciones)
└── Examen de Grado ← Sección independiente
    ├── Crear Examen
    ├── Calificaciones
    ├── Documentos del Examen (?)
```

En este caso, necesitaría hacer lo mismo que hice en Documentos pero en una nueva página.

---

### Opción A: Examen de Grado como Modalidad

Si es este caso, **aquí te muestro cómo verificarlo:**

```bash
# En Django shell o admin
Modalidad.objects.all()

# Debería devolver algo como:
# [<Modalidad: Tesis>, <Modalidad: Trabajo Dirigido>, <Modalidad: Examen de Grado>]
```

Si no existe "Examen de Grado", puedo crear:
```python
from modalidades.models import Modalidad, Etapa

# Crear modalidad
examen_grado = Modalidad.objects.create(
    nombre="Examen de Grado",
    descripcion="Modalidad de evaluación mediante examen",
    activa=True
)

# Crear etapas (ejemplo)
Etapa.objects.create(modalidad=examen_grado, nombre="Inscripción", orden=1)
Etapa.objects.create(modalidad=examen_grado, nombre="Revisión de Requisitos", orden=2)
Etapa.objects.create(modalidad=examen_grado, nombre="Examen Oral", orden=3)
Etapa.objects.create(modalidad=examen_grado, nombre="Aprobado", orden=4)
```

---

### Opción B: Examen de Grado como Sección Separada

Si necesita ser independiente, seguiría el **MISMO PATRÓN** que Documentos:

#### **Nuevo archivo: [ExamenGrado.jsx](frontend/src/pages/ExamenGrado.jsx)**

```jsx
// Paso 1: Estados
const [etapaActualNombre, setEtapaActualNombre] = useState('');
const [etapas, setEtapas] = useState([]);
const [postulaciones, setPostulaciones] = useState([]);

// Paso 2: Cargar datos
const fetchData = async () => {
  const [postRes, etapaRes] = await Promise.all([
    api.getAll(API_CONFIG.ENDPOINTS.POSTULACIONES),
    api.getAll(API_CONFIG.ENDPOINTS.ETAPAS),
  ]);
  setPostulaciones(postRes.data);
  setEtapas(etapaRes.data);
};

// Paso 3: Extraer etapa al seleccionar postulación
const handlePostulacionChange = (postulacionId) => {
  const post = postulaciones.find(p => p.id === postulacionId);
  const etapa = etapas.find(e => e.id === post.etapa_actual);
  setEtapaActualNombre(etapa?.nombre || '');
};

// Paso 4: Mostrar en formulario
<FormField
  label="Etapa Actual"
  value={etapaActualNombre}
  readOnly={true}
/>

// Paso 5: useEffect para sincronización
useEffect(() => {
  handlePostulacionChange(formData.postulacion);
}, [formData.postulacion, etapas]);
```

---

## 🔗 Comparación: Documentos vs Examen de Grado

| Elemento | Documentos | Examen de Grado |
|----------|-----------|-----------------|
| **Página** | [Documentos.jsx](frontend/src/pages/Documentos.jsx) | ExamenGrado.jsx (nuevo) |
| **¿Qué se carga?** | Documentos de postulaciones | Calificaciones/datos del examen |
| **Relación con etapas** | Documentos filtrados por etapa | Calificaciones filtradas por etapa |
| **Campo a sincronizar** | Etapa de la postulación | Etapa de la postulación |
| **Sincronización** | `postulacion.etapa_actual` | `postulacion.etapa_actual` |

---

## 📊 Diagrama: Cómo Funciona la Sincronización

```
DATABASE
├── POSTULACION (id=1)
│   ├── modalidad_id: 1 (Tesis)
│   ├── etapa_actual_id: 2
│   └── estado: en_revision
│
├── ETAPA (id=2)
│   ├── nombre: "Defensa"
│   ├── modalidad_id: 1
│   └── orden: 2
│
└── DOCUMENTOPOSTULACION (id=10)
    ├── postulacion_id: 1
    └── tipo_documento_id: 5

FRONTEND FLOW:
User selecciona postulación 1
    ↓
JavaScript busca en array etapas:
    find(e => e.id === 2)  ← Buscar etapa con id=2
    ↓
Encuentra: {id: 2, nombre: "Defensa"}
    ↓
Muestra en input: "Defensa"
    ↓
API carga documentos con etapa_nombre incluido
    ↓
Tabla muestra [Defensa] para cada documento
```

---

## 🎯 Conclusión: Qué Hiciste y Cómo Extrapolarlo

### Lo que hice:
1. ✅ Cargar etapas del backend
2. ✅ Extraer etapa_actual de la postulación seleccionada
3. ✅ Buscar el nombre de la etapa en la lista
4. ✅ Mostrar el nombre visualmente (read-only)
5. ✅ Sincronizar automáticamente con useEffect
6. ✅ Hacer que el backend envíe etapa_nombre en respuestas
7. ✅ Mostrar etapa en tabla con badge visual

### Cómo aplicarlo a Examen de Grado:
- **Si es modalidad:** Ya funciona automáticamente (crear la modalidad + etapas)
- **Si es sección separada:** Repetir el mismo patrón en una nueva página

---

## 🚀 Verificación: ¿Qué Necesitas Saber?

Para decidir cómo proceder, necesito que me confirmes:

1. **¿Examen de Grado existe en tu BD?** 
   - ¿Es una modalidad actual?
   - ¿Tiene etapas definidas?

2. **¿Cómo se usa Examen de Grado?**
   - ¿Los estudiantes crean postulaciones como si fuera una modalidad?
   - ¿O es un proceso completamente diferente?

3. **¿Qué documentos necesita sincronizar?**
   - ¿Los mismos tipos de documento que otras modalidades?
   - ¿Documentos diferentes?

Responde estas preguntas y te creo el plan exacto para sincronizar Examen de Grado.

---

**Status:** ✅ Diagnóstico Completado - Esperando tu respuesta para Examen de Grado
