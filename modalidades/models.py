from django.db import models


class Modalidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Etapa(models.Model):
    nombre = models.CharField(max_length=100)
    orden = models.PositiveIntegerField()
    modalidad = models.ForeignKey(Modalidad, on_delete=models.CASCADE, related_name='etapas')
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['modalidad__nombre', 'orden']
        constraints = [
            models.UniqueConstraint(fields=['modalidad', 'orden'], name='unique_orden_por_modalidad'),
        ]

    def __str__(self):
        return f"{self.modalidad.nombre} - {self.orden}. {self.nombre}"


class ModalidadRequisito(models.Model):
    modalidad = models.ForeignKey(Modalidad, on_delete=models.CASCADE, related_name='requisitos')
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=1)
    archivo = models.FileField(upload_to='modalidades/requisitos/', blank=True, null=True)
    categoria = models.CharField(max_length=100, blank=True, default='General')
    obligatorio = models.BooleanField(default=True)
    version = models.CharField(max_length=50, default='1.0')
    observaciones = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['modalidad__nombre', 'orden', 'nombre']

    def __str__(self):
        return f"{self.modalidad.nombre} - {self.nombre}"
