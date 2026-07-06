from django.db import migrations

ACTA_DEFENSA_NAME = 'Acta de Defensa de Tesis o de Modalidad de Graduación'


def create_associations(apps, schema_editor):
    """Asocia tipos de documento a la modalidad Excelencia Académica usando la misma tabla que usa Proyecto de Grado."""
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    Etapa = apps.get_model('modalidades', 'Etapa')
    TipoDocumento = apps.get_model('documentos', 'TipoDocumento')
    ModalidadTipoDocumento = apps.get_model('documentos', 'ModalidadTipoDocumento')

    modalidad = Modalidad.objects.filter(nombre__iexact='Excelencia Académica').first()
    if not modalidad:
        modalidad = Modalidad.objects.filter(nombre__icontains='excelencia').first()
    if not modalidad:
        return

    etapa_1 = Etapa.objects.filter(modalidad=modalidad, orden=1).first()
    etapa_2 = Etapa.objects.filter(modalidad=modalidad, orden=2).first()
    etapa_3 = Etapa.objects.filter(modalidad=modalidad, orden=3).first()
    etapa_4 = Etapa.objects.filter(modalidad=modalidad, orden=4).first()

    # Definir mapeos por etapa (sin duplicar tipos entre etapas)
    mappings = [
        # Registro
        {'etapa': etapa_1, 'tipo_documentos': [
            {'nombre': 'Carta de solicitud', 'obligatorio': True, 'orden': 1},
            {'nombre': 'CV del Estudiante', 'obligatorio': True, 'orden': 2},
            {'nombre': 'Fotocopia de CI', 'obligatorio': True, 'orden': 3},
        ]},
        # Revisión de Expediente
        {'etapa': etapa_2, 'tipo_documentos': [
            {'nombre': 'Certificado Académico', 'obligatorio': True, 'orden': 1},
            {'nombre': 'Historial académico', 'obligatorio': True, 'orden': 2},
        ]},
        # Evaluación del Tribunal
        {'etapa': etapa_3, 'tipo_documentos': [
            {'nombre': ACTA_DEFENSA_NAME, 'obligatorio': True, 'orden': 1},
        ]},
        # Acta Final
        {'etapa': etapa_4, 'tipo_documentos': [
            {'nombre': 'Documento Final', 'obligatorio': True, 'orden': 1},
        ]},
    ]

    for group in mappings:
        etapa_obj = group['etapa']
        if not etapa_obj:
            continue

        for td in group['tipo_documentos']:
            tipo_obj, _ = TipoDocumento.objects.update_or_create(
                nombre=td['nombre'],
                defaults={
                    'descripcion': '',
                    'obligatorio': td['obligatorio'],
                    'activo': True,
                    'etapa': None,
                }
            )

            ModalidadTipoDocumento.objects.update_or_create(
                modalidad=modalidad,
                tipo_documento=tipo_obj,
                etapa=etapa_obj,
                defaults={
                    'obligatorio': td['obligatorio'],
                    'orden': td['orden'],
                    'activo': True,
                    'descripcion_requerimiento': '',
                }
            )


def reverse_associations(apps, schema_editor):
    """Elimina las asociaciones creadas para la modalidad Excelencia Académica."""
    ModalidadTipoDocumento = apps.get_model('documentos', 'ModalidadTipoDocumento')
    ModalidadTipoDocumento.objects.filter(
        modalidad__nombre='Excelencia Académica',
        tipo_documento__nombre__in=[
            'Carta de solicitud',
            'CV del Estudiante',
            'Fotocopia de CI',
            'Certificado Académico',
            'Historial académico',
            ACTA_DEFENSA_NAME,
            'Documento Final',
        ],
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('documentos', '0006_modalidadtipodocumento_and_more'),
    ]

    operations = [
        migrations.RunPython(create_associations, reverse_associations),
    ]
