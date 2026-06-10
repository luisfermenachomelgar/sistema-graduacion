#!/usr/bin/env python
"""
Análisis detallado de Modalidades y sus flujos académicos esperados
Busca referencias en documentos, requisitos y descripciones existentes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from modalidades.models import Modalidad, Etapa, ModalidadRequisito
from documentos.models import TipoDocumento

print("\n" + "=" * 100)
print("ANÁLISIS DETALLADO: FLUJOS ACADÉMICOS Y REQUISITOS POR MODALIDAD")
print("=" * 100)

# ============================================================================
# 1. DESCRIPCIÓN ACTUAL DE MODALIDADES
# ============================================================================

print("\n📚 DESCRIPCIONES ACTUALES DE MODALIDADES EN EL SISTEMA:\n")

for modalidad in Modalidad.objects.all():
    print(f"▸ {modalidad.nombre}")
    print(f"  Descripción: {modalidad.descripcion}")
    print()

# ============================================================================
# 2. ANÁLISIS DE REQUISITOS POR MODALIDAD
# ============================================================================

print("=" * 100)
print("REQUISITOS EXISTENTES POR MODALIDAD")
print("=" * 100)

for modalidad in Modalidad.objects.prefetch_related('requisitos'):
    print(f"\n📋 {modalidad.nombre}:")
    requisitos = modalidad.requisitos.all()
    
    if requisitos.exists():
        for req in requisitos:
            print(f"  • {req.nombre}")
            print(f"    Categoría: {req.categoria}")
            print(f"    Obligatorio: {'Sí' if req.obligatorio else 'No'}")
            if req.descripcion:
                print(f"    Descripción: {req.descripcion}")
    else:
        print("  (sin requisitos definidos)")

# ============================================================================
# 3. ANÁLISIS DE TIPOS DE DOCUMENTOS POR ETAPA
# ============================================================================

print("\n" + "=" * 100)
print("TIPOS DE DOCUMENTOS ASOCIADOS A ETAPAS")
print("=" * 100)

print("\n📄 Documentos vinculados a etapas:\n")

for modalidad in Modalidad.objects.prefetch_related('etapas'):
    print(f"\n▸ {modalidad.nombre}:")
    etapas = modalidad.etapas.all()
    
    if etapas.exists():
        for etapa in etapas:
            docs = etapa.tipos_documento.all()
            print(f"  Etapa {etapa.orden}: {etapa.nombre}")
            if docs.exists():
                for doc in docs:
                    print(f"    - {doc.nombre} (Obligatorio: {'Sí' if doc.obligatorio else 'No'})")
            else:
                print(f"    (sin documentos asociados)")
    else:
        print("  (sin etapas - no hay documentos vinculados)")

# ============================================================================
# 4. ETAPA ACTUAL EN POSTULACIONES
# ============================================================================

print("\n" + "=" * 100)
print("POSTULACIONES Y ETAPAS ACTUALES")
print("=" * 100)

from postulantes.models import Postulacion

postulaciones_por_modalidad = {}
for post in Postulacion.objects.select_related('modalidad', 'etapa_actual'):
    mod_nombre = post.modalidad.nombre
    if mod_nombre not in postulaciones_por_modalidad:
        postulaciones_por_modalidad[mod_nombre] = []
    postulaciones_por_modalidad[mod_nombre].append({
        'postulante': post.postulante.get_full_name(),
        'etapa': post.etapa_actual.nombre if post.etapa_actual else '(Sin etapa)',
        'estado': post.estado,
    })

for modalidad, posts in sorted(postulaciones_por_modalidad.items()):
    print(f"\n▸ {modalidad}: {len(posts)} postulaciones")
    for post in posts:
        print(f"  • {post['postulante']}")
        print(f"    Etapa actual: {post['etapa']}")
        print(f"    Estado: {post['estado']}")

# ============================================================================
# 5. COMPARACIÓN CON TESIS DE GRADO (REFERENCIA)
# ============================================================================

print("\n" + "=" * 100)
print("MODALIDAD DE REFERENCIA: TESIS DE GRADO (Completamente configurada)")
print("=" * 100)

tesis = Modalidad.objects.get(nombre='Tesis de Grado')
print(f"\nDescripción: {tesis.descripcion}\n")

print("Etapas definidas:")
for etapa in tesis.etapas.all():
    print(f"  {etapa.orden}. {etapa.nombre}")
    docs = etapa.tipos_documento.all()
    if docs.exists():
        print(f"     Documentos requeridos:")
        for doc in docs:
            print(f"       - {doc.nombre}")

# ============================================================================
# 6. PROPUESTA ACTUAL VS REFERENCIAS DEL SISTEMA
# ============================================================================

print("\n" + "=" * 100)
print("ANÁLISIS: ¿DE DÓNDE VIENEN LOS NOMBRES PROPUESTOS?")
print("=" * 100)

propuesta_actual = {
    'Proyecto de Grado': [
        'Propuesta de Proyecto',
        'Desarrollo del Proyecto',
        'Defensa de Proyecto',
    ],
    'Examen de Grado': [
        'Inscripción al Examen',
        'Realización del Examen',
        'Evaluación Tribunal',
    ],
    'Vía Diplomado': [
        'Inscripción Diplomado',
        'Cursada del Diplomado',
        'Defensa Monografía',
    ],
}

print("\n📝 ORIGEN DE NOMBRES PROPUESTOS:\n")

for mod_nombre, etapas in propuesta_actual.items():
    print(f"▸ {mod_nombre}:")
    print("  Origen: PROPUESTOS POR DEFECTO (No existen en el sistema)")
    print("  Basados en: Flujo académico lógico esperado")
    print("  Etapas propuestas:")
    for i, etapa in enumerate(etapas, 1):
        print(f"    {i}. {etapa}")
    print()

print("\nℹ️  NOTA: No se encontraron referencias específicas en el código")
print("    que definan etapas para estas modalidades.")
print("    Los nombres propuestos se basan en flujos académicos estándar.")

print("\n" + "=" * 100)
