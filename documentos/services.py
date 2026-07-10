from __future__ import annotations

from django.db import transaction

from modalidades.models import Etapa, Modalidad
from .models import ModalidadTipoDocumento, TipoDocumento


def _ensure_stage(modalidad: Modalidad, name: str, order: int) -> Etapa:
    stage = Etapa.objects.filter(modalidad=modalidad, nombre=name).first()
    if stage is not None:
        if stage.orden != order:
            stage.orden = order
            stage.save(update_fields=['orden'])
        return stage

    existing_at_order = Etapa.objects.filter(modalidad=modalidad, orden=order).order_by('id').first()
    if existing_at_order is not None:
        existing_at_order.nombre = name
        existing_at_order.orden = order
        existing_at_order.save(update_fields=['nombre', 'orden'])
        return existing_at_order

    return Etapa.objects.create(modalidad=modalidad, nombre=name, orden=order, activo=True)


@transaction.atomic
def sync_excelencia_academica_catalog() -> dict[str, int]:
    """Sincroniza de forma idempotente el catálogo oficial de documentos para Excelencia Académica."""
    modalidad = Modalidad.objects.filter(nombre__icontains='excelencia').first()
    if not modalidad:
        return {'etapas': 0, 'relaciones': 0}

    stage_map = {}
    for stage_name, order in [('Registro', 1), ('Presentación de Requisitos', 2), ('Revisión de Expediente', 3), ('Acta Final', 4)]:
        stage_map[stage_name] = _ensure_stage(modalidad, stage_name, order)

    official_docs = {
        'Presentación de Requisitos': [
            ('Carta de solicitud a la Dirección de la Carrera.', True, 1),
            ('Fotocopia del recibo de pago de matrícula.', True, 2),
            ('Historial Académico.', True, 3),
            ('Fólder amarillo rotulado.', True, 4),
            ('Certificaciones de investigación e interacción social.', True, 5),
        ],
        'Revisión de Expediente': [
            ('Certificado de la Dirección de Planificación Académica.', True, 1),
            ('Certificado de Solvencia Universitaria.', True, 2),
            ('Certificado de Solvencia Bibliotecaria.', True, 3),
            ('Timbre Universitario para la modalidad Excelencia Académica.', True, 4),
        ],
        'Acta Final': [
            ('Acta de Graduación por Excelencia Académica.', True, 1),
        ],
    }

    # Eliminar todas las asociaciones actuales de esta modalidad antes de recrearlas.
    ModalidadTipoDocumento.objects.filter(modalidad=modalidad).delete()

    for stage_name, etapa_obj in stage_map.items():
        docs = official_docs.get(stage_name, [])
        for nombre, obligatorio, orden in docs:
            tipo_doc, _ = TipoDocumento.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': '', 'obligatorio': obligatorio, 'activo': True, 'etapa': None},
            )
            ModalidadTipoDocumento.objects.create(
                modalidad=modalidad,
                tipo_documento=tipo_doc,
                etapa=etapa_obj,
                obligatorio=obligatorio,
                orden=orden,
                activo=True,
                descripcion_requerimiento='',
            )

    etapa_sequence = list(Etapa.objects.filter(modalidad=modalidad).order_by('orden'))
    for index, etapa in enumerate(etapa_sequence, start=1):
        if etapa.nombre == 'Registro' and etapa.orden != 1:
            etapa.orden = 1
            etapa.save(update_fields=['orden'])
        elif etapa.nombre == 'Presentación de Requisitos' and etapa.orden != 2:
            etapa.orden = 2
            etapa.save(update_fields=['orden'])
        elif etapa.nombre == 'Revisión de Expediente' and etapa.orden != 3:
            etapa.orden = 3
            etapa.save(update_fields=['orden'])
        elif etapa.nombre == 'Acta Final' and etapa.orden != 4:
            etapa.orden = 4
            etapa.save(update_fields=['orden'])

    return {'etapas': Etapa.objects.filter(modalidad=modalidad).count(), 'relaciones': ModalidadTipoDocumento.objects.filter(modalidad=modalidad).count()}
