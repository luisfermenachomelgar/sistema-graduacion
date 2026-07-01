from rest_framework import serializers

from .models import Etapa, Modalidad, ModalidadRequisito


class EtapaSerializer(serializers.ModelSerializer):
    """Serializer para etapas."""
    modalidad_nombre = serializers.CharField(source='modalidad.nombre', read_only=True)
    
    class Meta:
        model = Etapa
        fields = ['id', 'nombre', 'orden', 'modalidad', 'modalidad_nombre', 'activo']
        read_only_fields = ['id']


class ModalidadListSerializer(serializers.ModelSerializer):
    """Serializer para listado de modalidades."""
    total_etapas = serializers.SerializerMethodField()
    
    class Meta:
        model = Modalidad
        fields = ['id', 'nombre', 'descripcion', 'activa', 'total_etapas', 'creada_en']
        read_only_fields = ['id', 'creada_en']
    
    def get_total_etapas(self, obj):
        """Retorna el número de etapas en la modalidad."""
        return obj.etapas.filter(activo=True).count()


class ModalidadDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para modalidades con etapas."""
    etapas = EtapaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Modalidad
        fields = ['id', 'nombre', 'descripcion', 'activa', 'etapas', 'creada_en', 'actualizada_en']
        read_only_fields = ['id', 'creada_en', 'actualizada_en']


class ModalidadSerializer(serializers.ModelSerializer):
    """Serializer general para modalidades."""
    
    class Meta:
        model = Modalidad
        fields = '__all__'
        read_only_fields = ['id', 'creada_en', 'actualizada_en']


class ModalidadRequisitoSerializer(serializers.ModelSerializer):
    modalidad_nombre = serializers.CharField(source='modalidad.nombre', read_only=True)
    archivo_url = serializers.SerializerMethodField()
    archivo_nombre = serializers.SerializerMethodField()
    archivo_tipo = serializers.SerializerMethodField()
    archivo_tamano = serializers.SerializerMethodField()

    class Meta:
        model = ModalidadRequisito
        fields = [
            'id',
            'modalidad',
            'modalidad_nombre',
            'nombre',
            'orden',
            'descripcion',
            'archivo',
            'archivo_url',
            'archivo_nombre',
            'archivo_tipo',
            'archivo_tamano',
            'categoria',
            'obligatorio',
            'version',
            'observaciones',
            'activo',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'modalidad', 'modalidad_nombre', 'orden', 'archivo_url', 'archivo_nombre', 'archivo_tipo', 'archivo_tamano', 'created_at', 'updated_at']

    def validate_archivo(self, value):
        if not value:
            return value

        max_size = 25 * 1024 * 1024
        allowed_extensions = ['pdf', 'doc', 'docx', 'xls', 'xlsx']

        if value.size > max_size:
            raise serializers.ValidationError('El archivo no debe exceder 25MB.')

        extension = value.name.split('.')[-1].lower()
        if extension not in allowed_extensions:
            raise serializers.ValidationError(
                f'Extensión no permitida. Usa: {", ".join(allowed_extensions)}'
            )

        return value

    def validate(self, attrs):
        if self.instance is None and not attrs.get('archivo'):
            raise serializers.ValidationError({'archivo': 'El archivo es requerido para crear el requisito.'})
        return attrs

    def get_archivo_url(self, obj):
        if obj.archivo:
            request = self.context.get('request')
            url = obj.archivo.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None

    def get_archivo_nombre(self, obj):
        if obj.archivo:
            return obj.archivo.name.split('/')[-1]
        return None

    def get_archivo_tipo(self, obj):
        if obj.archivo:
            return obj.archivo.name.split('.')[-1].upper()
        return None

    def get_archivo_tamano(self, obj):
        if obj.archivo:
            return round(obj.archivo.size / 1024, 2)
        return None
