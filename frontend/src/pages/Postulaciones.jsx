/**
 * Postulaciones Page - CRUD Completo (Refactorizado)
 * Manage applications and their status using shared components
 */

import { useState, useEffect } from 'react';
import useAuth from '../hooks/useAuth';
import { useSearchParams } from 'react-router-dom';
import { Plus } from 'lucide-react';
import api from '../api/api';
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
  anio_academico: '',
  semestre_academico: '',
  estado: 'borrador',
  estado_general: 'EN_PROCESO',
  tutor: '',
  observaciones: '',
};

const ESTADO_OPTIONS = [
  { label: 'Borrador', value: 'borrador' },
  { label: 'En revision', value: 'en_revision' },
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
  
  const [filterEstado, setFilterEstado] = useState(searchParams.get('estado') || '');
  const [filterAnioAcademico, setFilterAnioAcademico] = useState(searchParams.get('anio_academico') || '');
  const [filterSemestreAcademico, setFilterSemestreAcademico] = useState(searchParams.get('semestre_academico') || '');

  const { search, setSearch, page, setPage } = useListFilters(list, {
    estado: filterEstado,
    anio_academico: filterAnioAcademico,
    semestre_academico: filterSemestreAcademico,
  }, {
    requestConfig: { skipGlobalLoader: true },
    errorMessage: 'Error al cargar postulaciones',
    exceptionMessage: 'Error loading postulaciones',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const { isOpen, isEditMode, formData, openModal, closeModal, setFormData } = useModal(INITIAL_FORM_DATA);

  useEffect(() => {
    const fetchData = async () => {
      if (isStudent) return;

      try {
        const [postResult, modResult, etapaResult] = await Promise.all([
          api.getAll(API_CONFIG.ENDPOINTS.POSTULANTES, {}, { skipGlobalLoader: true }),
          api.getAll(API_CONFIG.ENDPOINTS.MODALIDADES, {}, { skipGlobalLoader: true }),
          api.getAll(API_CONFIG.ENDPOINTS.ETAPAS, {}, { skipGlobalLoader: true }),
        ]);

        if (postResult.success) {
          const postsData = Array.isArray(postResult.data) ? postResult.data : postResult.data.results || [];
          setPostulantes(postsData);
        }

        if (modResult.success) {
          const modsData = Array.isArray(modResult.data) ? modResult.data : modResult.data.results || [];
          setModalidades(modsData);
        }

        if (etapaResult.success) {
          const etapasData = Array.isArray(etapaResult.data) ? etapaResult.data : etapaResult.data.results || [];
          setEtapas(etapasData);
        }
      } catch (err) {
        console.error('Error loading dropdown data:', err);
      }
    };

    fetchData();
  }, [isStudent]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    const numericFields = ['modalidad', 'postulante_id', 'anio_academico', 'semestre_academico', 'etapa_actual'];
    setFormData({
      ...formData,
      [name]: numericFields.includes(name) ? (value ? parseInt(value) : '') : value,
    });
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError('');
    setSuccess('');

    // Validar campos requeridos (dropdowns)
    if (!formData.postulante_id || !formData.modalidad || !formData.anio_academico || !formData.semestre_academico || !formData.titulo_trabajo) {
      setError('Por favor completa todos los campos requeridos (Postulante, Modalidad, Título del Trabajo, Año y Semestre Académico)');
      setIsSubmitting(false);
      return;
    }

    try {
      const endpoint = isEditMode
        ? API_CONFIG.ENDPOINTS.POSTULACION_DETAIL(formData.id)
        : API_CONFIG.ENDPOINTS.POSTULACIONES;

      const payload = {
        postulante_id: formData.postulante_id,
        titulo_trabajo: formData.titulo_trabajo,
        anio_academico: formData.anio_academico,
        semestre_academico: formData.semestre_academico,
        estado: formData.estado,
        modalidad: formData.modalidad,
        etapa_actual: formData.etapa_actual || null,
        tutor: formData.tutor,
        observaciones: formData.observaciones,
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
      key: 'estado',
      label: 'Estado',
      render: (value, row) => {
        const badgeClass = getEstadoBadge(value);
        const label = row.estado_display || value || '-';
        return (
          <span className={`px-2 py-1 rounded text-sm font-medium ${badgeClass}`}>
            {label}
          </span>
        );
      },
    },
    {
      key: 'estado_general',
      label: 'Estado General',
      render: (value) => value || '-',
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

      {/* Alerts */}
      {error && <Alert type="error" message={error} onClose={() => setError('')} autoClose={false} />}
      {success && <Alert type="success" message={success} onClose={() => setSuccess('')} />}

      {/* Filters */}
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
            placeholder="Año académico"
            value={filterAnioAcademico}
            onChange={(e) => {
              setFilterAnioAcademico(e.target.value);
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
                label="Año académico"
                name="anio_academico"
                type="number"
                value={formData.anio_academico}
                onChange={handleInputChange}
                placeholder="2026"
                required
              />

              <FormField
                label="Semestre académico"
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

          {/* 3. Estado de postulación */}
          <section className="rounded-2xl border border-gray-200/80 bg-gray-50/60 p-5 sm:p-6 dark:border-gray-700 dark:bg-gray-800/60 shadow-sm">
            <div className="mb-3">
              <h3 className="text-sm font-semibold tracking-wide text-gray-900 dark:text-gray-100">Estado de postulación</h3>
              <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">Estado actual, estado general y observaciones.</p>
            </div>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-5">
              <FormField
                label="Estado"
                name="estado"
                type="select"
                value={formData.estado}
                onChange={handleInputChange}
                options={ESTADO_OPTIONS}
                required
              />

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

          {/* 4. Configuración adicional */}
          <section className="rounded-2xl border border-gray-200/80 bg-gray-50/60 p-5 sm:p-6 dark:border-gray-700 dark:bg-gray-800/60 shadow-sm">
            <div className="mb-3">
              <h3 className="text-sm font-semibold tracking-wide text-gray-900 dark:text-gray-100">Configuración adicional</h3>
              <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">Etapa actual de la postulación, según la modalidad seleccionada.</p>
            </div>
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
                        .filter((etapa) => formData.modalidad && etapa.modalidad === formData.modalidad)
                        .map((etapa) => ({ id: etapa.id, label: etapa.nombre }))
                    : []
                }
                placeholder="Sin etapa actual"
                helperText="Opcional. Si no se selecciona, la postulación queda sin etapa asignada."
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
