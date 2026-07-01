from django.db import migrations


def create_etapas(apps, schema_editor):
    """Crea las etapas para la modalidad Excelencia Académica usando el mismo mecanismo de las migraciones previas."""
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    Etapa = apps.get_model('modalidades', 'Etapa')

    modalidad = Modalidad.objects.filter(nombre='Excelencia Académica').first()
    if not modalidad:
        return

    etapas = [
        {'orden': 1, 'nombre': 'Presentación de documentos'},
        {'orden': 2, 'nombre': 'Cumplimiento de requisitos'},
        {'orden': 3, 'nombre': 'Graduación aprobada'},
    ]

    for etapa_data in etapas:
        Etapa.objects.get_or_create(
            modalidad=modalidad,
            orden=etapa_data['orden'],
            defaults={
                'nombre': etapa_data['nombre'],
                'activo': True,
            },
        )


def reverse_etapas(apps, schema_editor):
    """Elimina las etapas creadas para la modalidad Excelencia Académica."""
    Etapa = apps.get_model('modalidades', 'Etapa')
    Etapa.objects.filter(
        modalidad__nombre='Excelencia Académica',
        nombre__in=[
            'Presentación de documentos',
            'Cumplimiento de requisitos',
            'Graduación aprobada',
        ],
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('modalidades', '0007_historial_cambio_modalidad'),
    ]

    operations = [
        migrations.RunPython(create_etapas, reverse_etapas),
    ]
