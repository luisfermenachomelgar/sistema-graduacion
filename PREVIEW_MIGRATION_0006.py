"""
Django Data Migration: Populate etapas for incomplete modalidades

SEGURIDAD:
✅ Usa get_or_create() - idempotente, sin duplicados
✅ Solo inserta en modalidades vacías
✅ No afecta etapas existentes
✅ Reversible (función reverse incluida)
✅ No afecta postulaciones (etapa_actual es nullable)

DATOS A INSERTAR:
- Proyecto de Grado: 3 etapas (Propuesta → Desarrollo → Defensa)
- Examen de Grado: 3 etapas (Inscripción → Examen → Evaluación)
- Vía Diplomado: 3 etapas (Inscripción → Cursada → Monografía)

Total: 9 nuevas etapas + 4 existentes = 13 etapas en total
"""

from django.db import migrations

def create_etapas(apps, schema_editor):
    """
    Crea etapas para modalidades incompletas.
    Usa get_or_create() para ser idempotente (seguro ejecutar múltiples veces).
    """
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    Etapa = apps.get_model('modalidades', 'Etapa')
    
    # ========================================================================
    # 1. PROYECTO DE GRADO (ID: 3)
    # ========================================================================
    print("\n📌 Insertando etapas para Proyecto de Grado...")
    proyecto = Modalidad.objects.get(nombre='Proyecto de Grado')
    
    etapas_proyecto = [
        {'orden': 1, 'nombre': 'Propuesta de Proyecto'},
        {'orden': 2, 'nombre': 'Desarrollo del Proyecto'},
        {'orden': 3, 'nombre': 'Defensa de Proyecto'},
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
    
    # ========================================================================
    # 2. EXAMEN DE GRADO (ID: 5)
    # ========================================================================
    print("\n📌 Insertando etapas para Examen de Grado...")
    examen = Modalidad.objects.get(nombre='Examen de Grado')
    
    etapas_examen = [
        {'orden': 1, 'nombre': 'Inscripción al Examen'},
        {'orden': 2, 'nombre': 'Realización del Examen'},
        {'orden': 3, 'nombre': 'Evaluación Tribunal'},
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
    
    # ========================================================================
    # 3. VÍA DIPLOMADO (ID: 4)
    # ========================================================================
    print("\n📌 Insertando etapas para Vía Diplomado...")
    diplomado = Modalidad.objects.get(nombre='Vía Diplomado')
    
    etapas_diplomado = [
        {'orden': 1, 'nombre': 'Inscripción Diplomado'},
        {'orden': 2, 'nombre': 'Cursada del Diplomado'},
        {'orden': 3, 'nombre': 'Defensa Monografía'},
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
    
    print("\n✅ Migración completada: 9 nuevas etapas insertadas\n")


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
