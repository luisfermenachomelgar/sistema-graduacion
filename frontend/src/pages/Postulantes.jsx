/**
 * Postulantes Page - CRUD Moderno
 * List and manage applicants with modern UI and full CRUD
 */

import { useState, useEffect } from 'react';
import useAuth from '../hooks/useAuth';
import DataTable from '../components/DataTable';
import api from '../api/api';
import { API_CONFIG } from '../constants/api';
import Modal from '../components/Modal';
import FormField from '../components/FormField';
import Alert from '../components/Alert';
import { useModal } from '../hooks/useModal';
import { useCrud } from '../hooks/useCrud';
import { Plus } from 'lucide-react';

const INITIAL_FORM_DATA = {
  usuario: '',
  nombre: '',
  apellido: '',
  ci: '',
  codigo_estudiante: '',
  telefono: '',
  carrera: '',
  facultad: '',
};

// NOTE: cache removed - rely on useCrud state directly

const Postulantes = () => {
  const {
    data: postulantes,
    loading,
    error,
    setError,
    meta,
    list,
    refresh,
    create,
    patch,
    remove,
  } = useCrud(API_CONFIG.ENDPOINTS.POSTULANTES);
  const { user } = useAuth();

  const effectiveRole = user?.role ?? (user?.is_superuser ? 'admin' : null);
  const isAdmin = effectiveRole === 'admin';
  const isStudent = effectiveRole === 'estudiante';
  const canManagePostulantes = !isStudent;
  const [usuarios, setUsuarios] = useState([]);
  const [success, setSuccess] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { isOpen, isEditMode, formData, openModal, closeModal, setFormData } = useModal(
    INITIAL_FORM_DATA
  );

  useEffect(() => {
    const load = async () => {
      // Carga principal de postulantes
      const result = await list({}, { requestConfig: { skipGlobalLoader: true } });

      // Si el backend responde 403 para estudiantes, ocultamos el mensaje técnico
      if (!result.success && isStudent && result.status === 403) {
        setError('');
      }
    };

    load();
  }, [canManagePostulantes, isStudent, list, setError]);

  useEffect(() => {
    const loadUsuarios = async () => {
      if (!isAdmin) return;

      try {
        const result = await api.getAll(API_CONFIG.ENDPOINTS.USUARIOS, {}, { skipGlobalLoader: true });
        if (result.success) {
          const data = Array.isArray(result.data) ? result.data : result.data.results || [];
          setUsuarios(data);
        }
      } catch (err) {
        console.error('Error loading usuarios:', err);
      }
    };

    loadUsuarios();
  }, [isAdmin]);

  

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    // Validar teléfono: solo números y guiones
    if (name === 'telefono') {
      const onlyNumeric = value.replace(/[^0-9-]/g, '');
      setFormData({
        ...formData,
        [name]: onlyNumeric,
      });
      return;
    }
    
    // Validar CI: solo números y guiones
    if (name === 'ci') {
      const onlyNumeric = value.replace(/[^0-9-]/g, '');
      setFormData({
        ...formData,
        [name]: onlyNumeric,
      });
      return;
    }
    
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError('');
    setSuccess('');

    try {
      const endpoint = isEditMode
        ? API_CONFIG.ENDPOINTS.POSTULANTE_DETAIL(formData.id)
        : API_CONFIG.ENDPOINTS.POSTULANTES;

      const payload = {
        ...(isAdmin ? { usuario: formData.usuario ? Number(formData.usuario) : null } : {}),
        nombre: formData.nombre,
        apellido: formData.apellido,
        ci: formData.ci,
        codigo_estudiante: formData.codigo_estudiante,
        telefono: formData.telefono,
        carrera: formData.carrera,
        facultad: formData.facultad,
      };

      const result = isEditMode
        ? await patch(endpoint, payload, { skipGlobalLoader: true })
        : await create(payload, { skipGlobalLoader: true });

      if (result.success) {
        setSuccess(isEditMode ? 'Postulante actualizado exitosamente' : 'Postulante creado exitosamente');
        await refresh({ requestConfig: { skipGlobalLoader: true } });
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

  const handleDelete = async (postulante) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar este postulante?')) return;
    
    setError('');
    setSuccess('');

    try {
      const result = await remove(API_CONFIG.ENDPOINTS.POSTULANTE_DETAIL(postulante.id), { skipGlobalLoader: true });
      if (result.success) {
        setSuccess('Postulante eliminado exitosamente');
        await refresh({ requestConfig: { skipGlobalLoader: true } });
      } else {
        setError(result.error || 'Error al eliminar');
      }
    } catch (err) {
      setError('Error al eliminar postulante');
    }
  };

  const columns = [
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
      key: 'codigo_estudiante',
      label: 'Código Estudiante',
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
      key: 'telefono',
      label: 'Teléfono',
      sortable: false,
      render: (value) => value || '-',
    },
  ];

  return (
    <div className="space-y-6">
        {/* Encabezado */}
        <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Postulantes
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Administra los postulantes del sistema
            </p>
          </div>
          {canManagePostulantes && (
            <button
              onClick={() => openModal()}
              className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition font-medium shadow"
            >
              <Plus className="w-5 h-5" />
              Nuevo Postulante
            </button>
          )}
        </div>

        {/* Alertas */}
        {error && <Alert type="error" message={error} onClose={() => setError('')} autoClose={false} />}
        {success && <Alert type="success" message={success} onClose={() => setSuccess('')} />}

        {isStudent && (
          <div className="rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 text-blue-900 dark:border-blue-900/40 dark:bg-blue-900/20 dark:text-blue-100">
            <p className="font-medium">Vista de solo lectura</p>
            <p className="text-sm text-blue-800 dark:text-blue-200">
              Tu cuenta puede consultar postulantes asociados, pero no crear, editar ni eliminar registros.
            </p>
          </div>
        )}

        {/* Tabla */}
        {loading ? (
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-gray-500 dark:text-gray-400">Cargando postulantes...</p>
            </div>
          </div>
        ) : (
          // Cuando no está cargando, mostramos tabla o estado vacío (según rol y datos)
          (isStudent && (!postulantes || postulantes.length === 0)) ? (
            <div className="rounded-xl border border-dashed border-gray-300 bg-white px-6 py-10 text-center text-gray-600 shadow-sm dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300">
              <p className="text-lg font-semibold text-gray-900 dark:text-white">No hay postulantes visibles</p>
              <p className="mt-2 text-sm">Cuando existan postulantes asociados a tu cuenta, aparecerán aquí sin mostrar acciones administrativas.</p>
            </div>
          ) : (
            <DataTable
              data={postulantes || []}
              columns={columns}
              pageSize={10}
              onEdit={canManagePostulantes ? (row) => openModal(isAdmin ? { ...row, usuario: row.usuario_id || '' } : row) : undefined}
              onDelete={canManagePostulantes ? handleDelete : undefined}
            />
          )
        )}

        {/* Modal */}
        <Modal
          isOpen={isOpen}
          title={isEditMode ? 'Editar Postulante' : 'Nuevo Postulante'}
          onSubmit={handleSubmit}
          onClose={closeModal}
          submitText={isEditMode ? 'Actualizar' : 'Crear'}
          isLoading={isSubmitting}
          sizeClass="max-w-4xl"
        >
          <div className="space-y-6">
            {isAdmin && (
              <section className="rounded-2xl border border-gray-200/80 bg-gray-50/60 p-5 sm:p-6 dark:border-gray-700 dark:bg-gray-800/60 shadow-sm">
                <div className="mb-3">
                  <h3 className="text-sm font-semibold tracking-wide text-gray-900 dark:text-gray-100">Asignación de usuario</h3>
                  <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">Opcional. Puedes vincular el postulante a un usuario existente o dejarlo sin asignar.</p>
                </div>
                <div className="grid grid-cols-1 gap-4">
                  <FormField
                    label="Usuario"
                    name="usuario"
                    type="select"
                    value={formData.usuario}
                    onChange={handleInputChange}
                    placeholder="Sin usuario asignado"
                    options={usuarios.map((currentUser) => ({
                      id: currentUser.id,
                      label: `${currentUser.username} - ${currentUser.first_name || ''} ${currentUser.last_name || ''}`.trim(),
                    }))}
                    helperText="Déjalo vacío si el postulante no debe quedar vinculado a un usuario."
                  />
                </div>
              </section>
            )}

            {/* Información Personal */}
            <section className="rounded-2xl border border-gray-200/80 bg-gray-50/60 p-5 sm:p-6 dark:border-gray-700 dark:bg-gray-800/60 shadow-sm">
              <div className="mb-3">
                <h3 className="text-sm font-semibold tracking-wide text-gray-900 dark:text-gray-100">Información personal</h3>
                <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">Datos básicos del postulante.</p>
              </div>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-5">
                <FormField
                  label="Nombre"
                  name="nombre"
                  type="text"
                  value={formData.nombre}
                  onChange={handleInputChange}
                  placeholder="Juan"
                  required
                />
                <FormField
                  label="Apellido"
                  name="apellido"
                  type="text"
                  value={formData.apellido}
                  onChange={handleInputChange}
                  placeholder="Perez"
                  required
                />
                <FormField
                  label="CI"
                  name="ci"
                  type="text"
                  value={formData.ci}
                  onChange={handleInputChange}
                  placeholder="12345678"
                  required
                  className="sm:col-span-2"
                />
              </div>
            </section>

            {/* Información Académica */}
            <section className="rounded-2xl border border-gray-200/80 bg-gray-50/60 p-5 sm:p-6 dark:border-gray-700 dark:bg-gray-800/60 shadow-sm">
              <div className="mb-3">
                <h3 className="text-sm font-semibold tracking-wide text-gray-900 dark:text-gray-100">Información académica</h3>
                <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">Datos de formación y carrera.</p>
              </div>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-5">
                <FormField
                  label="Código de Estudiante"
                  name="codigo_estudiante"
                  type="text"
                  value={formData.codigo_estudiante}
                  onChange={handleInputChange}
                  placeholder="202412345"
                  required
                />
                <FormField
                  label="Carrera"
                  name="carrera"
                  type="text"
                  value={formData.carrera}
                  onChange={handleInputChange}
                  placeholder="Ingeniería"
                />
                <FormField
                  label="Facultad"
                  name="facultad"
                  type="text"
                  value={formData.facultad}
                  onChange={handleInputChange}
                  placeholder="Facultad de Tecnología"
                  className="sm:col-span-2"
                />
              </div>
            </section>

            {/* Información de Contacto */}
            <section className="rounded-2xl border border-gray-200/80 bg-gray-50/60 p-5 sm:p-6 dark:border-gray-700 dark:bg-gray-800/60 shadow-sm">
              <div className="mb-3">
                <h3 className="text-sm font-semibold tracking-wide text-gray-900 dark:text-gray-100">Información de contacto</h3>
                <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">Datos para comunicación.</p>
              </div>
              <div className="grid grid-cols-1 gap-4">
                <FormField
                  label="Teléfono"
                  name="telefono"
                  type="text"
                  value={formData.telefono}
                  onChange={handleInputChange}
                  placeholder="70000000"
                  required
                />
              </div>
            </section>
          </div>
        </Modal>
      </div>
  );
};

export default Postulantes;
