# Generated migration: Populate etapas for incomplete modalidades
# Date: 2026-06-10
# 
# Inserta 11 etapas nuevas (4 + 3 + 4) para las 3 modalidades incompletas:
# - Proyecto de Grado: 4 etapas
# - Examen de Grado: 3 etapas
# - Vía Diplomado: 4 etapas
#
# SEGURIDAD:
# ✅ Usa get_or_create() - idempotente, sin duplicados
# ✅ Respeta unique_orden_por_modalidad constraint
# ✅ No afecta postulaciones existentes (todas con etapa_actual=NULL)
# ✅ Completamente reversible

from django.db import migrations


def create_etapas(apps, schema_editor):
    """
    Crea etapas para modalidades incompletas.
    Usa get_or_create() para ser idempotente (seguro ejecutar múltiples veces).
    """
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    Etapa = apps.get_model('modalidades', 'Etapa')
    
    # ========================================================================
    # 1. PROYECTO DE GRADO (ID: 3) - 4 etapas
    # ========================================================================
    print("\n📌 Insertando etapas para Proyecto de Grado...")
    proyecto = Modalidad.objects.filter(nombre='Proyecto de Grado').first()
    if proyecto is None:
        print("⚠️ Modalidad 'Proyecto de Grado' no encontrada, omitiendo etapas.")
    else:
        etapas_proyecto = [
            {'orden': 1, 'nombre': 'Propuesta/Perfil'},
            {'orden': 2, 'nombre': 'Desarrollo del Proyecto'},
            {'orden': 3, 'nombre': 'Defensa de Proyecto'},
            {'orden': 4, 'nombre': 'Correcciones'},
        ]
        
        for etapa_data in etapas_proyecto:
            etapa, created = Etapa.objects.get_or_create(
                modalidad=proyecto,
                orden=etapa_data['orden'],
                defaults={
                    'nombre': etapa_data['nombre'],
                    'activo': True,
                }
            )
            status = "✓ CREADA" if created else "✓ EXISTE"
            print(f"  {status}: Orden {etapa_data['orden']} - {etapa_data['nombre']}")
        status = "✓ CREADA" if created else "✓ EXISTE"
        print(f"  {status}: Orden {etapa_data['orden']} - {etapa_data['nombre']}")
    
    # ========================================================================
    # 2. EXAMEN DE GRADO (ID: 5) - 3 etapas
    # ========================================================================
    print("\n📌 Insertando etapas para Examen de Grado...")
    examen = Modalidad.objects.filter(nombre='Examen de Grado').first()
    if examen is None:
        print("⚠️ Modalidad 'Examen de Grado' no encontrada, omitiendo etapas.")
    else:
        etapas_examen = [
            {'orden': 1, 'nombre': 'Registro'},
            {'orden': 2, 'nombre': 'Examen – Ciencias Básicas y Matemáticas'},
            {'orden': 3, 'nombre': 'Examen – Ciencias Sociales y Humanísticas'},
            {'orden': 4, 'nombre': 'Examen – Ciencias de la Ingeniería'},
            {'orden': 5, 'nombre': 'Examen – Ingeniería Aplicada'},
            {'orden': 6, 'nombre': 'Acta de Calificación'},
            {'orden': 7, 'nombre': 'Acta Final'},
        ]
        
        for etapa_data in etapas_examen:
            etapa, created = Etapa.objects.get_or_create(
                modalidad=examen,
                orden=etapa_data['orden'],
                defaults={
                    'nombre': etapa_data['nombre'],
                    'activo': True,
                }
            )
            status = "✓ CREADA" if created else "✓ EXISTE"
            print(f"  {status}: Orden {etapa_data['orden']} - {etapa_data['nombre']}")
        status = "✓ CREADA" if created else "✓ EXISTE"
        print(f"  {status}: Orden {etapa_data['orden']} - {etapa_data['nombre']}")
    
    # ========================================================================
    # 3. VÍA DIPLOMADO (ID: 4) - 4 etapas
    # ========================================================================
    print("\n📌 Insertando etapas para Vía Diplomado...")
    diplomado = Modalidad.objects.filter(nombre='Vía Diplomado').first()
    if diplomado is None:
        print("⚠️ Modalidad 'Vía Diplomado' no encontrada, omitiendo etapas.")
    else:
        etapas_diplomado = [
            {'orden': 1, 'nombre': 'Inscripción Diplomado'},
            {'orden': 2, 'nombre': 'Desarrollo Diplomado'},
            {'orden': 3, 'nombre': 'Defensa Monografía'},
            {'orden': 4, 'nombre': 'Correcciones'},
        ]
        
        for etapa_data in etapas_diplomado:
            etapa, created = Etapa.objects.get_or_create(
                modalidad=diplomado,
                orden=etapa_data['orden'],
                defaults={
                    'nombre': etapa_data['nombre'],
                    'activo': True,
                }
            )
            status = "✓ CREADA" if created else "✓ EXISTE"
            print(f"  {status}: Orden {etapa_data['orden']} - {etapa_data['nombre']}")
        status = "✓ CREADA" if created else "✓ EXISTE"
        print(f"  {status}: Orden {etapa_data['orden']} - {etapa_data['nombre']}")
    
    print("\n✅ Migración completada: 11 nuevas etapas insertadas\n")


def reverse_etapas(apps, schema_editor):
    """
    Elimina las etapas agregadas.
    NOTA: Seguro porque on_delete=SET_NULL en Postulacion.etapa_actual
    """
    print("\n⚠️  Revirtiendo migración: Eliminando etapas agregadas...")
    
    Etapa = apps.get_model('modalidades', 'Etapa')
    
    # Eliminar etapas de las 3 modalidades actualizadas
    etapas_a_eliminar = Etapa.objects.filter(
        modalidad__nombre__in=[
            'Proyecto de Grado',
            'Examen de Grado',
            'Vía Diplomado',
        ]
    )
    
    count = etapas_a_eliminar.count()
    etapas_a_eliminar.delete()
    print(f"✓ Eliminadas {count} etapas\n")


class Migration(migrations.Migration):
    dependencies = [
        ('modalidades', '0005_fix_modalidadrequisito_timestamps'),
    ]

    operations = [
        migrations.RunPython(
            create_etapas,
            reverse_etapas,
        ),
    ]
