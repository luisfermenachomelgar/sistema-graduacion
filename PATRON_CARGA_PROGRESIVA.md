# Patrón de Carga Progresiva - Eliminación de Overlay Fullscreen

## Objetivo
Eliminar overlay fullscreen global que bloquea UI en páginas, permitiendo que contenido sea usable inmediatamente mientras requests secundarias se hidratan en background.

## Problema Identificado
- GlobalLoader permanecía visible mientras requests secundarias estaban en vuelo
- Overlay bloqueaba UI aunque contenido principal ya estuviera renderizado
- Efecto: UI se sentía congelada aunque datos estuvieran disponibles

## Solución Implementada (3 cambios mínimos)

### 1. Dashboard.jsx - Reorden de Carga
```javascript
// ANTES (problema):
await Promise.all([primary_request_1, primary_request_2]);
await fetchSecondaryRequest(); // ← Bloquea loading
setLoading(false);

// DESPUÉS (solucionado):
await Promise.all([primary_request_1, primary_request_2]);
setLoading(false); // ← UI visible inmediatamente
fetchSecondaryRequest(); // ← En background, no bloquea
```

### 2. GlobalLoader.jsx - Prevención de Reaparición
```javascript
// Agregar useRef para prevenir que overlay reaparezca después de mostrarse
const hasShownContentRef = useRef(false);

// Si contenido ya fue mostrado, overlay no se reactiva para requests secundarias
if (!hasShownContentRef.current) {
  setShowLoader(true);
}
```

### 3. Dashboard.jsx - Renderizar Siempre
```javascript
// ANTES: Mostrar components SOLO si datos disponibles
{dashboardStats && <StatsCards stats={...} />}

// DESPUÉS: Mostrar components siempre (con 0 inicialmente)
<StatsCards stats={dashboardStats ? {...} : {}} />
```

## Checklist de Implementación

Para cada página (Postulantes, Postulaciones, Documentos, Modalidades, Usuarios, Reportes):

- [ ] Identificar requests primarias (críticas para renderizar contenido básico)
- [ ] Identificar requests secundarias (stats, métricas, datos adicionales)
- [ ] Mover `setLoading(false)` ANTES de requests secundarias
- [ ] Hacer requests secundarias con `.then()` o `async/await` sin await en flujo principal
- [ ] Renderizar componentes SIEMPRE (permitir valores iniciales 0/null)
- [ ] Verificar visualmente que UI sea usable inmediatamente

## Beneficios

✓ UI instantáneamente usable
✓ Navbar/Sidebar siempre accesibles
✓ SIN overlay bloqueando
✓ Carga progresiva natural
✓ UX moderna y responsiva
✓ Cambios mínimos, sin refactor
✓ NO requiere cambios en backend

## Ejemplo Completo: Dashboard

**Cambios en `/frontend/src/pages/Dashboard.jsx`:**

1. En `fetchDashboardData()`:
   - Ejecutar `Promise.all()` con requests primarias
   - Setear `loading=false`
   - Luego llamar `fetchDashboardStatsInBackground()` sin await

2. En render:
   - `<StatsCards stats={dashboardStats ? {...} : {}} />` (siempre renderizar)
   - Charts usan mock data hasta que se hidraten

3. En `GlobalLoader.jsx`:
   - Agregar `hasShownContentRef` para evitar reaparición

---

## Próximas Páginas

Aplicar el MISMO patrón a:
- [ ] Postulantes
- [ ] Postulaciones
- [ ] Documentos
- [ ] Modalidades
- [ ] Usuarios
- [ ] Reportes

Cada página seguirá el mismo flujo:
1. Requests primarias (necesarias para contenido básico)
2. `setLoading(false)` - UI visible
3. Requests secundarias en background - datos hidratan silenciosamente
