/**
 * Documentos Page - CRUD Moderno
 * Manage application documents with modern UI and full CRUD
 */

import { useState, useEffect } from 'react';
import DataTable from '../components/DataTable';
import TableSkeleton from '../components/TableSkeleton';
import api from '../api/api';
import { API_CONFIG } from '../constants/api';
import Modal from '../components/Modal';
import FormField from '../components/FormField';
import Alert from '../components/Alert';
import { useModal } from '../hooks/useModal';
import { useCrud } from '../hooks/useCrud';
import { Plus, AlertCircle } from 'lucide-react';
import axiosInstance from '../api/axios';

const INITIAL_FORM_DATA = {
  postulacion: '',
  tipo_documento: '',
  estado: 'pendiente',
  comentario_revision: '',
};

const ESTADO_DOCUMENTO_OPTIONS = [
  { label: 'Pendiente', value: 'pendiente' },
  { label: 'Aprobado', value: 'aprobado' },
  { label: 'Rechazado', value: 'rechazado' },
];

const Documentos = () => {
  const {
    data: documentos,
    loading,
    error,
    setError,
    list,
    refresh,
    create,
    patch,
    remove,
  } = useCrud(API_CONFIG.ENDPOINTS.DOCUMENTOS);
  
  const [success, setSuccess] = useState('');
  const [tiposDocumento, setTiposDocumento] = useState([]);
  const [postulaciones, setPostulaciones] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [archivoFile, setArchivoFile] = useState(null);
  const { isOpen, isEditMode, formData, openModal, closeModal, setFormData } = useModal(
    INITIAL_FORM_DATA
  );

  useEffect(() => {
    fetchDropdownData();
    // Load main table with local loader (no global overlay)
    list({}, { requestConfig: { skipGlobalLoader: true } });
  }, []);

  const fetchDropdownData = async () => {
    try {
      const [tiposRes, postRes] = await Promise.all([
        api.getAll(API_CONFIG.ENDPOINTS.TIPOS_DOCUMENTO, {}, { skipGlobalLoader: true }),
        api.getAll(API_CONFIG.ENDPOINTS.POSTULACIONES, {}, { skipGlobalLoader: true }),
      ]);

      if (tiposRes.success) {
        const tiposData = Array.isArray(tiposRes.data) ? tiposRes.data : tiposRes.data.results || [];
        setTiposDocumento(tiposData);
      }
      if (postRes.success) {
        const postsData = Array.isArray(postRes.data) ? postRes.data : postRes.data.results || [];
        setPostulaciones(postsData);
      }
    } catch (err) {
      console.error('Error loading dropdown data:', err);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, files } = e.target;
    if (name === 'archivo') {
      const file = files?.[0] || null;
      if (file) {
        // Validar extensión permitida
        const extensionesPermitidas = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'];
        const extension = file.name.split('.').pop().toLowerCase();
        if (!extensionesPermitidas.includes(extension)) {
          setError(`Extensión no permitida. Use: ${extensionesPermitidas.join(', ')}`);
          return;
        }
        // Validar tamaño máximo (5MB)
        const MAX_SIZE = 5 * 1024 * 1024;
        if (file.size > MAX_SIZE) {
          setError('El archivo no debe exceder 5MB');
          return;
        }
      }
      setArchivoFile(file);
      return;
    }
    setFormData({
      ...formData,
      [name]: ['postulacion', 'tipo_documento'].includes(name) ? parseInt(value) : value,
    });
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError('');
    setSuccess('');

    try {
      const endpoint = isEditMode
        ? API_CONFIG.ENDPOINTS.DOCUMENTO_DETAIL(formData.id)
        : API_CONFIG.ENDPOINTS.DOCUMENTOS;

      let result;

      if (archivoFile) {
        // Con archivo, usar FormData
        const payload = new FormData();
        payload.append('postulacion', formData.postulacion);
        payload.append('tipo_documento', formData.tipo_documento);
        payload.append('estado', formData.estado);
        payload.append('archivo', archivoFile);
        if (formData.comentario_revision) {
          payload.append('comentario_revision', formData.comentario_revision);
        }

        const method = isEditMode ? 'put' : 'post';
        try {
          const response = await axiosInstance[method](endpoint, payload, {
            headers: { 'Content-Type': 'multipart/form-data' },
          });
          result = { success: true, data: response.data };
        } catch (error) {
          result = { success: false, error: error.response?.data?.error || error.response?.data?.detail || 'Error en la operación' };
        }
      } else {
        // Sin archivo, usar JSON
        const payload = {
          postulacion: formData.postulacion,
          tipo_documento: formData.tipo_documento,
          estado: formData.estado,
          comentario_revision: formData.comentario_revision,
        };

        result = isEditMode
          ? await patch(endpoint, payload)
          : await create(payload);
      }

      if (result.success) {
        setSuccess(isEditMode ? 'Documento actualizado exitosamente' : 'Documento creado exitosamente');
        await refresh({});
        setArchivoFile(null);
        closeModal();
      } else {
        setError(result.error || 'Error en la operación');
      }
    } catch (err) {
      setError(err.message || 'Error en la operación');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (documento) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar este documento?')) return;
    
    setError('');
    setSuccess('');

    try {
      const result = await remove(API_CONFIG.ENDPOINTS.DOCUMENTO_DETAIL(documento.id));
      if (result.success) {
        setSuccess('Documento eliminado exitosamente');
        await refresh({});
      } else {
        setError(result.error || 'Error al eliminar');
      }
    } catch (err) {
      setError('Error al eliminar documento');
    }
  };

  const getEstadoBadge = (estado) => {
    const colors = {
      pendiente: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
      aprobado: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
      rechazado: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    };
    return colors[estado] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400';
  };

  const columns = [
    {
      key: 'tipo_documento_nombre',
      label: 'Tipo Documento',
      sortable: true,
      render: (value) => value || '-',
    },
    {
      key: 'postulacion',
      label: 'Postulación',
      sortable: true,
      render: (value) => `#${value}`,
    },
    {
      key: 'estado',
      label: 'Estado',
      sortable: true,
      render: (value) => (
        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getEstadoBadge(value)}`}>
          {value}
        </span>
      ),
    },
    {
      key: 'comentario_revision',
      label: 'Comentario',
      sortable: false,
      render: (value) => value ? value.substring(0, 50) + '...' : '-',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Encabezado */}
        <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Documentos
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Administra los documentos de postulación
            </p>
          </div>
          <button
            onClick={() => {
              setFormData(INITIAL_FORM_DATA);
              setArchivoFile(null);
              openModal();
            }}
            className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition font-medium shadow"
          >
            <Plus className="w-5 h-5" />
            Nuevo Documento
          </button>
        </div>

        {/* Alertas */}
        {error && <Alert type="error" message={error} onClose={() => setError('')} autoClose={false} />}
        {success && <Alert type="success" message={success} onClose={() => setSuccess('')} />}

        {/* Aviso si no hay documentos tipos */}
        {tiposDocumento.length === 0 && !loading && (
          <div className="mb-6 p-4 rounded-lg border flex items-start gap-3 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-400">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <p>Por favor, crea tipos de documento antes de agregar documentos.</p>
          </div>
        )}

        {/* Tabla */}
        {loading && (
          <TableSkeleton rows={10} columns={4} />
        )}

        {!loading && (
          <DataTable
            data={documentos || []}
            columns={columns}
            pageSize={10}
            onEdit={(row) => {
              setFormData(row);
              setArchivoFile(null);
              openModal();
            }}
            onDelete={handleDelete}
          />
        )}

        {/* Modal */}
        <Modal
          isOpen={isOpen}
          title={isEditMode ? '✏️ Editar Documento' : '➕ Nuevo Documento'}
          onSubmit={handleSubmit}
          onClose={closeModal}
          submitText={isEditMode ? 'Actualizar' : 'Crear'}
          isLoading={isSubmitting}
        >
          <form className="space-y-4">
            <FormField
              label="Postulación *"
              name="postulacion"
              type="select"
              value={formData.postulacion}
              onChange={handleInputChange}
              options={postulaciones.map((p) => ({
                id: p.id,
                label: `#${p.id} - Postulación`,
              }))}
              required
            />

            <FormField
              label="Tipo de Documento *"
              name="tipo_documento"
              type="select"
              value={formData.tipo_documento}
              onChange={handleInputChange}
              options={tiposDocumento.map((t) => ({
                id: t.id,
                label: t.nombre || t.tipo,
              }))}
              required
            />

            <FormField
              label="Estado"
              name="estado"
              type="select"
              value={formData.estado}
              onChange={handleInputChange}
              options={ESTADO_DOCUMENTO_OPTIONS}
            />

            <FormField
              label="Comentario de Revisión"
              name="comentario_revision"
              type="textarea"
              value={formData.comentario_revision || ''}
              onChange={handleInputChange}
              placeholder="Agregar comentarios si es necesario..."
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Archivo de Documento *
              </label>
              <input
                type="file"
                name="archivo"
                onChange={handleInputChange}
                required
                accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-200 focus:ring-2 focus:ring-blue-500 outline-none transition"
              />
              {archivoFile && (
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  Archivo seleccionado: {archivoFile.name}
                </p>
              )}
            </div>
          </form>
        </Modal>
    </div>
  );
};

export default Documentos;
