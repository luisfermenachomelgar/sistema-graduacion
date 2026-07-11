/**
 * Reportes Page - Modern Dashboard
 * Analytics and reports with modern UI
 */

import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api/api';
import axiosInstance from '../api/axios';
import { API_CONFIG } from '../constants/api';
import Alert from '../components/Alert';
import Table from '../components/Table';
import StatsCards from '../components/StatsCards';
import { AlertCircle, Download, TrendingUp, CheckCircle, Zap } from 'lucide-react';

const POSTULACIONES_TAB = 'postulaciones';
const POSTULACIONES_PAGE_SIZE = 20;

const Reportes = () => {
  const [reportData, setReportData] = useState(null);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('tutores');
  const [exportingTutores, setExportingTutores] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();
  const [postulaciones, setPostulaciones] = useState([]);
  const [postulacionesMeta, setPostulacionesMeta] = useState({ count: 0, next: null, previous: null });
  const [postulacionesSummary, setPostulacionesSummary] = useState(null);
  const [postulacionesLoading, setPostulacionesLoading] = useState(false);
  const [postulacionesError, setPostulacionesError] = useState('');
  const [modalidadesOptions, setModalidadesOptions] = useState([]);
  const [gestionesOptions, setGestionesOptions] = useState([]);
  const [anioOptions, setAnioOptions] = useState([]);
  const [semestresOptions, setSemestresOptions] = useState([]);
  const [estadoOptions, setEstadoOptions] = useState([]);
  const [estadoGeneralOptions, setEstadoGeneralOptions] = useState([]);
  const [carreraOptions, setCarreraOptions] = useState([]);
  const [tutorOptions, setTutorOptions] = useState([]);
  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [page, setPage] = useState(Number(searchParams.get('page')) || 1);
  const [filterModalidad, setFilterModalidad] = useState(searchParams.get('modalidad') || '');
  const [filterGestion, setFilterGestion] = useState(searchParams.get('gestion') || '');
  const [filterSemestre, setFilterSemestre] = useState(searchParams.get('semestre_academico') || '');
  const [filterAnio, setFilterAnio] = useState(searchParams.get('anio_academico') || '');
  const [filterEstado, setFilterEstado] = useState(searchParams.get('estado') || '');
  const [filterEstadoGeneral, setFilterEstadoGeneral] = useState(searchParams.get('estado_general') || '');
  const [filterCarrera, setFilterCarrera] = useState(searchParams.get('carrera') || '');
  const [filterTutor, setFilterTutor] = useState(searchParams.get('tutor') || '');

  useEffect(() => {
    if (activeTab !== POSTULACIONES_TAB) {
      fetchReportData();
    }
  }, [activeTab]);

  const fetchDashboardStats = useCallback(async () => {
    try {
      const result = await api.getAll(API_CONFIG.ENDPOINTS.DASHBOARD_GENERAL, {}, { skipGlobalLoader: true });
      if (result.success) {
        setDashboardStats(result.data);
      } else {
        console.error('Error loading dashboard stats:', result.error);
      }
    } catch (err) {
      console.error('Error loading dashboard stats:', err);
    }
  }, []);

  useEffect(() => {
    if (activeTab === POSTULACIONES_TAB) {
      fetchDashboardStats();
    }
  }, [activeTab, fetchDashboardStats]);

  const fetchPostulaciones = useCallback(async (params = {}) => {
    setPostulacionesLoading(true);
    setPostulacionesError('');

    try {
      const queryParams = {
        ...params,
        page_size: POSTULACIONES_PAGE_SIZE,
      };
      const result = await api.getAll(
        API_CONFIG.ENDPOINTS.REPORTE_POSTULACIONES,
        queryParams,
        { skipGlobalLoader: true }
      );

      if (result.success) {
        const data = result.data || {};
        const rows = Array.isArray(data) ? data : data.results || [];
        setPostulaciones(rows);
        setPostulacionesMeta({
          count: data.count ?? rows.length,
          next: data.next ?? null,
          previous: data.previous ?? null,
        });
        setPostulacionesSummary(data.summary || null);

        const filtersAvailable = data.filters_available || {};
        setModalidadesOptions(filtersAvailable.modalidades || []);
        setGestionesOptions(filtersAvailable.gestiones || []);
        setAnioOptions(filtersAvailable.anio_academicos || []);
        setSemestresOptions(filtersAvailable.semestres_academicos || []);
        setEstadoOptions(filtersAvailable.estados || []);
        setEstadoGeneralOptions(filtersAvailable.estado_generales || []);
        setCarreraOptions(filtersAvailable.carreras || []);
        setTutorOptions(filtersAvailable.tutores || []);
      } else {
        setPostulacionesError(result.error || 'Error al cargar el reporte de postulaciones');
      }
    } catch (err) {
      setPostulacionesError('Error al cargar el reporte de postulaciones');
    } finally {
      setPostulacionesLoading(false);
    }
  }, []);

  useEffect(() => {
    if (activeTab !== POSTULACIONES_TAB) {
      return;
    }

    const params = {};
    if (search) params.search = search;
    if (page > 1) params.page = page;
    if (filterModalidad) params.modalidad = filterModalidad;
    if (filterGestion) params.gestion = filterGestion;
    if (filterSemestre) params.semestre_academico = filterSemestre;
    if (filterEstado) params.estado = filterEstado;
    if (filterEstadoGeneral) params.estado_general = filterEstadoGeneral;
    if (filterCarrera) params.carrera = filterCarrera;
    if (filterTutor) params.tutor = filterTutor;

    setSearchParams(params, { replace: true });
    fetchPostulaciones(params);
  }, [
    activeTab,
    search,
    page,
    filterModalidad,
    filterGestion,
    filterAnio,
    filterSemestre,
    filterEstado,
    filterEstadoGeneral,
    filterCarrera,
    filterTutor,
    setSearchParams,
    fetchPostulaciones,
  ]);

  const fetchReportData = async () => {
    try {
      setLoading(true);
      setError('');
      
      let endpoint = API_CONFIG.ENDPOINTS.DASHBOARD_GENERAL;

      if (activeTab === 'tutores') {
        endpoint = API_CONFIG.ENDPOINTS.ESTADISTICAS_TUTORES;
      } else if (activeTab === 'carreras') {
        endpoint = API_CONFIG.ENDPOINTS.EFICIENCIA_CARRERAS;
      }

      const result = await api.getAll(endpoint, {}, { skipGlobalLoader: true });

      if (result.success) {
        setReportData(result.data);
      } else {
        throw new Error(result.error || 'Error al cargar reportes');
      }
    } catch (err) {
      console.error('Error loading reports:', err);
      setError(err.message || 'Error al cargar los reportes');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      setExportingTutores(true);

      const response = await axiosInstance.get(
        API_CONFIG.ENDPOINTS.EXPORTAR_ESTADISTICAS,
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `estadisticas_tutores_${new Date().toISOString().split('T')[0]}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export failed:', err);
      setError('Error al exportar estadísticas');
    } finally {
      setExportingTutores(false);
    }
  };

  const renderGeneralStats = () => {
    if (!reportData) return null;

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Postulantes */}
        <div className="p-6 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Total Postulantes
              </p>
              <p className="text-3xl font-bold mt-2 text-gray-900 dark:text-white">
                {reportData.total_postulantes || 0}
              </p>
            </div>
            <div className="text-4xl">👥</div>
          </div>
        </div>

        {/* Total Postulaciones */}
        <div className="p-6 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Total Postulaciones
              </p>
              <p className="text-3xl font-bold mt-2 text-gray-900 dark:text-white">
                {reportData.total_postulaciones || 0}
              </p>
            </div>
            <div className="text-4xl">📋</div>
          </div>
        </div>

        {/* Modalidades Disponibles */}
        <div className="p-6 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Modalidades Disponibles
              </p>
              <p className="text-3xl font-bold mt-2 text-gray-900 dark:text-white">
                {reportData.total_modalidades || 0}
              </p>
            </div>
            <div className="text-4xl">🎓</div>
          </div>
        </div>

        {/* Total Titulados */}
        <div className="p-6 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Total Titulados
              </p>
              <p className="text-3xl font-bold mt-2 text-gray-900 dark:text-white">
                {reportData.total_titulados || 0}
              </p>
            </div>
            <div className="text-4xl">🏆</div>
          </div>
        </div>
      </div>
    );
  };

  const renderByEstado = () => {
    if (!reportData?.postulaciones_por_estado_general) return null;

    return (
      <div className="p-6 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
          Postulaciones por Estado
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {reportData.postulaciones_por_estado_general.map((item, idx) => (
            <div
              key={idx}
              className="p-4 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-700"
            >
              <p className="text-xs font-medium uppercase text-gray-600 dark:text-gray-400">
                {item.estado}
              </p>
              <p className="text-2xl font-bold mt-2 text-gray-900 dark:text-white">
                {item.total}
              </p>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const getEtapaActualLabel = (row) => {
    const etapaNombre = row?.etapa_nombre || row?.etapa_actual?.nombre || row?.etapa_actual_nombre || '';
    if (etapaNombre) {
      return etapaNombre;
    }
    return row?.estado_general === 'FINALIZADA' ? 'Modalidad Finalizada' : 'Modalidad Finalizada';
  };

  const renderTutoresStats = () => {
    if (!reportData?.results) return null;

    return (
      <div className="p-6 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b border-gray-200 dark:border-gray-700">
              <tr>
                <th className="text-left py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">
                  Tutor
                </th>
                <th className="text-center py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">
                  Modalidades Finalizadas
                </th>
                <th className="text-center py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">
                  Modalidades Rechazadas
                </th>
                <th className="text-center py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">
                  Total Asignadas
                </th>
              </tr>
            </thead>
            <tbody>
              {reportData.results.map((tutor, idx) => (
                <tr
                  key={idx}
                  className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  <td className="py-3 px-4 text-gray-900 dark:text-gray-200">
                    {tutor.tutor_nombre || 'Sin datos'}
                  </td>
                  <td className={`py-3 px-4 text-center font-medium text-green-600 dark:text-green-400`}>
                    {tutor.modalidades_finalizadas || 0}
                  </td>
                  <td className={`py-3 px-4 text-center font-medium text-red-600 dark:text-red-400`}>
                    {tutor.rechazados || 0}
                  </td>
                  <td className="py-3 px-4 text-center font-semibold text-gray-900 dark:text-white">
                    {tutor.total_asignadas || 0}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderPostulacionesSummary = () => null;

  const renderPostulacionesEstadoGeneral = () => {
    if (!postulacionesSummary?.estado_general_counts) return null;

    return (
      <div className="p-6 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 mb-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Postulaciones por Estado General</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {postulacionesSummary.estado_general_counts.map((item, idx) => (
            <div key={idx} className="rounded-lg border border-gray-300 dark:border-gray-700 p-4 bg-gray-50 dark:bg-gray-900">
              <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">{item.estado_general || 'Sin estado'}</p>
              <p className="text-2xl font-bold mt-2 text-gray-900 dark:text-white">{item.total ?? 0}</p>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderPostulacionesTable = () => {
    const columns = [
      { key: 'id', label: 'ID' },
      { key: 'postulante_nombre', label: 'Postulante' },
      { key: 'postulante_carrera', label: 'Carrera' },
      { key: 'modalidad_nombre', label: 'Modalidad' },
      { key: 'tutor', label: 'Tutor' },
      {
        key: 'periodo_academico_display',
        label: 'Período',
        render: (value, row) => value || (row.anio_academico && row.semestre_academico ? `${row.semestre_academico}/${row.anio_academico}` : '-'),
      },
      {
        key: 'etapa_nombre',
        label: 'Etapa Actual',
        render: (_, row) => (
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {getEtapaActualLabel(row) || '-'}
          </span>
        ),
      },
      { key: 'fecha_postulacion', label: 'Fecha' },
    ];

    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-4 mb-4">
          <div>
            <input
              type="text"
              placeholder="Buscar por postulante, título, tutor..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 outline-none transition"
            />
          </div>
          <div>
            <select
              value={filterModalidad}
              onChange={(e) => {
                setFilterModalidad(e.target.value);
                setPage(1);
              }}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 outline-none transition"
            >
              <option value="">Todas las modalidades</option>
              {modalidadesOptions.map((item) => (
                <option key={item.id} value={item.id}>{item.nombre}</option>
              ))}
            </select>
          </div>
          <div>
            <select
              value={filterGestion}
              onChange={(e) => {
                setFilterGestion(e.target.value);
                setPage(1);
              }}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 outline-none transition"
            >
              <option value="">Gestión</option>
              {gestionesOptions.map((item) => (
                <option key={item.value} value={item.value}>{item.label}</option>
              ))}
            </select>
          </div>
          <div>
            <select
              value={filterSemestre}
              onChange={(e) => {
                setFilterSemestre(e.target.value);
                setPage(1);
              }}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 outline-none transition"
            >
              <option value="">Semestre</option>
              {semestresOptions.map((item) => (
                <option key={item.value} value={item.value}>{item.label}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-4 gap-4 mb-4">
          <div>
            <select
              value={filterEstado}
              onChange={(e) => {
                setFilterEstado(e.target.value);
                setPage(1);
              }}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 outline-none transition"
            >
              <option value="">Estado</option>
              {estadoOptions.map((item) => (
                <option key={item.value} value={item.value}>{item.label}</option>
              ))}
            </select>
          </div>
          <div>
            <select
              value={filterEstadoGeneral}
              onChange={(e) => {
                setFilterEstadoGeneral(e.target.value);
                setPage(1);
              }}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 outline-none transition"
            >
              <option value="">Estado general</option>
              {estadoGeneralOptions.map((item) => (
                <option key={item.value} value={item.value}>{item.label}</option>
              ))}
            </select>
          </div>
          <div>
            <select
              value={filterCarrera}
              onChange={(e) => {
                setFilterCarrera(e.target.value);
                setPage(1);
              }}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 outline-none transition"
            >
              <option value="">Todas las carreras</option>
              {carreraOptions.map((item) => (
                <option key={item.value} value={item.value}>{item.label}</option>
              ))}
            </select>
          </div>
          <div>
            <select
              value={filterTutor}
              onChange={(e) => {
                setFilterTutor(e.target.value);
                setPage(1);
              }}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 outline-none transition"
            >
              <option value="">Todos los tutores</option>
              {tutorOptions.map((item) => (
                <option key={item.value} value={item.value}>{item.label}</option>
              ))}
            </select>
          </div>
        </div>

        <Table
          columns={columns}
          data={postulaciones}
          loading={postulacionesLoading}
        />

        <div className="mt-4 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <span className="text-sm text-gray-600 dark:text-gray-400">
            Mostrando {postulaciones.length > 0 ? (page - 1) * POSTULACIONES_PAGE_SIZE + 1 : 0}–{Math.min((page - 1) * POSTULACIONES_PAGE_SIZE + postulaciones.length, postulacionesMeta.count || 0)} de {postulacionesMeta.count || 0} registros
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => page > 1 && setPage((prev) => Math.max(1, prev - 1))}
              disabled={!postulacionesMeta.previous}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition disabled:opacity-50"
            >
              Anterior
            </button>
            <button
              onClick={() => postulacionesMeta.next && setPage((prev) => prev + 1)}
              disabled={!postulacionesMeta.next}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition disabled:opacity-50"
            >
              Siguiente
            </button>
          </div>
        </div>
      </div>
    );
  };

  const renderCarrerasStats = () => {
    if (!reportData) return null;

    if (!Array.isArray(reportData) || reportData.length === 0) {
      return (
        <div className="p-6 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
          <p className="text-gray-600 dark:text-gray-400">No existen datos para mostrar.</p>
        </div>
      );
    }

    return (
      <div className="p-6 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b border-gray-200 dark:border-gray-700">
              <tr>
                <th className="text-left py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">
                  Carrera
                </th>
                <th className="text-center py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">
                  Total Iniciados
                </th>
                <th className="text-center py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">
                  Total Titulados
                </th>
                <th className="text-center py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">
                  Tasa de Titulación (%)
                </th>
                <th className="text-right py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">
                  Tiempo Promedio (días)
                </th>
              </tr>
            </thead>
            <tbody>
              {reportData.map((item, idx) => (
                <tr
                  key={idx}
                  className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  <td className="py-3 px-4 text-gray-900 dark:text-gray-200">
                    {item.carrera || 'Sin Carrera Asignada'}
                  </td>
                  <td className="py-3 px-4 text-center text-gray-900 dark:text-gray-200">
                    {item.total_iniciados ?? 0}
                  </td>
                  <td className="py-3 px-4 text-center text-gray-900 dark:text-gray-200">
                    {item.total_titulados ?? 0}
                  </td>
                  <td className="py-3 px-4 text-center font-semibold text-gray-900 dark:text-white">
                    {item.tasa_titulacion != null ? `${item.tasa_titulacion.toFixed(2)}%` : '0%'}
                  </td>
                  <td className="py-3 px-4 text-right font-semibold text-gray-900 dark:text-white">
                    {item.tiempo_promedio_dias != null ? `${item.tiempo_promedio_dias.toFixed(2)} días` : '0 días'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Encabezado */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Reportes y Análisis
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Visualiza estadísticas y análisis del sistema
          </p>
        </div>

        {/* Error Alert */}
        {error && <Alert type="error" message={error} onClose={() => setError('')} autoClose={false} />}

        {/* Tabs */}
        <div className="mb-6 flex flex-wrap gap-2 border-b border-gray-200 dark:border-gray-700">
          {[
            { id: 'tutores', label: 'Tutores', icon: '👨‍🏫' },
            { id: POSTULACIONES_TAB, label: 'Postulaciones', icon: '📑' },
            { id: 'carreras', label: 'Carreras', icon: '🎓' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-3 font-medium transition border-b-2 flex items-center gap-2 ${
                activeTab === tab.id
                  ? `border-blue-600 text-blue-600 dark:text-blue-400`
                  : `border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200`
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 rounded-lg border flex items-start gap-3 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-800 dark:text-red-400">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Error al cargar reportes</p>
              <p className="text-sm mt-1">{error}</p>
              <button
                onClick={fetchReportData}
                className="text-sm mt-2 underline hover:no-underline"
              >
                Reintentar
              </button>
            </div>
          </div>
        )}

        {/* Loading */}
        {loading && activeTab !== POSTULACIONES_TAB && (
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-gray-500 dark:text-gray-400">Cargando datos...</p>
            </div>
          </div>
        )}

        {/* Content */}
        {activeTab !== POSTULACIONES_TAB && !loading && !error && (
          <>
            {activeTab === 'general' && renderGeneralStats()}
            {activeTab === 'general' && reportData && renderByEstado()}

            {activeTab === 'tutores' && (
              <div className="flex justify-end mb-4">
                <button
                  onClick={handleExport}
                  disabled={exportingTutores}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white rounded-lg transition font-medium"
                >
                  <Download className="w-4 h-4" />
                  {exportingTutores ? 'Exportando...' : 'Exportar Excel'}
                </button>
              </div>
            )}
            {activeTab === 'tutores' && renderTutoresStats()}

            {activeTab === 'carreras' && renderCarrerasStats()}

            {/* Footer */}
            <div className="mt-8 p-4 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-sm text-gray-600 dark:text-gray-400">
              <p>ℹ️ Última actualización: {new Date().toLocaleString('es-ES')}</p>
            </div>
          </>
        )}

        {activeTab === POSTULACIONES_TAB && (
          <>
            {postulacionesError && (
              <Alert
                type="error"
                message={postulacionesError}
                onClose={() => setPostulacionesError('')}
                autoClose={false}
              />
            )}
            <StatsCards
              cards={[
                {
                  title: 'Total Postulaciones',
                  value: dashboardStats?.total_postulaciones || 0,
                  change: 0,
                  Icon: TrendingUp,
                  color: 'cyan',
                },
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
              gridClass="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6"
              compact
            />
            {renderPostulacionesEstadoGeneral()}
            {renderPostulacionesTable()}
            <div className="mt-8 p-4 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-sm text-gray-600 dark:text-gray-400">
              <p>ℹ️ Última actualización: {new Date().toLocaleString('es-ES')}</p>
            </div>
          </>
        )}
    </div>
  );
};

export default Reportes;
