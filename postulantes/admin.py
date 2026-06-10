from django.contrib import admin

from .models import Postulante, Postulacion


@admin.register(Postulante)
class PostulanteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'codigo_estudiante', 'ci', 'carrera', 'facultad')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'codigo_estudiante', 'ci')


@admin.register(Postulacion)
class PostulacionAdmin(admin.ModelAdmin):
    list_display = (
        'postulante',
        'modalidad',
        'etapa_actual',
        'anio_academico',
        'semestre_academico',
        'periodo_academico_display',
        'estado',
        'estado_general',
        'fecha_postulacion',
    )
    list_filter = ('estado', 'estado_general', 'modalidad', 'etapa_actual', 'anio_academico', 'semestre_academico')
    search_fields = ('postulante__usuario__username', 'titulo_trabajo', 'tutor')

    @admin.display(description='Período académico')
    def periodo_academico_display(self, obj):
        return obj.periodo_academico_display or '-'
