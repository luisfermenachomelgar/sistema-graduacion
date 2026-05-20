from django.conf import settings
from django.db import models


class Postulante(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perfil_postulante',
    )
    nombre = models.CharField(max_length=150)
    apellido = models.CharField(max_length=150)
    ci = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20)
    
    # Campos Legacy (Mantener para compatibilidad, relajar validación)
    carrera = models.CharField(max_length=150, blank=True)
    facultad = models.CharField(max_length=150, blank=True)
    
    codigo_estudiante = models.CharField(max_length=30, unique=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.codigo_estudiante}"

    def get_full_name(self):
        nombre = getattr(self, "nombre", "") or ""
        apellido = getattr(self, "apellido", "") or ""
        return f"{nombre} {apellido}".strip()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Postulacion(models.Model):
    ESTADO_CHOICES = (
        ('borrador', 'Borrador'),
        ('en_revision', 'En revision'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    )
    ESTADO_GENERAL_CHOICES = (
        ('EN_PROCESO', 'En proceso'),
        ('PERFIL_APROBADO', 'Perfil aprobado'),
        ('PRIVADA_APROBADA', 'Privada aprobada'),
        ('PUBLICA_APROBADA', 'Publica aprobada'),
        ('TITULADO', 'Titulado'),
    )

    postulante = models.ForeignKey(Postulante, on_delete=models.CASCADE, related_name='postulaciones')
    modalidad = models.ForeignKey('modalidades.Modalidad', on_delete=models.PROTECT, related_name='postulaciones')
    etapa_actual = models.ForeignKey(
        'modalidades.Etapa',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='postulaciones_actuales',
    )
    titulo_trabajo = models.CharField(max_length=255)
    
    # Campo Legacy
    tutor = models.CharField(max_length=150, blank=True)
    
    gestion = models.PositiveIntegerField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    estado_general = models.CharField(
        max_length=30,
        choices=ESTADO_GENERAL_CHOICES,
        default='EN_PROCESO',
    )
    observaciones = models.TextField(blank=True)
    fecha_postulacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_postulacion']
        unique_together = ('postulante', 'gestion')
        permissions = (
            ('puede_avanzar_etapa', 'Puede avanzar etapa'),
        )

    def __str__(self):
        return f"{self.postulante} - {self.modalidad.nombre} ({self.gestion})"

class Notificacion(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones',
    )
    mensaje = models.CharField(max_length=255)
    leida = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.usuario} - {self.mensaje}"


class ComentarioInterno(models.Model):
    postulacion = models.ForeignKey(Postulacion, on_delete=models.CASCADE, related_name='comentarios_internos')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    texto = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
