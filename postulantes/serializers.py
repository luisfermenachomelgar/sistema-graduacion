from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Notificacion, Postulacion, Postulante

User = get_user_model()


class PostulanteListSerializer(serializers.ModelSerializer):
    """Serializer para listado de postulantes (lectura)."""
    usuario_nombre = serializers.SerializerMethodField()
    usuario_email = serializers.SerializerMethodField()
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Postulante
        fields = [
            'id', 'nombre', 'apellido_paterno', 'apellido_materno', 'nombre_completo', 'ci', 'codigo_estudiante',
            'telefono', 'usuario_nombre', 'usuario_email', 'creado_en'
        ]
        read_only_fields = ['id', 'creado_en']

    def get_usuario_nombre(self, obj):
        usuario = getattr(obj, 'usuario', None)
        return usuario.get_full_name() if usuario else None

    def get_usuario_email(self, obj):
        usuario = getattr(obj, 'usuario', None)
        return usuario.email if usuario else None

    def get_nombre_completo(self, obj):
        return obj.get_full_name()


class PostulanteDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para postulante con información de usuario."""
    usuario = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    usuario_id = serializers.IntegerField(source='usuario.id', read_only=True, allow_null=True)
    usuario_nombre = serializers.SerializerMethodField()
    usuario_email = serializers.SerializerMethodField()
    usuario_username = serializers.SerializerMethodField()
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Postulante
        fields = [
            'id', 'usuario', 'usuario_id', 'usuario_username', 'usuario_nombre', 'usuario_email',
            'nombre', 'apellido_paterno', 'apellido_materno', 'nombre_completo', 'ci', 'codigo_estudiante', 'telefono',
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

    def get_nombre_completo(self, obj):
        return obj.get_full_name()


class PostulacionListSerializer(serializers.ModelSerializer):
    """Serializer para listado de postulaciones."""
    postulante_nombre = serializers.SerializerMethodField()
    ru = serializers.SerializerMethodField()
    tutor = serializers.CharField(read_only=True)
    postulante_carrera = serializers.CharField(source='postulante.carrera', read_only=True)
    modalidad = serializers.IntegerField(source='modalidad.id', read_only=True)
    modalidad_nombre = serializers.CharField(source='modalidad.nombre', read_only=True)
    etapa_actual = serializers.IntegerField(source='etapa_actual.id', read_only=True, allow_null=True)
    etapa_nombre = serializers.CharField(source='etapa_actual.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    periodo_academico_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = Postulacion
        fields = [
            'id', 'ru', 'postulante_nombre', 'postulante_carrera', 'modalidad', 'modalidad_nombre', 'etapa_actual', 'titulo_trabajo',
            'tutor', 'etapa_nombre', 'anio_academico', 'semestre_academico', 'periodo_academico_display', 'estado', 'estado_display',
            'estado_general', 'fecha_postulacion'
        ]
        read_only_fields = ['id', 'fecha_postulacion']

    def get_postulante_nombre(self, obj):
        postulante = obj.postulante
        if postulante is None:
            return ''
        return postulante.get_full_name()

    def get_ru(self, obj):
        postulante = getattr(obj, 'postulante', None)
        if postulante is None:
            return '-'
        value = getattr(postulante, 'codigo_estudiante', None)
        value = str(value).strip() if value is not None else ''
        return value if value else '-'


class PostulacionDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para postulación."""
    titulo_trabajo = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    tutor = serializers.CharField(required=False, allow_blank=True, allow_null=True)
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
    periodo_academico_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = Postulacion
        fields = [
            'id', 'postulante', 'postulante_id', 'modalidad', 'modalidad_nombre',
            'etapa_actual', 'etapa_nombre', 'titulo_trabajo', 'tutor', 'anio_academico', 'semestre_academico', 'periodo_academico_display',
            'estado', 'estado_display', 'estado_general', 'estado_general_display',
            'observaciones', 'fecha_postulacion'
        ]
        read_only_fields = ['id', 'fecha_postulacion', 'estado_general']
        validators = [
            UniqueTogetherValidator(
                queryset=Postulacion.objects.all(),
                fields=['postulante', 'anio_academico', 'semestre_academico'],
                message='El postulante ya cuenta con una postulación registrada para la gestión y período académico seleccionados.'
            )
        ]

    def validate(self, attrs):
        # Determinar modalidad desde datos entrantes o instancia
        modalidad_val = attrs.get('modalidad') or getattr(self.instance, 'modalidad', None)
        modalidad_nombre = None
        if modalidad_val is not None:
            try:
                modalidad_obj = modalidad_val if hasattr(modalidad_val, 'nombre') else None
                if modalidad_obj is None:
                    from modalidades.models import Modalidad
                    modalidad_obj = Modalidad.objects.filter(pk=modalidad_val).first()
                modalidad_nombre = modalidad_obj.nombre if modalidad_obj else None
            except Exception:
                modalidad_nombre = None

        requires = ('PROYECTO DE GRADO', 'TESIS', 'TRABAJO DIRIGIDO')
        optional = ('EXAMEN DE GRADO', 'EXCELENCIA ACADÉMICA')

        modalidad_upper = ' '.join(modalidad_nombre.strip().upper().split()) if modalidad_nombre else None

        # El modelo no permite titulo_trabajo = None, así que normalizamos a cadena vacía
        if attrs.get('titulo_trabajo') is None:
            attrs['titulo_trabajo'] = ''
        if attrs.get('tutor') is None:
            attrs['tutor'] = ''

        if modalidad_upper in requires:
            if not attrs.get('titulo_trabajo'):
                raise serializers.ValidationError({
                    'titulo_trabajo': 'Este campo es requerido para la modalidad seleccionada.'
                })
            if not attrs.get('tutor'):
                raise serializers.ValidationError({
                    'tutor': 'Este campo es requerido para la modalidad seleccionada.'
                })
        elif modalidad_upper in optional:
            attrs.setdefault('titulo_trabajo', '')
            attrs.setdefault('tutor', '')

        etapa_actual = attrs.get('etapa_actual') or getattr(self.instance, 'etapa_actual', None)
        anio_academico = attrs.get('anio_academico', getattr(self.instance, 'anio_academico', None))
        semestre_academico = attrs.get('semestre_academico', getattr(self.instance, 'semestre_academico', None))

        if anio_academico is None:
            raise serializers.ValidationError({'anio_academico': 'El año académico es requerido.'})

        if semestre_academico is None:
            raise serializers.ValidationError({'semestre_academico': 'El semestre académico es requerido.'})

        if semestre_academico not in (1, 2):
            raise serializers.ValidationError({'semestre_academico': 'El semestre académico debe ser 1 o 2.'})

        postulante = attrs.get('postulante') or getattr(self.instance, 'postulante', None)
        if postulante is not None:
            existing = Postulacion.objects.filter(
                postulante=postulante,
                anio_academico=anio_academico,
                semestre_academico=semestre_academico,
            )
            if self.instance is not None:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise serializers.ValidationError({
                    'non_field_errors': [
                        'El postulante ya cuenta con una postulación registrada para la gestión y período académico seleccionados.'
                    ]
                })

        modalidad_obj = modalidad_val if hasattr(modalidad_val, 'nombre') else modalidad_val
        if postulante is not None and modalidad_obj is not None:
            rechazadas_qs = Postulacion.objects.filter(
                postulante=postulante,
                modalidad=modalidad_obj,
                estado='rechazada',
            )
            if self.instance is not None:
                rechazadas_qs = rechazadas_qs.exclude(pk=self.instance.pk)
            if rechazadas_qs.exists():
                raise serializers.ValidationError({
                    'modalidad': 'El estudiante ya fue rechazado anteriormente en esta modalidad y no puede volver a postularse a la misma.'
                })

        if modalidad_val and etapa_actual and etapa_actual.modalidad_id != modalidad_val.id:
            raise serializers.ValidationError(
                {'etapa_actual': 'La etapa debe pertenecer a la modalidad seleccionada.'}
            )

        return attrs

        postulante = attrs.get('postulante') or getattr(self.instance, 'postulante', None)
        if postulante is not None:
            existing = Postulacion.objects.filter(
                postulante=postulante,
                anio_academico=anio_academico,
                semestre_academico=semestre_academico,
            )
            if self.instance is not None:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise serializers.ValidationError({
                    'non_field_errors': [
                        'El postulante ya cuenta con una postulación registrada para la gestión y período académico seleccionados.'
                    ]
                })

        # Validación adicional: si el postulante ya fue rechazado en la misma modalidad
        # no puede volver a postularse a esa modalidad en el futuro.
        modalidad_obj = modalidad
        if postulante is not None and modalidad_obj is not None:
            rechazadas_qs = Postulacion.objects.filter(
                postulante=postulante,
                modalidad=modalidad_obj,
                estado='rechazada',
            )
            if self.instance is not None:
                rechazadas_qs = rechazadas_qs.exclude(pk=self.instance.pk)
            if rechazadas_qs.exists():
                raise serializers.ValidationError({
                    'modalidad': 'El estudiante ya fue rechazado anteriormente en esta modalidad y no puede volver a postularse a la misma.'
                })

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
