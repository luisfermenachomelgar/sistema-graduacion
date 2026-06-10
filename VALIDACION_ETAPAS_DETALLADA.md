# 📋 VALIDACIÓN DETALLADA DE ETAPAS PROPUESTAS

## Contexto del Análisis

Las descripciones de modalidades del sistema indican el flujo académico esperado. A continuación se proponen etapas coherentes con esas descripciones.

---

## 1️⃣ PROYECTO DE GRADO

### Descripción de la Modalidad (en el sistema)
> "Propuesta técnica de aplicación práctica que soluciona problemas concretos."

### Flujo Académico Esperado
Un proyecto requiere: ideación → ejecución → presentación ante tribunal

### Etapas Propuestas

| Orden | Nombre de Etapa | Descripción | Propósito |
|-------|-----------------|-------------|-----------|
| 1 | **Propuesta de Proyecto** | Etapa inicial donde el estudiante presenta la idea, objetivos, metodología y viabilidad del proyecto. | Validar que la idea es viable y está bien planteada |
| 2 | **Desarrollo del Proyecto** | Etapa de ejecución donde el estudiante implementa, desarrolla y construye la solución propuesta. | Avance en la realización del proyecto según propuesta aprobada |
| 3 | **Defensa de Proyecto** | Etapa final donde el estudiante presenta y defiende su proyecto ante un tribunal académico. | Validación final del trabajo completado |

### Origen de Nombres
- **PROPUESTOS POR DEFECTO** (No existen referencias en el sistema)
- Basados en: Flujo lógico de un proyecto técnico

### Referencia Comparable
Similar a "Tesis de Grado" pero:
- Tesis = Investigación científica (4 etapas + revisiones)
- Proyecto = Aplicación práctica (3 etapas + entrega)

---

## 2️⃣ EXAMEN DE GRADO

### Descripción de la Modalidad (en el sistema)
> "Evaluación integral de los conocimientos adquiridos a lo largo de la carrera, que puede incluir un examen de contenidos, análisis de expedientes o examen clínico/técnico."

### Flujo Académico Esperado
Un examen requiere: registro → administración → calificación

### Etapas Propuestas

| Orden | Nombre de Etapa | Descripción | Propósito |
|-------|-----------------|-------------|-----------|
| 1 | **Inscripción al Examen** | Etapa administrativa donde el estudiante se registra y cumple requisitos previos para presentar el examen. | Validar que el estudiante cumple con prerrequisitos |
| 2 | **Realización del Examen** | Etapa de ejecución donde el estudiante presenta el examen en la fecha y hora programada. | Participación en la evaluación integral |
| 3 | **Evaluación Tribunal** | Etapa de calificación donde el tribunal académico revisa el desempeño y emite el resultado. | Revisión y calificación final por tribunal |

### Origen de Nombres
- **PROPUESTOS POR DEFECTO** (No existen referencias en el sistema)
- Basados en: Proceso administrativo de examen integral

### Características Especiales
- Más orientado a **procesos administrativos** que académicos
- Etapas más cortas que Proyecto o Tesis
- Enfoque en evaluación de conocimientos consolidados

---

## 3️⃣ VÍA DIPLOMADO

### Descripción de la Modalidad (en el sistema)
> "Consiste en cursar y aprobar un programa de posgrado autorizado por la universidad, culminando con la elaboración, presentación y defensa exitosa de una monografía académica para la obtención del título de grado."

### Flujo Académico Esperado
Un diplomado requiere: registro → formación → evaluación final

### Etapas Propuestas

| Orden | Nombre de Etapa | Descripción | Propósito |
|-------|-----------------|-------------|-----------|
| 1 | **Inscripción Diplomado** | Etapa administrativa donde el estudiante se inscribe en el programa de diplomado autorizado por la universidad. | Registro y validación de admisión al diplomado |
| 2 | **Cursada del Diplomado** | Etapa de formación donde el estudiante cursa los módulos/asignaturas del programa de posgrado. | Formación académica y adquisición de competencias |
| 3 | **Defensa Monografía** | Etapa final donde el estudiante presenta y defiende la monografía académica ante tribunal. | Evaluación final de aprendizajes mediante monografía |

### Origen de Nombres
- **PROPUESTOS POR DEFECTO** (No existen referencias en el sistema)
- Basados en: Descripción textual de la modalidad

### Características Especiales
- Única modalidad que menciona explícitamente "monografía" en descripción
- Requiere cursada completa (diferente a examen)
- Etapas similares a Proyecto pero orientadas a formación de posgrado

---

## 📊 COMPARACIÓN: PROPUESTAS VS TESIS DE GRADO (Referencia)

### Tesis de Grado (Completamente Configurada)

```
1. Propuesta/Perfil
   └─ Documentos: Propuesta de Tesis, CV del Autor, Carta de Tutor
2. Privada
3. Pública
4. Correcciones
```

**Características:**
- 4 etapas (más que otras modalidades)
- Revisión multi-etapa antes de defensa
- Documentos específicos en etapa 1

### Resumen Comparativo

| Aspecto | Proyecto | Examen | Diplomado | Tesis |
|---------|----------|--------|-----------|-------|
| **Tipo** | Aplicación práctica | Evaluación | Formación + monografía | Investigación científica |
| **Etapas propuestas** | 3 | 3 | 3 | 4 (ya existe) |
| **Etapa final** | Defensa | Evaluación Tribunal | Defensa Monografía | Públicas + Correcciones |
| **Duración típica** | Corta-Media | Corta | Larga | Larga |
| **Documentos en etapa 1** | No definidos | No definidos | No definidos | Sí (CV, Propuesta, Tutor) |

---

## ✅ VALIDACIÓN FINAL

### Coherencia con Descripciones del Sistema
- ✅ **Proyecto**: Flujo coherente con "Propuesta técnica de aplicación práctica"
- ✅ **Examen**: Flujo coherente con "Evaluación integral de conocimientos"
- ✅ **Diplomado**: Flujo coherente con "Cursar, elaborar y defender monografía"

### Consistencia con Tesis de Grado
- ✅ Nombres usan patrón similar (etapas descriptivas)
- ✅ Órdenes coherentes (1 → inicio, 3 → final)
- ✅ No entran en conflicto con 4 etapas existentes de Tesis

### Seguridad de Integridad
- ✅ No afecta postulaciones existentes (todas con `etapa_actual = NULL`)
- ✅ Respeta constraint `unique_orden_por_modalidad`
- ✅ Usa `get_or_create()` (idempotente)

---

## 🎯 Preguntas para Validación

**¿Necesitas cambios en alguno de los nombres?**
- Ejemplo: ¿"Realización del Examen" vs "Aplicación del Examen"?
- Ejemplo: ¿"Cursada del Diplomado" vs "Estudio del Diplomado"?

**¿Deseas agregar más etapas?**
- Ejemplo: ¿Diplomado debería tener "Evaluación Final" separada de "Defensa"?

**¿Hay requisitos específicos para cada modalidad?**
- Ejemplo: ¿Documentos requeridos en cada etapa?
- Actualmente solo Tesis de Grado tiene documentos requeridos en Etapa 1

---

## 📝 Decisión Pendiente

Este documento propone **nombres estándar** basados en flujos académicos lógicos.

**Opciones:**
1. ✅ **Aprobar propuesta** → Proceder con migration
2. 📝 **Modificar nombres** → Indicar qué cambiar
3. ❌ **Rechazar** → Proponer alternativa

