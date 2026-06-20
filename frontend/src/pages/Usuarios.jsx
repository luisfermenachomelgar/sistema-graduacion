/**
 * Usuarios Page - CRUD Completo
 * Manage system users
 */

import { useState } from 'react';
import { Modal, FormField, Table, Alert } from '../components';
import { PageHeader, SectionCard } from '../components';
import { useModal } from '../hooks/useModal';
import { useCrud } from '../hooks/useCrud';
import { useListFilters } from '../hooks/useListFilters';
import { API_CONFIG } from '../constants/api';
import { Plus } from 'lucide-react';

const INITIAL_FORM_DATA = {
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  role: 'estudiante',
  password: '',
  is_staff: false,
  is_active: true,
};

const LIST_REQUEST_OPTIONS = {
  errorMessage: 'Error al cargar usuarios',
  exceptionMessage: 'Error loading usuarios',
  requestConfig: { skipGlobalLoader: true },
};

const Usuarios = () => {
  const {
    data: usuarios,
    loading,
    error,
    setError,
    meta,
    list,
    refresh,
    create,
    patch,
    remove,
  } = useCrud(API_CONFIG.ENDPOINTS.USUARIOS);
  const [success, setSuccess] = useState('');

  const { search, setSearch, page, setPage } = useListFilters(list, {}, LIST_REQUEST_OPTIONS);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const { isOpen, isEditMode, formData, openModal, closeModal, setFormData } = useModal(INITIAL_FORM_DATA);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError('');
    setSuccess('');

    if (!formData.username.trim()) {
      setError('El nombre de usuario es requerido');
      setIsSubmitting(false);
      return;
    }

    if (!formData.email.trim()) {
      setError('El email es requerido');
      setIsSubmitting(false);
      return;
    }

    if (!isEditMode && !formData.password.trim()) {
      setError('La contraseña es requerida para nuevos usuarios');
      setIsSubmitting(false);
      return;
    }

    try {
      const payload = { ...formData };
      if (payload.password === '') {
        delete payload.password;
      }
      delete payload.is_staff;

      const endpoint = isEditMode
        ? API_CONFIG.ENDPOINTS.USUARIO_DETAIL(formData.id)
        : API_CONFIG.ENDPOINTS.USUARIOS;

      const result = isEditMode
        ? await patch(endpoint, payload)
        : await create(payload);

      if (result.success) {
        setSuccess(isEditMode ? 'Usuario actualizado exitosamente' : 'Usuario creado exitosamente');
        await refresh(LIST_REQUEST_OPTIONS);
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

  const handleDelete = async (usuario) => {
    setError('');
    setSuccess('');

    try {
      const result = await remove(API_CONFIG.ENDPOINTS.USUARIO_DETAIL(usuario.id));
      if (result.success) {
        setSuccess('Usuario eliminado exitosamente');
        await refresh(LIST_REQUEST_OPTIONS);
      } else {
        setError(result.error || 'Error al eliminar');
      }
    } catch (err) {
      setError('Error al eliminar usuario');
    }
  };

  const columns = [
    { key: 'username', label: 'Usuario' },
    { key: 'email', label: 'Email' },
    {
      key: 'first_name',
      label: 'Nombre',
      render: (value, row) => `${value || ''} ${row.last_name || ''}`.trim() || '—',
    },
    {
      key: 'role_display',
      label: 'Rol',
      render: (value) => (
        <span className={`px-2 py-1 rounded text-xs font-medium ${value ? 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'}`}>
          {value || '—'}
        </span>
      ),
    },
    {
      key: 'is_active',
      label: 'Estado',
      render: (value) => (
        <span className={`px-2 py-1 rounded text-xs font-medium ${value ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'}`}>
          {value ? '✓ Activo' : '✗ Inactivo'}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Gestión de Usuarios"
        description="Administra accesos, roles y estado de los usuarios del sistema"
        action={(
          <button
            onClick={() => {
              setFormData(INITIAL_FORM_DATA);
              openModal();
            }}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-2 font-medium text-white shadow transition hover:bg-blue-700"
          >
            <Plus className="h-5 w-5" />
            Nuevo Usuario
          </button>
        )}
      />

      {success && <Alert type="success" message={success} />}
      {error && <Alert type="error" message={error} />}

      <div className="mb-6">
        <input
          type="text"
          placeholder="Buscar por usuario, email o nombre..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 outline-none transition"
        />
      </div>

      <Modal
        isOpen={isOpen}
        title={isEditMode ? 'Editar Usuario' : 'Nuevo Usuario'}
        onClose={closeModal}
        onSubmit={handleSubmit}
        isLoading={isSubmitting}
        sizeClass="max-w-4xl"
      >
        <div className="space-y-6">
          <SectionCard title="Información de acceso" description="Credenciales para ingreso al sistema.">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-5">
              <FormField
                label="Usuario"
                type="text"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                required
                className="md:col-span-1"
              />
              <FormField
                label="Email"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
                className="md:col-span-1"
              />
              {!isEditMode && (
                <FormField
                  label="Contraseña"
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  required
                  className="md:col-span-2"
                />
              )}
            </div>
          </SectionCard>

          <SectionCard title="Información personal" description="Datos básicos del usuario.">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-5">
              <FormField
                label="Nombre"
                type="text"
                name="first_name"
                value={formData.first_name}
                onChange={handleInputChange}
              />
              <FormField
                label="Apellido"
                type="text"
                name="last_name"
                value={formData.last_name}
                onChange={handleInputChange}
              />
            </div>
          </SectionCard>

          <SectionCard title="Permisos y estado" description="Nivel de acceso y estado de habilitación.">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-5">
              <FormField
                label="Rol"
                type="select"
                name="role"
                value={formData.role}
                onChange={handleInputChange}
                disabled={!!formData.is_superuser}
                options={[
                  { id: 'admin', label: 'Administrador' },
                  { id: 'administ', label: 'Administrativo' },
                  { id: 'estudiante', label: 'Estudiante' },
                ]}
                required
              />
              <div className="rounded-xl border border-gray-200 bg-white px-4 py-3 dark:border-gray-600 dark:bg-gray-700/60">
                <FormField
                  label="Usuario activo"
                  type="checkbox"
                  name="is_active"
                    value={formData.is_active}
                    onChange={handleInputChange}
                    disabled={!!formData.is_superuser}
                />
              </div>
            </div>
          </SectionCard>
        </div>
      </Modal>

      {loading ? (
        <div className="flex h-96 items-center justify-center rounded-2xl border border-gray-200/80 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800">
          <div className="text-center">
            <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-b-2 border-blue-500" />
            <p className="text-gray-500 dark:text-gray-400">Cargando usuarios...</p>
          </div>
        </div>
      ) : (
        <Table
          columns={columns}
          data={usuarios}
          onEdit={(user) => {
            const userData = {
              ...user,
              password: '',
              id: user.id,
            };
            // ✅ CORRECCIÓN: Pasar userData a openModal para establecer isEditMode=true
            openModal(userData);
          }}
          onDelete={handleDelete}
          keyField="id"
        />
      )}
      {(meta.previous || meta.next || meta.count > 0) && (
        <div className="mt-4 flex items-center justify-between">
          <span className="text-sm transition-colors text-gray-600 dark:text-gray-400">
            Mostrando {usuarios?.length > 0 ? (page - 1) * 20 + 1 : 0}–{Math.min((page - 1) * 20 + (usuarios?.length || 0), meta.count || 0)} de {meta.count || 0} registros
          </span>
          <div className="flex items-center gap-4">
            <span className="text-sm transition-colors text-gray-600 dark:text-gray-400">Página {page}</span>
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
    </div>
  );
};

export default Usuarios;
