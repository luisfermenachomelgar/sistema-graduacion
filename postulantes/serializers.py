from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Notificacion, Postulacion, Postulante

User = get_user_model()


class PostulanteListSerializer(serializers.ModelSerializer):
    """Serializer para listado de postulantes (lectura)."""
    usuario_nombre = serializers.SerializerMethodField()
    usuario_email = serializers.SerializerMethodField()
    
    class Meta:
        model = Postulante
        fields = [
            'id', 'nombre', 'apellido', 'ci', 'codigo_estudiante',
            'telefono', 'usuario_nombre', 'usuario_email', 'creado_en'
        ]
        read_only_fields = ['id', 'creado_en']

    def get_usuario_nombre(self, obj):
        usuario = getattr(obj, 'usuario', None)
        return usuario.get_full_name() if usuario else None

    def get_usuario_email(self, obj):
        usuario = getattr(obj, 'usuario', None)
        return usuario.email if usuario else None


class PostulanteDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para postulante con información de usuario."""
    usuario = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    usuario_id = serializers.IntegerField(source='usuario.id', read_only=True, allow_null=True)
    usuario_nombre = serializers.SerializerMethodField()
    usuario_email = serializers.SerializerMethodField()
    usuario_username = serializers.SerializerMethodField()
    
    class Meta:
        model = Postulante
        fields = [
            'id', 'usuario', 'usuario_id', 'usuario_username', 'usuario_nombre', 'usuario_email',
            'nombre', 'apellido', 'ci', 'codigo_estudiante', 'telefono',
            'carrera', 'facultad', 'creado_en'
        ]
        read_only_fields = ['id', 'creado_en', 'usuario_id']

    def get_usuario_nombre(self, obj):
        usuario = getattr(obj, 'usuario', None)
        return usuario.get_full_name() if usuario else None

    def get_usuario_email(self, obj):
        usuario = getattr(obj, 'usuario', None)
        return usuario.email if usuario else None

    def get_usuario_username(self, obj):
        usuario = getattr(obj, 'usuario', None)
        return usuario.username if usuario else None


class PostulacionListSerializer(serializers.ModelSerializer):
    """Serializer para listado de postulaciones."""
    postulante_nombre = serializers.SerializerMethodField()
    modalidad_nombre = serializers.CharField(source='modalidad.nombre', read_only=True)
    etapa_nombre = serializers.CharField(source='etapa_actual.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Postulacion
        fields = [
            'id', 'postulante_nombre', 'modalidad_nombre', 'titulo_trabajo',
            'etapa_nombre', 'gestion', 'estado', 'estado_display',
            'estado_general', 'fecha_postulacion'
        ]
        read_only_fields = ['id', 'fecha_postulacion']

    def get_postulante_nombre(self, obj):
        nombre = (obj.postulante.nombre or '').strip()
        apellido = (obj.postulante.apellido or '').strip()
        return f"{nombre} {apellido}".strip()


class PostulacionDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para postulación."""
    postulante = PostulanteDetailSerializer(read_only=True)
    postulante_id = serializers.PrimaryKeyRelatedField(
        queryset=Postulante.objects.all(),
        source='postulante',
        write_only=True,
    )
    modalidad_nombre = serializers.CharField(source='modalidad.nombre', read_only=True)
    etapa_nombre = serializers.CharField(source='etapa_actual.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    estado_general_display = serializers.CharField(
        source='get_estado_general_display', read_only=True
    )
    
    class Meta:
        model = Postulacion
        fields = [
            'id', 'postulante', 'postulante_id', 'modalidad', 'modalidad_nombre',
            'etapa_actual', 'etapa_nombre', 'titulo_trabajo', 'tutor', 'gestion',
            'estado', 'estado_display', 'estado_general', 'estado_general_display',
            'observaciones', 'fecha_postulacion'
        ]
        read_only_fields = ['id', 'fecha_postulacion']
    
    def validate(self, attrs):
        """Valida que la etapa pertenezca a la modalidad."""
        modalidad = attrs.get('modalidad') or getattr(self.instance, 'modalidad', None)
        etapa_actual = attrs.get('etapa_actual') or getattr(self.instance, 'etapa_actual', None)

        if modalidad and etapa_actual and etapa_actual.modalidad_id != modalidad.id:
            raise serializers.ValidationError(
                {'etapa_actual': 'La etapa debe pertenecer a la modalidad seleccionada.'}
            )

        return attrs


class NotificacionSerializer(serializers.ModelSerializer):
    """Serializer para notificaciones."""
    usuario_email = serializers.CharField(source='usuario.email', read_only=True)
    
    class Meta:
        model = Notificacion
        fields = ['id', 'usuario', 'usuario_email', 'mensaje', 'leida', 'link', 'fecha_creacion']
        read_only_fields = ['id', 'usuario', 'fecha_creacion']


class NotificacionUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar notificaciones (marcar como leída)."""
    
    class Meta:
        model = Notificacion
        fields = ['leida']


class ComentarioInternoSerializer(serializers.ModelSerializer):
    """Serializer para comentarios internos de postulaciones."""
    autor_nombre = serializers.CharField(source='autor.get_full_name', read_only=True)
    
    class Meta:
        from postulantes.models import ComentarioInterno
        model = ComentarioInterno
        fields = ['id', 'postulacion', 'autor', 'autor_nombre', 'texto', 'fecha']
        read_only_fields = ['id', 'autor', 'fecha']


class EtapaSerializer(serializers.ModelSerializer):
    """Serializer para etapas (importado desde modalidades)."""
    modalidad_nombre = serializers.CharField(source='modalidad.nombre', read_only=True)
    
    class Meta:
        from modalidades.models import Etapa
        model = Etapa
        fields = ['id', 'nombre', 'orden', 'modalidad', 'modalidad_nombre', 'activo']
        read_only_fields = ['id']


# Aliases para compatibilidad con views.py
PostulacionSerializer = PostulacionDetailSerializer
PostulanteSerializer = PostulanteDetailSerializer
