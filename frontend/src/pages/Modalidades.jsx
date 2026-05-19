/**
 * Modalidades Page - CRUD Completo
 * Manage graduation modalities
 */

import { useState, useEffect } from 'react';
import { API_CONFIG } from '../constants/api';
import { useCrud } from '../hooks/useCrud';
import Modal from '../components/Modal';
import Alert from '../components/Alert';
import FormField from '../components/FormField';

const Modalidades = () => {
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
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Modalidades</h1>
        <button
          onClick={() => openModal()}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg shadow hover:bg-blue-700 transition font-medium"
        >
          ➕ Nueva Modalidad
        </button>
      </div>

      {error && <Alert type="error" message={error} autoClose={false} />}
      {success && <Alert type="success" message={success} />}

      {!loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {modalidades.length > 0 ? (
            modalidades.map((modalidad) => (
              <div key={modalidad.id} className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 border-l-4 border-blue-600">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="font-bold text-lg text-gray-900 dark:text-white">{modalidad.nombre}</h3>
                  <span className={`text-xs px-2 py-1 rounded ${modalidad.activa ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'}`}>
                    {modalidad.activa ? '✓ Activa' : '✗ Inactiva'}
                  </span>
                </div>
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 min-h-12">{modalidad.descripcion}</p>
                <div className="text-xs text-gray-500 dark:text-gray-400 mb-4">
                  Creada: {new Date(modalidad.creada_en).toLocaleDateString()}
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => openModal(modalidad)}
                    className="flex-1 px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition text-sm font-medium"
                  >
                    ✏️ Editar
                  </button>
                  <button
                    onClick={() => handleDelete(modalidad.id)}
                    className="flex-1 px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition text-sm font-medium"
                  >
                    🗑️ Eliminar
                  </button>
                </div>
              </div>
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
        title={editingId ? '✏️ Editar Modalidad' : '➕ Nueva Modalidad'}
        onClose={closeModal}
        onSubmit={handleSubmit}
        submitText={editingId ? 'Actualizar' : 'Crear'}
      >
        <form className="space-y-4">
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

          <div className="flex items-center">
            <input
              type="checkbox"
              name="activa"
              checked={formData.activa}
              onChange={handleInputChange}
              className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
            />
            <label className="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300">
              Modalidad activa
            </label>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Modalidades;
