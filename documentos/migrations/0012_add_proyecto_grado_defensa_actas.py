from django.db import migrations


def add_proyecto_grado_defensa_actas(apps, schema_editor):
    ModalidadTipoDocumento = apps.get_model('documentos', 'ModalidadTipoDocumento')
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    Etapa = apps.get_model('modalidades', 'Etapa')
    TipoDocumento = apps.get_model('documentos', 'TipoDocumento')

    modalidad = Modalidad.objects.filter(nombre='PROYECTO DE GRADO').first()
    if not modalidad:
        return

    etapa_privada = Etapa.objects.filter(modalidad=modalidad, nombre='Defensa Privada').first()
    etapa_publica = Etapa.objects.filter(modalidad=modalidad, nombre='Defensa Pública').first()
    if not etapa_privada or not etapa_publica:
        return

    acta_privada = TipoDocumento.objects.filter(nombre='Acta de defensa privada').first()
    acta_publica = TipoDocumento.objects.filter(nombre='Acta de defensa pública').first()

    if acta_privada:
        ModalidadTipoDocumento.objects.get_or_create(
            modalidad=modalidad,
            tipo_documento=acta_privada,
            etapa=etapa_privada,
            defaults={
                'obligatorio': True,
                'orden': 1,
                'descripcion_requerimiento': '',
                'activo': True,
            },
        )

    if acta_publica:
        ModalidadTipoDocumento.objects.get_or_create(
            modalidad=modalidad,
            tipo_documento=acta_publica,
            etapa=etapa_publica,
            defaults={
                'obligatorio': True,
                'orden': 1,
                'descripcion_requerimiento': '',
                'activo': True,
            },
        )


def remove_proyecto_grado_defensa_actas(apps, schema_editor):
    ModalidadTipoDocumento = apps.get_model('documentos', 'ModalidadTipoDocumento')
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    Etapa = apps.get_model('modalidades', 'Etapa')
    TipoDocumento = apps.get_model('documentos', 'TipoDocumento')

    modalidad = Modalidad.objects.filter(nombre='PROYECTO DE GRADO').first()
    if not modalidad:
        return

    etapa_privada = Etapa.objects.filter(modalidad=modalidad, nombre='Defensa Privada').first()
    etapa_publica = Etapa.objects.filter(modalidad=modalidad, nombre='Defensa Pública').first()
    acta_privada = TipoDocumento.objects.filter(nombre='Acta de defensa privada').first()
    acta_publica = TipoDocumento.objects.filter(nombre='Acta de defensa pública').first()

    if acta_privada and etapa_privada:
        ModalidadTipoDocumento.objects.filter(
            modalidad=modalidad,
            tipo_documento=acta_privada,
            etapa=etapa_privada,
        ).delete()

    if acta_publica and etapa_publica:
        ModalidadTipoDocumento.objects.filter(
            modalidad=modalidad,
            tipo_documento=acta_publica,
            etapa=etapa_publica,
        ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('documentos', '0011_add_preview_pdf'),
        ('modalidades', '0013_add_registro_stage_excelencia_academica'),
    ]

    operations = [
        migrations.RunPython(add_proyecto_grado_defensa_actas, remove_proyecto_grado_defensa_actas),
    ]
