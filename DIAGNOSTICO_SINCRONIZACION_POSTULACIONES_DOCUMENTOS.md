# 🔍 Diagnóstico: Sincronización de Etapas en Postulaciones y Documentos

**Fecha:** 2026-07-05  
**Estado:** ⚠️ INCONSISTENCIA ENCONTRADA

---

## 📋 Resumen Ejecutivo

El sistema de **postulaciones** y **documentos** NO está completamente sincronizado en cuanto a la presentación de etapas. El problema es:

| Sección | Etapas Visibles | Filtrado | Sincronización |
|---------|-----------------|----------|-----------------|
| **Nueva Postulación** | ✅ Sí (dropdown) | ✅ Por modalidad | Manual (usuario elige) |
| **Subir Documentos** | ❌ **NO** (ocultas) | ✅ Por modalidad + etapa | Automático (de postulación) |

---

## 🎯 Problema Principal

### Actual en Documentos.jsx:
```
Usuario selecciona Postulación 
    → Sistema extrae modalidad + etapa_actual
    → Sistema OCULTA las etapas
    → Documentos se filtran automáticamente
```

### Deseado (según usuario):
```
Usuario selecciona Postulación
    → Sistema MUESTRA las etapas disponibles
    → Usuario VE qué etapa le corresponde
    → Documentos están filtrados por esa etapa (igual que ahora)
```

---

## 🔧 Análisis del Código Actual

### 1. En **Postulaciones.jsx** (líneas 575-588)

```jsx
<FormField
  label="Etapa actual"
  name="etapa_actual"
  type="select"
  value={formData.etapa_actual}
  onChange={handleInputChange}
  options={
    formData.modalidad
      ? etapas
          .filter((etapa) => formData.modalidad && etapa.modalidad === formData.modalidad)
          .map((etapa) => ({ id: etapa.id, label: etapa.nombre }))
      : []
  }
  placeholder="Sin etapa actual"
  helperText="Opcional. Si no se selecciona, la postulación queda sin etapa asignada."
  className="sm:col-span-2"
/>
```

**✅ Funciona correctamente:**
- Filtra etapas por modalidad seleccionada
- Usuario VE las opciones disponibles
- Usuario PUEDE cambiar la etapa

---

### 2. En **Documentos.jsx** (líneas 140-152)

```jsx
const getTiposDocumentoFiltrados = async (modalidadId, etapaId = null) => {
  const modalidadTipos = await fetchTiposDocumentoPorModalidad(modalidadId, etapaId);
  // ... filtrado de documentos ...
  // Las etapas se usan pero NO se muestran al usuario
};
```

**❌ PROBLEMA AQUÍ:**
- Las etapas se FILTRAN internamente (línea 97: `etapa: etapaId`)
- Pero NO se muestran en el formulario
- Usuario NO SABE qué etapa tiene asignada
- Usuario NO PUEDE cambiar la etapa desde Documentos

---

## 📊 Flujo de Datos Actual

### Creación de Postulación:
```
1. Admin crea postulación → Selecciona modalidad
2. Admin selecciona etapa_actual (visible en dropdown)
3. Sistema guarda: postulacion.etapa_actual = Etapa(id=2, nombre="Defensa")
```

### Al Subir Documentos:
```
1. Usuario selecciona postulacion
2. Sistema EXTRAE: etapa_actual = postulacion.etapa_actual
3. Sistema LLAMA: getTiposDocumentoPorModalidad(modalidad, etapa)
   → API retorna solo documentos de esa etapa
4. Usuario VE: solo documentos de esa etapa (pero NO VE cuál es)
```

---

## 🎨 Comparación con Postulaciones

### Postulaciones - Visible:
```
┌─────────────────────────────┐
│ Formulario Nueva Postulación│
├─────────────────────────────┤
│ Postulante:  [dropdown]     │
│ Modalidad:   [Tesis]        │
│ Año:         [2024]         │
│ Semestre:    [1]            │
├─────────────────────────────┤
│ Título:      [texto]        │
│ Tutor:       [texto]        │
├─────────────────────────────┤
│ Estado:      [borrador]     │
├─────────────────────────────┤
│ Etapa Actual: [Defensa] ✅  │ ← VISIBLE
└─────────────────────────────┘
```

### Documentos - Oculto:
```
┌──────────────────────────────┐
│ Formulario Nuevo Documento   │
├──────────────────────────────┤
│ Postulación: [Usuario — Tesis│ ← Selecciona aquí
│ Tipo Doc:    [Propuesta] ✅  │ ← Se filtra automáticamente
│                              │    por la etapa oculta
│ Estado:      [pendiente]     │
│                              │
│ Etapa Actual: [NO VISIBLE] ❌│ ← PROBLEMA
└──────────────────────────────┘
```

---

## 🔴 Inconsistencias Identificadas

### #1: Etapas NO VISIBLES en Documentos
- **Ubicación:** [Documentos.jsx](frontend/src/pages/Documentos.jsx) líneas 440-448
- **Problema:** Modalidad se muestra pero Etapa se usa internamente sin mostrar
- **Impacto:** Usuario no sabe qué documentos necesita, solo ve lo que el sistema permite

### #2: Falta control de etapa en Documentos
- **Ubicación:** [Documentos.jsx](frontend/src/pages/Documentos.jsx) Modal
- **Problema:** No hay campo `etapa` en el formulario de Documentos
- **Impacto:** No se pueden cambiar etapas desde Documentos, solo desde Postulaciones

### #3: Flujo inconsistente
- **En Postulaciones:** User → elige modalidad → ve etapas → elige etapa
- **En Documentos:** System → oculta etapa → filtra documentos automáticamente

---

## ✅ Propuesta de Solución

### Opción 1: Mostrar Etapa Actual (Recomendado)
**Añadir campo de lectura (read-only) en Documentos.jsx**

```jsx
<FormField
  label="Etapa Actual"
  name="etapa_actual"
  type="select"
  value={formData.etapa_actual || ''}
  readOnly={true}  // ← Solo lectura
  options={etapasDisponibles.map(e => ({ id: e.id, label: e.nombre }))}
  helperText="Etapa sincronizada de la postulación seleccionada"
/>
```

**Ventajas:**
- ✅ Usuario VE qué etapa tiene asignada
- ✅ Sincronización clara y visible
- ✅ No cambia la lógica actual
- ✅ Mantiene coherencia con Postulaciones

---

### Opción 2: Permitir Cambiar Etapa desde Documentos
**Permitir editar etapa_actual en Documentos.jsx**

```jsx
// En handleInputChange
if (name === 'etapa_actual') {
  // Llamar API para cambiar etapa_actual de la postulación
  await api.patch(`/postulaciones/${formData.postulacion}/`, {
    etapa_actual: value
  });
}
```

**Ventajas:**
- ✅ Mayor flexibilidad
- ✅ Usuario puede avanzar etapas desde Documentos
- ❌ Mayor complejidad
- ❌ Podrían inconsistencias si se edita desde ambos lados

---

### Opción 3: Mostrar Etapas en vistazo previo
**Mostrar etapa en la lista de documentos**

```jsx
// En columns, añadir:
{
  key: 'etapa_nombre',
  label: 'Etapa',
  render: (value, row) => row.etapa_nombre || '-'
}
```

---

## 📂 Archivos Involucrados

| Archivo | Línea | Problema | Severidad |
|---------|-------|----------|-----------|
| [frontend/src/pages/Documentos.jsx](frontend/src/pages/Documentos.jsx) | 440-450 | Modal sin campo de etapa | 🔴 Alta |
| [frontend/src/pages/Postulaciones.jsx](frontend/src/pages/Postulaciones.jsx) | 575-588 | Funciona correctamente | ✅ OK |
| [postulantes/serializers.py](postulantes/serializers.py) | 18 | Import redundante de EtapaSerializer | 🟡 Media |
| [modalidades/serializers.py](modalidades/serializers.py) | 6 | Define EtapaSerializer correctamente | ✅ OK |

---

## 🔗 Relaciones de Datos

```
MODALIDAD (Tesis, Trabajo Dirigido, Seminario, etc.)
    ↓
ETAPA (Perfil, Defensa, Titulación)
    ↓
POSTULACION (postulante + modalidad + etapa_actual)
    ↓
DOCUMENTOPOSTULACION (archivos que sube el usuario)
```

**Sincronización esperada:**
1. Postulación tiene `etapa_actual` ← Usuario la define en Postulaciones
2. Al crear Documento, se EXTRAE `etapa_actual` de la postulación
3. Se FILTRAN documentos por esa etapa
4. **FALTA:** Mostrar esa etapa en la UI de Documentos

---

## 🎯 Recomendación

**Implementar Opción 1 (Mostrar Etapa Actual como read-only)**

1. ✅ Mínimo impacto en código existente
2. ✅ Máxima claridad para el usuario
3. ✅ Sincronización visible
4. ✅ Consistencia con Postulaciones
5. ✅ No requiere cambios en backend

**Pasos:**
1. Modificar [Documentos.jsx](frontend/src/pages/Documentos.jsx)
2. Extraer etapa_actual cuando se selecciona postulación
3. Mostrar en un FormField como read-only
4. Agregar etapa_nombre en la tabla de documentos

---

## 📝 Notas Adicionales

- El Backend está correctamente diseñado: las etapas están correctamente filtradas
- El problema es puramente de UI/UX: etapas filtradas pero NO VISIBLES
- La sincronización ya existe, solo falta hacerla visible al usuario
- La funcionalidad de "Proyecto de Grado" referida por el usuario probablemente usa un patrón similar

---

**Próximos pasos:** ¿Deseas que implemente la Opción 1 para sincronizar las etapas visibles en Documentos?
