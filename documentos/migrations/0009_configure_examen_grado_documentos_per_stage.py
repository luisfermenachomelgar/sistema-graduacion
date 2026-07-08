from django.db import migrations


STAGE_DOCUMENTS = {
    'Registro': [
        'Carta de Solicitud',
        'Formulario de Inscripción',
        'Historial Académico',
        'Certificado de Planificación Académica',
        'Certificado de Solvencia Universitaria',
        'Certificado de Solvencia Bibliotecaria',
        'Recibo de Matrícula',
        'Comprobante de Pago (Boleta de Depósito)',
        'Timbre Universitario',
    ],
    'Examen 1 – Ciencias Básicas y Matemáticas': [
        'Acta del Examen – Ciencias Básicas y Matemáticas',
    ],
    'Examen 2 – Ciencias Sociales y Humanísticas': [
        'Acta del Examen – Ciencias Sociales y Humanísticas',
    ],
    'Examen 3 – Ciencias de la Ingeniería': [
        'Acta del Examen – Ciencias de la Ingeniería',
    ],
    'Examen 4 – Ingeniería Aplicada': [
        'Acta del Examen – Ingeniería Aplicada',
    ],
    'Acta Final': [
        'Acta Final del Examen de Grado',
    ],
}


def configure_examen_grado_documentos(apps, schema_editor):
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    Etapa = apps.get_model('modalidades', 'Etapa')
    TipoDocumento = apps.get_model('documentos', 'TipoDocumento')
    ModalidadTipoDocumento = apps.get_model('documentos', 'ModalidadTipoDocumento')

    modalidad = Modalidad.objects.filter(nombre__iexact='EXAMEN DE GRADO').first()
    if not modalidad:
        return

    configured_stages = []
    for stage_name, doc_names in STAGE_DOCUMENTS.items():
        etapa = Etapa.objects.filter(modalidad=modalidad, nombre__iexact=stage_name).first()
        if not etapa:
            continue

        tipo_docs = []
        for orden, doc_name in enumerate(doc_names, start=1):
            tipo_doc, _ = TipoDocumento.objects.update_or_create(
                nombre__iexact=doc_name,
                defaults={
                    'nombre': doc_name,
                    'descripcion': '',
                    'obligatorio': True,
                    'activo': True,
                    'etapa': None,
                },
            )
            tipo_docs.append((tipo_doc, orden))

        configured_stages.append((etapa, tipo_docs))

    for etapa, tipo_docs in configured_stages:
        allowed_ids = [tipo_doc.id for tipo_doc, _ in tipo_docs]
        ModalidadTipoDocumento.objects.filter(modalidad=modalidad, etapa=etapa).exclude(
            tipo_documento_id__in=allowed_ids
        ).delete()

        for tipo_doc, orden in tipo_docs:
            ModalidadTipoDocumento.objects.update_or_create(
                modalidad=modalidad,
                tipo_documento=tipo_doc,
                etapa=etapa,
                defaults={
                    'obligatorio': True,
                    'orden': orden,
                    'activo': True,
                    'descripcion_requerimiento': '',
                },
            )

    for etapa, tipo_docs in configured_stages:
        for tipo_doc, _ in tipo_docs:
            ModalidadTipoDocumento.objects.filter(
                modalidad=modalidad,
                tipo_documento=tipo_doc,
            ).exclude(etapa=etapa).delete()


def reverse_configure_examen_grado_documentos(apps, schema_editor):
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    ModalidadTipoDocumento = apps.get_model('documentos', 'ModalidadTipoDocumento')

    modalidad = Modalidad.objects.filter(nombre__iexact='EXAMEN DE GRADO').first()
    if not modalidad:
        return

    ModalidadTipoDocumento.objects.filter(
        modalidad=modalidad,
        tipo_documento__nombre__in=[
            'Carta de Solicitud',
            'Formulario de Inscripción',
            'Historial Académico',
            'Certificado de Planificación Académica',
            'Certificado de Solvencia Universitaria',
            'Certificado de Solvencia Bibliotecaria',
            'Recibo de Matrícula',
            'Comprobante de Pago (Boleta de Depósito)',
            'Timbre Universitario',
            'Acta del Examen – Ciencias Básicas y Matemáticas',
            'Acta del Examen – Ciencias Sociales y Humanísticas',
            'Acta del Examen – Ciencias de la Ingeniería',
            'Acta del Examen – Ingeniería Aplicada',
            'Acta Final del Examen de Grado',
        ],
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('documentos', '0008_configure_examen_grado_documentos'),
        ('modalidades', '0012_fix_examen_de_grado_etapa_labels'),
    ]

    operations = [
        migrations.RunPython(
            configure_examen_grado_documentos,
            reverse_configure_examen_grado_documentos,
        ),
    ]
