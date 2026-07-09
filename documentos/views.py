from rest_framework import filters, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from django.conf import settings

BLOCKED_DOCUMENT_MESSAGE = 'Solo es posible subir documentos durante la etapa de Registro. Las actas de evaluación son registradas por la administración de la Carrera.'
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
from .serializers import (
    DocumentoPostulacionSerializer,
    TipoDocumentoSerializer,
    DocumentoPostulacionCreateSerializer,
)
from postulantes.models import Postulacion
from rest_framework.response import Response
from rest_framework import status


# FASE 3: Custom Pagination with max_page_size limit
class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class DocumentoPostulacionViewSet(viewsets.ModelViewSet):
    queryset = DocumentoPostulacion.objects.select_related(
        'postulacion__postulante__usuario',
        'postulacion__modalidad',
        'tipo_documento',
        'revisado_por',
    ).all()
    serializer_class = DocumentoPostulacionSerializer
    pagination_class = CustomPagination
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['postulacion', 'estado', 'tipo_documento']
    search_fields = ['postulacion__postulante__usuario__username', 'tipo_documento__nombre']
    ordering_fields = ['fecha_subida', 'fecha_revision']
    ordering = ['-fecha_subida']
    permission_classes = [DocumentoRolePermission]

    def create(self, request, *args, **kwargs):
        """Crear o reutilizar documento existente para reenvío por estudiante."""
        if request.GET.get('debug_request') == '1':
            return Response({
                'data_type': type(request.data).__name__,
                'data_keys': list(request.data.keys()),
                'data_values': {k: request.data.get(k) for k in ['postulacion', 'tipo_documento', 'archivo']},
                'files': list(request.FILES.keys()),
                'content_type': request.content_type,
            })

        user = request.user
        is_privileged = bool(
            user and (user.has_perm('documentos.change_documentopostulacion') or can_view_all_documentos(user))
        )

        postulacion_id = request.data.get('postulacion')
        tipo_documento_id = request.data.get('tipo_documento')
        try:
            postulacion_id = int(postulacion_id) if postulacion_id is not None else None
        except Exception:
            postulacion_id = None
        try:
            tipo_documento_id = int(tipo_documento_id) if tipo_documento_id is not None else None
        except Exception:
            tipo_documento_id = None

        if not is_privileged and postulacion_id:
            postulacion = Postulacion.objects.select_related('etapa_actual').filter(id=postulacion_id).first()
            if postulacion:
                etapa_actual = getattr(postulacion.etapa_actual, 'nombre', '') or ''
                etapa_actual_norm = etapa_actual.strip().upper()
                if etapa_actual_norm != 'REGISTRO':
                    return Response(
                        {
                            'detail': BLOCKED_DOCUMENT_MESSAGE,
                            'error': BLOCKED_DOCUMENT_MESSAGE,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if tipo_documento_id:
                    tipo_documento_name = (
                        TipoDocumento.objects.filter(id=tipo_documento_id).values_list('nombre', flat=True).first() or ''
                    )
                    if tipo_documento_name and 'ACTA' in tipo_documento_name.upper():
                        return Response(
                            {
                                'detail': BLOCKED_DOCUMENT_MESSAGE,
                                'error': BLOCKED_DOCUMENT_MESSAGE,
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

        existente = None
        if postulacion_id and tipo_documento_id:
            existente = DocumentoPostulacion.objects.filter(
                postulacion_id=postulacion_id, tipo_documento_id=tipo_documento_id
            ).first()

        if existente:
            if not is_privileged and existente.estado != 'rechazado':
                raise ValidationError('Ya existe un documento para este tipo; no puede crear uno nuevo.')

            serializer = DocumentoPostulacionCreateSerializer(
                instance=existente,
                data=request.data,
                partial=True,
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            instancia = serializer.save()
            output = DocumentoPostulacionSerializer(instancia, context={'request': request})
            return Response(output.data, status=status.HTTP_200_OK)

        create_serializer = DocumentoPostulacionCreateSerializer(data=request.data, context={'request': request})
        create_serializer.is_valid(raise_exception=True)
        instancia = create_serializer.save()
        output = DocumentoPostulacionSerializer(instancia, context={'request': request})
        return Response(output.data, status=status.HTTP_201_CREATED)

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

        archivo_anterior = None
        if getattr(instancia_anterior, 'archivo', None):
            archivo_anterior = (instancia_anterior.archivo.name, instancia_anterior.archivo.size)

        instancia = serializer.save()

        archivo_nuevo = None
        if getattr(instancia, 'archivo', None):
            archivo_nuevo = (instancia.archivo.name, instancia.archivo.size)

        if archivo_nuevo and archivo_nuevo != archivo_anterior:
            pass
        elif getattr(instancia, 'archivo', None) and not getattr(instancia, 'preview_pdf', None):
            pass

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
        """Envía un correo al estudiante notificando que su documento fue rechazado."""
        try:
            postulante = documento.postulacion.postulante
            usuario = postulante.usuario

            if not usuario:
                return

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
        except Exception:
            # No-op: no queremos ruido en logs por errores de notificación
            pass


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
