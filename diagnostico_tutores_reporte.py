#!/usr/bin/env python
"""
Diagnóstico: Verificar datos reales de tutores y etapas en la BD
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from postulantes.models import Postulacion
from modalidades.models import Etapa
from django.db.models import Count, Q

print("=" * 80)
print("DIAGNÓSTICO: REPORTE DE TUTORES Y ETAPAS")
print("=" * 80)

# 1. Verificar todas las etapas disponibles
print("\n1️⃣  ETAPAS DISPONIBLES EN LA BD:")
print("-" * 80)
etapas = Etapa.objects.all().select_related('modalidad')
for etapa in etapas:
    print(f"  ID={etapa.id:3d} | Nombre: '{etapa.nombre}' | Modalidad: {etapa.modalidad.nombre} | Orden: {etapa.orden}")

# 2. Verificar postulaciones con tutores asignados
print("\n2️⃣  POSTULACIONES CON TUTORES ASIGNADOS:")
print("-" * 80)
postulaciones_con_tutor = Postulacion.objects.exclude(tutor__isnull=True).exclude(tutor='').select_related('etapa_actual', 'modalidad')
print(f"Total postulaciones con tutor: {postulaciones_con_tutor.count()}")

for post in postulaciones_con_tutor[:20]:  # Mostrar primeras 20
    etapa_nombre = post.etapa_actual.nombre if post.etapa_actual else "NULL"
    etapa_id = post.etapa_actual.id if post.etapa_actual else "NULL"
    print(f"  ID={post.id:3d} | Tutor: '{post.tutor}' | Estado: {post.estado} | Estado General: {post.estado_general}")
    print(f"         | Etapa Actual: ID={etapa_id} | Nombre: '{etapa_nombre}' | Modalidad: {post.modalidad.nombre}")

# 3. Buscar postulaciones con etapa "Modalidad Finalizada"
print("\n3️⃣  BÚSQUEDA: Etapas con nombre 'Modalidad Finalizada':")
print("-" * 80)
modalidad_finalizada_etapas = Etapa.objects.filter(nombre__iexact='Modalidad Finalizada')
print(f"Etapas encontradas: {modalidad_finalizada_etapas.count()}")
for etapa in modalidad_finalizada_etapas:
    print(f"  ID={etapa.id} | Nombre exacto: '{etapa.nombre}' | Modalidad: {etapa.modalidad.nombre}")

# 4. Contar postulaciones con etapa "Modalidad Finalizada" por tutor
print("\n4️⃣  POSTULACIONES CON ETAPA 'Modalidad Finalizada' POR TUTOR:")
print("-" * 80)
postulaciones_modalidad_fin = Postulacion.objects.filter(
    etapa_actual__nombre__iexact='Modalidad Finalizada'
).exclude(tutor__isnull=True).exclude(tutor='')
print(f"Total postulaciones con etapa 'Modalidad Finalizada': {postulaciones_modalidad_fin.count()}")

tutores_stats = (
    postulaciones_modalidad_fin
    .values('tutor')
    .annotate(total=Count('id'))
    .order_by('-total')
)
for item in tutores_stats:
    print(f"  Tutor: '{item['tutor']}' | Postulaciones con Modalidad Finalizada: {item['total']}")

# 5. Estadísticas completas de tutores (la lógica actual del reporte)
print("\n5️⃣  ESTADÍSTICAS ACTUALES DEL REPORTE (lógica actual):")
print("-" * 80)
stats = (
    Postulacion.objects
    .exclude(tutor__isnull=True)
    .exclude(tutor='')
    .values('tutor')
    .annotate(
        modalidades_finalizadas=Count('id', filter=Q(etapa_actual__nombre__iexact='Modalidad Finalizada')),
        rechazados=Count('id', filter=Q(estado='rechazada')),
        total_asignadas=Count('id'),
    )
    .order_by('-modalidades_finalizadas', '-total_asignadas')
)

for item in stats:
    print(f"  Tutor: '{item['tutor']}'")
    print(f"    - Modalidades Finalizadas: {item['modalidades_finalizadas']}")
    print(f"    - Rechazadas: {item['rechazados']}")
    print(f"    - Total Asignadas: {item['total_asignadas']}")

# 6. Buscar todas las variantes de nombres de etapas que contengan "finaliz" o "fin"
print("\n6️⃣  BÚSQUEDA: Etapas con nombres similares a 'finalizada':")
print("-" * 80)
similar_etapas = Etapa.objects.filter(nombre__icontains='final')
print(f"Etapas encontradas: {similar_etapas.count()}")
for etapa in similar_etapas:
    count = Postulacion.objects.filter(etapa_actual=etapa).exclude(tutor__isnull=True).exclude(tutor='').count()
    print(f"  ID={etapa.id:3d} | Nombre: '{etapa.nombre}' | Postulaciones con tutor: {count}")

# 7. Debug: mostrar exactamente qué se está comparando
print("\n7️⃣  DEBUG: Comparación de cadenas:")
print("-" * 80)
test_postulaciones = Postulacion.objects.exclude(tutor__isnull=True).exclude(tutor='').select_related('etapa_actual')[:5]
for post in test_postulaciones:
    if post.etapa_actual:
        etapa_nombre = post.etapa_actual.nombre or ""
        print(f"  Post ID={post.id} | Etapa nombre: '{etapa_nombre}'")
        print(f"    - Comparar con 'Modalidad Finalizada' (iexact): {etapa_nombre.lower() == 'modalidad finalizada'.lower()}")
        print(f"    - .iexact() match: {Postulacion.objects.filter(etapa_actual=post.etapa_actual, etapa_actual__nombre__iexact='Modalidad Finalizada').exists()}")

print("\n" + "=" * 80)
print("FIN DEL DIAGNÓSTICO")
print("=" * 80)
