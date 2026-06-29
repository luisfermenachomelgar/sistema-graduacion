from auditoria.views import AuditoriaLogViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from documentos.views import DocumentoPostulacionViewSet, TipoDocumentoViewSet
from modalidades.views import EtapaViewSet, ModalidadViewSet
from postulantes.views import NotificacionViewSet, PostulacionViewSet, PostulanteViewSet
from reportes.views import DashboardGeneralView, DetalleAlumnosTutorView, EstadisticasTutoresView, ExportarEstadisticasTutoresView, ReporteEficienciaCarrerasView, HealthCheckView, DashboardChartDataView  # FASE 4: Health check
from usuarios.views import LoginView, CustomUserViewSet

router = DefaultRouter()
router.register(r'auditoria', AuditoriaLogViewSet, basename='auditoria-log')
router.register(r'modalidades', ModalidadViewSet, basename='modalidad')
router.register(r'etapas', EtapaViewSet, basename='etapa')
router.register(r'postulantes', PostulanteViewSet, basename='postulante')
router.register(r'postulaciones', PostulacionViewSet, basename='postulacion')
router.register(r'notificaciones', NotificacionViewSet, basename='notificacion')
router.register(r'documentos', DocumentoPostulacionViewSet, basename='documento')
router.register(r'tipos-documento', TipoDocumentoViewSet, basename='tipo-documento')
router.register(r'usuarios', CustomUserViewSet, basename='usuario')

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('health/', HealthCheckView.as_view(), name='health_check'),  # FASE 4: Health check (sin autenticación)
    path('reportes/dashboard-general/', DashboardGeneralView.as_view(), name='dashboard_general'),
    path('reportes/dashboard-chart-data/', DashboardChartDataView.as_view(), name='dashboard_chart_data'),
    path('reportes/estadisticas-tutores/', EstadisticasTutoresView.as_view(), name='estadisticas_tutores'),
    path('reportes/estadisticas-tutores/exportar/', ExportarEstadisticasTutoresView.as_view(), name='exportar_estadisticas_tutores'),
    path('reportes/estadisticas-tutores/<int:tutor_id>/alumnos/', DetalleAlumnosTutorView.as_view(), name='detalle_alumnos_tutor'),
    path('reportes/eficiencia-carreras/', ReporteEficienciaCarrerasView.as_view(), name='eficiencia_carreras'),
    path('', include(router.urls)),
]
