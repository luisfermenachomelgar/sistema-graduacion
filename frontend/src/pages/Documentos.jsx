/**
 * Documentos Page - CRUD Moderno
 * Manage application documents with modern UI and full CRUD
 */

import { useState, useEffect } from 'react';
import useAuth from '../hooks/useAuth';
import DataTable from '../components/DataTable';
import api from '../api/api';
import { API_CONFIG } from '../constants/api';
import Modal from '../components/Modal';
import FormField from '../components/FormField';
import Alert from '../components/Alert';
import { PageHeader, SectionCard } from '../components';
import { useModal } from '../hooks/useModal';
import { useCrud } from '../hooks/useCrud';
import { Plus, AlertCircle, X, Upload, Trash2 } from 'lucide-react';

const INITIAL_FORM_DATA = {
  postulacion: '',
  tipo_documento: '',
  estado: 'pendiente',
  comentario_revision: '',
};

const BLOCKED_STAGE_ERROR_MESSAGE = 'Solo es posible subir documentos durante la etapa de Registro. Las actas de evaluación son registradas por la administración de la Carrera.';

const ESTADO_DOCUMENTO_OPTIONS = [
  { label: 'Pendiente', value: 'pendiente' },
  { label: 'Aprobado', value: 'aprobado' },
  { label: 'Rechazado', value: 'rechazado' },
];

// Documentos que NO debe ver el estudiante
const RESTRICTED_DOCUMENT_KEYWORDS = [
  'acta',
  'dictamen',
  'resolución',
  'dictámen', // variante sin tilde
  'acta de',
  'evaluación',
  'calificación final',
];

// Función para determinar si un documento es permitido para estudiante
const isDocumentAllowedForStudent = (documentName) => {
  if (!documentName || typeof documentName !== 'string') return false;
  
  const lowerName = documentName.toLowerCase().trim();
  
  // Excluir documentos internos de la universidad
  return !RESTRICTED_DOCUMENT_KEYWORDS.some((keyword) =>
    lowerName.includes(keyword.toLowerCase())
  );
};

const normalizeErrorMessage = (message) => {
  if (typeof message !== 'string') return message;
  return message.replace(/^detail:\s*/i, '').trim();
};

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
  const { user } = useAuth();

  const resolveRole = () => {
    if (user?.role) return user.role;
    if (user?.is_superuser === true) return 'admin';
    return null;
  };

  const effectiveRole = resolveRole();
  const isStudent = effectiveRole === 'estudiante';
  
  const [success, setSuccess] = useState('');
  const [tiposDocumento, setTiposDocumento] = useState([]);
  const [tiposDocumentoFiltrados, setTiposDocumentoFiltrados] = useState([]);
  const [postulaciones, setPostulaciones] = useState([]);
  const [tiposDocumentoPorModalidad, setTiposDocumentoPorModalidad] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [archivoFile, setArchivoFile] = useState(null);
  const [etapaActualNombre, setEtapaActualNombre] = useState('');
  const [etapas, setEtapas] = useState([]);
  
  // Para administradores: mapea tipo_documento_id -> { file, fileName }
  const [selectedDocuments, setSelectedDocuments] = useState({});
  
  // Modal de preview para visualizar PDFs
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  const [previewDocumento, setPreviewDocumento] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [previewExtension, setPreviewExtension] = useState('');
  
  const { isOpen, isEditMode, formData, openModal, closeModal, setFormData } = useModal(
    INITIAL_FORM_DATA
  );

  useEffect(() => {
    fetchDropdownData();
    // Load main table with local loader (no global overlay)
    list({}, { requestConfig: { skipGlobalLoader: true } });
  }, []);

  useEffect(() => {
    // Limpiar estado cuando se cierre el modal
    if (!isOpen) {
      setEtapaActualNombre('');
      setSelectedDocuments({});
    }
  }, [isOpen]);

  // Cuando se abre el modal para crear un nuevo documento, si el usuario
  // es estudiante y solo tiene una postulación, seleccionala automáticamente
  // y carga los tipos de documento correspondientes.
  useEffect(() => {
    const autoSelectSinglePostulacion = async () => {
      if (!isOpen) return;
      if (isEditMode) return; // No tocar cuando estamos editando
      if (!isStudent) return;
      if (!postulaciones || postulaciones.length !== 1) return;

      const single = postulaciones[0];
      if (single && formData.postulacion !== single.id) {
        setFormData((prev) => ({ ...prev, postulacion: single.id }));

        const modalidadId = single?.modalidad?.id || single?.modalidad;
        const etapaId = single?.etapa_actual || undefined;

        if (etapaId) {
          const etapaSeleccionada = etapas.find((e) => e.id === etapaId);
          setEtapaActualNombre(etapaSeleccionada?.nombre || '');
        } else {
          setEtapaActualNombre('');
        }

        if (modalidadId) {
          await getTiposDocumentoFiltrados(modalidadId, etapaId);
        }
      }
    };

    autoSelectSinglePostulacion();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, postulaciones, isStudent, isEditMode, etapas]);

  const fetchDropdownData = async () => {
    try {
      const [tiposRes, postRes, etapaRes] = await Promise.all([
        api.getAll(API_CONFIG.ENDPOINTS.TIPOS_DOCUMENTO, {}, { skipGlobalLoader: true }),
        api.getAll(API_CONFIG.ENDPOINTS.POSTULACIONES, {}, { skipGlobalLoader: true }),
        api.getAll(API_CONFIG.ENDPOINTS.ETAPAS, {}, { skipGlobalLoader: true }),
      ]);

      if (tiposRes.success) {
        const tiposData = Array.isArray(tiposRes.data) ? tiposRes.data : tiposRes.data.results || [];
        setTiposDocumento(tiposData);
      }
      if (postRes.success) {
        const postsData = Array.isArray(postRes.data) ? postRes.data : postRes.data.results || [];
        setPostulaciones(postsData);
      }
      if (etapaRes.success) {
        const etapasData = Array.isArray(etapaRes.data) ? etapaRes.data : etapaRes.data.results || [];
        setEtapas(etapasData);
      }
    } catch (err) {
      console.error('Error loading dropdown data:', err);
    }
  };

  const fetchTiposDocumentoPorModalidad = async (modalidadId, etapaId = null) => {
    if (!modalidadId) {
      return [];
    }

    const cacheKey = `${modalidadId}:${etapaId || 'null'}`;
    if (tiposDocumentoPorModalidad[cacheKey]) {
      return tiposDocumentoPorModalidad[cacheKey];
    }

    try {
      const url = API_CONFIG.ENDPOINTS.MODALIDAD_TIPOS_DOCUMENTO(modalidadId);
      const params = etapaId ? { etapa: etapaId } : {};
      const result = await api.getAll(url, params, { skipGlobalLoader: true });

      if (result.success) {
        const data = Array.isArray(result.data) ? result.data : result.data.results || [];
        setTiposDocumentoPorModalidad((current) => ({
          ...current,
          [cacheKey]: data,
        }));
        return data;
      }

      return [];
    } catch (err) {
      console.error('Error fetching modalidad tipos documento:', err);
      return [];
    }
  };

  const getTiposDocumentoFiltrados = async (modalidadId, etapaId = null) => {
    const modalidadTipos = await fetchTiposDocumentoPorModalidad(modalidadId, etapaId);
    const deduplicated = [];
    const seenDocumentos = new Set();

    modalidadTipos.forEach((item) => {
      const tipoDocumento = item.tipo_documento;
      if (!tipoDocumento || seenDocumentos.has(tipoDocumento.id)) return;
      seenDocumentos.add(tipoDocumento.id);
      deduplicated.push(item);
    });

    const filtered = deduplicated.map((item) => ({
      id: item.tipo_documento.id,
      label: item.tipo_documento.nombre,
      obligatorio: item.obligatorio,
      etapa_nombre: item.etapa_nombre,
    }));
    setTiposDocumentoFiltrados(filtered);
    return filtered;
  };

  const handleInputChange = async (e) => {
    const { name, value, files } = e.target;
    
    // Manejo de archivos para administradores (múltiples documentos)
    if (name.startsWith('archivo_')) {
      const tipoDocId = parseInt(name.split('_')[1], 10);
      const file = files?.[0] || null;
      
      if (file) {
        // Validar extensión permitida
        const extensionesPermitidas = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'];
        const extension = file.name.split('.').pop().toLowerCase();
        if (!extensionesPermitidas.includes(extension)) {
          setError(`Extensión no permitida. Use: ${extensionesPermitidas.join(', ')}`);
          return;
        }
        // Validar tamaño máximo (25MB)
        const MAX_SIZE = 25 * 1024 * 1024;
        if (file.size > MAX_SIZE) {
          setError('El archivo no debe exceder 25MB');
          return;
        }
        
        setSelectedDocuments((prev) => ({
          ...prev,
          [tipoDocId]: { file, fileName: file.name },
        }));
      } else {
        // Si se limpia el archivo, eliminar del objeto
        setSelectedDocuments((prev) => {
          const updated = { ...prev };
          delete updated[tipoDocId];
          return updated;
        });
      }
      setError('');
      return;
    }
    
    // Manejo de archivo único para estudiantes
    if (name === 'archivo') {
      const file = files?.[0] || null;
      if (file) {
        // Validar extensión permitida
        const extensionesPermitidas = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'];
        const extension = file.name.split('.').pop().toLowerCase();
        if (!extensionesPermitidas.includes(extension)) {
          setError(`Extensión no permitida. Use: ${extensionesPermitidas.join(', ')}`);
          return;
        }
        // Validar tamaño máximo (25MB)
        const MAX_SIZE = 25 * 1024 * 1024;
        if (file.size > MAX_SIZE) {
          setError('El archivo no debe exceder 25MB');
          return;
        }
      }
      setArchivoFile(file);
      return;
    }

    const numericFields = ['postulacion', 'tipo_documento'];
    const newValue = numericFields.includes(name) ? (value ? parseInt(value, 10) : '') : value;
    const newFormData = {
      ...formData,
      [name]: newValue,
    };

    setFormData(newFormData);

    if (name === 'postulacion') {
      if (!newValue) {
        setTiposDocumentoFiltrados([]);
        setEtapaActualNombre('');
        setFormData((prev) => ({
          ...prev,
          tipo_documento: '',
        }));
        setSelectedDocuments({});
        return;
      }

      const selectedPostulacion = postulaciones.find((p) => p.id === newValue);
      const modalidadId = selectedPostulacion?.modalidad?.id || selectedPostulacion?.modalidad;
      const etapaId = selectedPostulacion?.etapa_actual || undefined;

      // Extraer y mostrar el nombre de la etapa actual
      if (etapaId) {
        const etapaSeleccionada = etapas.find((e) => e.id === etapaId);
        setEtapaActualNombre(etapaSeleccionada?.nombre || '');
      } else {
        setEtapaActualNombre('');
      }

      if (modalidadId) {
        await getTiposDocumentoFiltrados(modalidadId, etapaId);
        setFormData((prev) => ({
          ...prev,
          tipo_documento: '',
        }));
        setSelectedDocuments({});
      } else {
        setTiposDocumentoFiltrados([]);
        setFormData((prev) => ({
          ...prev,
          tipo_documento: '',
        }));
        setSelectedDocuments({});
      }
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError('');
    setSuccess('');

    try {
      // Para administradores y estudiantes: crear múltiples documentos
      if (Object.keys(selectedDocuments).length > 0) {
        const postulacionId = formData.postulacion;
        if (!postulacionId) {
          setError('Debes seleccionar una postulación');
          setIsSubmitting(false);
          return;
        }

        const documentos = Object.entries(selectedDocuments).map(([tipoDocId, data]) => ({
          tipoDocId: parseInt(tipoDocId, 10),
          file: data.file,
        }));

        if (documentos.length === 0) {
          setError('Debes seleccionar al menos un archivo');
          setIsSubmitting(false);
          return;
        }

        let successCount = 0;
        const errors = [];

        // Enviar un request por cada documento
        for (const doc of documentos) {
          try {
            const payload = new FormData();
            payload.append('postulacion', postulacionId);
            payload.append('tipo_documento', doc.tipoDocId);
            payload.append('estado', formData.estado || 'pendiente');
            payload.append('archivo', doc.file);
            if (formData.comentario_revision) {
              payload.append('comentario_revision', formData.comentario_revision);
            }

            const endpoint = API_CONFIG.ENDPOINTS.DOCUMENTOS;
            const result = await api.create(endpoint, payload, { suppressErrorToast: true });

            if (result.success) {
              successCount++;
            } else {
              errors.push(normalizeErrorMessage(result.error || 'Error desconocido'));
            }
          } catch (err) {
            errors.push(normalizeErrorMessage(err.message || 'Error en la creación'));
          }
        }

        if (successCount > 0) {
          setSuccess(`${successCount} documento(s) creado(s) exitosamente${errors.length > 0 ? ` (${errors.length} error(es))` : ''}`);
          await refresh({});
          setSelectedDocuments({});
          setArchivoFile(null);
          closeModal();
        }

        if (errors.length > 0) {
          if (successCount === 0) {
            setError(errors[0]);
          }
        }

        setIsSubmitting(false);
        return;
      }

      // Para estudiantes: crear un único documento (comportamiento original)
      const endpoint = isEditMode
        ? API_CONFIG.ENDPOINTS.DOCUMENTO_DETAIL(formData.id)
        : API_CONFIG.ENDPOINTS.DOCUMENTOS;

      let result;
      const suppressToast = isStudent;

      if (archivoFile) {
        // Con archivo, usar FormData a través de api.js para que gestione headers correctamente
        const payload = new FormData();
        payload.append('postulacion', formData.postulacion);
        payload.append('tipo_documento', formData.tipo_documento);
        payload.append('estado', formData.estado);
        payload.append('archivo', archivoFile);
        if (formData.comentario_revision) {
          payload.append('comentario_revision', formData.comentario_revision);
        }

        result = isEditMode
          ? await api.update(endpoint, payload, { suppressErrorToast: suppressToast })
          : await api.create(endpoint, payload, { suppressErrorToast: suppressToast });
      } else {
        // Sin archivo, usar JSON
        const payload = {
          postulacion: formData.postulacion,
          tipo_documento: formData.tipo_documento,
          estado: formData.estado,
          comentario_revision: formData.comentario_revision,
        };

        result = isEditMode
          ? await patch(endpoint, payload, { suppressErrorToast: suppressToast })
          : await create(payload, { suppressErrorToast: suppressToast });
      }

      if (result.success) {
        setSuccess(isEditMode ? 'Documento actualizado exitosamente' : 'Documento creado exitosamente');
        await refresh({});
        setArchivoFile(null);
        closeModal();
      } else {
        const errorMessage = normalizeErrorMessage(result.error || 'Error en la operación');
        setError(errorMessage);

        const isBlockedStageError = isStudent && typeof errorMessage === 'string' && errorMessage.includes(BLOCKED_STAGE_ERROR_MESSAGE);

        if (isBlockedStageError) {
          setArchivoFile(null);
          closeModal();
        }
      }
    } catch (err) {
      setError(normalizeErrorMessage(err.message || 'Error en la operación'));
    } finally {
      setIsSubmitting(false);
    }
  };

  useEffect(() => {
    const loadFilteredTipos = async () => {
      if (!formData.postulacion) {
        setTiposDocumentoFiltrados([]);
        setEtapaActualNombre('');
        return;
      }

      const selectedPostulacion = postulaciones.find((p) => p.id === formData.postulacion);
      const modalidadId = selectedPostulacion?.modalidad?.id || selectedPostulacion?.modalidad;
      const etapaId = selectedPostulacion?.etapa_actual || undefined;

      // Extraer y mostrar el nombre de la etapa actual
      if (etapaId) {
        const etapaSeleccionada = etapas.find((e) => e.id === etapaId);
        setEtapaActualNombre(etapaSeleccionada?.nombre || '');
      } else {
        setEtapaActualNombre('');
      }

      if (modalidadId) {
        await getTiposDocumentoFiltrados(modalidadId, etapaId);
      }
    };

    loadFilteredTipos();
  }, [formData.postulacion, postulaciones, etapas]);

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
        setError(normalizeErrorMessage(result.error || 'Error al eliminar'));
      }
    } catch (err) {
      setError(normalizeErrorMessage('Error al eliminar documento'));
    }
  };

  const handleView = (documento) => {
    const archivoUrl = documento?.archivo_url;
    const previewPdfUrl = documento?.preview_pdf_url;
    const chosenUrl = previewPdfUrl || archivoUrl;
    if (!chosenUrl) return;

    const extension = chosenUrl.split('.').pop().toLowerCase();
    const urlCompleta = new URL(chosenUrl, API_CONFIG.PUBLIC_SERVER_URL).toString();

    setPreviewDocumento(documento);
    setPreviewUrl(urlCompleta);
    setPreviewExtension(extension);
    setIsPreviewOpen(true);
  };

  const closePreview = () => {
    setIsPreviewOpen(false);
    setPreviewDocumento(null);
    setPreviewUrl('');
    setPreviewExtension('');
  };

  // Render preview content for different file types
  const renderPreviewContent = () => {
    if (!previewUrl) {
      return (
        <div className="flex h-96 items-center justify-center">
          <p className="text-gray-500 dark:text-gray-400">Cargando documento...</p>
        </div>
      );
    }

    const imgExt = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'];
    const textExt = ['txt', 'csv', 'md', 'json', 'xml'];

    if (['pdf'].includes(previewExtension)) {
      return (
        <iframe
          title="Vista previa del documento"
          src={previewUrl}
          className="h-[72vh] w-full bg-neutral-100 dark:bg-neutral-950"
        />
      );
    }

    if (imgExt.includes(previewExtension)) {
      return (
        <div className="flex h-[72vh] w-full items-center justify-center bg-neutral-100 dark:bg-neutral-950 p-4">
          <img src={previewUrl} alt={previewDocumento?.tipo_documento_nombre || 'Documento'} className="max-h-full max-w-full object-contain" />
        </div>
      );
    }

    if (textExt.includes(previewExtension)) {
      return (
        <iframe
          title="Vista previa del documento"
          src={previewUrl}
          className="h-[72vh] w-full bg-neutral-100 dark:bg-neutral-950"
        />
      );
    }

    return (
      <div className="flex min-h-[72vh] flex-col items-center justify-center gap-4 p-8 text-center">
        <p className="text-lg font-semibold text-gray-900 dark:text-white">Vista previa no disponible para este formato.</p>
        <p className="text-sm text-gray-600 dark:text-gray-400">Puedes descargar el archivo o abrirlo en una aplicación de escritorio para verlo correctamente.</p>
        <a
          href={previewUrl}
          target="_blank"
          rel="noreferrer"
          className="rounded-lg bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-700"
        >
          Abrir archivo
        </a>
      </div>
    );
  };

  const getEstadoBadge = (estado) => {
    const colors = {
      pendiente: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
      aprobado: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
      rechazado: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    };
    return colors[estado] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400';
  };

  const getPostulacionLabel = (postulacion) => {
    const postulanteNombre = postulacion.postulante
      ? `${postulacion.postulante.nombre || ''} ${postulacion.postulante.apellido || ''}`.trim()
      : postulacion.postulante_nombre || '';
    const modalidadNombre = postulacion.modalidad_nombre || postulacion.modalidad?.nombre || '';

    const parts = [postulanteNombre, modalidadNombre].filter(Boolean);

    if (parts.length > 0) {
      return parts.join(' — ');
    }

    return 'Postulación sin datos';
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
      render: (value, row) => {
        const postulanteNombre = row.postulante_nombre || '-';
        const modalidadNombre = row.modalidad_nombre || '-';
        return (
          <div className="flex flex-col">
            <span className="font-medium text-gray-900 dark:text-gray-100">{postulanteNombre}</span>
            <span className="text-xs text-gray-600 dark:text-gray-400">{modalidadNombre}</span>
          </div>
        );
      },
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
      render: (value) => {
        const text = value?.toString().trim();
        return (
          <span className="max-w-xs whitespace-normal break-words text-sm text-gray-700 dark:text-gray-300">
            {text || '-'}
          </span>
        );
      },
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Documentos"
        description="Administra los documentos de postulación"
        action={(
          <button
            onClick={() => {
              setFormData(INITIAL_FORM_DATA);
              setArchivoFile(null);
              openModal();
            }}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-2 font-medium text-white shadow transition hover:bg-blue-700"
          >
            <Plus className="h-5 w-5" />
            Nuevo Documento
          </button>
        )}
      />

        {/* Alertas */}
        {error && <Alert type="error" message={error} onClose={() => setError('')} autoClose={false} />}
        {success && <Alert type="success" message={success} onClose={() => setSuccess('')} />}

        {/* Aviso si no hay documentos tipos */}
        {tiposDocumento.length === 0 && !loading && (
          <div className="mb-6 flex items-start gap-3 rounded-2xl border border-blue-200 bg-blue-50 p-4 text-blue-800 dark:border-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <p>Por favor, crea tipos de documento antes de agregar documentos.</p>
          </div>
        )}

        {/* Tabla */}
        {loading ? (
          <div className="flex h-96 items-center justify-center rounded-2xl border border-gray-200/80 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800">
            <div className="text-center">
              <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-b-2 border-blue-500" />
              <p className="text-gray-500 dark:text-gray-400">Cargando documentos...</p>
            </div>
          </div>
        ) : (
          <DataTable
            data={documentos || []}
            columns={columns}
            pageSize={10}
            onView={!isStudent ? handleView : undefined}
            onEdit={!isStudent ? (row) => {
              setArchivoFile(null);
              openModal(row);
            } : undefined}
            onDelete={!isStudent ? handleDelete : undefined}
          />
        )}

        {/* Modal */}
        <Modal
          isOpen={isOpen}
          title={isEditMode ? 'Editar Documento' : 'Nuevo Documento'}
          onSubmit={handleSubmit}
          onClose={closeModal}
          submitText={isEditMode ? 'Actualizar' : 'Crear'}
          isLoading={isSubmitting}
          sizeClass="max-w-4xl"
        >
          <div className="space-y-6">
            <SectionCard
              title="Información principal"
              description="Postulación asociada, tipo de documento y estado de revisión."
            >
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-5">
                {isStudent && postulaciones.length === 1 ? (
                  <>
                    <FormField
                      label="Postulación *"
                      name="postulacion_display"
                      type="text"
                      value={getPostulacionLabel(postulaciones[0])}
                      readOnly
                      className="md:col-span-1"
                    />
                  </>
                ) : (
                  <FormField
                    label="Postulación *"
                    name="postulacion"
                    type="select"
                    value={formData.postulacion}
                    onChange={handleInputChange}
                    options={postulaciones.map((p) => ({
                      id: p.id,
                      label: getPostulacionLabel(p),
                    }))}
                    required
                    className="md:col-span-1"
                  />
                )}

                <FormField
                  label="Etapa Actual"
                  name="etapa_actual"
                  type="text"
                  value={etapaActualNombre}
                  readOnly={true}
                  placeholder="Sincronizada automáticamente"
                  helperText="Etapa sincronizada desde la postulación seleccionada"
                  className="md:col-span-1"
                />

                {/* En modo edición: mostrar select tradicional */}
                {isEditMode && (
                  <>
                    <FormField
                      label="Tipo de Documento *"
                      name="tipo_documento"
                      type="select"
                      value={formData.tipo_documento}
                      onChange={handleInputChange}
                      options={(formData.postulacion ? tiposDocumentoFiltrados : []).map((t) => ({
                        id: t.id,
                        label: t.label || t.nombre,
                      }))}
                      required
                      className="md:col-span-1"
                    />
                    {formData.postulacion && tiposDocumentoFiltrados.length === 0 && (
                      <p className="text-sm text-yellow-700 dark:text-yellow-300 md:col-span-1">
                        No hay tipos de documento configurados para la modalidad y etapa actual de esta postulación.
                      </p>
                    )}

                    {!isStudent && (
                      <FormField
                        label="Estado"
                        name="estado"
                        type="select"
                        value={formData.estado}
                        onChange={handleInputChange}
                        options={ESTADO_DOCUMENTO_OPTIONS}
                        className="md:col-span-2"
                      />
                    )}
                  </>
                )}

                {/* Para administradores en modo creación: mostrar Estado */}
                {!isStudent && !isEditMode && (
                  <>
                    <FormField
                      label="Estado"
                      name="estado"
                      type="select"
                      value={formData.estado}
                      onChange={handleInputChange}
                      options={ESTADO_DOCUMENTO_OPTIONS}
                      className="md:col-span-2"
                    />
                  </>
                )}
              </div>
            </SectionCard>

            {/* Para administradores y estudiantes: lista de documentos con selectores de archivo */}
            {!isEditMode && formData.postulacion && tiposDocumentoFiltrados.length > 0 && (
              <SectionCard
                title="Documentos a cargar"
                description="Selecciona los archivos que deseas cargar. Solo se guardarán los documentos que tengan archivo."
              >
                <div className="space-y-3">
                  {tiposDocumentoFiltrados
                    .filter((tipoDoc) =>
                      isStudent ? isDocumentAllowedForStudent(tipoDoc.label || tipoDoc.nombre) : true
                    )
                    .map((tipoDoc) => (
                    <div
                      key={tipoDoc.id}
                      className="flex items-center gap-4 rounded-lg border border-gray-300 bg-gray-50 p-4 transition dark:border-gray-600 dark:bg-gray-800"
                    >
                      {/* Nombre del documento */}
                      <div className="min-w-0 flex-1">
                        <p className="font-medium text-gray-900 dark:text-white">
                          {tipoDoc.label || tipoDoc.nombre}
                        </p>
                        {selectedDocuments[tipoDoc.id]?.fileName && (
                          <p className="text-xs text-green-600 dark:text-green-400">
                            ✓ {selectedDocuments[tipoDoc.id].fileName}
                          </p>
                        )}
                      </div>

                      {/* Selector de archivo */}
                      <div className="flex gap-2">
                        <label className="relative inline-flex cursor-pointer items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700">
                          <Upload className="h-4 w-4" />
                          <span>Seleccionar</span>
                          <input
                            type="file"
                            name={`archivo_${tipoDoc.id}`}
                            onChange={handleInputChange}
                            accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png"
                            className="hidden"
                          />
                        </label>

                        {/* Botón para quitar/cambiar */}
                        {selectedDocuments[tipoDoc.id] && (
                          <button
                            type="button"
                            onClick={() => {
                              setSelectedDocuments((prev) => {
                                const updated = { ...prev };
                                delete updated[tipoDoc.id];
                                return updated;
                              });
                            }}
                            className="inline-flex items-center gap-2 rounded-lg border border-red-300 bg-red-50 px-3 py-2 text-sm font-medium text-red-700 transition hover:bg-red-100 dark:border-red-700 dark:bg-red-900/20 dark:text-red-400 dark:hover:bg-red-900/40"
                          >
                            <Trash2 className="h-4 w-4" />
                            <span>Quitar</span>
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                {Object.keys(selectedDocuments).length === 0 && (
                  <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-800 dark:border-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300">
                    Selecciona al menos un archivo para guardar.
                  </div>
                )}
              </SectionCard>
            )}

            {!isEditMode && isStudent && formData.postulacion && tiposDocumentoFiltrados.length > 0 && 
              tiposDocumentoFiltrados.filter((d) => isDocumentAllowedForStudent(d.label || d.nombre)).length === 0 && (
              <div className="rounded-lg border border-blue-200 bg-blue-50 p-4 text-sm text-blue-800 dark:border-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
                No tienes documentos que entregar en esta etapa. Los documentos internos de la universidad son registrados por la administración.
              </div>
            )}

            {!isEditMode && formData.postulacion && tiposDocumentoFiltrados.length === 0 && (
              <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-800 dark:border-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300">
                No hay tipos de documento configurados para la modalidad y etapa actual de esta postulación.
              </div>
            )}

            {/* Para modo edición: mostrar sección de revisión y archivo */}
            {isEditMode && (
              <SectionCard
                title="Revisión y archivo"
                description="Comentario opcional para revisión y carga del archivo físico."
              >
                <div className="grid grid-cols-1 gap-4">
                  <FormField
                    label="Comentario de Revisión"
                    name="comentario_revision"
                    type="textarea"
                    value={formData.comentario_revision || ''}
                    onChange={handleInputChange}
                    placeholder="Agregar comentarios si es necesario..."
                  />

                  <div>
                    <label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Archivo de Documento *
                    </label>
                    <input
                      type="file"
                      name="archivo"
                      onChange={handleInputChange}
                      required={!isEditMode}
                      accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png"
                      className="w-full rounded-xl border border-gray-300 bg-white px-4 py-2.5 text-gray-900 transition focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200"
                    />
                    {archivoFile && (
                      <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
                        Archivo seleccionado: {archivoFile.name}
                      </p>
                    )}
                  </div>
                </div>
              </SectionCard>
            )}
          </div>
        </Modal>

        {/* Modal de Preview de PDF */}
        {isPreviewOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <div className="relative w-full max-w-5xl rounded-3xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-900">
              {/* Header */}
              <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4 dark:border-gray-700">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Vista previa: {previewDocumento?.tipo_documento_nombre || 'Documento'}
                </h2>
                <button
                  onClick={closePreview}
                  className="rounded-lg p-1 text-gray-500 transition hover:bg-gray-100 hover:text-gray-900 dark:hover:bg-gray-800 dark:hover:text-white"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>

              {/* Content */}
              <div className="relative overflow-hidden rounded-b-3xl border-t border-gray-200 dark:border-gray-700">
                {previewUrl ? (
                  ['pdf'].includes(previewExtension) ? (
                    <iframe
                      title="Vista previa del documento"
                      src={previewUrl}
                      className="h-[72vh] w-full bg-neutral-100 dark:bg-neutral-950"
                    />
                  ) : (
                    <div className="flex min-h-[72vh] flex-col items-center justify-center gap-4 p-8 text-center">
                      <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        Vista previa no disponible para este formato.
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Puedes descargar el archivo para verlo en tu aplicación de escritorio.
                      </p>
                      <a
                        href={previewUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="rounded-lg bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-700"
                      >
                        Abrir archivo
                      </a>
                    </div>
                  )
                ) : (
                  <div className="flex h-96 items-center justify-center">
                    <p className="text-gray-500 dark:text-gray-400">Cargando documento...</p>
                  </div>
                )}
              </div>

              {/* Footer */}
              <div className="flex justify-end gap-3 border-t border-gray-200 px-6 py-4 dark:border-gray-700">
                <button
                  onClick={closePreview}
                  className="rounded-lg border border-gray-300 bg-white px-4 py-2 font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}
    </div>
  );
};

export default Documentos;
