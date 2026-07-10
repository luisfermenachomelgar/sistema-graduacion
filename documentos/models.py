from django.conf import settings
from django.db import models

from .utils import generar_preview_pdf


class DocumentoPostulacionQuerySet(models.QuerySet):
    def delete(self):
        postulacion_ids = list(self.values_list('postulacion_id', flat=True).distinct())
        result = super().delete()

        from postulantes.models import Postulacion
        from postulantes.services import finalizar_postulacion_si_corresponde

        for postulacion_id in postulacion_ids:
            postulacion = Postulacion.objects.filter(pk=postulacion_id).first()
            if postulacion is not None:
                finalizar_postulacion_si_corresponde(postulacion, actor=None)

        return result


class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    etapa = models.ForeignKey(
        'modalidades.Etapa',
        on_delete=models.PROTECT,
        related_name='tipos_documento',
        null=True,
        blank=True,
    )
    descripcion = models.TextField(blank=True)
    obligatorio = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class DocumentoPostulacion(models.Model):
    objects = DocumentoPostulacionQuerySet.as_manager()
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    )

    postulacion = models.ForeignKey('postulantes.Postulacion', on_delete=models.CASCADE, related_name='documentos')
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.PROTECT, related_name='documentos_cargados')
    archivo = models.FileField(upload_to='documentos/postulaciones/')
    preview_pdf = models.FileField(upload_to='documentos/previews/', null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    comentario_revision = models.TextField(blank=True)
    revisado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos_revisados',
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)
    fecha_revision = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha_subida']
        unique_together = ('postulacion', 'tipo_documento')
        permissions = (
            ('puede_aprobar_documentos', 'Puede aprobar documentos'),
        )

    def __str__(self):
        return f"{self.postulacion} - {self.tipo_documento.nombre}"

    def save(self, *args, **kwargs):
        archivo_anterior = None
        if self.pk:
            try:
                anterior = DocumentoPostulacion.objects.get(pk=self.pk)
                if getattr(anterior, 'archivo', None):
                    archivo_anterior = (anterior.archivo.name, anterior.archivo.size)
            except DocumentoPostulacion.DoesNotExist:
                archivo_anterior = None

        super().save(*args, **kwargs)

        archivo_actual = None
        if getattr(self, 'archivo', None):
            archivo_actual = (self.archivo.name, self.archivo.size)

        if archivo_actual and archivo_actual != archivo_anterior:
            generar_preview_pdf(self)
        elif archivo_actual and not getattr(self, 'preview_pdf', None):
            generar_preview_pdf(self)

        from postulantes.services import finalizar_postulacion_si_corresponde

        if getattr(self, 'postulacion_id', None):
            postulacion = self.postulacion
            if postulacion is not None:
                finalizar_postulacion_si_corresponde(postulacion, actor=None)

    def delete(self, *args, **kwargs):
        postulacion = getattr(self, 'postulacion', None)
        if postulacion is None and getattr(self, 'postulacion_id', None):
            from postulantes.models import Postulacion

            postulacion = Postulacion.objects.filter(pk=self.postulacion_id).first()

        result = super().delete(*args, **kwargs)

        if postulacion is not None:
            from postulantes.services import finalizar_postulacion_si_corresponde

            finalizar_postulacion_si_corresponde(postulacion, actor=None)

        return result


class ModalidadTipoDocumento(models.Model):
    """
    Relación M2M entre Modalidad y TipoDocumento.
    Define qué documentos son permitidos/obligatorios por modalidad y etapa.
    """
    modalidad = models.ForeignKey(
        'modalidades.Modalidad',
        on_delete=models.CASCADE,
        related_name='tipos_documento_requeridos',
    )
    tipo_documento = models.ForeignKey(
        TipoDocumento,
        on_delete=models.CASCADE,
        related_name='modalidades',
    )
    etapa = models.ForeignKey(
        'modalidades.Etapa',
        on_delete=models.CASCADE,
        related_name='documentos_requeridos',
        null=True,
        blank=True,
        help_text='Si está vacío, el documento aplica a todas las etapas'
    )
    obligatorio = models.BooleanField(
        default=False,
        help_text='Si es True, el documento debe presentarse en esta etapa'
    )
    orden = models.PositiveIntegerField(
        default=0,
        help_text='Orden de presentación sugerido'
    )
    descripcion_requerimiento = models.TextField(
        blank=True,
        help_text='Especificaciones adicionales para este documento en esta modalidad'
    )
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['modalidad__nombre', 'orden', 'tipo_documento__nombre']
        constraints = [
            models.UniqueConstraint(
                fields=['modalidad', 'tipo_documento', 'etapa'],
                name='unique_modalidad_documento_etapa',
            ),
        ]
        verbose_name = 'Modalidad Tipo Documento'
        verbose_name_plural = 'Modalidades Tipos Documentos'

    def __str__(self):
        etapa_str = f" - E{self.etapa.orden}" if self.etapa else ''
        oblig_str = '(Obligatorio)' if self.obligatorio else '(Opcional)'
        return f"{self.modalidad.nombre} - {self.tipo_documento.nombre}{etapa_str} {oblig_str}"
