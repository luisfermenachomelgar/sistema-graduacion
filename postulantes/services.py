from django.db import transaction
from rest_framework import serializers

from auditoria.services import registrar_auditoria
from django.db.models import Q
from documentos.models import DocumentoPostulacion, TipoDocumento, ModalidadTipoDocumento
from modalidades.models import Etapa

from .models import Postulacion

ESTADO_GENERAL_FINALIZADA = 'FINALIZADA'


def condicion_postulacion_finalizada() -> Q:
    """Predicado canónico para consultar modalidades finalizadas.

    El flujo de postulaciones asigna este estado cuando una modalidad llega a
    su finalización. Los consumidores de datos (como reportes) deben usar esta
    función en lugar de inferir la finalización desde el nombre u orden de una
    etapa.
    """
    return Q(estado_general=ESTADO_GENERAL_FINALIZADA)


def es_registro_historico(postulacion: Postulacion) -> bool:
    return getattr(postulacion, 'etapa_actual_id', None) is None


def required_documents_missing_for_historical_flow(postulacion: Postulacion) -> list[dict]:
    mtd_qs = ModalidadTipoDocumento.objects.filter(
        modalidad_id=postulacion.modalidad_id,
        obligatorio=True,
        activo=True,
    )

    if not mtd_qs.exists():
        return []

    missing: list[dict] = []
    for mtd in mtd_qs.select_related('tipo_documento'):
        tipo = mtd.tipo_documento
        docs = DocumentoPostulacion.objects.filter(postulacion_id=postulacion.id, tipo_documento_id=tipo.id)
        if not docs.exists():
            missing.append({'id': tipo.id, 'nombre': tipo.nombre, 'motivo': 'no_cargado'})
            continue
        aprobado = docs.filter(estado='aprobado').exists()
        if not aprobado:
            missing.append({'id': tipo.id, 'nombre': tipo.nombre, 'motivo': 'no_aprobado'})

    return missing


def finalizar_postulacion_si_corresponde(postulacion: Postulacion, *, actor=None) -> Postulacion:
    if not es_registro_historico(postulacion):
        return postulacion

    estado_general_anterior = postulacion.estado_general
    missing_docs = required_documents_missing_for_historical_flow(postulacion)

    if missing_docs:
        if estado_general_anterior == ESTADO_GENERAL_FINALIZADA:
            postulacion.estado_general = 'EN_PROCESO'
            postulacion.save(update_fields=['estado_general'])
            if estado_general_anterior != postulacion.estado_general:
                registrar_auditoria(
                    usuario=actor,
                    accion='CAMBIO_ESTADO_GENERAL',
                    modelo_afectado='Postulacion',
                    objeto_id=postulacion.id,
                    estado_anterior={'estado_general': estado_general_anterior},
                    estado_nuevo={'estado_general': postulacion.estado_general},
                    detalles={'motivo': 'reapertura_por_documentos_historicos'},
                )
        return postulacion

    if estado_general_anterior == ESTADO_GENERAL_FINALIZADA:
        return postulacion

    postulacion.estado_general = ESTADO_GENERAL_FINALIZADA
    postulacion.save(update_fields=['estado_general'])

    if estado_general_anterior != postulacion.estado_general:
        registrar_auditoria(
            usuario=actor,
            accion='CAMBIO_ESTADO_GENERAL',
            modelo_afectado='Postulacion',
            objeto_id=postulacion.id,
            estado_anterior={'estado_general': estado_general_anterior},
            estado_nuevo={'estado_general': postulacion.estado_general},
            detalles={'motivo': 'finalizacion_por_documentos_historicos'},
        )

    return postulacion


ESTADO_GENERAL_BY_ORDEN = {
    1: 'EN_PROCESO',
    2: 'PERFIL_APROBADO',
    3: 'PRIVADA_APROBADA',
    4: 'PUBLICA_APROBADA',
}


class EtapaIncompletaError(serializers.ValidationError):
    pass


def resolve_estado_general(etapa: Etapa | None) -> str:
    if not etapa:
        return 'EN_PROCESO'
    return ESTADO_GENERAL_BY_ORDEN.get(etapa.orden, 'EN_PROCESO')


def required_documents_missing(postulacion: Postulacion) -> list[dict]:
    etapa = postulacion.etapa_actual
    if not etapa:
        return []
    # Usar la configuración de ModalidadTipoDocumento (documentos por modalidad y etapa)
    mtd_qs = ModalidadTipoDocumento.objects.filter(
        modalidad_id=postulacion.modalidad_id,
        obligatorio=True,
        activo=True,
    ).filter(Q(etapa_id=etapa.id) | Q(etapa__isnull=True))

    if not mtd_qs.exists():
        return []

    missing: list[dict] = []
    # Para cada tipo requerido, comprobar que exista un DocumentoPostulacion aprobado
    for mtd in mtd_qs.select_related('tipo_documento'):
        tipo = mtd.tipo_documento
        # ¿se cargó algún documento de este tipo para la postulación?
        docs = DocumentoPostulacion.objects.filter(postulacion_id=postulacion.id, tipo_documento_id=tipo.id)
        if not docs.exists():
            missing.append({'id': tipo.id, 'nombre': tipo.nombre, 'motivo': 'no_cargado'})
            continue
        # Hay al menos uno cargado; verificar que alguno esté aprobado
        aprobado = docs.filter(estado='aprobado').exists()
        if not aprobado:
            missing.append({'id': tipo.id, 'nombre': tipo.nombre, 'motivo': 'no_aprobado'})

    return missing


def finalizar_postulacion_por_avance(
    postulacion: Postulacion,
    *,
    etapa_anterior: Etapa,
    estado_general_anterior: str,
    actor=None,
) -> Postulacion:
    """Finaliza una postulación que llegó a la última etapa de su modalidad."""
    postulacion.etapa_actual = None
    postulacion.estado_general = ESTADO_GENERAL_FINALIZADA
    postulacion.save(update_fields=['etapa_actual', 'estado_general'])

    registrar_auditoria(
        usuario=actor,
        accion='CAMBIO_ETAPA',
        modelo_afectado='Postulacion',
        objeto_id=postulacion.id,
        estado_anterior={
            'etapa_id': etapa_anterior.id,
            'etapa_nombre': etapa_anterior.nombre,
        },
        estado_nuevo={
            'etapa_id': None,
            'etapa_nombre': None,
        },
        detalles={'modalidad_id': postulacion.modalidad_id, 'motivo': 'finalizacion_modalidad'},
    )
    if estado_general_anterior != postulacion.estado_general:
        registrar_auditoria(
            usuario=actor,
            accion='CAMBIO_ESTADO_GENERAL',
            modelo_afectado='Postulacion',
            objeto_id=postulacion.id,
            estado_anterior={'estado_general': estado_general_anterior},
            estado_nuevo={'estado_general': postulacion.estado_general},
            detalles={'motivo': 'finalizacion_modalidad'},
        )
    # Refrescar la instancia desde la base de datos para evitar estados
    # en memoria que puedan dar lugar a reasignaciones posteriores.
    postulacion.refresh_from_db()
    return postulacion


@transaction.atomic
def avanzar_postulacion(postulacion_id: int, *, actor=None) -> Postulacion:
    postulacion = (
        Postulacion.objects.select_for_update()
        .select_related('modalidad')
        .get(pk=postulacion_id)
    )
    etapa_anterior = postulacion.etapa_actual
    estado_general_anterior = postulacion.estado_general

    if postulacion.estado_general == ESTADO_GENERAL_FINALIZADA:
        raise EtapaIncompletaError(
            {
                'detail': 'La postulación ya está finalizada.',
            }
        )

    if not postulacion.etapa_actual:
        raise serializers.ValidationError(
            {'etapa_actual': 'La postulacion no tiene etapa actual configurada.'}
        )

    missing_docs = required_documents_missing(postulacion)
    if missing_docs:
        missing_names = [item['nombre'] for item in missing_docs]
        raise EtapaIncompletaError(
            {
                'detail': 'Existen documentos obligatorios pendientes o no aprobados.',
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

    result = finalizar_postulacion_por_avance(
        postulacion,
        etapa_anterior=etapa_anterior,
        estado_general_anterior=estado_general_anterior,
        actor=actor,
    )
    # Asegurar que devolvemos la instancia actualizada desde BD
    try:
        result.refresh_from_db()
    except Exception:
        pass
    return result
