from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('estudiante', 'Estudiante'),
    )

    # Role is descriptive (UI/reporting). Authorization must rely on Django permissions.
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        help_text='Campo descriptivo para interfaz/reportes. No usar para autorizacion.',
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
