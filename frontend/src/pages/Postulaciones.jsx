/**
 * Postulaciones Page - CRUD Completo (Refactorizado)
 * Manage applications and their status using shared components
 */

import { useState, useEffect } from 'react';
import useAuth from '../hooks/useAuth';
import { useSearchParams } from 'react-router-dom';
import { Plus } from 'lucide-react';
import api from '../api/api';
import axiosInstance from '../api/axios';
import { API_CONFIG } from '../constants/api';
import Modal from '../components/Modal';
import FormField from '../components/FormField';
import Table from '../components/Table';
import Alert from '../components/Alert';
import { useModal } from '../hooks/useModal';
import { useCrud } from '../hooks/useCrud';
import { useListFilters } from '../hooks/useListFilters';

const INITIAL_FORM_DATA = {
  postulante_id: '',
  modalidad: '',
  titulo_trabajo: '',
  anio_academico: new Date().getFullYear(),
  semestre_academico: '',
  estado: 'en_revision',
  estado_general: 'EN_PROCESO',
  tutor: '',
  observaciones: '',
};

const ESTADO_OPTIONS = [
  { label: 'Revisión', value: 'en_revision' },
  { label: 'Aprobada', value: 'aprobada' },
  { label: 'Rechazada', value: 'rechazada' },
];

const ESTADO_GENERAL_OPTIONS = [
  { label: 'En proceso', value: 'EN_PROCESO' },
  { label: 'Perfil aprobado', value: 'PERFIL_APROBADO' },
  { label: 'Privada aprobada', value: 'PRIVADA_APROBADA' },
  { label: 'Publica aprobada', value: 'PUBLICA_APROBADA' },
  { label: 'Titulado', value: 'TITULADO' },
];

const currentYear = new Date().getFullYear();
const ACADEMIC_YEAR_OPTIONS = Array.from({ length: currentYear - 1990 + 1 }, (_, index) => ({
  id: 1990 + index,
  label: String(1990 + index),
}));

const HIDDEN_TITLE_TUTOR_MODALIDADES = ['EXAMEN DE GRADO', 'EXCELENCIA ACADÉMICA'];

const normalizeModalidadName = (name = '') =>
  String(name || '')
    .trim()
    .toUpperCase()
    .replace(/\s+/g, ' ');

const Postulaciones = () => {
  const {
    data: postulaciones,
    loading,
    error,
    setError,
    meta,
    list,
    refresh,
    create,
    patch,
    remove,
  } = useCrud(API_CONFIG.ENDPOINTS.POSTULACIONES);
  const { user } = useAuth();

  const resolveRole = () => {
    if (user?.role) return user.role;
    if (user?.is_superuser === true) return 'admin';
    return null;
  };

  const effectiveRole = resolveRole();
  const isStudent = effectiveRole === 'estudiante';
  // Usamos useSearchParams solo para inicializar el filtro local
  const [searchParams] = useSearchParams();
  const [postulantes, setPostulantes] = useState([]);
  const [modalidades, setModalidades] = useState([]);
  const [etapas, setEtapas] = useState([]);
  const [success, setSuccess] = useState('');
  const [formError, setFormError] = useState('');
  const [exportingPdf, setExportingPdf] = useState(false);
  const [exportingExcel, setExportingExcel] = useState(false);
  
  const [filterModalidad, setFilterModalidad] = useState(searchParams.get('modalidad') || '');
  const [filterEstado, setFilterEstado] = useState(searchParams.get('estado') || '');
  const [filterGestion, setFilterGestion] = useState(searchParams.get('gestion') || searchParams.get('anio_academico') || '');
  const [filterSemestreAcademico, setFilterSemestreAcademico] = useState(searchParams.get('semestre_academico') || '');

  const { search, setSearch, page, setPage } = useListFilters(list, {
    modalidad: filterModalidad,
    estado: filterEstado,
    gestion: filterGestion,
    anio_academico: filterGestion,
    semestre_academico: filterSemestreAcademico,
  }, {
    requestConfig: { skipGlobalLoader: true },
    errorMessage: 'Error al cargar postulaciones',
    exceptionMessage: 'Error loading postulaciones',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const { isOpen, isEditMode, formData, openModal, closeModal, setFormData } = useModal(INITIAL_FORM_DATA);

  const selectedModalidadNombre = formData.modalidad
    ? (modalidades.find((m) => String(m.id) === String(formData.modalidad))?.nombre || '')
    : '';
  const shouldShowTrabajoFields = !HIDDEN_TITLE_TUTOR_MODALIDADES.includes(
    normalizeModalidadName(selectedModalidadNombre)
  );

  useEffect(() => {
    const fetchData = async () => {
      if (isStudent) return;

      try {
        const [postResult, modResult] = await Promise.all([
          api.getAll(API_CONFIG.ENDPOINTS.POSTULANTES, {}, { skipGlobalLoader: true }),
          api.getAll(API_CONFIG.ENDPOINTS.MODALIDADES, {}, { skipGlobalLoader: true }),
        ]);

        if (postResult.success) {
          const postsData = Array.isArray(postResult.data) ? postResult.data : postResult.data.results || [];
          setPostulantes(postsData);
        }

        if (modResult.success) {
          const modsData = Array.isArray(modResult.data) ? modResult.data : modResult.data.results || [];
          setModalidades(modsData);
        }

        // Fetch all etapas by iterating paginated results
        const allEtapas = [];
        let page = 1;
        // eslint-disable-next-line no-constant-condition
        while (true) {
          const res = await api.getAll(API_CONFIG.ENDPOINTS.ETAPAS, { page }, { skipGlobalLoader: true });
          if (!res.success) break;
          const payload = res.data;
          if (Array.isArray(payload)) {
            allEtapas.push(...payload);
            break;
          }
          const results = payload.results || [];
          allEtapas.push(...results);
          if (!payload.next) break;
          page += 1;
        }
        setEtapas(allEtapas);
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error('Error loading dropdown data:', err);
      }
    };

    fetchData();
  }, [isStudent]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    const numericFields = ['modalidad', 'postulante_id', 'anio_academico', 'semestre_academico', 'etapa_actual'];
    const nextValue = numericFields.includes(name) ? (value ? parseInt(value) : '') : value;
    const nextFormData = {
      ...formData,
      [name]: nextValue,
    };

    if (name === 'modalidad') {
      const selectedModalidad = modalidades.find((m) => String(m.id) === String(nextValue));
      const normalizedModalidad = normalizeModalidadName(selectedModalidad?.nombre);

      if (HIDDEN_TITLE_TUTOR_MODALIDADES.includes(normalizedModalidad)) {
        nextFormData.titulo_trabajo = '';
        nextFormData.tutor = '';
      }
    }

    setFormData(nextFormData);
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError('');
    setFormError('');
    setSuccess('');

    const hasRequiredTrabajoFields = shouldShowTrabajoFields ? !!formData.titulo_trabajo : true;

    if (!formData.postulante_id || !formData.modalidad || !formData.anio_academico || !formData.semestre_academico || !hasRequiredTrabajoFields) {
      setFormError(
        shouldShowTrabajoFields
          ? 'Por favor completa todos los campos requeridos (Postulante, Modalidad, Título del Trabajo, Año y Semestre Académico)'
          : 'Por favor completa todos los campos requeridos (Postulante, Modalidad, Año y Semestre Académico)'
      );
      setIsSubmitting(false);
      return;
    }

    try {
      const endpoint = isEditMode
        ? API_CONFIG.ENDPOINTS.POSTULACION_DETAIL(formData.id)
        : API_CONFIG.ENDPOINTS.POSTULACIONES;

      const payload = {
        postulante_id: formData.postulante_id,
        anio_academico: formData.anio_academico,
        semestre_academico: formData.semestre_academico,
        estado: formData.estado,
        modalidad: formData.modalidad,
        etapa_actual: formData.etapa_actual || null,
        observaciones: formData.observaciones,
        // El backend espera las claves; cuando los campos están ocultos
        // enviamos cadenas vacías para evitar errores de "This field is required."
        titulo_trabajo: shouldShowTrabajoFields ? formData.titulo_trabajo : '',
        tutor: shouldShowTrabajoFields ? formData.tutor : '',
      };

      const result = isEditMode
        ? await patch(endpoint, payload)
        : await create(payload);

      if (result.success) {
        setSuccess(isEditMode ? 'Postulación actualizada exitosamente' : 'Postulación creada exitosamente');
        await refresh({
          errorMessage: 'Error al cargar postulaciones',
          exceptionMessage: 'Error loading postulaciones',
        });
        closeModal();
      } else {
        setError(result.error || 'Error en la operación');
      }
    } catch (err) {
      setError('Error en la operación');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (postulacion) => {
    if (!window.confirm(`¿Estás seguro de que deseas eliminar la postulación #${postulacion.id}?`)) {
      return;
    }
    
    setError('');
    setSuccess('');

    try {
      const result = await remove(API_CONFIG.ENDPOINTS.POSTULACION_DETAIL(postulacion.id));
      if (result.success) {
        setSuccess('Postulación eliminada exitosamente');
        await refresh({
          errorMessage: 'Error al cargar postulaciones',
          exceptionMessage: 'Error loading postulaciones',
        });
      } else {
        setError(result.error || 'Error al eliminar');
      }
    } catch (err) {
      setError('Error al eliminar postulación');
    }
  };

  const handleAvanzarEtapa = async (postulacion) => {
    setError('');
    setSuccess('');

    try {
      const result = await api.create(API_CONFIG.ENDPOINTS.POSTULACION_AVANZAR_ETAPA(postulacion.id));
      if (result.success) {
        setSuccess('Postulación avanzada exitosamente');
        await refresh({
          errorMessage: 'Error al cargar postulaciones',
          exceptionMessage: 'Error loading postulaciones',
        });
      } else {
        setError(result.error || 'Error al avanzar la etapa');
      }
    } catch (err) {
      setError('Error al avanzar la etapa');
    }
  };

  const getExportQueryParams = () => {
    const params = {};
    if (search) params.search = search;
    if (filterModalidad) params.modalidad = filterModalidad;
    if (filterEstado) params.estado = filterEstado;
    if (filterGestion) {
      params.gestion = filterGestion;
      params.anio_academico = filterGestion;
    }
    if (filterSemestreAcademico) params.semestre_academico = filterSemestreAcademico;
    return params;
  };

  const downloadBlob = (blob, filename) => {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  };

  const handleExportPdf = async () => {
    setExportingPdf(true);
    setError('');

    try {
      const response = await axiosInstance.get(API_CONFIG.ENDPOINTS.EXPORTAR_POSTULACIONES_PDF, {
        params: getExportQueryParams(),
        responseType: 'blob',
        skipGlobalLoader: true,
      });

      downloadBlob(response.data, `postulaciones_${new Date().toISOString().split('T')[0]}.pdf`);
    } catch (err) {
      console.error('Export PDF failed:', err);
      setError('Error al exportar PDF de postulaciones');
    } finally {
      setExportingPdf(false);
    }
  };

  const handleExportExcel = async () => {
    setExportingExcel(true);
    setError('');

    try {
      const response = await axiosInstance.get(API_CONFIG.ENDPOINTS.EXPORTAR_POSTULACIONES_EXCEL, {
        params: getExportQueryParams(),
        responseType: 'blob',
        skipGlobalLoader: true,
      });

      downloadBlob(response.data, `postulaciones_${new Date().toISOString().split('T')[0]}.xlsx`);
    } catch (err) {
      console.error('Export Excel failed:', err);
      setError('Error al exportar Excel de postulaciones');
    } finally {
      setExportingExcel(false);
    }
  };

  const getEstadoBadge = (estado) => {
    const colors = {
      borrador: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
      en_revision: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
      aprobada: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
      rechazada: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    };
    return colors[estado] || 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300';
  };

  const columns = [
    { key: 'id', label: 'ID' },
    {
      key: 'postulante',
      label: 'Postulante',
      render: (value, row) => {
        if (row.postulante?.nombre || row.postulante?.apellido) {
          return `${row.postulante.nombre || ''} ${row.postulante.apellido || ''}`.trim();
        }
        return row.postulante_nombre || '-';
      },
    },
    {
      key: 'modalidad_nombre',
      label: 'Modalidad',
      render: (value) => value || '-',
    },
    {
      key: 'titulo_trabajo',
      label: 'Titulo',
      render: (value) => value || '-',
    },
    {
      key: 'periodo_academico_display',
      label: 'Período',
      render: (value, row) => value || (row.anio_academico && row.semestre_academico ? `${row.semestre_academico}/${row.anio_academico}` : '-'),
    },
    {
      key: 'etapa_actual',
      label: 'Etapa Actual',
      render: (_, row) => {
        const isHistoricalFlow = !row.etapa_actual && !row.etapa_nombre && row.estado_general !== 'FINALIZADA';
        if (row.estado_general === 'FINALIZADA' || (!row.etapa_actual && !row.etapa_nombre && row.estado_general === 'EN_PROCESO')) {
          return (
            <span className={isHistoricalFlow ? 'text-red-600 dark:text-red-400 font-medium' : 'text-gray-700 dark:text-gray-300'}>
              Modalidad Finalizada
            </span>
          );
        }
        return row.etapa_actual?.nombre || row.etapa_nombre || 'Modalidad Finalizada';
      },
    },
    {
      key: 'acciones_avance',
      label: 'Acción',
      render: (_, row) => {
        if (isStudent) return null;

        const isHistoricalFlow = !row.etapa_actual && !row.etapa_nombre && row.estado_general !== 'FINALIZADA';
        if (row.estado_general === 'FINALIZADA') {
          return <span className="text-sm font-medium text-green-700 dark:text-green-400">Finalizada</span>;
        }
        if (isHistoricalFlow) {
          return <span className="text-sm font-medium text-red-600 dark:text-red-400">Documentos pendientes</span>;
        }

        return (
          <button
            type="button"
            onClick={() => handleAvanzarEtapa(row)}
            className="px-3 py-1 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded hover:bg-indigo-200 dark:hover:bg-indigo-800 transition text-xs font-medium"
          >
            Avanzar Etapa
          </button>
        );
      },
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Postulaciones</h1>
          <p className="text-gray-600 dark:text-gray-400">Administra las postulaciones del sistema</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={handleExportPdf}
            disabled={exportingPdf}
            className="px-4 py-2 border border-gray-300 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition disabled:opacity-50"
          >
            {exportingPdf ? 'Exportando PDF...' : 'Exportar PDF'}
          </button>
          <button
            type="button"
            onClick={handleExportExcel}
            disabled={exportingExcel}
            className="px-4 py-2 border border-gray-300 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition disabled:opacity-50"
          >
            {exportingExcel ? 'Exportando Excel...' : 'Exportar Excel'}
          </button>
          {!isStudent && (
            <button
              onClick={() => openModal()}
              className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition font-medium shadow"
            >
              <Plus className="w-5 h-5" />
              Nueva Postulación
            </button>
          )}
        </div>
      </div>

      {/* Alerts */}
      {formError && <Alert type="error" message={formError} onClose={() => setFormError('')} autoClose={false} />}
      {success && <Alert type="success" message={success} onClose={() => setSuccess('')} />}

      {/* Filters */}
      {!isStudent && (
        <div className="mb-6 flex flex-col sm:flex-row gap-4">
          <input
            type="text"
            placeholder="Buscar por título, postulante..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="w-full sm:w-1/2 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 outline-none transition"
          />
          <div className="w-full sm:w-auto">
            <select
              value={filterModalidad}
              onChange={(e) => {
                setFilterModalidad(e.target.value);
                setPage(1);
              }}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 outline-none transition"
            >
              <option value="">Todas las modalidades</option>
              {modalidades.map((modalidad) => (
                <option key={modalidad.id} value={modalidad.id}>
                  {modalidad.nombre}
                </option>
              ))}
            </select>
          </div>
          <div className="w-full sm:w-auto">
            <select
              value={filterEstado}
              onChange={(e) => {
                setFilterEstado(e.target.value);
                setPage(1);
              }}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 outline-none transition"
            >
              <option value="">Todas las postulaciones</option>
              {ESTADO_OPTIONS.map((op) => (
                <option key={op.value} value={op.value}>
                  {op.label}
                </option>
              ))}
            </select>
          </div>
          <div className="w-full sm:w-44">
            <input
              type="number"
              min="2000"
              max="2100"
              placeholder="Gestión"
              value={filterGestion}
              onChange={(e) => {
                setFilterGestion(e.target.value);
                setPage(1);
              }}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 outline-none transition"
            />
          </div>
          <div className="w-full sm:w-44">
            <select
              value={filterSemestreAcademico}
              onChange={(e) => {
                setFilterSemestreAcademico(e.target.value);
                setPage(1);
              }}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 outline-none transition"
            >
              <option value="">Semestre</option>
              <option value="1">1</option>
              <option value="2">2</option>
            </select>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-96 rounded-xl border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-gray-500 dark:text-gray-400">Cargando postulaciones...</p>
          </div>
        </div>
      ) : (
        <Table
          columns={columns}
          data={postulaciones}
          onEdit={!isStudent ? (row) => openModal({
            ...row,
            postulante_id: row.postulante?.id || '',
          }) : undefined}
          onDelete={!isStudent ? handleDelete : undefined}
        />
      )}

      {(meta.previous || meta.next || meta.count > 0) && (
        <div className="mt-4 flex items-center justify-between">
          <span className="text-sm text-gray-600 dark:text-gray-400">
            Mostrando {postulaciones?.length > 0 ? (page - 1) * 20 + 1 : 0}–{Math.min((page - 1) * 20 + (postulaciones?.length || 0), meta.count || 0)} de {meta.count || 0} registros
          </span>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600 dark:text-gray-400">Página {page}</span>
            <div className="flex gap-2">
            <button
              onClick={() => meta.previous && setPage((prev) => Math.max(1, prev - 1))}
              disabled={!meta.previous}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition disabled:opacity-50"
            >
              Anterior
            </button>
            <button
              onClick={() => meta.next && setPage((prev) => prev + 1)}
              disabled={!meta.next}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition disabled:opacity-50"
            >
              Siguiente
            </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal */}
      <Modal
        isOpen={isOpen}
        title={isEditMode ? 'Editar Postulación' : 'Nueva Postulación'}
        onSubmit={handleSubmit}
        onClose={closeModal}
        submitText={isEditMode ? 'Actualizar' : 'Crear'}
        isLoading={isSubmitting}
        sizeClass="max-w-4xl"
      >
        <div className="space-y-6">
          {/* 1. Información principal */}
          <section className="rounded-2xl border border-gray-200/80 bg-gray-50/60 p-5 sm:p-6 dark:border-gray-700 dark:bg-gray-800/60 shadow-sm">
            <div className="mb-3">
              <h3 className="text-sm font-semibold tracking-wide text-gray-900 dark:text-gray-100">Información principal</h3>
              <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">Postulante, modalidad y período académico.</p>
            </div>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-5">
              <FormField
                label="Postulante"
                name="postulante_id"
                type="select"
                value={formData.postulante_id}
                onChange={handleInputChange}
                options={postulantes.map((p) => ({ id: p.id, label: `${p.nombre || ''} ${p.apellido || ''} (${p.codigo_estudiante || ''})`.trim() }))}
                required
              />

              <FormField
                label="Modalidad"
                name="modalidad"
                type="select"
                value={formData.modalidad}
                onChange={handleInputChange}
                options={modalidades.map((m) => ({ id: m.id, label: m.nombre }))}
                required
              />

              <FormField
                label="Gestión"
                name="anio_academico"
                type="select"
                value={formData.anio_academico}
                onChange={handleInputChange}
                options={ACADEMIC_YEAR_OPTIONS}
                required
              />

              <FormField
                label="Periodo"
                name="semestre_academico"
                type="select"
                value={formData.semestre_academico}
                onChange={handleInputChange}
                options={[
                  { id: 1, label: '1' },
                  { id: 2, label: '2' },
                ]}
                required
              />
            </div>
          </section>

          {/* 2. Información académica */}
          {shouldShowTrabajoFields && (
            <section className="rounded-2xl border border-gray-200/80 bg-gray-50/60 p-5 sm:p-6 dark:border-gray-700 dark:bg-gray-800/60 shadow-sm">
              <div className="mb-3">
                <h3 className="text-sm font-semibold tracking-wide text-gray-900 dark:text-gray-100">Información académica</h3>
                <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">Título del trabajo y tutor asociado.</p>
              </div>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-5">
                <FormField
                  label="Título del Trabajo"
                  name="titulo_trabajo"
                  type="text"
                  value={formData.titulo_trabajo}
                  onChange={handleInputChange}
                  placeholder="Título del trabajo"
                  required
                  className="sm:col-span-2"
                />

                <FormField
                  label="Tutor"
                  name="tutor"
                  type="text"
                  value={formData.tutor}
                  onChange={handleInputChange}
                  placeholder="(opcional)"
                />
              </div>
            </section>
          )}

          {/* 3. Configuración adicional */}
          <section className="rounded-2xl border border-gray-200/80 bg-gray-50/60 p-5 sm:p-6 dark:border-gray-700 dark:bg-gray-800/60 shadow-sm">
            <div className="mb-3"></div>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-5">
              <FormField
                label="Etapa actual"
                name="etapa_actual"
                type="select"
                value={formData.etapa_actual}
                onChange={handleInputChange}
                options={
                  formData.modalidad
                    ? etapas
                        .filter((etapa) => {
                          if (!formData.modalidad) return false;
                          // Filtrar por modalidad y ocultar etapas inválidas/legacy
                          const matchesModalidad = etapa.modalidad === formData.modalidad;
                          const nombreNormalized = (etapa.nombre || '').toString().trim().toUpperCase();
                          const isLegacyExamen1 = nombreNormalized === 'EXAMEN 1';
                          return matchesModalidad && !isLegacyExamen1;
                        })
                        .map((etapa) => ({ id: etapa.id, label: etapa.nombre }))
                    : []
                }
                placeholder="Modalidad Finalizada"
                helperText="Opcional. Si no se selecciona, la postulación queda en el flujo histórico sin etapa asignada."
                className="sm:col-span-2"
              />
            </div>
          </section>

          {/* 4. Seguimiento de postulación */}
          <section className="rounded-2xl border border-gray-200/80 bg-gray-50/60 p-5 sm:p-6 dark:border-gray-700 dark:bg-gray-800/60 shadow-sm">
            <div className="mb-3">
              <h3 className="text-sm font-semibold tracking-wide text-gray-900 dark:text-gray-100">Seguimiento de postulación</h3>
              <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">Etapa actual y observaciones del proceso.</p>
            </div>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-5">
              {isEditMode ? (
                <FormField
                  label="Estado General"
                  name="estado_general"
                  type="text"
                  value={formData.estado_general}
                  readOnly
                  className="sm:col-span-2"
                />
              ) : null}

              <FormField
                label="Observaciones"
                name="observaciones"
                type="textarea"
                value={formData.observaciones}
                onChange={handleInputChange}
                placeholder="(opcional) Notas internas visibles para administradores"
                className="sm:col-span-2"
              />
            </div>
          </section>
        </div>
      </Modal>
    </div>
  );
};

export default Postulaciones;
