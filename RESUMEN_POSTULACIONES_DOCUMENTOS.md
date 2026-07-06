# 🎯 Resumen Ejecutivo: Postulaciones y Documentos

## ✅ Lo que FUNCIONA Correctamente

### 1. Relaciones de Datos
```
MODALIDAD (Tesis, Trabajo Dirigido, etc.)
    ↓
ETAPA (1. Perfil → 2. Defensa → 3. Titulación)
    ↓
POSTULACION (Estudiante en etapa actual)
    ↓
TIPO_DOCUMENTO (Currículum, Anteproyecto, etc.)
    ↓
DOCUMENTO_POSTULACION (Archivo subido)
```

### 2. Flujo "Subir Documentos"
- ✅ Usuario selecciona postulación
- ✅ Sistema obtiene automaticamente: modalidad + etapa_actual
- ✅ Carga solo documentos válidos para esa modalidad + etapa
- ✅ Backend filtra con `ModalidadTipoDocumento`

### 3. Validaciones
- ✅ Backend valida: `etapa.modalidad == postulacion.modalidad`
- ✅ No permite mezclar etapas de diferentes modalidades

---

## ❌ Lo que NO FUNCIONA / INCONSISTENCIAS

### 🔴 CRÍTICO (Roto en Runtime)
**#1: Import Incorrecto**
```python
# postulantes/views.py línea 13
from .serializers import EtapaSerializer  # ❌ NO EXISTE

# Debería ser:
from modalidades.serializers import EtapaSerializer
```
**Causa:** `ImportError` cuando se carga la página

---

### 🟡 PROBLEMAS (Funcionan pero mal)

**#2: Carga de Etapas Sin Filtro**
```javascript
// Postulaciones.jsx línea 75-88
if (etapaResult.success) {
  setEtapas(etapasData);  // ❌ TODAS las etapas sin filtrar
}
```
- **Problema:** Carga etapas de TODAS las modalidades
- **Impacto:** Si hay dropdown de etapas, muestra datos irrelevantes
- **Solución:** Filtrar dinámicamente cuando selecciona modalidad

**#3: Dos Relaciones a Etapa**
```python
# TipoDocumento.etapa (nullable)
# ModalidadTipoDocumento.etapa (nullable)
```
- **Problema:** ¿Cuál es la "fuente de verdad"?
- **Ejemplo:** Si difieren, ¿cuál prevalece?
- **Solución:** Usar solo `ModalidadTipoDocumento.etapa`

**#4: `etapa_actual` es Nullable**
```python
# postulantes/models.py
etapa_actual = ForeignKey(..., null=True, blank=True)
```
- **Problema:** Campo es opcional pero hay validación que lo asume obligatorio
- **Pregunta:** ¿Debería ser obligatorio? ¿Se inicializa automáticamente?

**#5: Falta Filtro de Etapas en API**
```
GET /api/etapas/  ← Retorna TODAS
GET /api/etapas/?modalidad=3  ← No soportado
```
- **Problema:** No hay forma eficiente de cargar solo etapas de una modalidad
- **Solución:** Agregar `filterset_fields = ['modalidad']` en `EtapaViewSet`

**#6: Filtrado de Documentos es Implícito**
```javascript
// Documentos.jsx
const etapaId = selectedPostulacion?.etapa_actual;
// Filtra automáticamente según etapa_actual
```
- **Problema:** Usuario no puede ver documentos de otras etapas
- **Pregunta:** ¿Debería haber opción manual de filtrar?

---

## 📊 Comparativo: Frontend vs Backend

| Aspecto | Frontend | Backend | Estado |
|---------|----------|---------|--------|
| Carga de Etapas | Sin filtro | N/A | ❌ Mejora |
| Filtrado Documentos | Automático | Filtra OK | ✅ Funciona |
| Validación Etapa | No | SÍ | ✅ Protegido |
| Endpoint tipos-documento | Usa OK | Devuelve OK | ✅ Funciona |

---

## 🔧 Acciones Inmediatas

### 1. Corregir Import (5 minutos)
**Archivo:** `postulantes/views.py` línea 13
```python
# Cambiar
from .serializers import EtapaSerializer

# A
from modalidades.serializers import EtapaSerializer
```

### 2. Mejorar Filtrado de Etapas (30 minutos)

**Backend:** Agregar filtro en `modalidades/views.py`
```python
class EtapaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Etapa.objects.select_related('modalidad').all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['modalidad']  # ← AGREGAR
```

**Frontend:** Cargar etapas dinámicamente en `Postulaciones.jsx`
```javascript
// Cuando cambia modalidad, cargar sus etapas
const handleModalidadChange = async (modalidadId) => {
  const result = await api.getAll(
    API_CONFIG.ENDPOINTS.ETAPAS,
    { modalidad: modalidadId }
  );
  setEtapas(result.data);
};
```

### 3. Resolver Redundancia (Requiere análisis)
- ¿Se usa `TipoDocumento.etapa` en algún lado?
- ¿O es la obsoleta?
- Si es obsoleta → Migración para remover + cleanup

---

## 📈 Resumen de Datos

```
Archivos analizados:        10
├─ Backend:                 6
│  ├─ postulantes/          3
│  ├─ modalidades/          2
│  └─ documentos/           3
└─ Frontend:                4
   ├─ pages/                2
   └─ constants/            1

Inconsistencias encontradas: 6
├─ Críticas (Roto):        1
├─ Medianas (Mejora):      5
└─ Resueltas:              0

Impacto:
├─ Seguridad:             ✅ OK (backend valida)
├─ Funcionalidad:         ⚠️ Parcial (algunas mejoras)
└─ UX:                    ❌ Confusa (carga sin filtro)
```

---

## 📍 Dónde Están las Inconsistencias

```
POSTULACIONES.JSX
├─ ❌ Carga sin filtro de etapas (línea 75-88)
└─ ⚠️ No hay filtrado dinámico

DOCUMENTOS.JSX
├─ ✅ Filtrado correcto por modalidad + etapa
└─ ⚠️ Filtrado es implícito/automático

POSTULANTES/VIEWS.PY
├─ 🔴 Import incorrecto de EtapaSerializer (línea 13)
└─ ❌ Va a fallar en runtime

DOCUMENTOS/MODELS.PY
├─ ⚠️ TipoDocumento.etapa (redundante)
└─ ⚠️ ModalidadTipoDocumento.etapa (fuente principal)

POSTULANTES/MODELS.PY
├─ ⚠️ etapa_actual nullable pero con validación
└─ ❓ ¿Es realmente opcional?

MODALIDADES/VIEWS.PY
├─ ⚠️ EtapaViewSet sin filtro por modalidad
└─ 💡 Fácil de agregar
```

---

## 🎓 Conclusión

**La estructura es SÓLIDA pero tiene detalles a pulir:**

1. **Backend:** Validaciones correctas, protege integridad
2. **Frontend:** Funciona pero sin optimizaciones
3. **Datos:** Redundancia en relaciones (dos formas de especificar etapa)
4. **UX:** Sin filtrado dinámico, carga innecesaria

**Riesgo:** La única acción crítica es el import incorrecto que causará crash.
