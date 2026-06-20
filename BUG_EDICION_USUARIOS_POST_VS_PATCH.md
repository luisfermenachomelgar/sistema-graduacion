# 🐛 BUG ENCONTRADO: Editar Usuario Envía POST en Lugar de PATCH

## 📊 Resumen del Problema

**Síntoma:** 
```
Al editar usuario "admin" sin cambiar username:
POST /api/usuarios/   ❌ (debería ser PATCH /api/usuarios/1/)
Response: "username: A user with that username already exists."
```

**Causa:** El frontend está en modo creación cuando debería estar en modo edición.

---

## 🔍 Análisis del Flujo

### Flujo Esperado (CORRECTO)
```
1. Usuario hace click en Editar
2. Modal se abre con isEditMode = true
3. handleSubmit() valida isEditMode === true
4. Ejecuta: await patch(endpoint, payload)
5. Backend recibe PATCH /api/usuarios/1/
6. ✅ Usuario actualizado exitosamente
```

### Flujo Actual (INCORRECTO)
```
1. Usuario hace click en Editar
2. Modal se abre con isEditMode = false  ❌
3. handleSubmit() valida isEditMode === false
4. Ejecuta: await create(payload)  ❌
5. Backend recibe POST /api/usuarios/
6. ❌ "username already exists" error
```

---

## 🎯 Código Responsable del Bug

### Paso 1: Hook useModal.js - LÓGICA CORRECTA ✅

**Archivo:** `frontend/src/hooks/useModal.js` (línea 13)
```javascript
const openModal = (data = null) => {
  if (data) {
    setFormData(data);
    setIsEditMode(true);   // ✅ Se activa si data se pasa
  } else {
    setFormData(initialData || {});
    setIsEditMode(false);  // Se desactiva si data es null
  }
  setIsOpen(true);
};
```

**Lógica:**
- Si se pasa `data` → `isEditMode = true` (edición)
- Si NO se pasa nada → `isEditMode = false` (creación)

---

### Paso 2: Usuarios.jsx - CÓDIGO CON BUG ❌

**Archivo:** `frontend/src/pages/Usuarios.jsx` (línea 305)

**ANTES (INCORRECTO):**
```javascript
onEdit={(user) => {
  const userData = {
    ...user,
    password: '',
    id: user.id,
  };
  setFormData(userData);   // ← Aquí prepara los datos
  openModal();              // ❌ BUG: NO pasa userData a openModal()
  // openModal(null) implícitamente → isEditMode = false ❌
}}
```

**CONSECUENCIA:**
- `openModal()` no recibe parámetro
- `openModal()` hace `if (null)` → false
- `isEditMode` se queda en `false`
- Submit ejecuta `create()` en lugar de `patch()`

---

### Paso 3: handleSubmit() - LÓ GICA CORRECTA ✅

**Archivo:** `frontend/src/pages/Usuarios.jsx` (línea 88)
```javascript
const endpoint = isEditMode
  ? API_CONFIG.ENDPOINTS.USUARIO_DETAIL(formData.id)  // /api/usuarios/{id}/
  : API_CONFIG.ENDPOINTS.USUARIOS;                    // /api/usuarios/

const result = isEditMode
  ? await patch(endpoint, payload)    // PATCH correcto
  : await create(payload);            // POST para creación
```

**Lógica:** Depende de `isEditMode` que estaba en `false` debido al bug.

---

## ✅ SOLUCIÓN IMPLEMENTADA

**Archivo:** `frontend/src/pages/Usuarios.jsx` (línea 305)

**DESPUÉS (CORRECTO):**
```javascript
onEdit={(user) => {
  const userData = {
    ...user,
    password: '',
    id: user.id,
  };
  // ✅ CORRECCIÓN: Pasar userData a openModal()
  openModal(userData);
  // openModal(userData) → if (userData) true → isEditMode = true ✅
}}
```

**Resultado:**
- `openModal(userData)` recibe parámetro
- `openModal()` hace `if (userData)` → true ✅
- `isEditMode` se establece en `true` ✅
- Submit ejecuta `patch()` correctamente ✅

---

## 📈 Flujo Correcto Ahora

```
USUARIO HACE CLICK EN EDITAR
         ↓
onEdit={(user) => {
  userData = {...user, password: '', id: user.id}
  openModal(userData)  ← PASA userData
}}
         ↓
openModal(userData) recibe userData
         ↓
if (userData)  → TRUE ✅
  setFormData(userData)
  setIsEditMode(true)  ← AHORA SE ACTIVA
         ↓
Modal se abre con isEditMode = true
         ↓
Usuario modifica datos (o no)
         ↓
handleSubmit()
  if (isEditMode)  → TRUE ✅
    endpoint = /api/usuarios/1/
    result = await patch(endpoint, payload)
         ↓
PATCH /api/usuarios/1/
         ↓
✅ Usuario actualizado exitosamente
```

---

## 🧪 Verificación

### Escenario 1: Nuevo Usuario ✅
```javascript
onClick={() => {
  setFormData(INITIAL_FORM_DATA);
  openModal();  // ← No pasa parámetro
}}
// openModal() → isEditMode = false ✅
// handleSubmit → await create(payload) ✅
// POST /api/usuarios/ ✅
```

### Escenario 2: Editar Usuario ✅
```javascript
onEdit={(user) => {
  const userData = { ...user, password: '', id: user.id };
  openModal(userData);  // ← Pasa userData
}
// openModal(userData) → isEditMode = true ✅
// handleSubmit → await patch(endpoint, payload) ✅
// PATCH /api/usuarios/{id}/ ✅
```

---

## 📝 Resumen

| Aspecto | Antes | Después |
|--------|-------|---------|
| **openModal() recibe** | `null` | `userData` |
| **isEditMode** | `false` | `true` |
| **Método HTTP** | POST | PATCH |
| **Endpoint** | `/api/usuarios/` | `/api/usuarios/{id}/` |
| **Resultado** | ❌ Error "username already exists" | ✅ Usuario actualizado |

**Fix:** Una línea - cambiar `openModal()` a `openModal(userData)` en el manejador `onEdit`.
