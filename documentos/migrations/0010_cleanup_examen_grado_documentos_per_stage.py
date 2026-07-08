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

    configured_pairs = []
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

        configured_pairs.append((etapa, tipo_docs))

    allowed_pairs = set()
    for etapa, tipo_docs in configured_pairs:
        for tipo_doc, orden in tipo_docs:
            allowed_pairs.add((etapa.id, tipo_doc.id))
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

    ModalidadTipoDocumento.objects.filter(modalidad=modalidad).exclude(
        etapa_id__in=[etapa.id for etapa, _ in configured_pairs]
    ).delete()

    rows_to_keep = ModalidadTipoDocumento.objects.filter(modalidad=modalidad)
    for row in rows_to_keep:
        if (row.etapa_id, row.tipo_documento_id) not in allowed_pairs:
            row.delete()


def reverse_configure_examen_grado_documentos(apps, schema_editor):
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    ModalidadTipoDocumento = apps.get_model('documentos', 'ModalidadTipoDocumento')

    modalidad = Modalidad.objects.filter(nombre__iexact='EXAMEN DE GRADO').first()
    if not modalidad:
        return

    ModalidadTipoDocumento.objects.filter(modalidad=modalidad).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('documentos', '0009_configure_examen_grado_documentos_per_stage'),
        ('modalidades', '0012_fix_examen_de_grado_etapa_labels'),
    ]

    operations = [
        migrations.RunPython(
            configure_examen_grado_documentos,
            reverse_configure_examen_grado_documentos,
        ),
    ]
