# DIAGNÓSTICO: Por qué Proyecto de Grado permite avanzar sin validar documentos

# DIAGNÓSTICO FINAL: Por qué Proyecto de Grado permite avanzar sin validar documentos

## Problema Identificado

Cuando un estudiante intenta avanzar a la siguiente etapa en **Proyecto de Grado**, el sistema no valida documentos obligatorios como lo hace en **Examen de Grado**.

## Causa Raíz - CONFIRMADA

Las etapas 4 (Defensa Privada) y 5 (Defensa Pública) de **Proyecto de Grado** NO tienen documentos obligatorios configurados en la base de datos.

### Análisis de Base de Datos - VERIFICADO

#### Conteo de Documentos Obligatorios por Etapa

```
            etapa            | orden | obligatorios 
-----------------------------+-------|--------------
 Registro                    |     1 |            4 ✅
 Perfil de Proyecto de Grado |     2 |            4 ✅
 Documento Final             |     3 |            8 ✅
 Defensa Privada             |     4 |            0 ❌❌❌
 Defensa Pública             |     5 |            0 ❌❌❌
 Acta Final                  |     6 |            1 ✅
```

#### Comparación con EXAMEN DE GRADO

```
                   etapa                    | orden | obligatorios
---------------------------------------------+-------|--------------
 Registro                                    |     1 |            9 ✅
 Examen 1 – Ciencias Básicas y Matemáticas   |     2 |            1 ✅
 Examen 2 – Ciencias Sociales y Humanísticas |     3 |            1 ✅
 Examen 3 – Ciencias de la Ingeniería        |     4 |            1 ✅
 Examen 4 – Ingeniería Aplicada              |     5 |            1 ✅
 Acta Final                                  |     6 |            1 ✅
```

**Diferencia clave:** 
- EXAMEN DE GRADO: **Todos los 6 stages tienen documentos obligatorios** ✅
- PROYECTO DE GRADO: **2 de 6 stages están vacías** ❌

---

## Cómo funciona la Validación de Documentos

### Flujo en `avanzar_postulacion` (postulantes/services.py línea ~199)

```python
def avanzar_postulacion(postulacion_id: int, *, actor=None) -> Postulacion:
    # ...
    missing_docs = required_documents_missing(postulacion)  # ← VALIDACIÓN
    if missing_docs:
        raise EtapaIncompletaError(
            {
                'detail': 'Existen documentos obligatorios pendientes o no aprobados.',
                'faltantes': missing_names,
            }
        )
    # Si hay faltantes, se lanza excepción y NO avanza
```

### Función `required_documents_missing` (postulantes/services.py línea ~114)

```python
def required_documents_missing(postulacion: Postulacion) -> list[dict]:
    etapa = postulacion.etapa_actual
    if not etapa:
        return []
    
    # Busca documentos obligatorios configurados para esta etapa
    mtd_qs = ModalidadTipoDocumento.objects.filter(
        modalidad_id=postulacion.modalidad_id,
        obligatorio=True,
        activo=True,
    ).filter(Q(etapa_id=etapa.id) | Q(etapa__isnull=True))
    
    # Si no hay documentos configurados, retorna lista vacía []
    # Una lista vacía significa "no hay faltantes" y permite avanzar
```

### El Problema

Cuando la postulación está en **Defensa Privada** u **Defensa Pública**:

1. `required_documents_missing()` busca documentos obligatorios para esa etapa
2. No encuentra ninguno (porque están vacías en la BD)
3. Retorna una lista vacía `[]`
4. `if missing_docs:` evalúa a `False`
5. La postulación avanza **sin validar nada**

---

## Comparación con Examen de Grado

En **Examen de Grado**, cada etapa (incluso las de "Examen 1, 2, 3, 4") tiene **al menos 1 documento obligatorio** configurado (el acta correspondiente).

Por eso el flujo funciona correctamente:
- Etapa Examen 1: se valida que el acta esté aprobada
- Si falta, levanta excepción y NO permite avanzar
- Si existe y está aprobada, permite avanzar a Examen 2

---

## Solución Requerida

Para que **Proyecto de Grado** siga las **mismas reglas de negocio que Examen de Grado**, las etapas vacías deben tener documentos obligatorios configurados:

### Datos que Deben Agregarse

En la tabla `documentos_modalidadtipodocumento` para **Proyecto de Grado**:

**Etapa 4 - Defensa Privada** (orden=4):
- Debe tener AL MENOS 1 documento obligatorio (el acta de defensa privada)

**Etapa 5 - Defensa Pública** (orden=5):
- Debe tener AL MENOS 1 documento obligatorio (el acta de defensa pública)

Esto permitirá que `required_documents_missing()` valide correctamente y bloquee el avance si estos documentos no están aprobados.

---

## Archivos Involucrados

| Archivo | Línea | Función |
|---------|-------|---------|
| `postulantes/services.py` | 199 | `avanzar_postulacion()` - Valida y rechaza si hay documentos faltantes |
| `postulantes/services.py` | 114 | `required_documents_missing()` - Busca documentos obligatorios de la etapa |
| `documentos/models.py` | - | `ModalidadTipoDocumento` - Define qué documentos son obligatorios por modalidad y etapa |

---

## Confirmación de Datos Vacíos

Se verificó en BD que las etapas 23 (Defensa Privada) y 24 (Defensa Pública) tienen **0 documentos configurados**:

```sql
SELECT COUNT(*) FROM documentos_modalidadtipodocumento 
WHERE etapa_id IN (23, 24) AND modalidad_id = 1;

Result: 0 rows
```

---

## Próximos Pasos Requeridos

Para que Proyecto de Grado funcione idéntico a Examen de Grado, se debe determinar:

### Opción A: Agregar documentos a las etapas 4 y 5
Reutilizar "Acta de Defensa del Proyecto de Grado." (que ya existe) agregándola a:
- Etapa 4 (Defensa Privada) como obligatorio
- Etapa 5 (Defensa Pública) como obligatorio

### Opción B: Crear documentos específicos por etapa
Crear 2 documentos nuevos:
- "Acta de Defensa Privada del Proyecto de Grado"
- "Acta de Defensa Pública del Proyecto de Grado"

Y asignarlos respectivamente a etapas 4 y 5.

### Opción C: Sin documentos obligatorios en esas etapas
Si el negocio dice que Defensa Privada y Defensa Pública no requieren documentos obligatorios, entonces el comportamiento actual es **correcto** y no hay que cambiar nada.

---

## Conclusión

**La lógica de validación es idéntica para ambas modalidades.** El problema es puramente de **configuración de datos en la base de datos**: las etapas 4 y 5 de Proyecto de Grado no tienen documentos obligatorios configurados.

El código **NO necesita cambios**. Solo se debe:
1. Definir cuál opción es correcta según la regla de negocio
2. Ejecutar script SQL o migración para poblar las asignaciones de documentos faltantes
3. Luego Proyecto de Grado funcionará exactamente igual que Examen de Grado
