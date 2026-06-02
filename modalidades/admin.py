from django.contrib import admin

from .models import Etapa, Modalidad, ModalidadRequisito


@admin.register(Modalidad)
class ModalidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa', 'creada_en')
    list_filter = ('activa',)
    search_fields = ('nombre',)


@admin.register(Etapa)
class EtapaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'modalidad', 'orden', 'activo')
    list_filter = ('modalidad', 'activo')
    search_fields = ('nombre', 'modalidad__nombre')
    ordering = ('modalidad__nombre', 'orden')


@admin.register(ModalidadRequisito)
class ModalidadRequisitoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'modalidad', 'categoria', 'obligatorio', 'activo', 'updated_at')
    list_filter = ('modalidad', 'categoria', 'obligatorio', 'activo')
    search_fields = ('nombre', 'descripcion', 'modalidad__nombre')
    ordering = ('modalidad__nombre', 'nombre')
