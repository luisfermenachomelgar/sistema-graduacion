from django.db import migrations


def update_examen_de_grado_etapas(apps, schema_editor):
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    Etapa = apps.get_model('modalidades', 'Etapa')

    modalidad = Modalidad.objects.filter(nombre='EXAMEN DE GRADO').first()
    if not modalidad:
        return

    name_mapping = {
        'Examen – Ciencias Básicas y Matemáticas': 'Examen 1 – Ciencias Básicas y Matemáticas',
        'Examen – Ciencias Sociales y Humanísticas': 'Examen 2 – Ciencias Sociales y Humanísticas',
        'Examen – Ciencias de la Ingeniería': 'Examen 3 – Ciencias de la Ingeniería',
        'Examen – Ingeniería Aplicada': 'Examen 4 – Ingeniería Aplicada',
    }

    for old_name, new_name in name_mapping.items():
        Etapa.objects.filter(modalidad=modalidad, nombre=old_name).update(nombre=new_name)


def reverse_examen_de_grado_etapas(apps, schema_editor):
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    Etapa = apps.get_model('modalidades', 'Etapa')

    modalidad = Modalidad.objects.filter(nombre='EXAMEN DE GRADO').first()
    if not modalidad:
        return

    reverse_mapping = {
        'Examen 1 – Ciencias Básicas y Matemáticas': 'Examen – Ciencias Básicas y Matemáticas',
        'Examen 2 – Ciencias Sociales y Humanísticas': 'Examen – Ciencias Sociales y Humanísticas',
        'Examen 3 – Ciencias de la Ingeniería': 'Examen – Ciencias de la Ingeniería',
        'Examen 4 – Ingeniería Aplicada': 'Examen – Ingeniería Aplicada',
    }

    for old_name, new_name in reverse_mapping.items():
        Etapa.objects.filter(modalidad=modalidad, nombre=old_name).update(nombre=new_name)


class Migration(migrations.Migration):
    dependencies = [
        ('modalidades', '0011_update_examen_de_grado_etapas_enum'),
    ]

    operations = [
        migrations.RunPython(update_examen_de_grado_etapas, reverse_examen_de_grado_etapas),
    ]
