"""
Script de verificación: ¿Qué endpoint llama el botón "Avanzar Etapa"?

Analiza el código del frontend para determinar exactamente qué petición HTTP se envía.
"""

# El código en Postulaciones.jsx muestra claramente:

# LÍNEA 272-289: handleAvanzarEtapa
"""
const handleAvanzarEtapa = async (postulacion) => {
    setError('');
    setSuccess('');

    try {
      const result = await api.create(API_CONFIG.ENDPOINTS.POSTULACION_AVANZAR_ETAPA(postulacion.id));
      if (result.success) {
        setSuccess('Postulación avanzada exitosamente');
        await refresh({
          errorMessage: 'Error al cargar postulaciones',
          exceptionMessage: 'Error loading postulaciones',
        });
      } else {
        setError(result.error || 'Error al avanzar la etapa');
      }
    } catch (err) {
      setError('Error al avanzar la etapa');
    }
  };
"""

# El botón "Avanzar Etapa" (línea 430) llama:
"""
onClick={() => handleAvanzarEtapa(row)}
"""

# Por lo tanto, el botón "Avanzar Etapa" usa:
# - api.create() 
# - API_CONFIG.ENDPOINTS.POSTULACION_AVANZAR_ETAPA(postulacion.id)

# Veamos qué es POSTULACION_AVANZAR_ETAPA en frontend/src/constants/api.js:
"""
POSTULACION_AVANZAR_ETAPA: (id) => `/api/postulaciones/${id}/avanzar-etapa/`,
"""

# api.create() en Axios hace una petición POST

# CONCLUSIÓN:
# El botón "Avanzar Etapa" envía:
# POST /api/postulaciones/{id}/avanzar-etapa/

# Este endpoint en postulantes/views.py (línea 154) es:
"""
@action(
    detail=True,
    methods=['post'],
    permission_classes=[PuedeAvanzarEtapaPermission],
    url_path='avanzar-etapa'
)
def avanzar_etapa(self, request, pk=None):
    postulacion = avanzar_postulacion(pk, actor=request.user)
    return Response(self.get_serializer(postulacion).data)
"""

# Que llama a avanzar_postulacion(pk) que VALIDA documentos obligatorios

print("=" * 80)
print("ANÁLISIS DE CÓDIGO: ¿Qué endpoint usa el botón 'Avanzar Etapa'?")
print("=" * 80)
print()
print("✅ PUNTO 1: En frontend/src/pages/Postulaciones.jsx línea 277:")
print("   const result = await api.create(API_CONFIG.ENDPOINTS.POSTULACION_AVANZAR_ETAPA(postulacion.id));")
print()
print("✅ PUNTO 2: En frontend/src/constants/api.js:")
print("   POSTULACION_AVANZAR_ETAPA: (id) => `/api/postulaciones/${id}/avanzar-etapa/`,")
print()
print("✅ PUNTO 3: api.create() en Axios realiza: POST")
print()
print("=" * 80)
print("CONCLUSIÓN:")
print("=" * 80)
print()
print("El botón 'Avanzar Etapa' envía:")
print()
print("   POST /api/postulaciones/{id}/avanzar-etapa/")
print("   Content-Type: application/json")
print("   Authorization: Bearer <token>")
print("   Body: (vacío)")
print()
print("Este endpoint VALIDA documentos obligatorios mediante:")
print("   avanzar_postulacion() → required_documents_missing()")
print()
print("=" * 80)
print("IMPLICACIÓN:")
print("=" * 80)
print()
print("Si el botón 'Avanzar Etapa' REALMENTE está siendo usado por los usuarios,")
print("entonces AMBAS modalidades (Examen y Proyecto) deberían validar igual.")
print()
print("Si Proyecto de Grado permite avanzar sin documentos, el problema está en:")
print()
print("  1) La lógica de required_documents_missing() - pero es idéntica")
print("  2) La lógica de avanzar_postulacion() - pero no tiene condicionales por modalidad")
print("  3) El queryset de ModalidadTipoDocumento - ETAPAS 4 y 5 ESTÁN VACÍAS")
print()
print("Por lo tanto, el problema REAL es que las etapas 4 y 5 de Proyecto de Grado")
print("no tienen documentos obligatorios configurados.")
print()
print("Cuando required_documents_missing() ejecuta:")
print()
print("  mtd_qs = ModalidadTipoDocumento.objects.filter(")
print("      modalidad_id=postulacion.modalidad_id,")
print("      obligatorio=True,")
print("      activo=True,")
print("  ).filter(Q(etapa_id=etapa.id) | Q(etapa__isnull=True))")
print()
print("  if not mtd_qs.exists():")
print("      return []  # ← Retorna [] porque NO hay documentos configurados")
print()
print("Y luego en avanzar_postulacion():")
print()
print("  if missing_docs:  # ← False porque [] es lista vacía")
print("      raise EtapaIncompletaError(...)  # ← No se levanta excepción")
print()
print("=" * 80)
