from django.db import migrations


DOCUMENTOS_EXAMEN_GRADO = [
    'Carta de Solicitud',
    'Formulario de Inscripción',
    'Historial Académico',
    'Certificado de Planificación Académica',
    'Certificado de Solvencia Universitaria',
    'Certificado de Solvencia Bibliotecaria',
    'Recibo de Matrícula',
    'Comprobante de Pago (Boleta de Depósito)',
    'Timbre Universitario',
]


def configure_examen_grado_documentos(apps, schema_editor):
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    Etapa = apps.get_model('modalidades', 'Etapa')
    TipoDocumento = apps.get_model('documentos', 'TipoDocumento')
    ModalidadTipoDocumento = apps.get_model('documentos', 'ModalidadTipoDocumento')

    modalidad = Modalidad.objects.filter(nombre__iexact='EXAMEN DE GRADO').first()
    if not modalidad:
        return

    etapa_registro = Etapa.objects.filter(modalidad=modalidad, nombre__iexact='Registro').first()
    if not etapa_registro:
        return

    documentos_config = []
    for orden, nombre in enumerate(DOCUMENTOS_EXAMEN_GRADO, start=1):
        tipo_doc, _ = TipoDocumento.objects.update_or_create(
            nombre__iexact=nombre,
            defaults={
                'nombre': nombre,
                'descripcion': '',
                'obligatorio': True,
                'activo': True,
                'etapa': None,
            },
        )
        documentos_config.append((tipo_doc, orden))

    for tipo_doc, orden in documentos_config:
        ModalidadTipoDocumento.objects.update_or_create(
            modalidad=modalidad,
            tipo_documento=tipo_doc,
            etapa=etapa_registro,
            defaults={
                'obligatorio': True,
                'orden': orden,
                'activo': True,
                'descripcion_requerimiento': '',
            },
        )

    ModalidadTipoDocumento.objects.filter(
        modalidad=modalidad,
        tipo_documento__nombre__in=DOCUMENTOS_EXAMEN_GRADO,
    ).exclude(etapa=etapa_registro).delete()


def reverse_configure_examen_grado_documentos(apps, schema_editor):
    ModalidadTipoDocumento = apps.get_model('documentos', 'ModalidadTipoDocumento')
    Modalidad = apps.get_model('modalidades', 'Modalidad')

    modalidad = Modalidad.objects.filter(nombre__iexact='EXAMEN DE GRADO').first()
    if not modalidad:
        return

    ModalidadTipoDocumento.objects.filter(
        modalidad=modalidad,
        tipo_documento__nombre__in=DOCUMENTOS_EXAMEN_GRADO,
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('documentos', '0007_populate_modalidad_tipodocumento_excelencia_academica'),
        ('modalidades', '0012_fix_examen_de_grado_etapa_labels'),
    ]

    operations = [
        migrations.RunPython(
            configure_examen_grado_documentos,
            reverse_configure_examen_grado_documentos,
        ),
    ]
