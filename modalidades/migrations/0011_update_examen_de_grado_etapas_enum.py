from django.db import migrations


def update_examen_de_grado_etapas(apps, schema_editor):
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    Etapa = apps.get_model('modalidades', 'Etapa')

    modalidad = Modalidad.objects.filter(nombre__iexact='EXAMEN DE GRADO').first()
    if not modalidad:
        return

    etapas_examen = [
        {'orden': 1, 'nombre': 'Registro'},
        {'orden': 2, 'nombre': 'Examen 1 – Ciencias Básicas y Matemáticas'},
        {'orden': 3, 'nombre': 'Examen 2 – Ciencias Sociales y Humanísticas'},
        {'orden': 4, 'nombre': 'Examen 3 – Ciencias de la Ingeniería'},
        {'orden': 5, 'nombre': 'Examen 4 – Ingeniería Aplicada'},
        {'orden': 6, 'nombre': 'Acta de Calificación'},
        {'orden': 7, 'nombre': 'Acta Final'},
    ]

    alias_map = {
        'Examen 1 – Ciencias Básicas y Matemáticas': ['Examen 1 – Ciencias Básicas y Matemáticas', 'Examen – Ciencias Básicas y Matemáticas'],
        'Examen 2 – Ciencias Sociales y Humanísticas': ['Examen 2 – Ciencias Sociales y Humanísticas', 'Examen – Ciencias Sociales y Humanísticas'],
        'Examen 3 – Ciencias de la Ingeniería': ['Examen 3 – Ciencias de la Ingeniería', 'Examen – Ciencias de la Ingeniería'],
        'Examen 4 – Ingeniería Aplicada': ['Examen 4 – Ingeniería Aplicada', 'Examen – Ingeniería Aplicada'],
    }

    for etapa in Etapa.objects.filter(modalidad=modalidad):
        etapa.orden = etapa.orden + 1000
        etapa.save(update_fields=['orden'])

    for etapa_data in etapas_examen:
        nombres_posibles = [etapa_data['nombre']] + alias_map.get(etapa_data['nombre'], [])
        etapa_existente = None

        for nombre in nombres_posibles:
            etapa_existente = Etapa.objects.filter(modalidad=modalidad, nombre=nombre).first()
            if etapa_existente:
                break

        if etapa_existente:
            etapa_existente.nombre = etapa_data['nombre']
            etapa_existente.orden = etapa_data['orden']
            etapa_existente.activo = True
            etapa_existente.save(update_fields=['nombre', 'orden', 'activo'])
        else:
            Etapa.objects.create(
                modalidad=modalidad,
                nombre=etapa_data['nombre'],
                orden=etapa_data['orden'],
                activo=True,
            )


def reverse_examen_de_grado_etapas(apps, schema_editor):
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    Etapa = apps.get_model('modalidades', 'Etapa')

    modalidad = Modalidad.objects.filter(nombre__iexact='EXAMEN DE GRADO').first()
    if not modalidad:
        return

    reverse_names = [
        {'orden': 1, 'nombre': 'Examen – Ciencias Básicas y Matemáticas'},
        {'orden': 2, 'nombre': 'Examen – Ciencias Sociales y Humanísticas'},
        {'orden': 3, 'nombre': 'Examen – Ciencias de la Ingeniería'},
        {'orden': 4, 'nombre': 'Examen – Ingeniería Aplicada'},
    ]

    for etapa_data in reverse_names:
        etapa_existente = Etapa.objects.filter(modalidad=modalidad, nombre=etapa_data['nombre']).first()
        if etapa_existente:
            etapa_existente.orden = etapa_data['orden']
            etapa_existente.save(update_fields=['orden'])

    Etapa.objects.filter(modalidad=modalidad, nombre='Registro').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('modalidades', '0010_update_via_diplomado_etapas'),
    ]

    operations = [
        migrations.RunPython(update_examen_de_grado_etapas, reverse_examen_de_grado_etapas),
    ]
