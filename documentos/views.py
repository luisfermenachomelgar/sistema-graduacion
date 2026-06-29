from rest_framework import filters, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.conf import settings
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from auditoria.services import registrar_auditoria
from config.permissions import (
    DocumentoRolePermission,
    CRUDModelPermission,
    PuedeAprobarDocumentosPermission,
    can_view_all_documentos,
)
from postulantes.models import Notificacion
from .models import DocumentoPostulacion, TipoDocumento
from .serializers import DocumentoPostulacionSerializer, TipoDocumentoSerializer


# FASE 3: Custom Pagination with max_page_size limit
class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class DocumentoPostulacionViewSet(viewsets.ModelViewSet):
    queryset = DocumentoPostulacion.objects.select_related(
        'postulacion__postulante__usuario',  # FASE 2B: Complete chain (N+1 fix)
        'postulacion__modalidad',  # FASE 2C: Expose modalidad_nombre
        'tipo_documento',
        'revisado_por',
    ).all()
    serializer_class = DocumentoPostulacionSerializer
    pagination_class = CustomPagination  # FASE 3: Applied
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['postulacion', 'estado', 'tipo_documento']
    search_fields = ['postulacion__postulante__usuario__username', 'tipo_documento__nombre']
    ordering_fields = ['fecha_subida', 'fecha_revision']
    ordering = ['-fecha_subida']
    permission_classes = [DocumentoRolePermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        if can_view_all_documentos(self.request.user):
            return queryset
        return queryset.filter(postulacion__postulante__usuario=self.request.user)

    def perform_create(self, serializer):
        if (
            not self.request.user.has_perm('documentos.add_documentopostulacion')
            and serializer.validated_data['postulacion'].postulante.usuario != self.request.user
        ):
            raise PermissionDenied('Solo puedes subir documentos de tu propia postulacion.')

        if not self.request.user.has_perm('documentos.add_documentopostulacion'):
            serializer.save(estado='pendiente', revisado_por=None, fecha_revision=None)
            return
        serializer.save()

    def perform_update(self, serializer):
        instancia_anterior = self.get_object()
        if instancia_anterior.estado == 'aprobado':
            raise ValidationError('No se puede modificar un documento aprobado.')

        estado_anterior = instancia_anterior.estado
        nuevo_estado = serializer.validated_data.get('estado', estado_anterior)

        if nuevo_estado == 'aprobado' and estado_anterior != 'aprobado':
            permiso = PuedeAprobarDocumentosPermission()
            if not permiso.has_permission(self.request, self):
                raise PermissionDenied(permiso.message)

        instancia = serializer.save()

        if instancia.estado in {'aprobado', 'rechazado'} and estado_anterior != instancia.estado:
            instancia.revisado_por = self.request.user
            instancia.fecha_revision = timezone.now()
            instancia.save(update_fields=['revisado_por', 'fecha_revision'])

            accion = 'APROBACION_DOCUMENTO' if instancia.estado == 'aprobado' else 'RECHAZO_DOCUMENTO'
            registrar_auditoria(
                usuario=self.request.user,
                accion=accion,
                modelo_afectado='DocumentoPostulacion',
                objeto_id=instancia.id,
                estado_anterior={'estado': estado_anterior},
                estado_nuevo={'estado': instancia.estado},
                detalles={
                    'postulacion_id': instancia.postulacion_id,
                    'tipo_documento_id': instancia.tipo_documento_id,
                },
            )
            
            if instancia.estado == 'rechazado':
                self.enviar_notificacion_rechazo(instancia)
    def enviar_notificacion_rechazo(self, documento):
        """
        Envía un correo al estudiante notificando que su documento fue rechazado.
        """
        try:
            # Navegar relaciones para obtener datos del estudiante
            postulante = documento.postulacion.postulante
            usuario = postulante.usuario

            if not usuario:
                return
            
            # Crear notificación en sistema
            Notificacion.objects.create(
                usuario=usuario,
                mensaje=f"Documento rechazado: {documento.tipo_documento.nombre}",
                link=f'/postulaciones/{documento.postulacion.id}'
            )

            if not usuario.email:
                return

            asunto = f"Corrección requerida: {documento.tipo_documento.nombre}"
            periodo_academico = documento.postulacion.periodo_academico_display or 'período académico no registrado'
            mensaje = (
                f"Estimado(a) {postulante.nombre} {postulante.apellido},\n\n"
                f"Se ha revisado su documento '{documento.tipo_documento.nombre}' correspondiente al período académico {periodo_academico} y ha sido RECHAZADO.\n\n"
                f"Observaciones del revisor:\n"
                f"{documento.comentario_revision or 'Sin comentarios adicionales.'}\n\n"
                f"Por favor, ingrese al sistema para subir una nueva versión corregida.\n"
            )

            send_mail(
                asunto,
                mensaje,
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@sistema-graduacion.edu'),
                [usuario.email],
                fail_silently=True,
            )
        except Exception as e:
            # Evitar que un error de correo rompa el flujo de la aplicación
            print(f"Error al enviar notificación de rechazo: {e}")


from rest_framework.permissions import AllowAny  

class TipoDocumentoViewSet(viewsets.ModelViewSet):
    queryset = TipoDocumento.objects.all()
    serializer_class = TipoDocumentoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre']
    ordering = ['nombre']

    def get_permissions(self):
        if self.action in {'list', 'retrieve'}:
            return [AllowAny()]  # 👈 lectura pública

        if self.action in {'create', 'update', 'partial_update', 'destroy'}:
            return [CRUDModelPermission()]  # 👈 protegido

        return super().get_permissions()
