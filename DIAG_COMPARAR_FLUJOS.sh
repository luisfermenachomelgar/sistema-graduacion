#!/bin/bash
# Diagnóstico visual del problema: Proyecto de Grado vs Examen de Grado

echo "═══════════════════════════════════════════════════════════════════════"
echo "COMPARACIÓN: VALIDACIÓN DE DOCUMENTOS POR ETAPA"
echo "═══════════════════════════════════════════════════════════════════════"

docker compose exec db psql -U sistema_user -d sistema_graduacion << 'EOF'

-- Mostrar lado a lado la comparación
SELECT 
  m.nombre AS modalidad,
  e.orden,
  e.nombre AS etapa,
  COUNT(mtd.id) FILTER (WHERE mtd.obligatorio = true AND mtd.activo = true) as docs_obligatorios,
  COUNT(mtd.id) FILTER (WHERE mtd.obligatorio = false AND mtd.activo = true) as docs_opcionales
FROM modalidades_etapa e
JOIN modalidades_modalidad m ON e.modalidad_id = m.id
LEFT JOIN documentos_modalidadtipodocumento mtd ON mtd.etapa_id = e.id
WHERE m.nombre IN ('EXAMEN DE GRADO', 'PROYECTO DE GRADO')
GROUP BY m.id, m.nombre, e.id, e.orden, e.nombre
ORDER BY m.nombre, e.orden;

EOF

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "ANÁLISIS"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "EXAMEN DE GRADO:"
echo "  ✅ Todas las 6 etapas tienen AL MENOS 1 documento obligatorio"
echo "  ✅ Validación en avanzar_postulacion() bloquea etapas sin documentos aprobados"
echo ""
echo "PROYECTO DE GRADO:"
echo "  ✅ Etapas 1, 2, 3, 6 tienen documentos obligatorios"
echo "  ❌ Etapas 4 (Defensa Privada) y 5 (Defensa Pública) ESTÁN VACÍAS"
echo "  ❌ Validación no puede bloquear porque no hay documentos para validar"
echo ""
echo "CONCLUSIÓN:"
echo "  La lógica de código es idéntica (required_documents_missing() retorna [])"
echo "  El problema es la CONFIGURACIÓN: faltan documentos en las etapas 4 y 5"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "DOCUMENTOS DISPONIBLES EN PROYECTO DE GRADO"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

docker compose exec db psql -U sistema_user -d sistema_graduacion << 'EOF'

SELECT 
  e.orden,
  e.nombre AS etapa,
  td.id,
  td.nombre AS documento,
  mtd.obligatorio,
  CASE WHEN mtd.id IS NULL THEN 'NO ASIGNADO' ELSE 'ASIGNADO' END as estado
FROM modalidades_etapa e
LEFT JOIN documentos_modalidadtipodocumento mtd ON mtd.etapa_id = e.id
LEFT JOIN documentos_tipodocumento td ON mtd.tipo_documento_id = td.id
WHERE e.modalidad_id = (SELECT id FROM modalidades_modalidad WHERE nombre = 'PROYECTO DE GRADO')
ORDER BY e.orden, td.nombre;

EOF

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "SOLUCIÓN RECOMENDADA"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "Agregar a la base de datos:"
echo ""
echo "INSERT INTO documentos_modalidadtipodocumento"
echo "  (modalidad_id, tipo_documento_id, etapa_id, obligatorio, activo, orden)"
echo "VALUES"
echo "  (1, (SELECT id FROM documentos_tipodocumento WHERE nombre = 'Acta de Defensa del Proyecto de Grado.'), 23, true, true, 1),"
echo "  (1, (SELECT id FROM documentos_tipodocumento WHERE nombre = 'Acta de Defensa del Proyecto de Grado.'), 24, true, true, 1);"
echo ""
echo "Esto permitirá que la validación en avanzar_postulacion() bloquee el avance sin documentos"
echo ""
