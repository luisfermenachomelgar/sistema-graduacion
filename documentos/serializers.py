from rest_framework import serializers
from django.core.validators import FileExtensionValidator
from .models import DocumentoPostulacion, TipoDocumento, ModalidadTipoDocumento


# Extensiones y tamaño permitidos para documentos
DOCUMENT_EXTENSIONS = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png']
MAX_DOCUMENT_SIZE = 25 * 1024 * 1024  # 25MB


class TipoDocumentoSerializer(serializers.ModelSerializer):
    """Serializer para tipos de documento."""
    etapa_nombre = serializers.CharField(source='etapa.nombre', read_only=True)
    
    class Meta:
        model = TipoDocumento
        fields = ['id', 'nombre', 'etapa', 'etapa_nombre', 'descripcion', 'obligatorio', 'activo']
        read_only_fields = ['id']


class ModalidadTipoDocumentoSerializer(serializers.ModelSerializer):
    """Serializer para la relación Modalidad ↔ TipoDocumento."""
    tipo_documento = TipoDocumentoSerializer(read_only=True)
    etapa_nombre = serializers.CharField(source='etapa.nombre', read_only=True)
    modalidad_nombre = serializers.CharField(source='modalidad.nombre', read_only=True)
    documento_id = serializers.SerializerMethodField()
    documento_estado = serializers.SerializerMethodField()
    documento_estado_display = serializers.SerializerMethodField()
    documento_archivo_url = serializers.SerializerMethodField()
    documento_preview_pdf_url = serializers.SerializerMethodField()
    documento_archivo_nombre = serializers.SerializerMethodField()

    class Meta:
        model = ModalidadTipoDocumento
        fields = [
            'id',
            'modalidad',
            'modalidad_nombre',
            'tipo_documento',
            'etapa',
            'etapa_nombre',
            'obligatorio',
            'orden',
            'activo',
            'descripcion_requerimiento',
            'documento_id',
            'documento_estado',
            'documento_estado_display',
            'documento_archivo_url',
            'documento_preview_pdf_url',
            'documento_archivo_nombre',
        ]
        read_only_fields = ['id', 'modalidad', 'modalidad_nombre', 'tipo_documento', 'etapa_nombre']

    def _get_documento(self, obj):
        return getattr(obj, '_related_documento_postulacion', None)

    def get_documento_id(self, obj):
        documento = self._get_documento(obj)
        return documento.id if documento else None

    def get_documento_estado(self, obj):
        documento = self._get_documento(obj)
        return documento.estado if documento else None

    def get_documento_estado_display(self, obj):
        documento = self._get_documento(obj)
        if not documento:
            return None
        return getattr(documento, 'get_estado_display', lambda: None)() if hasattr(documento, 'get_estado_display') else None

    def get_documento_archivo_url(self, obj):
        documento = self._get_documento(obj)
        if not documento:
            return None
        return getattr(documento, 'archivo', None).url if getattr(documento, 'archivo', None) else None

    def get_documento_preview_pdf_url(self, obj):
        documento = self._get_documento(obj)
        if not documento:
            return None
        if getattr(documento, 'preview_pdf', None):
            try:
                return documento.preview_pdf.url
            except Exception:
                return None
        return None

    def get_documento_archivo_nombre(self, obj):
        documento = self._get_documento(obj)
        if not documento or not getattr(documento, 'archivo', None):
            return None
        return documento.archivo.name.split('/')[-1]


class DocumentoPostulacionListSerializer(serializers.ModelSerializer):
    """Serializer para listado de documentos."""
    postulacion_id = serializers.IntegerField(source='postulacion.id', read_only=True)
    postulante_nombre = serializers.CharField(
        source='postulacion.postulante.get_full_name', read_only=True
    )
    tipo_documento_nombre = serializers.CharField(
        source='tipo_documento.nombre', read_only=True
    )
    etapa_nombre = serializers.CharField(
        source='postulacion.etapa_actual.nombre', read_only=True, allow_null=True
    )
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    revisado_por_nombre = serializers.CharField(
        source='revisado_por.get_full_name', read_only=True
    )
    
    class Meta:
        model = DocumentoPostulacion
        fields = [
            'id', 'postulacion_id', 'postulante_nombre', 'tipo_documento_nombre',
            'etapa_nombre', 'estado', 'estado_display', 'revisado_por_nombre', 'fecha_subida', 'fecha_revision'
        ]
        read_only_fields = ['id', 'fecha_subida', 'fecha_revision']


class DocumentoPostulacionDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para documentos con validación de archivo."""
    tipo_documento_nombre = serializers.CharField(
        source='tipo_documento.nombre', read_only=True
    )
    etapa_nombre = serializers.CharField(
        source='postulacion.etapa_actual.nombre', read_only=True, allow_null=True
    )
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    revisado_por_nombre = serializers.CharField(
        source='revisado_por.get_full_name', read_only=True, allow_null=True
    )
    postulante_nombre = serializers.CharField(
        source='postulacion.postulante.get_full_name', read_only=True
    )
    modalidad_nombre = serializers.CharField(
        source='postulacion.modalidad.nombre', read_only=True
    )
    archivo_url = serializers.SerializerMethodField()
    archivo_tipo = serializers.SerializerMethodField()
    archivo_tamaño = serializers.SerializerMethodField()
    preview_pdf_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentoPostulacion
        fields = [
            'id', 'postulacion', 'tipo_documento', 'tipo_documento_nombre',
            'postulante_nombre', 'modalidad_nombre', 'etapa_nombre',
            'archivo', 'archivo_url', 'archivo_tipo', 'archivo_tamaño',
                'preview_pdf_url',
            'estado', 'estado_display', 'comentario_revision',
            'revisado_por', 'revisado_por_nombre',
            'fecha_subida', 'fecha_revision'
        ]
        read_only_fields = ['id', 'fecha_subida', 'fecha_revision', 'revisado_por']
    
    def validate_archivo(self, value):
        """Valida extensión y tamaño del archivo."""
        # Validar tamaño
        if value.size > MAX_DOCUMENT_SIZE:
            raise serializers.ValidationError(
                f'El archivo es demasiado grande. Máximo: {MAX_DOCUMENT_SIZE / (1024*1024):.0f}MB'
            )
        
        # Validar extensión
        ext = value.name.split('.')[-1].lower()
        if ext not in DOCUMENT_EXTENSIONS:
            raise serializers.ValidationError(
                f'Extensión no permitida. Extensiones válidas: {", ".join(DOCUMENT_EXTENSIONS)}'
            )
        
        return value
    
    def get_archivo_url(self, obj):
        """Retorna URL pública del archivo."""
        if obj.archivo:
            return obj.archivo.url
        return None
    
    def get_archivo_tipo(self, obj):
        """Retorna tipo de archivo."""
        if obj.archivo:
            return obj.archivo.name.split('.')[-1].upper()
        return None
    
    def get_archivo_tamaño(self, obj):
        """Retorna tamaño del archivo en KB."""
        if obj.archivo:
            return round(obj.archivo.size / 1024, 2)
        return None

    def get_preview_pdf_url(self, obj):
        if getattr(obj, 'preview_pdf', None):
            try:
                return obj.preview_pdf.url
            except Exception:
                return None
        return None


class DocumentoPostulacionCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear/subir documentos.
    
    Permitir que admin seleccione el estado al crear.
    Estudiantes siempre tendrán estado='pendiente' (forzado aquí).
    """
    
    class Meta:
        model = DocumentoPostulacion
        fields = ['postulacion', 'tipo_documento', 'archivo', 'estado']
    
    def validate_archivo(self, value):
        """Valida extensión y tamaño del archivo."""
        if value.size > MAX_DOCUMENT_SIZE:
            raise serializers.ValidationError(
                f'El archivo es demasiado grande. Máximo: {MAX_DOCUMENT_SIZE / (1024*1024):.0f}MB'
            )
        
        ext = value.name.split('.')[-1].lower()
        if ext not in DOCUMENT_EXTENSIONS:
            raise serializers.ValidationError(
                f'Extensión no permitida. Extensiones válidas: {", ".join(DOCUMENT_EXTENSIONS)}'
            )
        
        return value
    
    def save(self, **kwargs):
        """
        Guardar documento.
        
        REGLA DE NEGOCIO:
        - Admin: puede seleccionar cualquier estado (pendiente, aprobado, rechazado)
        - Estudiante: siempre se guarda como 'pendiente'
        """
        request = self.context.get('request')
        
        # Verificar si el usuario es admin/privilegiado
        is_admin = (
            request and request.user and (
                request.user.has_perm('documentos.add_documentopostulacion') or
                request.user.has_perm('documentos.change_documentopostulacion')
            )
        )
        
        # Si es estudiante, forzar estado='pendiente' y sin revisor
        if not is_admin:
            kwargs['estado'] = 'pendiente'
            kwargs['revisado_por'] = None
            kwargs['fecha_revision'] = None
        
        return super().save(**kwargs)


class DocumentoPostulacionUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar documentos (aprobación/rechazo)."""
    
    class Meta:
        model = DocumentoPostulacion
        fields = ['estado', 'comentario_revision']


# Alias para compatibilidad con views.py
DocumentoPostulacionSerializer = DocumentoPostulacionDetailSerializer
