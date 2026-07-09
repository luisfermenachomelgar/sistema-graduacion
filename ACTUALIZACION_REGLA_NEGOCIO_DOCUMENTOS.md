# 📋 ACTUALIZACIÓN: REGLA DE NEGOCIO DE DOCUMENTOS

**Fecha:** 9 de Julio de 2026  
**Estado:** ✅ COMPLETADO  
**Ámbito:** Gestión de estado de documentos por rol

---

## 🎯 REGLA DE NEGOCIO IMPLEMENTADA

### Administrador 🔑
✅ **Puede seleccionar libremente el estado del documento al crear:**
- `pendiente` - Documento en espera de revisión
- `aprobado` - Documento aprobado directamente
- `rechazado` - Documento rechazado directamente

✅ **Comportamiento al crear:**
```
Administrador sube documento + selecciona "Aprobado"
↓
Backend guarda con estado = "aprobado" (SIN cambios posteriores)
↓
Documento no puede ser editado (protegido)
```

✅ **Protección:** Una vez aprobado, el documento NO puede ser modificado

---

### Estudiante 👨‍🎓
✅ **El estado NO se muestra en el formulario (oculto)**

✅ **Backend ignora cualquier estado enviado:**
```
Estudiante sube documento (estado se ignora)
↓
Backend SIEMPRE guarda con estado = "pendiente"
↓
Documento espera revisión del administrador
```

✅ **Comportamiento actual MANTENIDO:**
- Solo puede subir en etapa "REGISTRO"
- No puede subir documentos tipo "ACTA"
- Si ya existe un documento rechazado, puede reenviar

---

## 🔧 CAMBIOS IMPLEMENTADOS

### 1. Backend - `documentos/serializers.py`

**Cambio:** Actualizar `DocumentoPostulacionCreateSerializer`

```python
class DocumentoPostulacionCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear/subir documentos.
    
    Permitir que admin seleccione el estado al crear.
    Estudiantes siempre tendrán estado='pendiente' (forzado aquí).
    """
    
    class Meta:
        model = DocumentoPostulacion
        # ✅ CAMBIO: Agregado 'estado' a los fields
        fields = ['postulacion', 'tipo_documento', 'archivo', 'estado']
    
    def save(self, **kwargs):
        """
        Guardar documento.
        
        REGLA DE NEGOCIO:
        - Admin: puede seleccionar cualquier estado (pendiente, aprobado, rechazado)
        - Estudiante: siempre se guarda como 'pendiente'
        """
        request = self.context.get('request')
        
        # Verificar si el usuario es admin/privilegiado
        is_admin = (
            request and request.user and (
                request.user.has_perm('documentos.add_documentopostulacion') or
                request.user.has_perm('documentos.change_documentopostulacion')
            )
        )
        
        # Si es estudiante, forzar estado='pendiente' y sin revisor
        if not is_admin:
            kwargs['estado'] = 'pendiente'
            kwargs['revisado_por'] = None
            kwargs['fecha_revision'] = None
        
        return super().save(**kwargs)
```

**¿Por qué?**
- El campo `estado` ahora se acepta en la entrada
- La lógica de permisos valida si es admin o estudiante
- Los estudiantes SIEMPRE guardan como 'pendiente', independientemente de lo que envíen

---

### 2. Frontend - `frontend/src/pages/Documentos.jsx`

**Estado:** ✅ **NO REQUIERE CAMBIOS**

El formulario ya está configurado correctamente:
```javascript
{!isStudent && (
  <FormField
    label="Estado"
    name="estado"
    type="select"
    value={formData.estado}
    onChange={handleInputChange}
    options={ESTADO_DOCUMENTO_OPTIONS}
    className="md:col-span-2"
  />
)}
```

✅ El campo se muestra SOLO para admin (`!isStudent`)  
✅ Permite seleccionar: Pendiente, Aprobado, Rechazado  
✅ El valor por defecto es 'pendiente'

---

## 📊 FLUJO DE DATOS

### Caso 1: Administrador crea documento aprobado

```
┌─ Frontend ─────────────────────────────────────┐
│ Form:                                           │
│  - Postulación: "Juan - Tesis"                 │
│  - Tipo Documento: "Proposal"                  │
│  - Estado: "Aprobado" ← SELECCIONADO           │
│  - Archivo: propuesta.pdf                      │
└─────────────────────────────────────────────────┘
           ↓
┌─ POST /api/documentos/ ────────────────────────┐
│ {                                               │
│   "postulacion": 1,                            │
│   "tipo_documento": 5,                         │
│   "estado": "aprobado",  ← ADMIN LO ENVÍA    │
│   "archivo": <file>                           │
│ }                                              │
└─────────────────────────────────────────────────┘
           ↓
┌─ Backend - DocumentoPostulacionCreateSerializer┐
│ save() verifica:                               │
│ - is_admin = True (tiene permisos)            │
│ - NO fuerza estado                            │
│ - Guarda con estado = "aprobado" ✓           │
└─────────────────────────────────────────────────┘
           ↓
┌─ Base de Datos ────────────────────────────────┐
│ DocumentoPostulacion:                          │
│ - estado = "aprobado"                         │
│ - estado NO cambia más                        │
│ - Protegido contra modificaciones             │
└─────────────────────────────────────────────────┘
```

---

### Caso 2: Estudiante sube documento

```
┌─ Frontend ─────────────────────────────────────┐
│ Form:                                           │
│  - Postulación: "Mi Postulación"              │
│  - Tipo Documento: "CV"                       │
│  - [Campo Estado OCULTO]                      │
│  - Archivo: cv.pdf                            │
└─────────────────────────────────────────────────┘
           ↓
┌─ POST /api/documentos/ ────────────────────────┐
│ {                                               │
│   "postulacion": 2,                            │
│   "tipo_documento": 3,                         │
│   "estado": "pendiente",  ← DEFAULT            │
│   "archivo": <file>                           │
│ }                                              │
└─────────────────────────────────────────────────┘
           ↓
┌─ Backend - DocumentoPostulacionCreateSerializer┐
│ save() verifica:                               │
│ - is_admin = False (estudiante)               │
│ - FUERZA estado = "pendiente"                 │
│ - Guarda con estado = "pendiente" ✓          │
│ - revisado_por = None                         │
│ - fecha_revision = None                       │
└─────────────────────────────────────────────────┘
           ↓
┌─ Base de Datos ────────────────────────────────┐
│ DocumentoPostulacion:                          │
│ - estado = "pendiente"                        │
│ - Espera revisión de admin                    │
│ - Puede reenviarse si es rechazado            │
└─────────────────────────────────────────────────┘
```

---

## 🔒 VALIDACIONES ADICIONALES

### Documento Aprobado (Protección)
```python
# En perform_update() - línea 150 de views.py
if instancia_anterior.estado == 'aprobado':
    raise ValidationError('No se puede modificar un documento aprobado.')
```
✅ Impide cualquier cambio a un documento aprobado

---

### Cambio a Aprobado (Requiere Permisos)
```python
# En perform_update() - línea 159 de views.py
if nuevo_estado == 'aprobado' and estado_anterior != 'aprobado':
    permiso = PuedeAprobarDocumentosPermission()
    if not permiso.has_permission(self.request, self):
        raise PermissionDenied(permiso.message)
```
✅ Solo usuarios con permiso `documentos.puede_aprobar_documentos` pueden cambiar a aprobado

---

## ✅ VERIFICACIÓN

### Checklist de Funcionalidad

| Escenario | Resultado | Evidencia |
|-----------|-----------|-----------|
| Admin crea doc con estado='aprobado' | ✅ Guarda | Serializer.save() no fuerza 'pendiente' para admin |
| Admin crea doc con estado='rechazado' | ✅ Guarda | Same as above |
| Admin crea doc con estado='pendiente' | ✅ Guarda | Same as above |
| Estudiante intenta enviar estado='aprobado' | ✅ Ignora | Serializer.save() fuerza 'pendiente' |
| Documento aprobado se intenta editar | ❌ Error | ValidationError en perform_update() |
| Estudiante ve campo estado en formulario | ❌ Oculto | Condicional `{!isStudent && (...)}` |

---

## 📝 NOTAS IMPORTANTES

1. **No se modificaron endpoints** ✅  
   - POST `/api/documentos/` - Igual
   - PATCH `/api/documentos/{id}/` - Igual

2. **Cambios mínimos en serializers** ✅  
   - Solo se agregó `estado` al campo fields
   - Solo se agregó método save() para validar permisos

3. **No se agregó nueva lógica de permisos** ✅  
   - Se usa `has_perm()` existente
   - Se valida admin vs estudiante en el serializer

4. **Funcionalidad existente mantenida** ✅  
   - Estudiantes siguen funcionando igual
   - Bloqueos de etapa REGISTRO
   - Bloqueos de documentos tipo ACTA

---

## 🚀 DEPLOYMENT

1. Commit de cambios en `documentos/serializers.py`
2. No se requiere migración de datos
3. No se requiere cambios en frontend
4. No se requiere cambios en configuración

---

**Implementación completada exitosamente.** 🎉
