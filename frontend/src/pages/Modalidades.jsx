/**
 * Modalidades Page - CRUD Completo
 * Manage graduation modalities
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_CONFIG } from '../constants/api';
import { useCrud } from '../hooks/useCrud';
import Modal from '../components/Modal';
import Alert from '../components/Alert';
import FormField from '../components/FormField';
import { PageHeader, SectionCard } from '../components';
import { ArrowRight, Plus, PencilLine, Trash2 } from 'lucide-react';

const Modalidades = () => {
  const navigate = useNavigate();
  const {
    data: modalidades,
    loading,
    error,
    setError,
    list,
    refresh,
    create,
    update,
    remove,
  } = useCrud(API_CONFIG.ENDPOINTS.MODALIDADES);
  const [success, setSuccess] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    nombre: '',
    descripcion: '',
    activa: true,
  });

  useEffect(() => {
    // Load main grid with local loader (no global overlay)
    list({}, { requestConfig: { skipGlobalLoader: true }, exceptionMessage: 'Error loading modalidades' });
  }, [list]);

  const resetForm = () => {
    setFormData({
      nombre: '',
      descripcion: '',
      activa: true,
    });
    setEditingId(null);
  };

  const openModal = (modalidad = null) => {
    if (modalidad) {
      setFormData(modalidad);
      setEditingId(modalidad.id);
    } else {
      resetForm();
    }
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    resetForm();
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async () => {
    setError('');
    setSuccess('');

    if (!formData.nombre.trim()) {
      setError('El nombre es requerido');
      return;
    }

    try {
      if (editingId) {
        const result = await update(API_CONFIG.ENDPOINTS.MODALIDAD_DETAIL(editingId), formData);
        if (result.success) {
          setSuccess('Modalidad actualizada exitosamente');
          await refresh({ exceptionMessage: 'Error loading modalidades' });
          closeModal();
        } else {
          setError(result.error || 'Error al actualizar');
        }
      } else {
        const result = await create(formData);
        if (result.success) {
          setSuccess('Modalidad creada exitosamente');
          await refresh({ exceptionMessage: 'Error loading modalidades' });
          closeModal();
        } else {
          setError(result.error || 'Error al crear');
        }
      }
    } catch (err) {
      setError('Error en la operación');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Estás seguro que deseas eliminar esta modalidad?')) {
      return;
    }

    setError('');
    setSuccess('');

    try {
      const result = await remove(API_CONFIG.ENDPOINTS.MODALIDAD_DETAIL(id));
      if (result.success) {
        setSuccess('Modalidad eliminada exitosamente');
        await refresh({ exceptionMessage: 'Error loading modalidades' });
      } else {
        setError(result.error || 'Error al eliminar');
      }
    } catch (err) {
      setError('Error al eliminar modalidad');
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Modalidades"
        description="Gestiona las modalidades de graduación del sistema"
        action={(
          <button
            onClick={() => openModal()}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-2 font-medium text-white shadow transition hover:bg-blue-700"
          >
            <Plus className="h-5 w-5" />
            Nueva Modalidad
          </button>
        )}
      />

      {error && <Alert type="error" message={error} autoClose={false} />}
      {success && <Alert type="success" message={success} />}

      {loading ? (
        <div className="flex h-96 items-center justify-center rounded-2xl border border-gray-200/80 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800">
          <div className="text-center">
            <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-b-2 border-blue-500" />
            <p className="text-gray-500 dark:text-gray-400">Cargando modalidades...</p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {modalidades.length > 0 ? (
            modalidades.map((modalidad) => (
              <SectionCard key={modalidad.id} className="border-l-4 border-l-blue-600 flex flex-col h-full">
                {/* Header */}
                <div className="mb-4">
                  <div className="flex items-start justify-between gap-4">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{modalidad.nombre}</h3>
                    <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${modalidad.activa ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'}`}>
                      {modalidad.activa ? '✓ Activa' : '✗ Inactiva'}
                    </span>
                  </div>
                </div>

                {/* Body */}
                <div className="mb-6">
                  <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">{modalidad.descripcion}</p>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Creada: {new Date(modalidad.creada_en).toLocaleDateString()}</div>
                </div>

                {/* Footer: acción principal + secundarias */}
                <div className="mt-auto pt-4 border-t border-gray-200/60 dark:border-gray-700/50">
                  <div className="flex flex-col gap-3">
                    <div className="flex-shrink-0">
                      <button
                        onClick={() => navigate(`/modalidades/${modalidad.id}`)}
                        className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-3.5 py-1.5 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40"
                      >
                        <ArrowRight className="h-4 w-4" />
                        Abrir modalidad
                      </button>
                    </div>

                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => openModal(modalidad)}
                        className="inline-flex items-center gap-2 rounded-lg border border-blue-500/15 bg-blue-500/10 px-3 py-1.5 text-sm font-medium text-blue-700 transition hover:border-blue-500/25 hover:bg-blue-500/15 hover:text-blue-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/20 dark:border-blue-400/15 dark:bg-blue-400/10 dark:text-blue-300 dark:hover:bg-blue-400/15 dark:hover:text-blue-200"
                      >
                        <PencilLine className="h-4 w-4" />
                        Editar
                      </button>

                      <button
                        onClick={() => handleDelete(modalidad.id)}
                        className="inline-flex items-center gap-2 rounded-lg border border-rose-500/15 bg-rose-500/10 px-3 py-1.5 text-sm font-medium text-rose-700 transition hover:border-rose-500/25 hover:bg-rose-500/15 hover:text-rose-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rose-500/20 dark:border-rose-400/15 dark:bg-rose-400/10 dark:text-rose-300 dark:hover:bg-rose-400/15 dark:hover:text-rose-200"
                      >
                        <Trash2 className="h-4 w-4" />
                        Eliminar
                      </button>
                    </div>
                  </div>
                </div>
              </SectionCard>
            ))
          ) : (
            <div className="col-span-full text-center py-8 text-gray-500 dark:text-gray-400">
              No hay modalidades registradas
            </div>
          )}
        </div>
      )}

      {/* Modal */}
      <Modal
        isOpen={showModal}
        title={editingId ? 'Editar Modalidad' : 'Nueva Modalidad'}
        onClose={closeModal}
        onSubmit={handleSubmit}
        submitText={editingId ? 'Actualizar' : 'Crear'}
        sizeClass="max-w-3xl"
      >
        <div className="space-y-6">
          <SectionCard title="Información principal" description="Nombre y descripción de la modalidad.">
            <div className="grid grid-cols-1 gap-4">
              <FormField
                label="Nombre *"
                name="nombre"
                type="text"
                value={formData.nombre}
                onChange={handleInputChange}
                placeholder="Ej: Tesis"
                required
              />

              <FormField
                label="Descripción"
                name="descripcion"
                type="textarea"
                value={formData.descripcion}
                onChange={handleInputChange}
                placeholder="Describe esta modalidad..."
              />
            </div>
          </SectionCard>

          <SectionCard title="Estado" description="Control de visibilidad de la modalidad.">
            <div className="flex items-center rounded-xl border border-gray-200 bg-white px-4 py-3 dark:border-gray-600 dark:bg-gray-700/60">
              <input
                type="checkbox"
                name="activa"
                checked={formData.activa}
                onChange={handleInputChange}
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500"
              />
              <label className="ml-3 text-sm font-medium text-gray-700 dark:text-gray-300">
                Modalidad activa
              </label>
            </div>
          </SectionCard>
        </div>
      </Modal>
    </div>
  );
};

export default Modalidades;
