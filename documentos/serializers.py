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
        ]
        read_only_fields = ['id', 'modalidad', 'modalidad_nombre', 'tipo_documento', 'etapa_nombre']


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
    
    class Meta:
        model = DocumentoPostulacion
        fields = [
            'id', 'postulacion', 'tipo_documento', 'tipo_documento_nombre',
            'postulante_nombre', 'modalidad_nombre', 'etapa_nombre',
            'archivo', 'archivo_url', 'archivo_tipo', 'archivo_tamaño',
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


class DocumentoPostulacionCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear/subir documentos."""
    
    class Meta:
        model = DocumentoPostulacion
        fields = ['postulacion', 'tipo_documento', 'archivo']
    
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


class DocumentoPostulacionUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar documentos (aprobación/rechazo)."""
    
    class Meta:
        model = DocumentoPostulacion
        fields = ['estado', 'comentario_revision']


# Alias para compatibilidad con views.py
DocumentoPostulacionSerializer = DocumentoPostulacionDetailSerializer
