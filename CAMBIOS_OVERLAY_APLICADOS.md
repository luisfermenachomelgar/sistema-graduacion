# Cambios Aplicados - Eliminación de Overlay Fullscreen

**Fecha:** 15 de mayo de 2026  
**Objetivo:** Render progresivo sin bloqueo de UI fullscreen

---

## ✅ Cambios Realizados

### Core (GlobalLoader)
| Archivo | Cambio |
|---------|--------|
| `frontend/src/components/ui/GlobalLoader.jsx` | Agregado `hasShownContentRef` para evitar que overlay reaparezca después de renderizar contenido |
| `frontend/src/context/LoaderContext.jsx` | Sin cambios (ya funcional) |

### Páginas - Optimización de Requests

| Página | Cambio | Detalles |
|--------|--------|----------|
| **Dashboard** | ✓ Reorden flujo | `setLoading(false)` antes de `fetchDashboardStatsInBackground()` |
| **Dashboard** | ✓ Always render | `<StatsCards>` renderiza siempre (con 0 inicial) |
| **Postulantes** | ✓ Tabla primaria | `list()` ahora DEFAULT (mostrará overlay) |
| **Postulantes** | ✓ Dropdown secundario | `fetchUsuarios()` con `skipGlobalLoader: true` |
| **Postulaciones** | ✓ Dropdowns secundarios | Both `fetchData()` requests con `skipGlobalLoader: true` |
| **Documentos** | ✓ Dropdowns secundarios | Both `fetchDropdownData()` requests con `skipGlobalLoader: true` |
| **Modalidades** | - | Solo `list()`, ya optimizada |
| **Usuarios** | - | Solo `list()`, ya optimizada |
| **Reportes** | - | Único request apropiado con overlay |

---

## 🔄 Comportamiento Esperado por Página

### Dashboard
1. Datos principales cargan rápido (postulantes + gráficos)
2. `loading=false` → UI visible
3. Stats se hidratan silenciosamente
4. **Sin overlay reaparición**

### Postulantes, Postulaciones, Documentos
1. Tabla/contenido principal carga con overlay (normal)
2. Una vez visible, overlay desaparece
3. Dropdowns/selects se cargan en background
4. **SIN reaparición de overlay**

### Modalidades, Usuarios
1. Funcionan igual (simple list)
2. Overlay normal durante carga

---

## 📋 Checklist de Verificación

```
[ ] Dashboard carga sin overlay fullscreen
[ ] Postulantes tabla visible rápidamente
[ ] Postulaciones tabla visible rápidamente
[ ] Documentos tabla visible rápidamente
[ ] Overlay NO reaparece durante actualizaciones secundarias
[ ] Navbar/Sidebar SIEMPRE visibles
[ ] Dropdowns se rellenan sin bloqueo
[ ] No hay parpadeos o flickering
```

---

## 🚀 Próximas Validaciones

1. Probar en todos los navegadores principales
2. Verificar carga en conexión lenta (throttle)
3. Confirmar que no hay race conditions
4. Validar performance en mobile

---

## 📝 Notas Técnicas

- **GlobalLoader**: Usa `useRef` para prevenir reaparición después de primer render
- **Axios**: Respeta `skipGlobalLoader: true` en requestConfig
- **useCrud**: Maneja loading para operación principal
- **Patrón aplicado**: Requests primarias con overlay, secundarias sin overlay

