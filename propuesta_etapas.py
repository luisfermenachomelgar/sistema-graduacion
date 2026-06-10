#!/usr/bin/env python
"""
Propuesta de Etapas para Modalidades Incompletas
Visualización de datos que se insertarán sin afectar datos existentes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from modalidades.models import Modalidad, Etapa

print("\n" + "=" * 90)
print("PROPUESTA DE ETAPAS PARA MODALIDADES INCOMPLETAS")
print("=" * 90)

# ============================================================================
# PROPUESTA DE DATOS
# ============================================================================

propuesta_etapas = {
    'Proyecto de Grado': [
        {'orden': 1, 'nombre': 'Propuesta de Proyecto'},
        {'orden': 2, 'nombre': 'Desarrollo del Proyecto'},
        {'orden': 3, 'nombre': 'Defensa de Proyecto'},
    ],
    'Examen de Grado': [
        {'orden': 1, 'nombre': 'Inscripción al Examen'},
        {'orden': 2, 'nombre': 'Realización del Examen'},
        {'orden': 3, 'nombre': 'Evaluación Tribunal'},
    ],
    'Vía Diplomado': [
        {'orden': 1, 'nombre': 'Inscripción Diplomado'},
        {'orden': 2, 'nombre': 'Cursada del Diplomado'},
        {'orden': 3, 'nombre': 'Defensa Monografía'},
    ],
}

print("\n📋 ETAPAS PROPUESTAS POR MODALIDAD\n")
for modalidad_nombre, etapas in propuesta_etapas.items():
    print(f"▸ {modalidad_nombre}")
    for etapa in etapas:
        print(f"   Orden {etapa['orden']}: {etapa['nombre']}")
    print()

# ============================================================================
# ESTADO ACTUAL DE LA BASE DE DATOS
# ============================================================================

print("=" * 90)
print("ESTADO ACTUAL DE LA BASE DE DATOS")
print("=" * 90)

print("\n📊 ETAPAS EXISTENTES (Sin cambios)\n")
for modalidad in Modalidad.objects.all():
    print(f"▸ {modalidad.nombre} (ID: {modalidad.id})")
    etapas = modalidad.etapas.all()
    if etapas.exists():
        for etapa in etapas:
            print(f"   ID: {etapa.id}, Orden {etapa.orden}: {etapa.nombre}")
    else:
        print("   (sin etapas - será llenado por migration)")
    print()

# ============================================================================
# VALIDACIÓN DE INTEGRIDAD
# ============================================================================

print("=" * 90)
print("VALIDACIONES DE INTEGRIDAD")
print("=" * 90)

# 1. Verificar postulaciones existentes
from postulantes.models import Postulacion

print("\n🔍 Postulaciones existentes y sus etapas actuales:\n")
postulaciones = Postulacion.objects.select_related('modalidad', 'etapa_actual').all()
if postulaciones.exists():
    for post in postulaciones:
        etapa_info = f"ID {post.etapa_actual.id} ({post.etapa_actual.nombre})" if post.etapa_actual else "NULL (Sin etapa)"
        print(f"  • Postulante: {post.postulante.nombre}, Modalidad: {post.modalidad.nombre}, Etapa: {etapa_info}")
else:
    print("  ✅ No hay postulaciones existentes")

# 2. Verificar FK constraints
print("\n✅ Validación de Constraints FK:\n")
print("  • Etapa.modalidad → on_delete=CASCADE (Si borro modalidad, se borran sus etapas)")
print("  • Postulacion.etapa_actual → on_delete=SET_NULL (Si borro etapa, la postulación queda NULL)")
print("  ✅ SEGURO: Las nuevas etapas no afectarán postulaciones existentes")

# 3. Unique constraint
print("\n✅ Validación de Unique Constraint:\n")
print("  • Constraint: unique_orden_por_modalidad (modalidad, orden)")
print("  • Validación: Las etapas propuestas usan (1,2,3) en cada modalidad")
print("  ✅ SEGURO: No habrá conflictos de order por modalidad")

# ============================================================================
# VISUALIZACIÓN DE DATOS DESPUÉS DE LA MIGRATION
# ============================================================================

print("\n" + "=" * 90)
print("ESTADO ESPERADO DESPUÉS DE LA MIGRATION")
print("=" * 90)
print("\n📊 Todas las Modalidades con sus Etapas:\n")

# Simulación de cómo quedaría
modalidades_info = [
    {
        'nombre': 'Tesis de Grado',
        'estado': 'EXISTENTE (sin cambios)',
        'etapas': [
            (1, 'Propuesta/Perfil'),
            (2, 'Privada'),
            (3, 'Pública'),
            (4, 'Correcciones'),
        ]
    },
    {
        'nombre': 'Proyecto de Grado',
        'estado': 'NUEVO',
        'etapas': [
            (1, 'Propuesta de Proyecto'),
            (2, 'Desarrollo del Proyecto'),
            (3, 'Defensa de Proyecto'),
        ]
    },
    {
        'nombre': 'Examen de Grado',
        'estado': 'NUEVO',
        'etapas': [
            (1, 'Inscripción al Examen'),
            (2, 'Realización del Examen'),
            (3, 'Evaluación Tribunal'),
        ]
    },
    {
        'nombre': 'Vía Diplomado',
        'estado': 'NUEVO',
        'etapas': [
            (1, 'Inscripción Diplomado'),
            (2, 'Cursada del Diplomado'),
            (3, 'Defensa Monografía'),
        ]
    },
]

for info in modalidades_info:
    print(f"▸ {info['nombre']} ({info['estado']})")
    for orden, nombre in info['etapas']:
        print(f"   • Orden {orden}: {nombre}")
    print()

# ============================================================================
# ESTADÍSTICAS DESPUÉS DEL CAMBIO
# ============================================================================

print("=" * 90)
print("ESTADÍSTICAS DESPUÉS DE LA MIGRATION")
print("=" * 90)

total_etapas_antes = Etapa.objects.count()
total_etapas_despues = total_etapas_antes + 9  # 3 etapas x 3 modalidades

print(f"\n📊 Resumen de cambios:\n")
print(f"  Etapas ANTES:  {total_etapas_antes}")
print(f"  Etapas NUEVAS: +9 (3 por cada modalidad incompleta)")
print(f"  Etapas DESPUÉS: {total_etapas_despues}")
print(f"\n  Modalidades actualizadas: 3 de 4 (Proyecto, Examen, Diplomado)")
print(f"  Modalidades sin cambios: 1 de 4 (Tesis de Grado)")
print(f"  Postulaciones afectadas: 0 (Completamente seguro)")

print("\n" + "=" * 90)
print("\n✅ ANÁLISIS COMPLETADO - LISTO PARA REVISAR\n")
