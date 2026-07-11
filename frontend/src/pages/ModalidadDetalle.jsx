/**
 * ModalidadDetalle Page
 * Vista de detalle moderna para cada modalidad de graduación
 */

import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axiosInstance from '../api/axios';
import api from '../api/api';
import { API_CONFIG } from '../constants/api';
import useAuth from '../hooks/useAuth';
import { Alert, FormField, Modal, PageHeader, SectionCard } from '../components';
import {
  ArrowLeft,
  CalendarDays,
  CheckCircle2,
  Download,
  Eye,
  FileText,
  Layers3,
  Loader2,
  PencilLine,
  Plus,
  ShieldCheck,
  Sparkles,
  Trash2,
  Upload,
} from 'lucide-react';

const ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'xls', 'xlsx'];

const CATEGORY_OPTIONS = [
  { id: 'General', label: 'General' },
  { id: 'Académico', label: 'Académico' },
  { id: 'Administrativo', label: 'Administrativo' },
  { id: 'Legal', label: 'Legal' },
  { id: 'Técnico', label: 'Técnico' },
];

const EMPTY_FORM = {
  nombre: '',
  descripcion: '',
  categoria: 'General',
  obligatorio: true,
  version: '1.0',
  observaciones: '',
  activo: true,
  archivo_nombre: '',
  archivo_tipo: '',
  archivo_url: '',
};

const formatDate = (value) => {
  if (!value) return 'Sin fecha';

  try {
    return new Intl.DateTimeFormat('es-BO', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(value));
  } catch {
    return value;
  }
};

const formatDateShort = (value) => {
  if (!value) return 'Sin fecha';

  try {
    return new Intl.DateTimeFormat('es-BO', {
      dateStyle: 'medium',
    }).format(new Date(value));
  } catch {
    return value;
  }
};

const extractFileName = (url = '') => {
  if (!url) return '';
  const cleaned = url.split('?')[0];
  return cleaned.split('/').pop() || '';
};

const getFileExtension = (name = '') => {
  const parts = name.split('.');
  return parts.length > 1 ? parts.pop().toLowerCase() : '';
};

const getRequirementFileType = (requirement) => {
  const fileName = requirement?.archivo_nombre || extractFileName(requirement?.archivo_url);
  return (requirement?.archivo_tipo || getFileExtension(fileName)).toLowerCase();
};

const normalizeItems = (payload) => {
  if (Array.isArray(payload)) return payload;
  return payload?.results || [];
};

const ModalidadDetalle = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const effectiveRole = user?.role || (user?.is_superuser ? 'admin' : null);
  const canManage = ['admin'].includes(effectiveRole);
  const isStudent = effectiveRole === 'estudiante';

  const [modalidad, setModalidad] = useState(null);
  const [requirements, setRequirements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  const [editingRequirement, setEditingRequirement] = useState(null);
  const [previewRequirement, setPreviewRequirement] = useState(null);
  const [previewBlobUrl, setPreviewBlobUrl] = useState(null);
  const [previewRendering, setPreviewRendering] = useState(false);
  const [previewRenderError, setPreviewRenderError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [archivoFile, setArchivoFile] = useState(null);
  const [formData, setFormData] = useState(EMPTY_FORM);
  const previewBlobUrlRef = useRef(null);

  const loadDetail = async () => {
    setLoading(true);
    setError('');

    try {
      const [modalidadResult, requisitosResult] = await Promise.all([
        api.getById(API_CONFIG.ENDPOINTS.MODALIDAD_DETAIL(id)),
        api.getAll(API_CONFIG.ENDPOINTS.MODALIDAD_REQUISITOS(id), {}, { skipGlobalLoader: true }),
      ]);

      if (!modalidadResult.success) {
        setError(modalidadResult.error || 'No se pudo cargar la modalidad');
        return;
      }

      setModalidad(modalidadResult.data);

      if (requisitosResult.success) {
        setRequirements(normalizeItems(requisitosResult.data));
      } else {
        setRequirements([]);
        setError(requisitosResult.error || 'No se pudieron cargar los requisitos');
      }
    } catch (fetchError) {
      setError(fetchError.message || 'No se pudo cargar la modalidad');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDetail();
  }, [id]);

  const summary = useMemo(() => {
    const total = requirements.length;
    const active = requirements.filter((requirement) => requirement.activo).length;
    const mandatory = requirements.filter((requirement) => requirement.obligatorio).length;
    const withFile = requirements.filter((requirement) => requirement.archivo_url).length;

    return [
      { label: 'Requisitos', value: total, icon: Layers3 },
      { label: 'Activos', value: active, icon: CheckCircle2 },
      { label: 'Obligatorios', value: mandatory, icon: ShieldCheck },
      { label: 'Con archivo', value: withFile, icon: FileText },
    ];
  }, [requirements]);

  const studentProgress = useMemo(() => {
    const activeRequirements = requirements.filter((requirement) => requirement.activo);
    if (activeRequirements.length === 0) return 0;

    const readyRequirements = activeRequirements.filter((requirement) => requirement.archivo_url);
    return Math.round((readyRequirements.length / activeRequirements.length) * 100);
  }, [requirements]);

  const revokePreviewBlobUrl = () => {
    if (previewBlobUrlRef.current) {
      window.URL.revokeObjectURL(previewBlobUrlRef.current);
      previewBlobUrlRef.current = null;
    }
  };

  const clearPreviewBlob = () => {
    revokePreviewBlobUrl();
    setPreviewBlobUrl(null);
    setPreviewRendering(false);
    setPreviewRenderError('');
  };

  const closeRequirementForm = () => {
    setIsFormOpen(false);
    setEditingRequirement(null);
    setFormData(EMPTY_FORM);
    setArchivoFile(null);
  };

  const closePreview = () => {
    clearPreviewBlob();
    setIsPreviewOpen(false);
    setPreviewRequirement(null);
  };

  const openNewRequirement = () => {
    setEditingRequirement(null);
    setFormData(EMPTY_FORM);
    setArchivoFile(null);
    setError('');
    setIsFormOpen(true);
  };

  const openEditRequirement = (requirement) => {
    setEditingRequirement(requirement);
    setFormData({
      nombre: requirement.nombre || '',
      descripcion: requirement.descripcion || '',
      categoria: requirement.categoria || 'General',
      obligatorio: Boolean(requirement.obligatorio),
      version: requirement.version || '1.0',
      observaciones: requirement.observaciones || '',
      activo: Boolean(requirement.activo),
      archivo_nombre: requirement.archivo_nombre || extractFileName(requirement.archivo_url),
      archivo_tipo: requirement.archivo_tipo || getFileExtension(extractFileName(requirement.archivo_url)).toUpperCase(),
      archivo_url: requirement.archivo_url || '',
    });
    setArchivoFile(null);
    setError('');
    setIsFormOpen(true);
  };

  const handleFormChange = (event) => {
    const { name, value, type, checked, files } = event.target;

    if (name === 'archivo') {
      const file = files?.[0];
      if (!file) return;

      const extension = getFileExtension(file.name);
      if (!ALLOWED_EXTENSIONS.includes(extension)) {
        setError(`Extensión no permitida. Usa: ${ALLOWED_EXTENSIONS.join(', ')}`);
        return;
      }

      if (file.size > 25 * 1024 * 1024) {
        setError('El archivo no debe superar 25MB');
        return;
      }

      setError('');
      setArchivoFile(file);
      setFormData((current) => ({
        ...current,
        archivo_nombre: file.name,
        archivo_tipo: extension.toUpperCase(),
      }));
      return;
    }

    setFormData((current) => ({
      ...current,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSaveRequirement = async () => {
    setError('');
    setSuccess('');

    if (!formData.nombre.trim()) {
      setError('El nombre del requisito es requerido');
      return;
    }

    if (!formData.version.trim()) {
      setError('La versión es requerida');
      return;
    }

    if (!editingRequirement && !archivoFile) {
      setError('Adjunta un archivo para crear el requisito');
      return;
    }

    setIsSubmitting(true);

    try {
      const payload = new FormData();
      payload.append('nombre', formData.nombre);
      payload.append('descripcion', formData.descripcion || '');
      payload.append('categoria', formData.categoria || 'General');
      payload.append('obligatorio', formData.obligatorio ? 'true' : 'false');
      payload.append('version', formData.version || '1.0');
      payload.append('observaciones', formData.observaciones || '');
      payload.append('activo', formData.activo ? 'true' : 'false');

      if (archivoFile) {
        payload.append('archivo', archivoFile);
      }

      const requestConfig = {};
      const endpoint = editingRequirement
        ? API_CONFIG.ENDPOINTS.MODALIDAD_REQUISITO_DETAIL(id, editingRequirement.id)
        : API_CONFIG.ENDPOINTS.MODALIDAD_REQUISITOS(id);

      const result = editingRequirement
        ? await api.patch(endpoint, payload, requestConfig)
        : await api.create(endpoint, payload, requestConfig);

      if (!result.success) {
        setError(result.error || 'No se pudo guardar el requisito');
        return;
      }

      setSuccess(editingRequirement ? 'Requisito actualizado' : 'Requisito creado');
      closeRequirementForm();
      await loadDetail();
    } catch (saveError) {
      setError(saveError.message || 'No se pudo guardar el requisito');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteRequirement = async (requirement) => {
    if (!window.confirm('¿Deseas eliminar este requisito?')) return;

    setError('');
    setSuccess('');

    const result = await api.delete(API_CONFIG.ENDPOINTS.MODALIDAD_REQUISITO_DETAIL(id, requirement.id));
    if (!result.success) {
      setError(result.error || 'No se pudo eliminar el requisito');
      return;
    }

    setSuccess('Requisito eliminado');
    await loadDetail();
  };

  const handleDownload = async (requirement) => {
    if (!requirement?.archivo_url) return;

    try {
      const response = await axiosInstance.get(
        API_CONFIG.ENDPOINTS.MODALIDAD_REQUISITO_DESCARGAR(id, requirement.id),
        { responseType: 'blob' }
      );

      if (!response.data || response.data.size === 0) {
        throw new Error('El archivo descargado está vacío');
      }

      const blobUrl = window.URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = requirement.archivo_nombre || extractFileName(requirement.archivo_url) || `${requirement.nombre}.pdf`;
      link.click();
      window.URL.revokeObjectURL(blobUrl);
    } catch {
      setError('No se pudo descargar el archivo');
    }
  };

  const handleOpenPreview = async (requirement) => {
    setPreviewRequirement(requirement);
    clearPreviewBlob();

    const fileType = getRequirementFileType(requirement);

    if (fileType !== 'pdf') {
      setIsPreviewOpen(true);
      setPreviewRenderError('La vista previa solo está disponible para archivos PDF.');
      return;
    }

    setIsPreviewOpen(true);
    setPreviewRendering(true);

    try {
      const response = await axiosInstance.get(
        API_CONFIG.ENDPOINTS.MODALIDAD_REQUISITO_PREVIEW(id, requirement.id),
        { responseType: 'blob', skipGlobalLoader: true }
      );

      if (!response.data || response.data.size === 0) {
        throw new Error('El archivo PDF está vacío');
      }

      const blobUrl = window.URL.createObjectURL(response.data);
      revokePreviewBlobUrl();
      previewBlobUrlRef.current = blobUrl;
      setPreviewBlobUrl(blobUrl);
    } catch (error) {
      setPreviewRenderError(
        error?.message
          ? `No se pudo cargar la vista previa del PDF: ${error.message}`
          : 'No se pudo cargar la vista previa del PDF'
      );
    } finally {
      setPreviewRendering(false);
    }
  };

  const isPreviewablePdf = useMemo(() => {
    if (!previewRequirement) return false;

    return getRequirementFileType(previewRequirement) === 'pdf';
  }, [previewRequirement]);

  useEffect(() => {
    return () => revokePreviewBlobUrl();
  }, []);

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center rounded-3xl border border-gray-200/80 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800">
        <div className="text-center">
          <Loader2 className="mx-auto mb-4 h-10 w-10 animate-spin text-blue-600" />
          <p className="text-gray-600 dark:text-gray-300">Cargando detalle de modalidad...</p>
        </div>
      </div>
    );
  }

  if (error && !modalidad) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Detalle de modalidad"
          description="Vista documental y administrativa"
          action={(
            <button
              onClick={() => navigate('/modalidades')}
              className="inline-flex items-center gap-2 rounded-xl border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700"
            >
              <ArrowLeft className="h-4 w-4" />
              Volver
            </button>
          )}
        />
        <Alert type="error" message={error} autoClose={false} />
      </div>
    );
  }

  const activeStateClass = modalidad?.activa
    ? 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900/40 dark:bg-emerald-950/40 dark:text-emerald-300'
    : 'border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-900/40 dark:bg-rose-950/40 dark:text-rose-300';

  return (
    <div className="space-y-6">
      <PageHeader
        title="Detalle de modalidad"
        description="Portal institucional para requisitos oficiales y seguimiento documental"
        action={(
          <button
            onClick={() => navigate('/modalidades')}
            className="inline-flex items-center gap-2 rounded-xl border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700"
          >
            <ArrowLeft className="h-4 w-4" />
            Volver a modalidades
          </button>
        )}
      />

      {error && <Alert type="error" message={error} autoClose={false} />}
      {success && <Alert type="success" message={success} />}

      {!isStudent && (
        <section className="overflow-hidden rounded-[2rem] border border-slate-200/80 bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 text-white shadow-2xl shadow-slate-950/20">
          <div className="grid gap-0 xl:grid-cols-[minmax(0,1.6fr)_minmax(280px,0.8fr)]">
            <div className="p-6 sm:p-8 xl:p-10">
              <div className="mb-5 flex flex-wrap items-center gap-3">
                <span className={`inline-flex items-center gap-2 rounded-full border px-4 py-1.5 text-xs font-semibold tracking-wide ${activeStateClass}`}>
                  <Sparkles className="h-3.5 w-3.5" />
                  {modalidad?.activa ? 'Modalidad activa' : 'Modalidad inactiva'}
                </span>
                <span className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-4 py-1.5 text-xs font-medium text-white/85">
                  <CalendarDays className="h-3.5 w-3.5" />
                  Creada {formatDateShort(modalidad?.creada_en)}
                </span>
              </div>

              <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">{modalidad?.nombre}</h1>
              <p className="mt-4 max-w-3xl text-sm leading-6 text-slate-200 sm:text-base">
                {modalidad?.descripcion || 'Sin descripción registrada para esta modalidad.'}
              </p>

              <div className="mt-8 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                {summary.map((item) => {
                  const Icon = item.icon;
                  return (
                    <div key={item.label} className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-sm">
                      <div className="flex items-center justify-between gap-4">
                        <div>
                          <p className="text-xs uppercase tracking-[0.2em] text-slate-300">{item.label}</p>
                          <p className="mt-2 text-2xl font-semibold text-white">{item.value}</p>
                        </div>
                        <div className="rounded-2xl bg-white/10 p-3 text-white">
                          <Icon className="h-5 w-5" />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="border-t border-white/10 bg-white/5 p-6 sm:p-8 xl:border-l xl:border-t-0 xl:p-10">
              <div className="rounded-3xl border border-white/10 bg-white/10 p-5 shadow-xl shadow-slate-950/20 backdrop-blur-sm">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-xs uppercase tracking-[0.24em] text-slate-300">Vista estudiante</p>
                    <h2 className="mt-2 text-xl font-semibold text-white">Portal de seguimiento</h2>
                  </div>
                  <div className="rounded-2xl bg-blue-500/20 p-3 text-blue-100 ring-1 ring-inset ring-blue-300/20">
                    <FileText className="h-5 w-5" />
                  </div>
                </div>

                <div className="mt-6 space-y-4">
                  <div>
                    <div className="mb-2 flex items-center justify-between text-sm text-slate-200">
                      <span>Avance documental</span>
                      <span>{studentProgress}%</span>
                    </div>
                    <div className="h-2 rounded-full bg-white/10">
                      <div className="h-2 rounded-full bg-gradient-to-r from-cyan-400 via-sky-400 to-blue-500 transition-all" style={{ width: `${studentProgress}%` }} />
                    </div>
                  </div>

                  <div className="rounded-2xl border border-white/10 bg-slate-950/40 p-4">
                    <p className="text-sm font-medium text-white">Acceso limpio y claro</p>
                    <p className="mt-1 text-sm leading-6 text-slate-300">
                      El estudiante ve los requisitos activos, archivos disponibles y el estado documental sin salir del portal.
                    </p>
                  </div>

                  <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
                    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                      <p className="text-xs uppercase tracking-[0.18em] text-slate-300">Actualización</p>
                      <p className="mt-2 text-sm font-medium text-white">{formatDate(modalidad?.actualizada_en || modalidad?.creada_en)}</p>
                    </div>
                    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                      <p className="text-xs uppercase tracking-[0.18em] text-slate-300">Estado</p>
                      <p className="mt-2 text-sm font-medium text-white">
                        {modalidad?.activa ? 'Disponible para postulantes' : 'Temporalmente deshabilitada'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      <div className={`grid gap-6 ${isStudent ? 'xl:grid-cols-1' : 'xl:grid-cols-[minmax(0,1.55fr)_minmax(320px,0.85fr)]'}`}>
        <div className="space-y-6">
          <SectionCard title="Requisitos oficiales" description="Lista editable de documentos y metadatos para la modalidad." className="bg-white dark:bg-gray-800">
            <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <ShieldCheck className="h-4 w-4 text-blue-600" />
                Gestión documental institucional
              </div>
              {canManage && (
                <button
                  onClick={openNewRequirement}
                  className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700"
                >
                  <Plus className="h-4 w-4" />
                  Nuevo requisito
                </button>
              )}
            </div>

            {requirements.length === 0 ? (
              <div className="rounded-3xl border border-dashed border-gray-300 bg-gray-50 p-8 text-center dark:border-gray-600 dark:bg-gray-900/40">
                <Upload className="mx-auto h-10 w-10 text-gray-400" />
                <h3 className="mt-4 text-lg font-semibold text-gray-900 dark:text-white">Todavía no hay requisitos cargados</h3>
                <p className="mx-auto mt-2 max-w-xl text-sm text-gray-600 dark:text-gray-400">
                  {canManage
                    ? 'Crea el primer documento oficial para esta modalidad y empieza a construir el portal documental.'
                    : 'Cuando exista información institucional cargada, aparecerá aquí para consulta y descarga.'}
                </p>
                {canManage && (
                  <button
                    onClick={openNewRequirement}
                    className="mt-5 inline-flex items-center gap-2 rounded-xl border border-blue-200 bg-white px-4 py-2.5 text-sm font-medium text-blue-700 shadow-sm transition hover:bg-blue-50 dark:border-blue-800 dark:bg-gray-800 dark:text-blue-300 dark:hover:bg-gray-700"
                  >
                    <Plus className="h-4 w-4" />
                    Crear primer requisito
                  </button>
                )}
              </div>
            ) : (
              <div className="grid gap-4 lg:grid-cols-2">
                {requirements.map((requirement) => (
                  <article
                    key={requirement.id}
                    className="rounded-3xl border border-gray-200/80 bg-gradient-to-br from-white to-slate-50 p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg dark:border-gray-700 dark:from-gray-800 dark:to-gray-900/80"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="text-base font-semibold text-gray-900 dark:text-white">{requirement.nombre}</h3>
                          <span className="rounded-full border border-sky-200 bg-sky-50 px-2.5 py-1 text-[11px] font-semibold text-sky-700 dark:border-sky-900/50 dark:bg-sky-950/40 dark:text-sky-300">
                            {requirement.categoria || 'General'}
                          </span>
                        </div>
                        <p className="mt-2 text-sm leading-6 text-gray-600 dark:text-gray-400">
                          {requirement.descripcion || 'Sin descripción registrada.'}
                        </p>
                      </div>

                      <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${requirement.activo ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300' : 'bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-300'}`}>
                        {requirement.activo ? 'Activo' : 'Inactivo'}
                      </span>
                    </div>

                    <div className="mt-4 grid gap-3 text-sm text-gray-600 dark:text-gray-400 sm:grid-cols-2">
                      <div className="rounded-2xl bg-white/70 p-3 dark:bg-gray-800/70">
                        <p className="text-xs uppercase tracking-[0.18em] text-gray-500 dark:text-gray-500">Versión</p>
                        <p className="mt-1 font-medium text-gray-900 dark:text-gray-100">{requirement.version}</p>
                      </div>
                      <div className="rounded-2xl bg-white/70 p-3 dark:bg-gray-800/70">
                        <p className="text-xs uppercase tracking-[0.18em] text-gray-500 dark:text-gray-500">Actualización</p>
                        <p className="mt-1 font-medium text-gray-900 dark:text-gray-100">{formatDateShort(requirement.updated_at)}</p>
                      </div>
                      <div className="rounded-2xl bg-white/70 p-3 dark:bg-gray-800/70">
                        <p className="text-xs uppercase tracking-[0.18em] text-gray-500 dark:text-gray-500">Obligatorio</p>
                        <p className="mt-1 font-medium text-gray-900 dark:text-gray-100">{requirement.obligatorio ? 'Sí' : 'No'}</p>
                      </div>
                      <div className="rounded-2xl bg-white/70 p-3 dark:bg-gray-800/70">
                        <p className="text-xs uppercase tracking-[0.18em] text-gray-500 dark:text-gray-500">Archivo</p>
                        <p className="mt-1 truncate font-medium text-gray-900 dark:text-gray-100">
                          {requirement.archivo_nombre || extractFileName(requirement.archivo_url) || 'Sin archivo'}
                        </p>
                      </div>
                    </div>

                    {requirement.observaciones && (
                      <div className="mt-4 rounded-2xl border border-dashed border-gray-300 bg-white/70 p-3 text-sm text-gray-600 dark:border-gray-600 dark:bg-gray-800/70 dark:text-gray-300">
                        {requirement.observaciones}
                      </div>
                    )}

                    <div className="mt-5 flex flex-wrap gap-2">
                      <button
                        onClick={() => handleOpenPreview(requirement)}
                        disabled={!requirement.archivo_url}
                        className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-3.5 py-2 text-sm font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-white dark:text-slate-900 dark:hover:bg-slate-100"
                      >
                        <Eye className="h-4 w-4" />
                        Ver PDF
                      </button>
                      <button
                        onClick={() => handleDownload(requirement)}
                        disabled={!requirement.archivo_url}
                        className="inline-flex items-center gap-2 rounded-xl border border-gray-300 bg-white px-3.5 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700"
                      >
                        <Download className="h-4 w-4" />
                        Descargar
                      </button>
                      {canManage && (
                        <>
                          <button
                            onClick={() => openEditRequirement(requirement)}
                            className="inline-flex items-center gap-2 rounded-xl border border-blue-200 bg-blue-50 px-3.5 py-2 text-sm font-medium text-blue-700 transition hover:bg-blue-100 dark:border-blue-900/40 dark:bg-blue-950/40 dark:text-blue-300 dark:hover:bg-blue-950/60"
                          >
                            <PencilLine className="h-4 w-4" />
                            Editar metadata
                          </button>
                          <button
                            onClick={() => handleDeleteRequirement(requirement)}
                            className="inline-flex items-center gap-2 rounded-xl border border-rose-200 bg-rose-50 px-3.5 py-2 text-sm font-medium text-rose-700 transition hover:bg-rose-100 dark:border-rose-900/40 dark:bg-rose-950/40 dark:text-rose-300 dark:hover:bg-rose-950/60"
                          >
                            <Trash2 className="h-4 w-4" />
                            Eliminar
                          </button>
                        </>
                      )}
                    </div>
                  </article>
                ))}
              </div>
            )}
          </SectionCard>
        </div>

        {!isStudent && (
          <div className="space-y-6">
            <SectionCard title="Seguimiento documental" description="Visión rápida para coordinación académica y estudiantes." className="bg-white dark:bg-gray-800">
              <div className="space-y-4">
                <div className="rounded-3xl bg-gradient-to-br from-blue-600 to-cyan-500 p-5 text-white shadow-lg">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <p className="text-xs uppercase tracking-[0.22em] text-white/80">Progreso</p>
                      <p className="mt-2 text-3xl font-bold">{studentProgress}%</p>
                    </div>
                    <div className="rounded-2xl bg-white/15 p-3">
                      <CheckCircle2 className="h-6 w-6" />
                    </div>
                  </div>
                  <div className="mt-5 h-2 rounded-full bg-white/20">
                    <div className="h-2 rounded-full bg-white" style={{ width: `${studentProgress}%` }} />
                  </div>
                </div>

                <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
                  <div className="rounded-3xl border border-gray-200/80 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-900/60">
                    <div className="flex items-center gap-3">
                      <div className="rounded-2xl bg-blue-100 p-2 text-blue-700 dark:bg-blue-950/50 dark:text-blue-300">
                        <Layers3 className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="text-xs uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">Documentos activos</p>
                        <p className="mt-1 text-lg font-semibold text-gray-900 dark:text-white">
                          {requirements.filter((requirement) => requirement.activo).length}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-3xl border border-gray-200/80 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-900/60">
                    <div className="flex items-center gap-3">
                      <div className="rounded-2xl bg-emerald-100 p-2 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300">
                        <FileText className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="text-xs uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">Con archivo</p>
                        <p className="mt-1 text-lg font-semibold text-gray-900 dark:text-white">
                          {requirements.filter((requirement) => requirement.archivo_url).length}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-3xl border border-gray-200/80 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-900/60 sm:col-span-2 xl:col-span-1">
                    <p className="text-xs uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">Fecha de creación</p>
                    <p className="mt-2 text-base font-semibold text-gray-900 dark:text-white">{formatDate(modalidad?.creada_en)}</p>
                  </div>
                </div>
              </div>
            </SectionCard>

            <SectionCard title="Estado institucional" description="Tarjeta de contexto para la vista de estudiantes." className="bg-white dark:bg-gray-800">
              <div className="space-y-3">
                <div className="flex items-center justify-between rounded-2xl border border-gray-200/80 bg-gray-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-900/60">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Modalidad</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">{modalidad?.nombre}</span>
                </div>
                <div className="flex items-center justify-between rounded-2xl border border-gray-200/80 bg-gray-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-900/60">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Estado</span>
                  <span className={`rounded-full px-3 py-1 text-xs font-semibold ${modalidad?.activa ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300' : 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300'}`}>
                    {modalidad?.activa ? 'Activa' : 'Inactiva'}
                  </span>
                </div>
                <div className="flex items-center justify-between rounded-2xl border border-gray-200/80 bg-gray-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-900/60">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Actualización</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">{formatDate(modalidad?.actualizada_en || modalidad?.creada_en)}</span>
                </div>
              </div>
            </SectionCard>
          </div>
        )}
      </div>

      <Modal
        isOpen={isFormOpen}
        title={editingRequirement ? 'Editar requisito' : 'Nuevo requisito'}
        onClose={closeRequirementForm}
        onSubmit={handleSaveRequirement}
        submitText={isSubmitting ? 'Guardando...' : editingRequirement ? 'Actualizar requisito' : 'Crear requisito'}
        isLoading={isSubmitting}
        sizeClass="max-w-5xl"
      >
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1.3fr)_minmax(300px,0.9fr)]">
          <SectionCard title="Metadata del requisito" description="Información pública y control institucional.">
            <div className="grid gap-4 sm:grid-cols-2">
              <FormField
                label="Nombre"
                name="nombre"
                value={formData.nombre}
                onChange={handleFormChange}
                placeholder="Ej: Reglamento PDF"
                required
              />

              <FormField
                label="Categoría"
                name="categoria"
                type="select"
                value={formData.categoria}
                onChange={handleFormChange}
                options={CATEGORY_OPTIONS}
                required
              />

              <FormField
                label="Versión"
                name="version"
                value={formData.version}
                onChange={handleFormChange}
                placeholder="1.0"
                required
              />

              <FormField
                label="Descripción"
                name="descripcion"
                type="textarea"
                value={formData.descripcion}
                onChange={handleFormChange}
                placeholder="Describe el alcance del requisito"
                className="sm:col-span-2"
              />

              <FormField
                label="Observaciones"
                name="observaciones"
                type="textarea"
                value={formData.observaciones}
                onChange={handleFormChange}
                placeholder="Notas administrativas, observaciones o validaciones"
                className="sm:col-span-2"
              />
            </div>
          </SectionCard>

          <div className="space-y-6">
            <SectionCard title="Archivo oficial" description="Carga un PDF o documento compatible.">
              <div className="space-y-4">
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Archivo</label>
                  <input
                    type="file"
                    name="archivo"
                    onChange={handleFormChange}
                    accept=".pdf,.doc,.docx,.xls,.xlsx"
                    className="w-full rounded-xl border border-gray-300 bg-white px-4 py-2.5 text-gray-900 shadow-sm transition focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200"
                  />
                  <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">Formatos permitidos: PDF, DOC, DOCX, XLS y XLSX.</p>
                </div>

                {formData.archivo_nombre && (
                  <div className="rounded-2xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-900/60">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">{formData.archivo_nombre}</p>
                    <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">Tipo: {formData.archivo_tipo || 'N/D'}</p>
                  </div>
                )}

                <FormField label="Obligatorio" name="obligatorio" type="checkbox" value={formData.obligatorio} onChange={handleFormChange} />
                <FormField label="Activo" name="activo" type="checkbox" value={formData.activo} onChange={handleFormChange} />
              </div>
            </SectionCard>

            <SectionCard title="Cobertura visual" description="Portal limpio y responsivo para la vista de estudiantes.">
              <div className="rounded-2xl bg-gradient-to-br from-slate-950 to-blue-950 p-5 text-white shadow-lg">
                <div className="flex items-start gap-3">
                  <div className="rounded-2xl bg-white/10 p-3">
                    <Sparkles className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold">Vista moderna</p>
                    <p className="mt-1 text-sm leading-6 text-slate-200">
                      Los requisitos se guardan ahora en la base de datos y se comparten entre administradores, docentes y postulantes.
                    </p>
                  </div>
                </div>
              </div>
            </SectionCard>
          </div>
        </div>
      </Modal>

      <Modal
        isOpen={isPreviewOpen}
        title={previewRequirement ? `Vista previa: ${previewRequirement.nombre}` : 'Vista previa del archivo'}
        onClose={closePreview}
        onSubmit={closePreview}
        submitText="Cerrar"
        sizeClass="max-w-5xl"
      >
        {previewRequirement?.archivo_url ? (
          isPreviewablePdf ? (
            previewRenderError ? (
              <div className="rounded-3xl border border-dashed border-gray-300 bg-gray-50 p-8 text-center dark:border-gray-600 dark:bg-gray-900/50">
                <FileText className="mx-auto h-10 w-10 text-gray-400" />
                <h3 className="mt-4 text-lg font-semibold text-gray-900 dark:text-white">No se pudo mostrar la vista previa</h3>
                <p className="mx-auto mt-2 max-w-2xl text-sm text-gray-600 dark:text-gray-400">{previewRenderError}</p>
                <button
                  onClick={() => handleDownload(previewRequirement)}
                  className="mt-5 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700"
                >
                  <Download className="h-4 w-4" />
                  Descargar archivo
                </button>
              </div>
            ) : (
              <div className="relative overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-900">
                <iframe
                  title={previewRequirement ? `Vista previa de ${previewRequirement.nombre}` : 'Vista previa del archivo'}
                  src={previewBlobUrl || undefined}
                  className="h-[72vh] w-full bg-neutral-100 dark:bg-neutral-950"
                />
                {previewRendering && (
                  <div className="absolute inset-0 flex items-center justify-center bg-white/80 p-8 text-center backdrop-blur-sm dark:bg-gray-950/80">
                    <div>
                      <Loader2 className="mx-auto h-10 w-10 animate-spin text-blue-600" />
                      <h3 className="mt-4 text-lg font-semibold text-gray-900 dark:text-white">Cargando PDF...</h3>
                      <p className="mx-auto mt-2 max-w-2xl text-sm text-gray-600 dark:text-gray-400">
                        Estamos obteniendo el archivo desde el backend para mostrarlo correctamente.
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )
          ) : (
            <div className="rounded-3xl border border-dashed border-gray-300 bg-gray-50 p-8 text-center dark:border-gray-600 dark:bg-gray-900/50">
              <FileText className="mx-auto h-10 w-10 text-gray-400" />
              <h3 className="mt-4 text-lg font-semibold text-gray-900 dark:text-white">Vista previa no disponible para este formato</h3>
              <p className="mx-auto mt-2 max-w-2xl text-sm text-gray-600 dark:text-gray-400">
                Puedes descargar el archivo para revisarlo en el programa correspondiente.
              </p>
              <button
                onClick={() => handleDownload(previewRequirement)}
                className="mt-5 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700"
              >
                <Download className="h-4 w-4" />
                Descargar archivo
              </button>
            </div>
          )
        ) : (
          <div className="rounded-3xl border border-dashed border-gray-300 bg-gray-50 p-8 text-center dark:border-gray-600 dark:bg-gray-900/50">
            <p className="text-sm text-gray-600 dark:text-gray-400">El requisito no tiene archivo adjunto.</p>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default ModalidadDetalle;