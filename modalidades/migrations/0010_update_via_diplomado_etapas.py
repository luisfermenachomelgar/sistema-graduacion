from django.db import migrations


def update_via_diplomado_etapas(apps, schema_editor):
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    Etapa = apps.get_model('modalidades', 'Etapa')

    # Buscar la modalidad por fragmento para evitar problemas con mayúsculas/acento
    modalidad = Modalidad.objects.filter(nombre__icontains='diplomad').first()
    if not modalidad:
        return

    # Evitar conflictos de unique constraint sobre orden mientras actualizamos.
    for etapa in Etapa.objects.filter(modalidad=modalidad):
        etapa.orden = etapa.orden + 1000
        etapa.save()

    # Etapas objetivo para Vía Diplomado (nuevo requerimiento)
    etapas_via = [
        {'orden': 1, 'nombre': 'Monografía'},
        {'orden': 2, 'nombre': 'Defensa Pública'},
        {'orden': 3, 'nombre': 'Acta Final'},
    ]

    for etapa_data in etapas_via:
        Etapa.objects.update_or_create(
            modalidad=modalidad,
            nombre=etapa_data['nombre'],
            defaults={
                'orden': etapa_data['orden'],
                'activo': True,
            },
        )

    # Eliminar las etapas que no están en la lista objetivo
    Etapa.objects.filter(modalidad=modalidad).exclude(
        nombre__in=[etapa_data['nombre'] for etapa_data in etapas_via]
    ).delete()


def reverse_via_diplomado_etapas(apps, schema_editor):
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    Etapa = apps.get_model('modalidades', 'Etapa')

    modalidad = Modalidad.objects.filter(nombre__icontains='diplomad').first()
    if not modalidad:
        return

    # Al revertir, desactivar las etapas objetivo (no restauramos eliminadas)
    Etapa.objects.filter(
        modalidad=modalidad,
        nombre__in=[
            'Monografía',
            'Defensa Pública',
            'Acta Final',
        ],
    ).update(activo=False)


class Migration(migrations.Migration):
    dependencies = [
        ('modalidades', '0009_update_trabajo_dirigido_etapas'),
    ]

    operations = [
        migrations.RunPython(update_via_diplomado_etapas, reverse_via_diplomado_etapas),
    ]
