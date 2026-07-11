from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer para CustomUser completo (lectura)."""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']
    
    def validate_username(self, value):
        """
        Validar que username sea único, excluyendo la instancia actual durante edición.
        
        IMPORTANTE: Esto resuelve el problema donde al editar un usuario sin cambiar
        el username, el sistema devolvía "A user with that username already exists."
        
        Flujo:
        - Si es CREACIÓN (POST): self.instance es None, valida contra todos los usuarios
        - Si es EDICIÓN (PUT/PATCH): self.instance existe, excluye el usuario actual
        """
        instance = self.instance
        
        # Buscar otro usuario con el mismo username
        queryset = CustomUser.objects.filter(username=value)
        
        # Si estamos editando un usuario existente, excluir la instancia actual
        if instance is not None:
            queryset = queryset.exclude(pk=instance.pk)
        
        # Si existe otro usuario con ese username, retornar error
        if queryset.exists():
            raise serializers.ValidationError(
                "A user with that username already exists."
            )
        
        return value

    def validate(self, attrs):
        """
        Validaciones globales: impedir cambios críticos en la cuenta maestra.
        Se basa únicamente en `is_superuser`.
        """
        instance = getattr(self, 'instance', None)
        if instance and instance.is_superuser:
            # Prohibir desactivar
            if 'is_active' in attrs and not bool(attrs.get('is_active')):
                raise serializers.ValidationError({'is_active': 'La cuenta maestra del sistema no puede ser desactivada.'})

            # Prohibir cambio de rol
            if 'role' in attrs and attrs.get('role') != 'admin':
                raise serializers.ValidationError({'role': 'La cuenta maestra del sistema debe conservar el rol de Administrador.'})

            # Prohibir revocar is_superuser
            if 'is_superuser' in attrs and not bool(attrs.get('is_superuser')):
                raise serializers.ValidationError({'is_superuser': 'La cuenta maestra del sistema no puede perder privilegios de superusuario.'})

        if 'role' in attrs and attrs.get('role') not in dict(CustomUser.ROLE_CHOICES):
            raise serializers.ValidationError({'role': 'Rol inválido.'})

        return attrs


class CustomUserDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para CustomUser con permisos."""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'permissions'
        ]
        read_only_fields = ['id', 'date_joined', 'permissions']
    
    def get_permissions(self, obj):
        """Retorna lista de permisos del usuario."""
        if obj.is_superuser:
            return ['admin']
        return list(obj.user_permissions.values_list('codename', flat=True))


class LoginSerializer(TokenObtainPairSerializer):
    """Serializer para login con información del usuario mejorada."""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['username'] = user.username
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        
        # Información del usuario en respuesta
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'role_display': user.get_role_display(),
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }
        
        return data
