from django.conf import settings
from django.db import models


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
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    )

    postulacion = models.ForeignKey('postulantes.Postulacion', on_delete=models.CASCADE, related_name='documentos')
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.PROTECT, related_name='documentos_cargados')
    archivo = models.FileField(upload_to='documentos/postulaciones/')
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
