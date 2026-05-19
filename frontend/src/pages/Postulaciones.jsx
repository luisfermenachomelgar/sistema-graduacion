/**
 * Postulaciones Page - CRUD Completo (Refactorizado)
 * Manage applications and their status using shared components
 */

import { useState, useEffect } from 'react';
import useAuth from '../hooks/useAuth';
import { useSearchParams } from 'react-router-dom';
import api from '../api/api';
import { API_CONFIG } from '../constants/api';
import Modal from '../components/Modal';
import FormField from '../components/FormField';
import Table from '../components/Table';
import TableSkeleton from '../components/TableSkeleton';
import Alert from '../components/Alert';
import { useModal } from '../hooks/useModal';
import { useCrud } from '../hooks/useCrud';
import { useListFilters } from '../hooks/useListFilters';

const INITIAL_FORM_DATA = {
  postulante_id: '',
  modalidad: '',
  titulo_trabajo: '',
  gestion: '',
  estado: 'borrador',
  estado_general: 'EN_PROCESO',
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
  const [success, setSuccess] = useState('');
  
  const [filterEstado, setFilterEstado] = useState(searchParams.get('estado') || '');

  const { search, setSearch, page, setPage } = useListFilters(list, { estado: filterEstado }, {
    errorMessage: 'Error al cargar postulaciones',
    exceptionMessage: 'Error loading postulaciones',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const { isOpen, isEditMode, formData, openModal, closeModal, setFormData } = useModal(INITIAL_FORM_DATA);

  useEffect(() => {
    fetchData();
    // Load main table with local loader (no global overlay)
    list({}, { requestConfig: { skipGlobalLoader: true } });
  }, []);

  const fetchData = async () => {
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
    } catch (err) {
      console.error('Error loading dropdown data:', err);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    const numericFields = ['modalidad', 'postulante_id', 'gestion'];
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
    if (!formData.postulante_id || !formData.modalidad || !formData.gestion) {
      setError('Por favor completa todos los campos requeridos (Postulante, Modalidad, Gestión)');
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
        gestion: formData.gestion,
        estado: formData.estado,
        estado_general: formData.estado_general,
        modalidad: formData.modalidad,
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
      key: 'gestion',
      label: 'Gestion',
      render: (value) => value || '-',
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
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Postulaciones</h1>
        {!isStudent && (
          <button
            onClick={() => openModal()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium shadow"
          >
            ➕ Nueva Postulación
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
      </div>

      {loading && <TableSkeleton rows={10} columns={6} />}

      {!loading && (
        <Table
          columns={columns}
          data={postulaciones}
          loading={loading}
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
        title={isEditMode ? '✏️ Editar Postulación' : '➕ Nueva Postulación'}
        onSubmit={handleSubmit}
        onClose={closeModal}
        submitText={isEditMode ? 'Actualizar' : 'Crear'}
        isLoading={isSubmitting}
      >
        <form className="space-y-4">
          <FormField
            label="Postulante"
            name="postulante_id"
            type="select"
            value={formData.postulante_id}
            onChange={handleInputChange}
            options={postulantes.map((p) => ({
              id: p.id,
              label: `${p.nombre || ''} ${p.apellido || ''} (${p.codigo_estudiante || ''})`.trim(),
            }))}
            required
          />

          <FormField
            label="Modalidad"
            name="modalidad"
            type="select"
            value={formData.modalidad}
            onChange={handleInputChange}
            options={modalidades.map((m) => ({
              id: m.id,
              label: m.nombre,
            }))}
            required
          />

          <FormField
            label="Titulo del Trabajo"
            name="titulo_trabajo"
            type="text"
            value={formData.titulo_trabajo}
            onChange={handleInputChange}
            placeholder="Titulo del trabajo"
            required
          />

          <FormField
            label="Gestion"
            name="gestion"
            type="number"
            value={formData.gestion}
            onChange={handleInputChange}
            placeholder="2025"
            required
          />

          <FormField
            label="Estado"
            name="estado"
            type="select"
            value={formData.estado}
            onChange={handleInputChange}
            options={ESTADO_OPTIONS}
            required
          />

          <FormField
            label="Estado General"
            name="estado_general"
            type="select"
            value={formData.estado_general}
            onChange={handleInputChange}
            options={ESTADO_GENERAL_OPTIONS}
            required
          />

        </form>
      </Modal>
    </div>
  );
};

export default Postulaciones;
