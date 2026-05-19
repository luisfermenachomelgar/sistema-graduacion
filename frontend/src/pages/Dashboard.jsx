/**
 * Dashboard Page - SaaS Style
 * Main analytics and metrics page with modern UI and real API data
 */

import { useState, useEffect } from 'react';
import StatsCards from '../components/StatsCards';
import Charts from '../components/Charts';
import DataTable from '../components/DataTable';
import SkeletonLoader from '../components/SkeletonLoader';
import { useTheme } from '../context/ThemeContext';
import api from '../api/api';
import { API_CONFIG } from '../constants/api';
import { AlertCircle } from 'lucide-react';

const DASHBOARD_CACHE_TTL = 2 * 60 * 1000;

let dashboardCache = {
  token: null,
  timestamp: 0,
  dashboardStats: null,
  postulantesRecientes: [],
  barChartData: null,
  lineChartData: null,
  pieChartData: null,
  metrics: null,
};

const Dashboard = () => {
  const { isDark } = useTheme();
  const hasCachedContent = dashboardCache.timestamp > 0;
  const isCacheFresh = hasCachedContent && Date.now() - dashboardCache.timestamp <= DASHBOARD_CACHE_TTL;

  const [dashboardStats, setDashboardStats] = useState(dashboardCache.dashboardStats);
  const [postulantesRecientes, setPostulantesRecientes] = useState(dashboardCache.postulantesRecientes || []);
  const [barChartData, setBarChartData] = useState(dashboardCache.barChartData);
  const [lineChartData, setLineChartData] = useState(dashboardCache.lineChartData);
  const [pieChartData, setPieChartData] = useState(dashboardCache.pieChartData);
  const [metrics, setMetrics] = useState(dashboardCache.metrics);
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
        barChartData: null,
        lineChartData: null,
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

    if (dashboardCache.barChartData) {
      setBarChartData(dashboardCache.barChartData);
    }

    if (dashboardCache.lineChartData) {
      setLineChartData(dashboardCache.lineChartData);
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

      const [postulantesResult, chartResponse] = await Promise.all([
        api.getAll(API_CONFIG.ENDPOINTS.POSTULANTES, { limit: 5 }),
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

      if (chartResponse.ok) {
        const chartData = await chartResponse.json();
        const normalizedMetrics = normalizeMetrics(chartData);
        setBarChartData(chartData.barChartData);
        setLineChartData(chartData.lineChartData);
        setPieChartData(chartData.pieChartData);
        setMetrics(normalizedMetrics);
        dashboardCache = {
          ...dashboardCache,
          token,
          timestamp: Date.now(),
          barChartData: chartData.barChartData,
          lineChartData: chartData.lineChartData,
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
    <div className="space-y-6 bg-white/5 dark:bg-white/5 rounded-lg p-6">
        {/* Encabezado */}
        <div className="mb-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Dashboard
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Resumen general del sistema de graduación
            </p>
          </div>
          <button
            onClick={handleRefresh}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg transition font-medium"
          >
            {loading ? '🔄 Actualizando...' : '🔄 Actualizar'}
          </button>
        </div>

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

        {/* Skeleton Loading */}
        {loading && !dashboardCache.timestamp && (
          <SkeletonLoader />
        )}

        {!loading && (
          <>
            {/* Tarjetas de Estadísticas */}
            <StatsCards
              stats={dashboardStats ? {
                totalPostulantes: {
                  value: dashboardStats.total_postulantes || 0,
                  change: dashboardStats.cambio_postulantes_porcentaje || 0,
                  color: 'blue',
                },
                documentosPendientes: {
                  value: dashboardStats.documentos_pendientes || 0,
                  change: dashboardStats.cambio_documentos_porcentaje || 0,
                  color: 'yellow',
                },
                graduados: {
                  value: dashboardStats.total_titulados || 0,
                  change: dashboardStats.cambio_titulados_porcentaje || 0,
                  color: 'green',
                },
                tasaAprobacion: {
                  value: dashboardStats.tasa_aprobacion || 0,
                  change: dashboardStats.cambio_tasa_porcentaje || 0,
                  color: 'purple',
                },
              } : {}}
            />

            {/* Gráficos */}
            <Charts
              isDark={isDark}
              barChartData={barChartData}
              lineChartData={lineChartData}
              pieChartData={pieChartData}
              metrics={metrics}
            />

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
