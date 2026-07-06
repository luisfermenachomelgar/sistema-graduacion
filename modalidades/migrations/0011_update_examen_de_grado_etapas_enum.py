from django.db import migrations


def update_examen_de_grado_etapas(apps, schema_editor):
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    Etapa = apps.get_model('modalidades', 'Etapa')

    modalidad = Modalidad.objects.filter(nombre='EXAMEN DE GRADO').first()
    if not modalidad:
        return

    etapas_examen = [
        {'orden': 1, 'nombre': 'Examen 1 – Ciencias Básicas y Matemáticas'},
        {'orden': 2, 'nombre': 'Examen 2 – Ciencias Sociales y Humanísticas'},
        {'orden': 3, 'nombre': 'Examen 3 – Ciencias de la Ingeniería'},
        {'orden': 4, 'nombre': 'Examen 4 – Ingeniería Aplicada'},
    ]

    for etapa_data in etapas_examen:
        Etapa.objects.update_or_create(
            modalidad=modalidad,
            orden=etapa_data['orden'],
            defaults={
                'nombre': etapa_data['nombre'],
            },
        )


def reverse_examen_de_grado_etapas(apps, schema_editor):
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    Etapa = apps.get_model('modalidades', 'Etapa')

    modalidad = Modalidad.objects.filter(nombre='EXAMEN DE GRADO').first()
    if not modalidad:
        return

    reverse_names = [
        {'orden': 1, 'nombre': 'Examen – Ciencias Básicas y Matemáticas'},
        {'orden': 2, 'nombre': 'Examen – Ciencias Sociales y Humanísticas'},
        {'orden': 3, 'nombre': 'Examen – Ciencias de la Ingeniería'},
        {'orden': 4, 'nombre': 'Examen – Ingeniería Aplicada'},
    ]

    for etapa_data in reverse_names:
        Etapa.objects.update_or_create(
            modalidad=modalidad,
            orden=etapa_data['orden'],
            defaults={
                'nombre': etapa_data['nombre'],
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ('modalidades', '0010_update_via_diplomado_etapas'),
    ]

    operations = [
        migrations.RunPython(update_examen_de_grado_etapas, reverse_examen_de_grado_etapas),
    ]
