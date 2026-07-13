from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from config.permissions import (
    CRUDModelPermission,
    PostulanteRolePermission,
    PostulacionRolePermission,
    PuedeAvanzarEtapaPermission,
    PuedeAprobarDocumentosPermission,
    can_view_all_postulantes,
    can_view_all_postulaciones,
)
from auditoria.models import AuditoriaLog
from auditoria.serializers import AuditoriaLogSerializer
from documentos.models import DocumentoPostulacion
from modalidades.models import Etapa
from .models import ComentarioInterno, Notificacion, Postulacion, Postulante
from .serializers import ComentarioInternoSerializer, EtapaSerializer, NotificacionSerializer, PostulacionSerializer, PostulanteSerializer
from .services import avanzar_postulacion, finalizar_postulacion_si_corresponde
from .tasks import limpiar_notificaciones_antiguas
from reportes.services import (
    dashboard_general,
    generar_pdf_dashboard,
    generar_pdf_postulaciones,
    generar_excel_postulaciones,
)


# FASE 3: Custom Pagination with max_page_size limit
class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class PostulanteViewSet(viewsets.ModelViewSet):
    queryset = Postulante.objects.select_related('usuario').order_by('id')
    serializer_class = PostulanteSerializer
    pagination_class = CustomPagination  # FASE 3: Applied
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'usuario__username', 'nombre', 'apellido_paterno', 'apellido_materno', 'ci', 'codigo_estudiante'
    ]
    ordering_fields = ['id', 'creado_en', 'codigo_estudiante', 'nombre', 'apellido_paterno', 'apellido_materno']
    ordering = ['id']
    permission_classes = [PostulanteRolePermission]

    def get_permissions(self):
        """
        Permisos dinámicos: permitir lectura a usuarios autenticados (PostulanteRolePermission),
        pero requerir permisos de modelo Django para acciones de escritura (CRUDModelPermission).
        Esto evita que un `estudiante` realice POST/PUT/PATCH/DELETE aunque intente llamar directamente.
        """
        if self.request and self.request.method in {'POST', 'PUT', 'PATCH', 'DELETE'}:
            return [CRUDModelPermission()]
        return [PostulanteRolePermission()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if can_view_all_postulantes(self.request.user):
            return queryset
        return queryset.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        if can_view_all_postulantes(self.request.user):
            serializer.save()
            return

        serializer.save(usuario=self.request.user)


class PostulacionViewSet(viewsets.ModelViewSet):
    queryset = Postulacion.objects.select_related('postulante', 'modalidad', 'etapa_actual').all()
    serializer_class = PostulacionSerializer
    pagination_class = CustomPagination  # FASE 3: Applied
    # Configuración de filtros
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['modalidad', 'gestion', 'anio_academico', 'semestre_academico', 'estado']

    search_fields = [
        'titulo_trabajo',
        'tutor',
        'postulante__usuario__username',
        'postulante__nombre',
        'postulante__apellido',
    ]
    ordering_fields = ['fecha_postulacion', 'anio_academico', 'semestre_academico']
    ordering = ['-fecha_postulacion']
    permission_classes = [PostulacionRolePermission]

    def get_permissions(self):
        """
        Permisos dinámicos equivalentes a PostulanteViewSet: lectura por rol/propiedad,
        escrituras protegidas por permisos de modelo.
        """
        if self.request and self.request.method in {'POST', 'PUT', 'PATCH', 'DELETE'}:
            return [CRUDModelPermission()]
        return [PostulacionRolePermission()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if can_view_all_postulaciones(self.request.user):
            return queryset
        return queryset.filter(postulante__usuario=self.request.user)

    @action(detail=False, methods=['get'], url_path='exportar-pdf')
    def exportar_pdf(self, request):
        queryset = self.filter_queryset(self.get_queryset()).order_by('-fecha_postulacion')
        return generar_pdf_postulaciones(queryset, request.user)

    @action(detail=False, methods=['get'], url_path='exportar-excel')
    def exportar_excel(self, request):
        queryset = self.filter_queryset(self.get_queryset()).order_by('-fecha_postulacion')
        return generar_excel_postulaciones(queryset, request.user)

    def perform_create(self, serializer):
        """
        Para la modalidad EXAMEN DE GRADO, asignar automáticamente la etapa inicial
        (orden=1) solo cuando el usuario inicia el flujo normal por etapas y
        envía una etapa válida. Si el usuario selecciona el flujo histórico
        (etapa_actual=null), se conserva null y no se reemplaza por Registro.
        """
        etapa_actual_valida = serializer.validated_data.get('etapa_actual')

        # Flujo histórico / Modalidad Finalizada: respetar el null recibido.
        if etapa_actual_valida is None:
            postulacion = serializer.save()
            finalizar_postulacion_si_corresponde(postulacion, actor=self.request.user)
            return

        # Solo asignar la etapa inicial si el usuario realmente envía una etapa válida.
        modalidad_obj = serializer.validated_data.get('modalidad')
        if modalidad_obj and getattr(modalidad_obj, 'nombre', None):
            nombre_modalidad = modalidad_obj.nombre.strip().upper()
            if nombre_modalidad in {'EXAMEN DE GRADO', 'EXCELENCIA ACADÉMICA', 'EXCELENCIA  ACADÉMICA', 'PROYECTO DE GRADO'}:
                etapa_inicial = Etapa.objects.filter(modalidad=modalidad_obj, orden=1, activo=True).first()
                if etapa_inicial:
                    serializer.save(etapa_actual=etapa_inicial)
                    return

        postulacion = serializer.save()
        finalizar_postulacion_si_corresponde(postulacion, actor=self.request.user)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[PuedeAvanzarEtapaPermission],
        url_path='avanzar-etapa'
    )
    def avanzar_etapa(self, request, pk=None):
        postulacion = avanzar_postulacion(pk, actor=request.user)
        return Response(self.get_serializer(postulacion).data)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        year = request.query_params.get('year')
        data = dashboard_general(fecha_inicio, fecha_fin, year)
        return Response(data)

    @action(detail=False, methods=['get'], url_path='exportar-dashboard-pdf')
    def exportar_dashboard_pdf(self, request):
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        year = request.query_params.get('year')
        data = dashboard_general(fecha_inicio, fecha_fin, year)
        return generar_pdf_dashboard(data, fecha_inicio, fecha_fin, year)

    @action(
        detail=True,
        methods=['get'],
        url_path='historial'
    )
    def historial(self, request, pk=None):
        """
        Devuelve el historial de auditoría para una postulación, incluyendo
        cambios de etapa y revisiones de sus documentos.
        """
        historial_qs = AuditoriaLog.objects.select_related('usuario').filter(
            Q(modelo_afectado='Postulacion', objeto_id=pk) |
            Q(modelo_afectado='DocumentoPostulacion', detalles__contains={'postulacion_id': int(pk)})
        ).order_by('-fecha')
        
        data = AuditoriaLogSerializer(historial_qs, many=True).data

        # Enriquecer registros con la URL del documento si existe
        doc_ids = [item['objeto_id'] for item in data if item['modelo_afectado'] == 'DocumentoPostulacion']
        if doc_ids:
            docs = DocumentoPostulacion.objects.filter(id__in=doc_ids)
            docs_map = {d.id: d.archivo.url for d in docs if d.archivo}
            for item in data:
                if item['modelo_afectado'] == 'DocumentoPostulacion':
                    item['documento_url'] = docs_map.get(item['objeto_id'])

        return Response(data)


class EtapaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Etapa.objects.filter(activo=True)
    serializer_class = EtapaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['modalidad']
    ordering_fields = ['orden']
    ordering = ['orden']


class NotificacionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notificacion.objects.filter(usuario=self.request.user)

    @action(detail=True, methods=['post'])
    def marcar_leida(self, request, pk=None):
        notificacion = self.get_object()
        notificacion.leida = True
        notificacion.save()
        return Response({'status': 'ok'})

    @action(detail=False, methods=['post'], url_path='marcar-todas-leidas')
    def marcar_todas_leidas(self, request):
        self.get_queryset().update(leida=True)
        return Response({'status': 'ok'})

    @action(detail=False, methods=['post'], permission_classes=[PuedeAvanzarEtapaPermission], url_path='forzar-limpieza')
    def forzar_limpieza(self, request):
        limpiar_notificaciones_antiguas.delay()
        return Response({'status': 'Tarea de limpieza encolada.'})


class ComentarioInternoViewSet(viewsets.ModelViewSet):
    serializer_class = ComentarioInternoSerializer
    permission_classes = [PuedeAprobarDocumentosPermission]

    def get_queryset(self):
        qs = ComentarioInterno.objects.select_related('autor').all()
        postulacion_id = self.request.query_params.get('postulacion')
        return qs.filter(postulacion_id=postulacion_id) if postulacion_id else qs

    def perform_create(self, serializer):
        serializer.save(autor=self.request.user)
