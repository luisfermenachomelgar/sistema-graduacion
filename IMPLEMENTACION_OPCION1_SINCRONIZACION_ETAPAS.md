# 📋 Implementación: Sincronización de Etapas Opción 1 ✅

**Fecha:** 2026-07-05  
**Estado:** ✅ COMPLETADO  
**Opción Implementada:** Mostrar Etapa Actual como read-only en Documentos

---

## 🎯 Cambios Realizados

### **Frontend: [Documentos.jsx](frontend/src/pages/Documentos.jsx)**

#### 1️⃣ Agregar Estados (línea 62-63)
```jsx
const [etapaActualNombre, setEtapaActualNombre] = useState('');
const [etapas, setEtapas] = useState([]);
```

**Propósito:** Almacenar:
- `etapaActualNombre` → Nombre de la etapa sincronizada
- `etapas` → Lista de todas las etapas disponibles

---

#### 2️⃣ Cargar Etapas en Dropdown (línea 87-108)
```jsx
const fetchDropdownData = async () => {
  try {
    const [tiposRes, postRes, etapaRes] = await Promise.all([
      // ... tipos documento ...
      // ... postulaciones ...
      api.getAll(API_CONFIG.ENDPOINTS.ETAPAS, {}, { skipGlobalLoader: true }),
    ]);
    
    if (etapaRes.success) {
      const etapasData = Array.isArray(etapaRes.data) ? ... : [];
      setEtapas(etapasData);
    }
  }
};
```

**Propósito:** Cargar la lista de etapas desde el backend para sincronización

---

#### 3️⃣ Sincronizar Etapa en Modo Manual (línea 180-195)
```jsx
if (name === 'postulacion' && newValue) {
  const selectedPostulacion = postulaciones.find((p) => p.id === newValue);
  
  // Extraer y mostrar el nombre de la etapa actual
  if (etapaId) {
    const etapaSeleccionada = etapas.find((e) => e.id === etapaId);
    setEtapaActualNombre(etapaSeleccionada?.nombre || '');
  } else {
    setEtapaActualNombre('');
  }
}
```

**Propósito:** Cuando el usuario selecciona una postulación, extraer automáticamente su etapa actual

---

#### 4️⃣ Sincronizar Etapa en useEffect (línea 283-303)
```jsx
useEffect(() => {
  const loadFilteredTipos = async () => {
    if (!formData.postulacion) {
      setTiposDocumentoFiltrados([]);
      setEtapaActualNombre('');
      return;
    }

    const etapaId = selectedPostulacion?.etapa_actual;
    
    // Extraer y mostrar el nombre de la etapa
    if (etapaId) {
      const etapaSeleccionada = etapas.find((e) => e.id === etapaId);
      setEtapaActualNombre(etapaSeleccionada?.nombre || '');
    } else {
      setEtapaActualNombre('');
    }
  };
  
  loadFilteredTipos();
}, [formData.postulacion, postulaciones, etapas]);
```

**Propósito:** Sincronizar automáticamente cuando cambian dependencias

---

#### 5️⃣ Limpiar Estado al Cerrar Modal (línea 78-84)
```jsx
useEffect(() => {
  // Limpiar estado cuando se cierre el modal
  if (!isOpen) {
    setEtapaActualNombre('');
  }
}, [isOpen]);
```

**Propósito:** Reset del estado cuando se cierra el formulario

---

#### 6️⃣ Mostrar Etapa en Modal como Read-Only (línea 478-486)
```jsx
<FormField
  label="Etapa Actual"
  name="etapa_actual"
  type="text"
  value={etapaActualNombre}
  readOnly={true}
  placeholder="Sincronizada automáticamente"
  helperText="Etapa sincronizada desde la postulación seleccionada"
  className="md:col-span-1"
/>
```

**Propósito:** 
- ✅ Mostrar visualmente la etapa actual
- ✅ Campo read-only (no se puede editar)
- ✅ Se actualiza automáticamente

**Resultado Visual:**
```
┌─────────────────────────────────────┐
│ Postulación *    [Usuario — Tesis▼] │
│ Etapa Actual     [Defensa]          │ ← READ-ONLY, sincronizada
│ Tipo de Doc *    [Propuesta▼]       │ ← Filtrado por etapa
└─────────────────────────────────────┘
```

---

#### 7️⃣ Agregar Etapa a Tabla (línea 393-401)
```jsx
{
  key: 'etapa_nombre',
  label: 'Etapa',
  sortable: true,
  render: (value) => (
    <span className="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
      {value || '-'}
    </span>
  ),
},
```

**Propósito:** Mostrar la etapa en la tabla con badge visual

---

### **Backend: [documentos/serializers.py](documentos/serializers.py)**

#### 1️⃣ Actualizar DocumentoPostulacionListSerializer (línea 46-67)
```python
class DocumentoPostulacionListSerializer(serializers.ModelSerializer):
    # ... campos existentes ...
    etapa_nombre = serializers.CharField(
        source='postulacion.etapa_actual.nombre', read_only=True, allow_null=True
    )
    
    class Meta:
        model = DocumentoPostulacion
        fields = [
            # ... otros campos ...
            'etapa_nombre',  # ← NUEVO
            # ...
        ]
```

**Propósito:** Incluir `etapa_nombre` en respuestas del API (lista de documentos)

---

#### 2️⃣ Actualizar DocumentoPostulacionDetailSerializer (línea 70-100)
```python
class DocumentoPostulacionDetailSerializer(serializers.ModelSerializer):
    # ... campos existentes ...
    etapa_nombre = serializers.CharField(
        source='postulacion.etapa_actual.nombre', read_only=True, allow_null=True
    )
    
    class Meta:
        model = DocumentoPostulacion
        fields = [
            # ... otros campos ...
            'etapa_nombre',  # ← NUEVO
            # ...
        ]
```

**Propósito:** Incluir `etapa_nombre` en respuestas del API (detalle de documentos)

---

## ✅ Resultado Final

### **Antes (Problema):**
```
Usuario selecciona Postulación "Juan — Tesis"
    ↓
[Etapa oculta internamente]
    ↓
Sistema filtra documentos automáticamente
    ↓
Usuario: "¿Qué documentos necesito?" 
Sistema: Te muestra documentos pero NO SABES QUÉ ETAPA ES
```

### **Después (Solución):**
```
Usuario selecciona Postulación "Juan — Tesis"
    ↓
Etapa Actual: [Defensa]  ← ✅ VISIBLE, READ-ONLY
    ↓
Sistema filtra documentos por esa etapa
    ↓
Tabla muestra documentos CON etapa [Defensa]  ← ✅ VISIBLE
    ↓
Usuario: "¿Qué documentos necesito?" 
Sistema: "Necesitas documentos de la etapa Defensa, aquí están:"
```

---

## 🔄 Flujo de Sincronización

```
POSTULACION en DB
├── id: 1
├── modalidad: Tesis
└── etapa_actual: 2 (Defensa)
        ↓
Frontend carga lista de POSTULACIONES
        ↓
Usuario selecciona postulación
        ↓
handleInputChange EXTRAE:
├── etapa_actual = 2
└── busca en lista de etapas → nombre = "Defensa"
        ↓
Muestra en FormField (read-only): "Defensa"
        ↓
Carga documentos filtrados por etapa 2
        ↓
Tabla muestra etapa_nombre: "Defensa" ✅
```

---

## 📊 Comparación Visual

### Modal - Antes vs Después

**ANTES:**
```
┌──────────────────────────┐
│ Postulación [Juan-Tesis] │
│ Tipo Doc [Propuesta]     │
│ Estado [pendiente]       │
│ Etapa: [NO VISIBLE] ❌   │
└──────────────────────────┘
```

**DESPUÉS:**
```
┌──────────────────────────┐
│ Postulación [Juan-Tesis] │
│ Etapa Actual [Defensa] ✅│  ← READ-ONLY
│ Tipo Doc [Propuesta]     │  ← Filtrado por etapa
│ Estado [pendiente]       │
└──────────────────────────┘
```

---

### Tabla - Antes vs Después

**ANTES:**
```
Tipo Doc  | Postulación  | Estado    | Comentario
Propuesta | Juan - Tesis | Pendiente | -
Defensa   | Juan - Tesis | Aprobado  | -
```

**DESPUÉS:**
```
Tipo Doc  | Postulación  | Etapa     | Estado    | Comentario
Propuesta | Juan - Tesis | Defensa ✅| Pendiente | -
Defensa   | Juan - Tesis | Defensa ✅| Aprobado  | -
```

---

## 🔗 Sincronización de Datos

### Flujo Completo:

1. **Admin crea Postulación** en `Postulaciones.jsx`
   - Selecciona: `Modalidad = Tesis`
   - Selecciona: `Etapa Actual = Defensa`
   - Guarda: `postulacion.etapa_actual = 2`

2. **Usuario va a Subir Documentos**
   - Selecciona: `Postulación = Juan Tesis`
   - Sistema EXTRAE: `postulacion.etapa_actual = 2`
   - Sistema BUSCA en etapas: `id=2` → `nombre="Defensa"`
   - **MUESTRA:** `Etapa Actual: [Defensa]` ✅
   - Sistema FILTRA: `documentos donde etapa=2`
   - **MUESTRA:** Solo documentos de Defensa

3. **API Retorna Documentos**
   - Backend incluye: `etapa_nombre: "Defensa"`
   - Tabla muestra etapa en badge: `[Defensa]` ✅

---

## 📦 Archivos Modificados

| Archivo | Cambios | Líneas |
|---------|---------|--------|
| [frontend/src/pages/Documentos.jsx](frontend/src/pages/Documentos.jsx) | 7 cambios | 62, 78, 87, 180, 283, 478, 393 |
| [documentos/serializers.py](documentos/serializers.py) | 2 cambios | 46, 70 |

---

## 🧪 Validación

### ✅ Checklist:
- [x] Estados agregados correctamente
- [x] Etapas cargadas en fetchDropdownData
- [x] Sincronización en handleInputChange
- [x] Sincronización en useEffect
- [x] Estado se limpia al cerrar modal
- [x] Campo read-only en modal
- [x] Etapa visible en tabla
- [x] Backend retorna etapa_nombre
- [x] Serializers actualizados

---

## 🚀 Próximos Pasos (Opcionales)

1. **Agregar histórico de etapas:** Mostrar por qué cambió de etapa
2. **Notificaciones:** Avisar cuando se cambia de etapa
3. **Auditoría:** Registrar quién cambió la etapa y cuándo
4. **Dashboard:** Gráfico de avance por etapas

---

## 📝 Notas Técnicas

### Sincronización Automática:
- No requiere interacción del usuario
- Se ejecuta automáticamente al seleccionar postulación
- Se actualiza si la postulación cambia en tiempo real

### Campo Read-Only:
- No se puede editar desde Documentos
- Solo se puede cambiar desde Postulaciones
- Evita inconsistencias de datos

### Compatibilidad:
- ✅ Compatible con edición de documentos existentes
- ✅ Compatible con null etapas (postulaciones sin etapa)
- ✅ Compatible con múltiples etapas por modalidad

---

**Estado:** 🟢 Implementación Completada y Lista para Producción
