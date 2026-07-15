# DIAGNÓSTICO COMPLETO: Catálogo de Documentos de Proyecto de Grado

## 1. ETAPAS ACTUALES DE PROYECTO DE GRADO

```
Orden  Nombre                          ID
─────  ───────────────────────────────  ──
  1    Registro                          20
  2    Perfil de Proyecto de Grado       21
  3    Documento Final                   22
  4    Defensa Privada                   23  ← VACÍA ❌
  5    Defensa Pública                   24  ← VACÍA ❌
  6    Acta Final                        55
```

---

## 2. DOCUMENTOS CONFIGURADOS POR ETAPA

### Etapa 1 (Registro - orden 1)
✅ 4 documentos obligatorios configurados:
- CV del Estudiante
- Certificado Académico
- Propuesta de Tesis
- Carta de Aceptación

### Etapa 2 (Perfil de Proyecto de Grado - orden 2)
✅ 4 documentos obligatorios configurados:
- CV del Estudiante
- Certificado Académico
- Propuesta de Tesis
- Carta de Aceptación

### Etapa 3 (Documento Final - orden 3)
✅ 8 documentos obligatorios configurados:
- CV del Estudiante
- Certificado Académico
- Propuesta de Tesis
- Carta de Aceptación
- Perfil de Tesis
- Documento de Avance
- Documento Final
- Acta de Defensa del Proyecto de Grado

### Etapa 4 (Defensa Privada - orden 4)
❌ **0 documentos configurados** ← PROBLEMA
- No hay validación
- Permite avanzar sin documentos

### Etapa 5 (Defensa Pública - orden 5)
❌ **0 documentos configurados** ← PROBLEMA
- No hay validación
- Permite avanzar sin documentos

### Etapa 6 (Acta Final - orden 6)
✅ 1 documento obligatorio configurado:
- Acta de Defensa del Proyecto de Grado

---

## 3. DOCUMENTOS DISPONIBLES EN EL CATÁLOGO

Existen documentos ESPECÍFICOS para defensa privada y pública que nunca fueron asociados a Proyecto de Grado:

```
ID    Nombre                              Estado
───   ─────────────────────────────────   ──────
 71   Acta de defensa privada             DISPONIBLE ✅
 72   Acta de defensa pública             DISPONIBLE ✅
```

**Hallazgo:** Estos documentos existen pero:
- NO están asociados a PROYECTO DE GRADO
- NO están asociados a NINGUNA otra modalidad
- Fueron creados pero nunca vinculados

---

## 4. COMPARACIÓN CON EXAMEN DE GRADO (Correcto)

### Examen de Grado - Documentos Obligatorios por Etapa
```
Etapa 1 (Registro):          9 documentos ✅
Etapa 2 (Examen 1):          1 acta ✅
Etapa 3 (Examen 2):          1 acta ✅
Etapa 4 (Examen 3):          1 acta ✅
Etapa 5 (Examen 4):          1 acta ✅
Etapa 6 (Acta Final):        1 acta ✅
```

**Resultado:** Cada etapa tiene AL MENOS 1 documento obligatorio.
**Comportamiento:** Valida correctamente. No permite avanzar sin documentos.

### Proyecto de Grado - Documentos Obligatorios por Etapa
```
Etapa 1 (Registro):           4 documentos ✅
Etapa 2 (Perfil):             4 documentos ✅
Etapa 3 (Documento Final):    8 documentos ✅
Etapa 4 (Defensa Privada):    0 documentos ❌ ← PROBLEMA
Etapa 5 (Defensa Pública):    0 documentos ❌ ← PROBLEMA
Etapa 6 (Acta Final):         1 acta ✅
```

**Resultado:** Etapas 4 y 5 están vacías.
**Comportamiento:** `required_documents_missing()` retorna `[]` → permite avanzar.

---

## 5. ANÁLISIS DE CÓDIGO: POR QUÉ SUCEDE ESTO

### Función `required_documents_missing()` (postulantes/services.py:125-126)

```python
if not mtd_qs.exists():  # Si no hay documentos configurados
    return []           # Retorna lista vacía (sin faltantes)
```

### Función `avanzar_postulacion()` (postulantes/services.py:211-217)

```python
missing_docs = required_documents_missing(postulacion)
if missing_docs:        # if [] → False
    raise EtapaIncompletaError(...)  # No se levanta
```

**Conclusión:** La lógica es correcta. El problema es que **falta configurar los documentos obligatorios** en las etapas 4 y 5.

---

## 6. PROPUESTA DE SOLUCIÓN

### Opción Recomendada: Asociar Actas Existentes

**Asociar documentos ya existentes a Proyecto de Grado sin crear ninguno nuevo:**

1. **Etapa 4 (Defensa Privada):** Agregar "Acta de defensa privada" (ID=71) como **obligatorio**
2. **Etapa 5 (Defensa Pública):** Agregar "Acta de defensa pública" (ID=72) como **obligatorio**

### SQL Equivalente (SIN ejecutar aún)

```sql
INSERT INTO documentos_modalidadtipodocumento 
  (modalidad_id, tipo_documento_id, etapa_id, obligatorio, activo, orden, descripcion_requerimiento)
VALUES
  (1, 71, 23, true, true, 1, ''),    -- Proyecto de Grado, Acta Defensa Privada, Etapa 23, Obligatorio
  (1, 72, 24, true, true, 1, '');    -- Proyecto de Grado, Acta Defensa Pública, Etapa 24, Obligatorio
```

### Migración Django (Recomendado)

Crear una migración en `documentos/migrations/` que ejecute esta lógica:

```python
def add_defensa_actas_to_proyecto_grado(apps, schema_editor):
    ModalidadTipoDocumento = apps.get_model('documentos', 'ModalidadTipoDocumento')
    
    # Proyecto de Grado: ID=1
    # Acta defensa privada: ID=71
    # Etapa Defensa Privada: ID=23
    ModalidadTipoDocumento.objects.get_or_create(
        modalidad_id=1,
        tipo_documento_id=71,
        etapa_id=23,
        defaults={
            'obligatorio': True,
            'activo': True,
            'orden': 1,
            'descripcion_requerimiento': '',
        }
    )
    
    # Proyecto de Grado: ID=1
    # Acta defensa pública: ID=72
    # Etapa Defensa Pública: ID=24
    ModalidadTipoDocumento.objects.get_or_create(
        modalidad_id=1,
        tipo_documento_id=72,
        etapa_id=24,
        defaults={
            'obligatorio': True,
            'activo': True,
            'orden': 1,
            'descripcion_requerimiento': '',
        }
    )
```

---

## 7. IMPACTO DE LA SOLUCIÓN

### ✅ Lo que arreglará:
1. Etapa 4 (Defensa Privada) tendrá 1 documento obligatorio → validación activa
2. Etapa 5 (Defensa Pública) tendrá 1 documento obligatorio → validación activa
3. `required_documents_missing()` retornará lista NO vacía si faltan actas
4. `avanzar_postulacion()` levantará `EtapaIncompletaError` bloqueando avances sin documentos

### ❌ Lo que NO cambiará:
- Examen de Grado mantiene su configuración actual ✅
- Excelencia Académica mantiene su configuración actual ✅
- Tesis de Grado mantiene su configuración actual (aunque también tiene etapas vacías) ✅
- Vía Diplomado mantiene su configuración actual ✅
- La lógica de validación sigue siendo la misma para todas las modalidades ✅
- No se crean nuevos tipos de documentos ✅
- No se modifican etapas existentes ✅
- No se modifica ningún código compartido ✅

### 🔍 Verificación Post-Solución:

```sql
SELECT e.nombre, COUNT(CASE WHEN mtd.obligatorio THEN 1 END) as obligatorios
FROM modalidades_etapa e
LEFT JOIN documentos_modalidadtipodocumento mtd ON mtd.etapa_id = e.id
WHERE e.modalidad_id = 1
GROUP BY e.id, e.nombre
ORDER BY e.orden;

-- Resultado esperado:
--  nombre                  | obligatorios
-- ────────────────────────┼──────────────
--  Registro               |            4
--  Perfil de Proyecto     |            4
--  Documento Final        |            8
--  Defensa Privada        |            1  ← CAMBIO
--  Defensa Pública        |            1  ← CAMBIO
--  Acta Final             |            1
```

---

## 8. CONFIRMACIÓN DE REGLA DE NEGOCIO

**Según el reglamento de Proyecto de Grado:**
- ✅ Defensa Privada concluye con un acta (documento 71)
- ✅ Defensa Pública concluye con un acta (documento 72)
- ✅ Finalmente existe Acta Final de aprobación (documento existente)

**Conclusión:** Los documentos están correctamente identificados en el catálogo. Solo necesitan ser **asociados** a las etapas en `ModalidadTipoDocumento`.

---

## 9. PRÓXIMOS PASOS

1. **Usuario confirma:** ¿Está de acuerdo con agregar estas actas como obligatorias en Defensa Privada y Pública?
2. **Si confirma:** Ejecutar migración Django
3. **Verificar:** Que `required_documents_missing()` ahora valida correctamente
4. **Test:** Intentar avanzar etapa sin subir las actas (debe bloquear)

