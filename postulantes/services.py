from django.db import transaction
from rest_framework import serializers

from auditoria.services import registrar_auditoria
from documentos.models import DocumentoPostulacion, TipoDocumento
from modalidades.models import Etapa

from .models import Postulacion

ACTA_DEFENSA_TIPO_DOCUMENTO_ID = 8


ESTADO_GENERAL_BY_ORDEN = {
    1: 'EN_PROCESO',
    2: 'PERFIL_APROBADO',
    3: 'PRIVADA_APROBADA',
    4: 'PUBLICA_APROBADA',
}


class EtapaIncompletaError(serializers.ValidationError):
    pass


def resolve_estado_general(etapa: Etapa | None, *, is_final: bool = False) -> str:
    if is_final:
        return 'TITULADO'
    if not etapa:
        return 'EN_PROCESO'
    return ESTADO_GENERAL_BY_ORDEN.get(etapa.orden, 'EN_PROCESO')


def required_documents_missing(postulacion: Postulacion) -> list[dict]:
    etapa = postulacion.etapa_actual
    if not etapa:
        return []

    required_types = list(
        TipoDocumento.objects.filter(etapa_id=etapa.id, obligatorio=True, activo=True).values('id', 'nombre')
    )
    if not required_types:
        return []

    required_ids = [item['id'] for item in required_types]
    approved_ids = set(
        DocumentoPostulacion.objects.filter(
            postulacion_id=postulacion.id,
            tipo_documento_id__in=required_ids,
            estado='aprobado',
        ).values_list('tipo_documento_id', flat=True)
    )
    return [item for item in required_types if item['id'] not in approved_ids]


@transaction.atomic
def avanzar_postulacion(postulacion_id: int, *, actor=None) -> Postulacion:
    postulacion = (
        Postulacion.objects.select_for_update()
        .select_related('modalidad')
        .get(pk=postulacion_id)
    )
    etapa_anterior = postulacion.etapa_actual
    estado_general_anterior = postulacion.estado_general

    if not postulacion.etapa_actual:
        raise serializers.ValidationError(
            {'etapa_actual': 'La postulacion no tiene etapa actual configurada.'}
        )

    missing_docs = required_documents_missing(postulacion)
    if missing_docs:
        missing_names = [item['nombre'] for item in missing_docs]
        raise EtapaIncompletaError(
            {
                'detail': 'No se puede avanzar de etapa: faltan documentos obligatorios aprobados.',
                'faltantes': missing_names,
            }
        )

    next_stage = (
        Etapa.objects.filter(
            modalidad_id=postulacion.modalidad_id,
            activo=True,
            orden__gt=postulacion.etapa_actual.orden,
        )
        .order_by('orden')
        .first()
    )

    if next_stage is None:
        has_acta_defensa = DocumentoPostulacion.objects.filter(
            postulacion_id=postulacion.id,
            tipo_documento_id=ACTA_DEFENSA_TIPO_DOCUMENTO_ID,
            estado='aprobado',
        ).exists()
        if not has_acta_defensa:
            raise EtapaIncompletaError(
                {
                    'detail': 'No se puede avanzar a TITULADO. Falta el Acta de Defensa de Tesis o de Modalidad de Graduación aprobada.',
                }
            )

    if next_stage:
        postulacion.etapa_actual = next_stage
        postulacion.estado_general = resolve_estado_general(next_stage)
        postulacion.save(update_fields=['etapa_actual', 'estado_general'])
        registrar_auditoria(
            usuario=actor,
            accion='CAMBIO_ETAPA',
            modelo_afectado='Postulacion',
            objeto_id=postulacion.id,
            estado_anterior={
                'etapa_id': etapa_anterior.id if etapa_anterior else None,
                'etapa_nombre': etapa_anterior.nombre if etapa_anterior else None,
            },
            estado_nuevo={
                'etapa_id': postulacion.etapa_actual.id,
                'etapa_nombre': postulacion.etapa_actual.nombre,
            },
            detalles={'modalidad_id': postulacion.modalidad_id},
        )
        if estado_general_anterior != postulacion.estado_general:
            registrar_auditoria(
                usuario=actor,
                accion='CAMBIO_ESTADO_GENERAL',
                modelo_afectado='Postulacion',
                objeto_id=postulacion.id,
                estado_anterior={'estado_general': estado_general_anterior},
                estado_nuevo={'estado_general': postulacion.estado_general},
                detalles={'motivo': 'avance_de_etapa'},
            )
        return postulacion

    postulacion.estado_general = resolve_estado_general(postulacion.etapa_actual, is_final=True)
    postulacion.save(update_fields=['estado_general'])
    if estado_general_anterior != postulacion.estado_general:
        registrar_auditoria(
            usuario=actor,
            accion='CAMBIO_ESTADO_GENERAL',
            modelo_afectado='Postulacion',
            objeto_id=postulacion.id,
            estado_anterior={'estado_general': estado_general_anterior},
            estado_nuevo={'estado_general': postulacion.estado_general},
            detalles={'motivo': 'proceso_completado'},
        )
    return postulacion
