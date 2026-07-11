/**
 * Dashboard Page - SaaS Style
 * Main analytics and metrics page with modern UI and real API data
 */

import { useState, useEffect } from 'react';
import StatsCards from '../components/StatsCards';
import Charts from '../components/Charts';
import DataTable from '../components/DataTable';
import { PageHeader } from '../components';
import { useTheme } from '../context/ThemeContext';
import api from '../api/api';
import { API_CONFIG } from '../constants/api';
import { AlertCircle, LoaderCircle, TrendingUp, CheckCircle, Zap, Users } from 'lucide-react';

const DASHBOARD_CACHE_TTL = 2 * 60 * 1000;

const DEFAULT_METRICS = {
  tasaAprobacion: 0,
  promedioProcesamiento: 0,
  satisfaccion: 'N/A',
  proyeccionMes: 0,
};

let dashboardCache = {
  token: null,
  timestamp: 0,
  dashboardStats: null,
  postulantesRecientes: [],
  ultimasPostulaciones: [],
  ultimosDocumentos: [],
  pieChartData: null,
  metrics: null,
};

const Dashboard = () => {
  const { isDark } = useTheme();
  const hasCachedContent = dashboardCache.timestamp > 0;
  const isCacheFresh = hasCachedContent && Date.now() - dashboardCache.timestamp <= DASHBOARD_CACHE_TTL;

  const [dashboardStats, setDashboardStats] = useState(dashboardCache.dashboardStats);
  const [postulantesRecientes, setPostulantesRecientes] = useState(dashboardCache.postulantesRecientes || []);
  const [ultimasPostulaciones, setUltimasPostulaciones] = useState(dashboardCache.ultimasPostulaciones || []);
  const [ultimosDocumentos, setUltimosDocumentos] = useState(dashboardCache.ultimosDocumentos || []);
  const [pieChartData, setPieChartData] = useState(dashboardCache.pieChartData);
  const [metrics, setMetrics] = useState(dashboardCache.metrics || DEFAULT_METRICS);
  const [loading, setLoading] = useState(!isCacheFresh);
  const [error, setError] = useState('');

  const postulantesColumns = [
    {
      key: 'nombre',
      label: 'Nombre',
      sortable: true,
      render: (value, row) => `${row.nombre || ''} ${row.apellido || ''}`.trim() || '-',
    },
    {
      key: 'ci',
      label: 'CI',
      sortable: true,
      render: (value) => value || '-',
    },
    {
      key: 'carrera',
      label: 'Carrera',
      sortable: true,
      render: (value) => value || '-',
    },
    {
      key: 'codigo_estudiante',
      label: 'Código',
      sortable: true,
      render: (value) => value || '-',
    },
  ];

  const ultimasPostulacionesColumns = [
    {
      key: 'titulo_trabajo',
      label: 'Título',
      sortable: true,
      render: (value) => value || '-',
    },
    {
      key: 'postulante_nombre',
      label: 'Postulante',
      sortable: true,
      render: (value) => value || '-',
    },
    {
      key: 'modalidad_nombre',
      label: 'Modalidad',
      sortable: true,
      render: (value) => value || '-',
    },
    {
      key: 'etapa_nombre',
      label: 'Etapa Actual',
      render: (_, row) => row?.etapa_nombre || 'Modalidad Finalizada',
    },
    {
      key: 'fecha_postulacion',
      label: 'Fecha',
      sortable: true,
      render: (value) => value ? new Date(value).toLocaleDateString('es-ES') : '-',
    },
  ];

  const ultimosDocumentosColumns = [
    {
      key: 'tipo_documento_nombre',
      label: 'Tipo',
      sortable: true,
      render: (value) => value || '-',
    },
    {
      key: 'postulante_nombre',
      label: 'Postulante',
      render: (value) => value || '-',
    },
    {
      key: 'estado',
      label: 'Estado',
      render: (value) => {
        const badgeClass = {
          'aprobado': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200',
          'pendiente': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200',
          'rechazado': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-200',
        }[value] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-200';
        return <span className={`px-2 py-1 rounded text-sm font-medium ${badgeClass}`}>{value || '-'}</span>;
      },
    },
    {
      key: 'fecha_subida',
      label: 'Fecha',
      sortable: true,
      render: (value) => value ? new Date(value).toLocaleDateString('es-ES') : '-',
    },
  ];

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const normalizePostulantes = (data) => {
    const normalized = Array.isArray(data) ? data : data?.results || [];
    return normalized.slice(0, 5);
  };

  const normalizeMetrics = (chartData) => ({
    tasaAprobacion: chartData.tasa_aprobacion ?? 0,
    promedioProcesamiento: chartData.promedio_procesamiento_dias ?? 0,
    satisfaccion: chartData.satisfaccion_score ?? 'N/A',
    proyeccionMes: chartData.proyeccion_mes_porcentaje ?? 0,
  });

  const applyCache = (token) => {
    if (dashboardCache.token && dashboardCache.token !== token) {
      dashboardCache = {
        token,
        timestamp: 0,
        dashboardStats: null,
        postulantesRecientes: [],
        ultimasPostulaciones: [],
        ultimosDocumentos: [],
        pieChartData: null,
        metrics: null,
      };
      return;
    }

    if (dashboardCache.dashboardStats) {
      setDashboardStats(dashboardCache.dashboardStats);
    }

    if (dashboardCache.postulantesRecientes?.length) {
      setPostulantesRecientes(dashboardCache.postulantesRecientes);
    }

    if (dashboardCache.ultimasPostulaciones?.length) {
      setUltimasPostulaciones(dashboardCache.ultimasPostulaciones);
    }

    if (dashboardCache.ultimosDocumentos?.length) {
      setUltimosDocumentos(dashboardCache.ultimosDocumentos);
    }

    if (dashboardCache.pieChartData) {
      setPieChartData(dashboardCache.pieChartData);
    }

    if (dashboardCache.metrics) {
      setMetrics(dashboardCache.metrics);
    }
  };

  const fetchDashboardStatsInBackground = async (token) => {
    try {
      const response = await fetch('/api/reportes/dashboard-general/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Error al cargar dashboard');
      }

      const data = await response.json();
      setDashboardStats(data);
      dashboardCache = {
        ...dashboardCache,
        token,
        timestamp: Date.now(),
        dashboardStats: data,
      };
    } catch (err) {
      console.error('Error loading dashboard stats:', err);
    }
  };

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No se encontró sesión autenticada');
      }

      applyCache(token);

      if (!dashboardCache.timestamp || Date.now() - dashboardCache.timestamp > DASHBOARD_CACHE_TTL) {
        setLoading(true);
      }

      setError('');

      const [postulantesResult, postulacionesResult, documentosResult, chartResponse] = await Promise.all([
        api.getAll(API_CONFIG.ENDPOINTS.POSTULANTES, { limit: 5 }),
        api.getAll('/api/postulaciones/', { page_size: 5 }),
        api.getAll('/api/documentos/', { page_size: 5 }),
        fetch('/api/reportes/dashboard-chart-data/?meses=6', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }),
      ]);

      if (postulantesResult.success) {
        const data = normalizePostulantes(postulantesResult.data);
        setPostulantesRecientes(data);
        dashboardCache = {
          ...dashboardCache,
          token,
          timestamp: Date.now(),
          postulantesRecientes: data,
        };
      }

      if (postulacionesResult.success) {
        const data = normalizePostulantes(postulacionesResult.data);
        setUltimasPostulaciones(data);
        dashboardCache = {
          ...dashboardCache,
          token,
          timestamp: Date.now(),
          ultimasPostulaciones: data,
        };
      }

      if (documentosResult.success) {
        const data = normalizePostulantes(documentosResult.data);
        setUltimosDocumentos(data);
        dashboardCache = {
          ...dashboardCache,
          token,
          timestamp: Date.now(),
          ultimosDocumentos: data,
        };
      }

      if (chartResponse.ok) {
        const chartData = await chartResponse.json();
        const normalizedMetrics = normalizeMetrics(chartData);
        setPieChartData(chartData.pieChartData);
        setMetrics(normalizedMetrics);
        dashboardCache = {
          ...dashboardCache,
          token,
          timestamp: Date.now(),
          pieChartData: chartData.pieChartData,
          metrics: normalizedMetrics,
        };
      } else {
        console.error('Error cargando gráficos:', chartResponse.status);
      }

      // Load dashboard stats in background WITHOUT blocking UI
      setLoading(false);
      fetchDashboardStatsInBackground(token);
    } catch (err) {
      console.error('Error loading dashboard:', err);
      setError(err.message || 'Error al cargar datos del dashboard');
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    await fetchDashboardData();
  };

  return (
    <div className="space-y-6">
        <PageHeader
          title="Dashboard"
          description="Resumen general del sistema de graduación"
          action={(
            <button
              onClick={handleRefresh}
              disabled={loading}
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 font-medium text-white transition hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <LoaderCircle className="h-4 w-4" />}
              {loading ? 'Actualizando...' : 'Actualizar'}
            </button>
          )}
        />

        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 rounded-lg border flex items-start gap-3 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-800 dark:text-red-400">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Error al cargar datos</p>
              <p className="text-sm mt-1">{error}</p>
              <button
                onClick={handleRefresh}
                className="text-sm mt-2 underline hover:no-underline"
              >
                Reintentar
              </button>
            </div>
          </div>
        )}

        {loading && !dashboardCache.timestamp ? (
          <div className="flex h-96 items-center justify-center rounded-2xl border border-gray-200/80 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800">
            <div className="text-center">
              <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-b-2 border-blue-500" />
              <p className="text-gray-500 dark:text-gray-400">Cargando dashboard...</p>
            </div>
          </div>
        ) : (
          <>
            {/* Tarjetas de Estadísticas */}
            <StatsCards
              cards={[
                {
                  title: 'Total Postulantes',
                  value: dashboardStats?.total_postulantes || 0,
                  change: dashboardStats?.cambio_postulantes_porcentaje || 0,
                  Icon: Users,
                  color: 'blue',
                },
                {
                  title: 'Total Postulaciones',
                  value: dashboardStats?.total_postulaciones || 0,
                  change: 0,
                  Icon: TrendingUp,
                  color: 'cyan',
                },
                {
                  title: 'Total Documentos',
                  value: dashboardStats?.total_documentos || 0,
                  change: 0,
                  Icon: CheckCircle,
                  color: 'green',
                },
              ]}
              gridClass="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mb-8"
            />

            <StatsCards
              cards={[
                {
                  title: 'Modalidades Finalizadas',
                  value: dashboardStats?.modalidades_finalizadas || 0,
                  change: 0,
                  Icon: CheckCircle,
                  color: 'green',
                },
                {
                  title: 'Modalidades Disponibles',
                  value: dashboardStats?.total_modalidades || 0,
                  change: 0,
                  Icon: Zap,
                  color: 'purple',
                },
              ]}
              gridClass="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8"
            />

            {/* Gráficos */}
            <Charts
              isDark={isDark}
              pieChartData={pieChartData}
              metrics={metrics}
            />

            {/* Tabla de Últimas Postulaciones */}
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                Últimas Postulaciones
              </h2>
              <DataTable
                data={ultimasPostulaciones}
                columns={ultimasPostulacionesColumns}
                pageSize={5}
                isDark={isDark}
              />
            </div>

            {/* Tabla de Últimos Documentos */}
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                Últimos Documentos
              </h2>
              <DataTable
                data={ultimosDocumentos}
                columns={ultimosDocumentosColumns}
                pageSize={5}
                isDark={isDark}
              />
            </div>

            {/* Tabla de Postulantes Recientes */}
            {postulantesRecientes.length > 0 && (
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                  Postulantes Recientes
                </h2>
                <DataTable
                  data={postulantesRecientes}
                  columns={postulantesColumns}
                  pageSize={5}
                  onView={(row) => console.log('Ver:', row)}
                  onEdit={(row) => console.log('Editar:', row)}
                />
              </div>
            )}

            {/* Info Footer */}
            <div className="p-4 rounded-lg border text-sm bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400">
              <p>ℹ️ Última actualización: {new Date().toLocaleTimeString('es-ES')}</p>
            </div>
          </>
        )}
      </div>
    );
};

export default Dashboard;
