from django.db import migrations


def create_associations(apps, schema_editor):
    """Asocia tipos de documento a la modalidad Excelencia Académica usando la misma tabla que usa Proyecto de Grado."""
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    Etapa = apps.get_model('modalidades', 'Etapa')
    TipoDocumento = apps.get_model('documentos', 'TipoDocumento')
    ModalidadTipoDocumento = apps.get_model('documentos', 'ModalidadTipoDocumento')

    modalidad = Modalidad.objects.filter(nombre='Excelencia Académica').first()
    if not modalidad:
        return

    etapa_1 = Etapa.objects.filter(modalidad=modalidad, orden=1).first()
    etapa_2 = Etapa.objects.filter(modalidad=modalidad, orden=2).first()
    etapa_3 = Etapa.objects.filter(modalidad=modalidad, orden=3).first()

    mappings = [
        {'nombre': 'Carta de solicitud', 'etapa': etapa_1, 'obligatorio': True, 'orden': 1},
        {'nombre': 'Certificado de notas', 'etapa': etapa_1, 'obligatorio': True, 'orden': 2},
        {'nombre': 'Historial académico', 'etapa': etapa_1, 'obligatorio': True, 'orden': 3},
        {'nombre': 'Fotocopia de CI', 'etapa': etapa_1, 'obligatorio': True, 'orden': 4},
    ]

    for mapping in mappings:
        tipo_documento = TipoDocumento.objects.filter(nombre=mapping['nombre']).first()
        if not tipo_documento:
            tipo_documento = TipoDocumento.objects.create(
                nombre=mapping['nombre'],
                obligatorio=mapping['obligatorio'],
                activo=True,
            )

        ModalidadTipoDocumento.objects.get_or_create(
            modalidad=modalidad,
            tipo_documento=tipo_documento,
            etapa=mapping['etapa'],
            defaults={
                'obligatorio': mapping['obligatorio'],
                'orden': mapping['orden'],
                'activo': True,
                'descripcion_requerimiento': '',
            },
        )


def reverse_associations(apps, schema_editor):
    """Elimina las asociaciones creadas para la modalidad Excelencia Académica."""
    ModalidadTipoDocumento = apps.get_model('documentos', 'ModalidadTipoDocumento')
    ModalidadTipoDocumento.objects.filter(
        modalidad__nombre='Excelencia Académica',
        tipo_documento__nombre__in=[
            'Carta de solicitud',
            'Certificado de notas',
            'Historial académico',
            'Fotocopia de CI',
        ],
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('documentos', '0006_modalidadtipodocumento_and_more'),
    ]

    operations = [
        migrations.RunPython(create_associations, reverse_associations),
    ]
