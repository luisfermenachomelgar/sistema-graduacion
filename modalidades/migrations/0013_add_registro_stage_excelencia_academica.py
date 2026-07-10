from django.db import migrations


def add_registro_stage(apps, schema_editor):
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    Etapa = apps.get_model('modalidades', 'Etapa')

    modalidad = Modalidad.objects.filter(nombre__icontains='excelencia').first()
    if not modalidad:
        return

    Etapa.objects.get_or_create(
        modalidad=modalidad,
        nombre='Registro',
        defaults={
            'orden': 1,
            'activo': True,
        },
    )


def remove_registro_stage(apps, schema_editor):
    Etapa = apps.get_model('modalidades', 'Etapa')
    Etapa.objects.filter(nombre='Registro', modalidad__nombre__icontains='excelencia').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('modalidades', '0012_fix_examen_de_grado_etapa_labels'),
    ]

    operations = [
        migrations.RunPython(add_registro_stage, remove_registro_stage),
    ]
