# Matriz de Modalidad ↔ Tipo de Documento

**Documento de Análisis:** Definición de requerimientos documentales por modalidad  
**Fecha:** 22 de junio de 2026  
**Estado:** Propuesta de Implementación

---

## 📊 Resumen Ejecutivo

El sistema de graduación tiene **3 modalidades**, **4-4 etapas** (variables), y **8 tipos de documento** actualmente desvinculados de modalidades. 

**Objetivo:** Establecer una matriz M2M (ModalidadTipoDocumento) que especifique:
- ✅ Qué documentos aplican a cada modalidad
- 🔒 Cuáles son obligatorios por etapa
- 📍 En qué etapa específica son requeridos

---

## 🏛️ Estructura Actual del Sistema

### Modalidades Activas

| ID | Nombre | Descripción |
|----|--------|------------|
| 1 | **Proyecto de Grado** | Desarrollo de proyecto integrador con defensa |
| 2 | **Examen de Grado** | Evaluación académica estándar |
| 3 | **Vía Diplomado** | Programa de diplomado con defensa de monografía |

### Etapas por Modalidad

#### 1️⃣ Proyecto de Grado (4 etapas)
| Orden | Etapa | Descripción |
|-------|-------|------------|
| 1 | Propuesta/Perfil | Presentación inicial del proyecto |
| 2 | Desarrollo del Proyecto | Ejecución y avance |
| 3 | Defensa de Proyecto | Presentación y defensa pública |
| 4 | Correcciones | Implementación de observaciones |

#### 2️⃣ Examen de Grado (3 etapas)
| Orden | Etapa | Descripción |
|-------|-------|------------|
| 1 | Inscripción | Registro y validación de requisitos |
| 2 | Evaluación | Realización de examen |
| 3 | Resultado Final | Publicación de resultados |

#### 3️⃣ Vía Diplomado (4 etapas)
| Orden | Etapa | Descripción |
|-------|-------|------------|
| 1 | Inscripción Diplomado | Registro en programa |
| 2 | Desarrollo Diplomado | Cursado de materias |
| 3 | Defensa Monografía | Presentación de trabajo final |
| 4 | Correcciones | Ajustes post-defensa |

### Tipos de Documento Disponibles

| ID | Nombre | Actual |
|----|--------|--------|
| 1 | Propuesta de Tesis | Sin etapa (etapa: NULL) |
| 2 | Certificado Académico | Sin etapa (etapa: NULL) |
| 3 | CV del Estudiante | Sin etapa (etapa: NULL) |
| 4 | Carta de Aceptación | Sin etapa (etapa: NULL) |
| 5 | Perfil de Tesis | Sin etapa (etapa: NULL) |
| 6 | Documento de Avance | Sin etapa (etapa: NULL) |
| 7 | Documento Final | Sin etapa (etapa: NULL) |
| 8 | Comprobante de Defensa | Sin etapa (etapa: NULL) |

---

## 📋 MATRIZ MODALIDAD → DOCUMENTOS

### Proyecto de Grado

#### Etapa 1: Propuesta/Perfil (Orden 1)

| Tipo Documento | Permitido | Obligatorio | Descripción |
|---|---|---|---|
| **CV del Estudiante** | ✅ | ✅ | Currículum actualizado del estudiante |
| **Certificado Académico** | ✅ | ✅ | Certificado de calificaciones válido |
| **Propuesta de Tesis** | ✅ | ✅ | Propuesta inicial del proyecto |
| **Carta de Aceptación** | ✅ | ✅ | Aceptación de tutor o institución |
| **Perfil de Tesis** | ✅ | ❌ | Perfil detallado (opcional en esta etapa) |
| **Documento de Avance** | ❌ | - | No aplica |
| **Documento Final** | ❌ | - | No aplica |
| **Comprobante de Defensa** | ❌ | - | No aplica |

**Requisitos Adicionales:**
- Mínimo 4 documentos obligatorios para pasar a siguiente etapa
- Todos los documentos requieren aprobación explícita

---

#### Etapa 2: Desarrollo del Proyecto (Orden 2)

| Tipo Documento | Permitido | Obligatorio | Descripción |
|---|---|---|---|
| **CV del Estudiante** | ✅ | ❌ | Actualización opcional si cambió |
| **Certificado Académico** | ✅ | ❌ | Actualización opcional |
| **Propuesta de Tesis** | ✅ | ❌ | Referencia de propuesta aprobada |
| **Carta de Aceptación** | ✅ | ❌ | Puede ser revalidada |
| **Perfil de Tesis** | ✅ | ✅ | Perfil completo y detallado requerido |
| **Documento de Avance** | ✅ | ✅ | Reporte de avance (mínimo semestral) |
| **Documento Final** | ❌ | - | Aún en desarrollo |
| **Comprobante de Defensa** | ❌ | - | No aplica |

**Requisitos Adicionales:**
- Perfil de Tesis y Documento de Avance son críticos para continuar
- Reportes de avance pueden ser múltiples (uno por reporte)

---

#### Etapa 3: Defensa de Proyecto (Orden 3)

| Tipo Documento | Permitido | Obligatorio | Descripción |
|---|---|---|---|
| **CV del Estudiante** | ✅ | ❌ | Referencia en expediente |
| **Certificado Académico** | ✅ | ❌ | Validación final si requiere |
| **Propuesta de Tesis** | ✅ | ❌ | Documento de referencia |
| **Carta de Aceptación** | ✅ | ❌ | Documento de respaldo |
| **Perfil de Tesis** | ✅ | ❌ | Referencia del perfil final |
| **Documento de Avance** | ✅ | ❌ | Ultimos avances |
| **Documento Final** | ✅ | ✅ | Trabajo completo para defensa |
| **Comprobante de Defensa** | ✅ | ✅ | Acta de defensa post-presentación |

**Requisitos Adicionales:**
- Documento Final es prerequisito para defensa
- Comprobante de Defensa se genera/sube post-defensa
- Defensa debe ser programada y ejecutada

---

#### Etapa 4: Correcciones (Orden 4)

| Tipo Documento | Permitido | Obligatorio | Descripción |
|---|---|---|---|
| **CV del Estudiante** | ✅ | ❌ | Referencia si cambió |
| **Certificado Académico** | ✅ | ❌ | Actualización si requiere |
| **Propuesta de Tesis** | ✅ | ❌ | Referencia |
| **Carta de Aceptación** | ✅ | ❌ | Referencia |
| **Perfil de Tesis** | ✅ | ❌ | Referencia |
| **Documento de Avance** | ✅ | ❌ | Referencia |
| **Documento Final** | ✅ | ✅ | Versión corregida post-observaciones |
| **Comprobante de Defensa** | ✅ | ❌ | Referencia |

**Requisitos Adicionales:**
- Documento Final corregido es obligatorio
- Plazo de correcciones: 30 días típicamente
- Validación post-correcciones antes de archivo final

---

### Examen de Grado

#### Etapa 1: Inscripción (Orden 1)

| Tipo Documento | Permitido | Obligatorio | Descripción |
|---|---|---|---|
| **CV del Estudiante** | ✅ | ✅ | CV actualizado |
| **Certificado Académico** | ✅ | ✅ | Certificado de calificaciones |
| **Propuesta de Tesis** | ❌ | - | No aplica en esta modalidad |
| **Carta de Aceptación** | ❌ | - | No aplica en esta modalidad |
| **Perfil de Tesis** | ❌ | - | No aplica en esta modalidad |
| **Documento de Avance** | ❌ | - | No aplica en esta modalidad |
| **Documento Final** | ❌ | - | No aplica en esta modalidad |
| **Comprobante de Defensa** | ❌ | - | No aplica en esta modalidad |

**Requisitos Adicionales:**
- Solo 2 documentos requeridos
- Validación rápida de antecedentes académicos
- Habilita inscripción a examen

---

#### Etapa 2: Evaluación (Orden 2)

| Tipo Documento | Permitido | Obligatorio | Descripción |
|---|---|---|---|
| **CV del Estudiante** | ✅ | ❌ | Referencia en expediente |
| **Certificado Académico** | ✅ | ❌ | Referencia validada |
| **Propuesta de Tesis** | ❌ | - | No aplica |
| **Carta de Aceptación** | ❌ | - | No aplica |
| **Perfil de Tesis** | ❌ | - | No aplica |
| **Documento de Avance** | ❌ | - | No aplica |
| **Documento Final** | ❌ | - | No aplica |
| **Comprobante de Defensa** | ✅ | ✅ | Acta/Comprobante de examen realizado |

**Requisitos Adicionales:**
- Comprobante de Defensa es resultado del examen
- Se genera por sistema o se carga post-examen
- Requisito para pasar a Resultado Final

---

#### Etapa 3: Resultado Final (Orden 3)

| Tipo Documento | Permitido | Obligatorio | Descripción |
|---|---|---|---|
| **CV del Estudiante** | ✅ | ❌ | Referencia final |
| **Certificado Académico** | ✅ | ❌ | Referencia final |
| **Propuesta de Tesis** | ❌ | - | No aplica |
| **Carta de Aceptación** | ❌ | - | No aplica |
| **Perfil de Tesis** | ❌ | - | No aplica |
| **Documento de Avance** | ❌ | - | No aplica |
| **Documento Final** | ❌ | - | No aplica |
| **Comprobante de Defensa** | ✅ | ❌ | Referencia de examen realizado |

**Requisitos Adicionales:**
- Etapa de cierre administrativo
- Generación de expediente final
- Publicación de resultados oficiales

---

### Vía Diplomado

#### Etapa 1: Inscripción Diplomado (Orden 1)

| Tipo Documento | Permitido | Obligatorio | Descripción |
|---|---|---|---|
| **CV del Estudiante** | ✅ | ✅ | CV para admisión al programa |
| **Certificado Académico** | ✅ | ✅ | Certificado de licenciatura/carrera |
| **Propuesta de Tesis** | ❌ | - | No aplica |
| **Carta de Aceptación** | ✅ | ✅ | Aceptación en programa de diplomado |
| **Perfil de Tesis** | ❌ | - | No aplica |
| **Documento de Avance** | ❌ | - | No aplica |
| **Documento Final** | ❌ | - | Monografía aún en desarrollo |
| **Comprobante de Defensa** | ❌ | - | No aplica |

**Requisitos Adicionales:**
- 3 documentos obligatorios
- Validación de elegibilidad académica
- Aceptación explícita en programa

---

#### Etapa 2: Desarrollo Diplomado (Orden 2)

| Tipo Documento | Permitido | Obligatorio | Descripción |
|---|---|---|---|
| **CV del Estudiante** | ✅ | ❌ | Referencia |
| **Certificado Académico** | ✅ | ❌ | Referencia |
| **Propuesta de Tesis** | ✅ | ✅ | Propuesta de monografía del diplomado |
| **Carta de Aceptación** | ✅ | ❌ | Referencia de admisión |
| **Perfil de Tesis** | ✅ | ✅ | Perfil de monografía requerido |
| **Documento de Avance** | ✅ | ✅ | Reportes de avance de monografía |
| **Documento Final** | ❌ | - | Monografía aún en desarrollo |
| **Comprobante de Defensa** | ❌ | - | No aplica |

**Requisitos Adicionales:**
- Propuesta, Perfil y Documento de Avance obligatorios
- Múltiples reportes de avance esperados
- Validación de progreso académico

---

#### Etapa 3: Defensa Monografía (Orden 3)

| Tipo Documento | Permitido | Obligatorio | Descripción |
|---|---|---|---|
| **CV del Estudiante** | ✅ | ❌ | Referencia en expediente |
| **Certificado Académico** | ✅ | ❌ | Referencia |
| **Propuesta de Tesis** | ✅ | ❌ | Referencia |
| **Carta de Aceptación** | ✅ | ❌ | Referencia |
| **Perfil de Tesis** | ✅ | ❌ | Referencia |
| **Documento de Avance** | ✅ | ❌ | Últimos avances |
| **Documento Final** | ✅ | ✅ | Monografía completa para defensa |
| **Comprobante de Defensa** | ✅ | ✅ | Acta de defensa de monografía |

**Requisitos Adicionales:**
- Documento Final (monografía) es crítico
- Comprobante de Defensa generado post-presentación
- Defensa pública requerida

---

#### Etapa 4: Correcciones (Orden 4)

| Tipo Documento | Permitido | Obligatorio | Descripción |
|---|---|---|---|
| **CV del Estudiante** | ✅ | ❌ | Referencia |
| **Certificado Académico** | ✅ | ❌ | Referencia |
| **Propuesta de Tesis** | ✅ | ❌ | Referencia |
| **Carta de Aceptación** | ✅ | ❌ | Referencia |
| **Perfil de Tesis** | ✅ | ❌ | Referencia |
| **Documento de Avance** | ✅ | ❌ | Referencia |
| **Documento Final** | ✅ | ✅ | Monografía corregida post-observaciones |
| **Comprobante de Defensa** | ✅ | ❌ | Referencia |

**Requisitos Adicionales:**
- Monografía corregida obligatoria
- Plazo de correcciones: 30 días típicamente
- Aprobación final antes de titulación

---

## 🔄 Documentos Reutilizables (Multi-Etapa)

Los siguientes documentos pueden ser utilizados en múltiples etapas dentro de la misma modalidad:

| Documento | Proyecto de Grado | Examen de Grado | Diplomado |
|---|---|---|---|
| **CV del Estudiante** | ✅ E1-E4 (ref) | ✅ E1,E3 (ref) | ✅ E1,E2 (ref) |
| **Certificado Académico** | ✅ E1-E4 (ref) | ✅ E1,E3 (ref) | ✅ E1,E2 (ref) |
| **Propuesta de Tesis** | ✅ E1-E3 (ref) | ❌ | ✅ E2-E3 (ref) |
| **Carta de Aceptación** | ✅ E1-E3 (ref) | ❌ | ✅ E1-E2 (ref) |
| **Perfil de Tesis** | ✅ E2-E3 (ref) | ❌ | ✅ E2-E3 (ref) |
| **Documento de Avance** | ✅ E2-E3 (ref) | ❌ | ✅ E2-E3 (ref) |
| **Documento Final** | ✅ E3,E4 (crítico) | ❌ | ✅ E3,E4 (crítico) |
| **Comprobante de Defensa** | ✅ E3,E4 (ref) | ✅ E2,E3 (ref) | ✅ E3,E4 (ref) |

---

## 🗂️ Validaciones de Negocio

### Por Modalidad

**Proyecto de Grado:**
- ✅ Requiere tutor asignado
- ✅ Requiere propuesta estructurada
- ✅ Requiere defensa pública
- ✅ Requiere correcciones post-defensa
- ✅ Ciclo completo: ~9-12 meses

**Examen de Grado:**
- ✅ Trámite más rápido (~3-4 meses)
- ✅ Documentación mínima (CV + Certificado)
- ✅ No requiere tutor ni proyecto
- ✅ Evaluación por examen estandarizado

**Vía Diplomado:**
- ✅ Requiere programa diplomado específico
- ✅ Similar a Proyecto pero con contenido de diplomado
- ✅ Requiere defensa de monografía
- ✅ Ciclo similar a Proyecto (~9-12 meses)

### Por Etapa (Validaciones de Transición)

1. **Propuesta/Perfil → Desarrollo**
   - ✅ Todos los documentos de E1 aprobados
   - ✅ Tutor confirmado

2. **Desarrollo → Defensa**
   - ✅ Documento Final completado
   - ✅ Perfil y Avances aprobados
   - ✅ Defensa programada (fecha/sala/tribunal)

3. **Defensa → Correcciones**
   - ✅ Defensa realizada (Comprobante)
   - ✅ Tribunal ha emitido observaciones

4. **Correcciones → Cierre**
   - ✅ Documento Final corregido aprobado
   - ✅ Todas las observaciones resueltas
   - ✅ Apto para titulación

---

## 🗄️ Propuesta de Modelo M2M

### Nueva Tabla: `ModalidadTipoDocumento`

```python
class ModalidadTipoDocumento(models.Model):
    modalidad = models.ForeignKey(Modalidad, on_delete=models.CASCADE)
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE)
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE, null=True, blank=True)
    obligatorio = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=0)
    descripcion_requerimiento = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('modalidad', 'tipo_documento', 'etapa')
        ordering = ['modalidad__nombre', 'orden']
    
    def __str__(self):
        return f"{self.modalidad} - {self.tipo_documento} (E{self.etapa.orden if self.etapa else 'X'})"
```

**Campos Clave:**
- `modalidad`: Referencia a Modalidad
- `tipo_documento`: Referencia a TipoDocumento
- `etapa`: Etapa donde aplica (NULL = aplica en todas/sin restricción)
- `obligatorio`: Si debe presentarse sí o sí
- `orden`: Orden de presentación sugerido
- `descripcion_requerimiento`: Especificaciones adicionales

---

## 📊 Datos de Prueba Iniciales

```python
# Proyecto de Grado - Etapa 1 (Propuesta/Perfil)
ModalidadTipoDocumento.objects.create(
    modalidad_id=1, tipo_documento_id=3,  # CV
    etapa_id=1, obligatorio=True, orden=1
)
ModalidadTipoDocumento.objects.create(
    modalidad_id=1, tipo_documento_id=2,  # Certificado
    etapa_id=1, obligatorio=True, orden=2
)
# ... (24 registros adicionales según matriz)

# Examen de Grado - Etapa 1 (Inscripción)
ModalidadTipoDocumento.objects.create(
    modalidad_id=2, tipo_documento_id=3,  # CV
    etapa_id=5, obligatorio=True, orden=1
)
# ... (más registros)
```

---

## 🔗 Relación con TipoDocumento Actual

**Estado Actual:** TipoDocumento.etapa = NULL (sin restricción)

**Migración Propuesta:**
1. ✅ Crear tabla ModalidadTipoDocumento M2M
2. ✅ Poblar con matriz de requerimientos
3. ⚠️ Mantener backward compatibility: TipoDocumento.etapa sigue existiendo
4. ⚠️ Lógica frontend: Filtrar TipoDocumento por modalidad + etapa usando ModalidadTipoDocumento

---

## ✅ Próximos Pasos de Implementación

**FASE 1: Crear Modelo M2M**
- [ ] Crear migración con tabla ModalidadTipoDocumento
- [ ] Aplicar migración a base de datos

**FASE 2: Poblar Matriz de Requerimientos**
- [ ] Crear script de bootstrap con 40-50 registros
- [ ] Validar completitud de matriz
- [ ] Ejecutar en base de datos

**FASE 3: Actualizar API**
- [ ] Crear ViewSet para ModalidadTipoDocumento (read-only)
- [ ] Endpoint: `GET /api/modalidades/{id}/documentos/` 
- [ ] Serializer con validación de requerimientos

**FASE 4: Actualizar Frontend**
- [ ] Modificar Documentos.jsx para filtrar por modalidad
- [ ] Integrar validación de obligatoriedad
- [ ] Mostrar documentos permitidos en modal

**FASE 5: Validaciones Avanzadas**
- [ ] Validar en serializer: Documentos requeridos presentes antes de transición de etapa
- [ ] Validar en viewset: No permitir cambio de estado a 'aprobado' sin documentos obligatorios

---

## 📝 Notas de Diseño

1. **Flexibilidad:** La matriz permite excepciones por etapa
2. **Extensibilidad:** Fácil agregar nuevas modalidades o tipos de documento
3. **Backward Compatibility:** TipoDocumento.etapa sigue funcionando
4. **Validaciones:** Pueden implementarse progresivamente (MVP simple, features después)
5. **Reporting:** Matriz facilita auditoría y análisis de completitud documental

---

**Versión:** 1.0  
**Autor:** Analysis Agent  
**Revisión Pendiente:** Confirmación de requerimientos por coordinación académica
