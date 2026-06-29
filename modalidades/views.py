from django.db.models.deletion import ProtectedError
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.db.models import Max
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from config.permissions import CRUDModelPermission
from documentos.models import ModalidadTipoDocumento
from documentos.serializers import ModalidadTipoDocumentoSerializer
from .models import Etapa, Modalidad, ModalidadRequisito
from .serializers import EtapaSerializer, ModalidadRequisitoSerializer, ModalidadSerializer


class ModalidadViewSet(viewsets.ModelViewSet):
    queryset = Modalidad.objects.prefetch_related('etapas', 'requisitos').all()
    serializer_class = ModalidadSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'creada_en', 'actualizada_en']
    ordering = ['nombre']

    def get_permissions(self):
        if self.action in {'create', 'update', 'partial_update', 'destroy'}:
            return [CRUDModelPermission()]
        return super().get_permissions()

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {
                    'detail': (
                        'No se puede eliminar la modalidad porque tiene registros asociados. '
                        'Elimine primero etapas, tipos de documento, postulaciones u otros registros relacionados.'
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

    def _can_manage_requisitos(self, user):
        return bool(
            user
            and user.is_authenticated
            and (
                user.is_superuser
                or user.has_perm('modalidades.add_modalidadrequisito')
                or user.has_perm('modalidades.change_modalidadrequisito')
                or user.has_perm('modalidades.delete_modalidadrequisito')
            )
        )

    def _get_requisito(self, modalidad_id, requisito_id):
        return get_object_or_404(ModalidadRequisito, pk=requisito_id, modalidad_id=modalidad_id)

    @action(detail=True, methods=['get', 'post'], url_path='requisitos')
    def requisitos(self, request, pk=None):
        modalidad = self.get_object()

        if request.method == 'GET':
            requisitos = modalidad.requisitos.all()
            serializer = ModalidadRequisitoSerializer(requisitos, many=True, context={'request': request})
            return Response(serializer.data)

        if not self._can_manage_requisitos(request.user):
            raise PermissionDenied('No tienes permiso para administrar requisitos.')

        serializer = ModalidadRequisitoSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Calcular el siguiente orden disponible
        max_orden = modalidad.requisitos.aggregate(Max('orden'))['orden__max'] or 0
        serializer.save(modalidad=modalidad, orden=max_orden + 1)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'put', 'patch', 'delete'], url_path=r'requisitos/(?P<requisito_id>[^/.]+)')
    def requisito_detail(self, request, pk=None, requisito_id=None):
        requisito = self._get_requisito(pk, requisito_id)

        if request.method == 'GET':
            serializer = ModalidadRequisitoSerializer(requisito, context={'request': request})
            return Response(serializer.data)

        if not self._can_manage_requisitos(request.user):
            raise PermissionDenied('No tienes permiso para administrar requisitos.')

        if request.method == 'DELETE':
            requisito.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = ModalidadRequisitoSerializer(
            requisito,
            data=request.data,
            partial=(request.method == 'PATCH'),
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='tipos-documento')
    def tipos_documento(self, request, pk=None):
        modalidad = self.get_object()
        queryset = ModalidadTipoDocumento.objects.select_related('tipo_documento', 'etapa').filter(
            modalidad=modalidad,
            activo=True,
            tipo_documento__activo=True,
        )

        etapa_id = request.query_params.get('etapa')
        if etapa_id:
            queryset = queryset.filter(etapa_id=etapa_id)

        serializer = ModalidadTipoDocumentoSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path=r'requisitos/(?P<requisito_id>[^/.]+)/descargar')
    def requisito_descargar(self, request, pk=None, requisito_id=None):
        requisito = self._get_requisito(pk, requisito_id)

        if not requisito.archivo:
            return Response({'detail': 'El requisito no tiene archivo disponible.'}, status=status.HTTP_404_NOT_FOUND)

        archivo = requisito.archivo.open('rb')
        filename = requisito.archivo.name.split('/')[-1]

        return FileResponse(archivo, as_attachment=True, filename=filename)

    @action(detail=True, methods=['get'], url_path=r'requisitos/(?P<requisito_id>[^/.]+)/preview')
    def requisito_preview(self, request, pk=None, requisito_id=None):
        requisito = self._get_requisito(pk, requisito_id)

        if not requisito.archivo:
            return Response({'detail': 'El requisito no tiene archivo disponible.'}, status=status.HTTP_404_NOT_FOUND)

        archivo = requisito.archivo.open('rb')
        filename = requisito.archivo.name.split('/')[-1]
        return FileResponse(archivo, as_attachment=False, filename=filename)


class EtapaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para Etapas.
    Las etapas son configuradas en la BD y no deben ser modificadas desde la API.
    """
    queryset = Etapa.objects.select_related('modalidad').all()
    serializer_class = EtapaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'modalidad__nombre']
    ordering_fields = ['orden', 'nombre', 'modalidad__nombre']
    ordering = ['modalidad__nombre', 'orden']
