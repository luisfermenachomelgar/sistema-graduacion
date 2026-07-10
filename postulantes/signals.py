from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver

from auditoria.services import registrar_auditoria
from documentos.models import DocumentoPostulacion
from .models import Postulacion
from .services import finalizar_postulacion_si_corresponde


@receiver(pre_delete, sender=Postulacion)
def auditar_eliminacion_postulacion(sender, instance, using, **kwargs):
    """
    Registra en auditoría antes de eliminar una Postulacion.
    
    Captura los datos completos del registro antes de que se pierdan.
    Útil para tribunal: proporciona evidencia de qué se eliminó, cuándo y qué contenía.
    
    Args:
        sender: Modelo que se está eliminando (Postulacion)
        instance: Instancia de Postulacion a eliminar
        using: Base de datos utilizada
        **kwargs: Argumentos adicionales del signal
    """
    registrar_auditoria(
        usuario=None,  # No sabemos quién eliminó (si fue vía admin, API o scripts)
        accion='ELIMINACION_POSTULACION',
        modelo_afectado='Postulacion',
        objeto_id=str(instance.id),
        estado_anterior={
            'postulante_id': instance.postulante_id,
            'postulante_nombre': str(instance.postulante),
            'modalidad_id': instance.modalidad_id,
            'modalidad_nombre': instance.modalidad.nombre if instance.modalidad else None,
            'titulo_trabajo': instance.titulo_trabajo,
            'etapa_actual_id': instance.etapa_actual_id,
            'etapa_actual_nombre': instance.etapa_actual.nombre if instance.etapa_actual else None,
            'estado': instance.estado,
            'estado_general': instance.estado_general,
            'anio_academico': instance.anio_academico,
            'semestre_academico': instance.semestre_academico,
            'observaciones': instance.observaciones,
            'fecha_postulacion': instance.fecha_postulacion.isoformat() if instance.fecha_postulacion else None,
        },
        estado_nuevo=None,  # Se elimina, no hay estado nuevo
        detalles={
            'tipo_eliminacion': 'fisica',
            'razon': 'eliminacion_manual',
        },
    )


@receiver(post_delete, sender=DocumentoPostulacion)
def reevalua_postulacion_al_eliminar_documento(sender, instance, **kwargs):
    postulacion = getattr(instance, 'postulacion', None)
    if postulacion is None:
        return
    finalizar_postulacion_si_corresponde(postulacion, actor=None)
