from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import CustomUser
from .serializers import LoginSerializer, CustomUserSerializer, CustomUserDetailSerializer


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar usuarios del sistema.
    Solo administradores pueden ver, crear, editar o eliminar usuarios.
    """
    queryset = CustomUser.objects.all()
    permission_classes = [IsAdminUser]
    
    def get_serializer_class(self):
        """Retorna diferentes serializadores según la acción."""
        if self.action in ['list', 'retrieve']:
            return CustomUserDetailSerializer
        return CustomUserSerializer
    
    def create(self, request, *args, **kwargs):
        """Crear nuevo usuario con password."""
        # Evitar crear nuevas cuentas maestras (basado en is_superuser)
        trying_master = bool(request.data.get('is_superuser'))
        master_exists = CustomUser.objects.filter(is_superuser=True).exists()

        if trying_master and master_exists:
            return Response(
                {'detail': 'Ya existe una cuenta maestra del sistema. No se pueden crear cuentas maestras adicionales.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            password = request.data.get('password')
            if not password:
                return Response(
                    {'password': 'Password es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user = CustomUser(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                first_name=serializer.validated_data.get('first_name', ''),
                last_name=serializer.validated_data.get('last_name', ''),
                is_staff=request.data.get('is_staff', False),
                is_active=request.data.get('is_active', True),
                role=request.data.get('role', 'estudiante'),
            )
            user.set_password(password)
            user.save()
            
            return Response(
                CustomUserDetailSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Actualizar usuario (PUT)."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Si se proporciona una nueva contraseña, actualizarla
        if 'password' in request.data and request.data['password']:
            instance.set_password(request.data['password'])
            # Remover password del data para el serializer
            data = {k: v for k, v in request.data.items() if k != 'password'}
        else:
            data = request.data
        
        # Protección específica para la cuenta maestra (basada en is_superuser)
        is_super = bool(instance.is_superuser)
        if is_super:
            # No permitir desactivar la cuenta maestra
            if 'is_active' in data and not bool(data.get('is_active')):
                return Response(
                    {'is_active': 'La cuenta maestra del sistema no puede ser desactivada.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # No permitir cambiar el rol de la cuenta maestra
            if 'role' in data and data.get('role') != 'admin':
                return Response(
                    {'role': 'La cuenta maestra del sistema debe conservar el rol de Administrador.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # No permitir revocar is_superuser
            if 'is_superuser' in data and not bool(data.get('is_superuser')):
                return Response(
                    {'is_superuser': 'La cuenta maestra del sistema no puede perder privilegios de superusuario.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = CustomUserSerializer(
            instance, data=data, partial=partial
        )
        
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(
                CustomUserDetailSerializer(instance).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """Proteger eliminación de la cuenta maestra (is_superuser)."""
        instance = self.get_object()
        is_super = bool(instance.is_superuser)
        if is_super:
            return Response(
                {'detail': 'La cuenta maestra del sistema no puede ser eliminada.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)
