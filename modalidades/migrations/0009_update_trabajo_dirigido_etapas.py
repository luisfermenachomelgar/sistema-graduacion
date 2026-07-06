from django.db import migrations


def update_trabajo_dirigido_etapas(apps, schema_editor):
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    Etapa = apps.get_model('modalidades', 'Etapa')

    modalidad = Modalidad.objects.filter(nombre__iexact='Trabajo Dirigido').first()
    if not modalidad:
        modalidad = Modalidad.objects.filter(nombre__iexact='TRABAJO DIRIGIDO').first()
    if not modalidad:
        return

    # Evitar conflictos de unique constraint sobre orden mientras actualizamos.
    for etapa in Etapa.objects.filter(modalidad=modalidad):
        etapa.orden = etapa.orden + 1000
        etapa.save()

    etapas_trabajo = [
        {'orden': 1, 'nombre': 'Perfil de Trabajo Dirigido'},
        {'orden': 2, 'nombre': 'Documento Final'},
        {'orden': 3, 'nombre': 'Defensa Privada'},
        {'orden': 4, 'nombre': 'Defensa Pública'},
        {'orden': 5, 'nombre': 'Acta Final'},
    ]

    for etapa_data in etapas_trabajo:
        Etapa.objects.update_or_create(
            modalidad=modalidad,
            nombre=etapa_data['nombre'],
            defaults={
                'orden': etapa_data['orden'],
                'activo': True,
            },
        )

    Etapa.objects.filter(modalidad=modalidad).exclude(
        nombre__in=[etapa_data['nombre'] for etapa_data in etapas_trabajo]
    ).update(activo=False)


def reverse_trabajo_dirigido_etapas(apps, schema_editor):
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    Etapa = apps.get_model('modalidades', 'Etapa')

    modalidad = Modalidad.objects.filter(nombre__iexact='Trabajo Dirigido').first()
    if not modalidad:
        modalidad = Modalidad.objects.filter(nombre__iexact='TRABAJO DIRIGIDO').first()
    if not modalidad:
        return

    Etapa.objects.filter(
        modalidad=modalidad,
        nombre__in=[
            'Perfil de Trabajo Dirigido',
            'Documento Final',
            'Defensa Privada',
            'Defensa Pública',
            'Acta Final',
        ],
    ).update(activo=False)


class Migration(migrations.Migration):
    dependencies = [
        ('modalidades', '0008_populate_etapas_excelencia_academica'),
    ]

    operations = [
        migrations.RunPython(update_trabajo_dirigido_etapas, reverse_trabajo_dirigido_etapas),
    ]
