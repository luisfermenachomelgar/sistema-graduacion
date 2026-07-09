/**
 * BulkUploadModal - Modal para carga masiva de documentos
 * Reutiliza completamente la lógica de carga individual
 */

import { useState, useEffect } from 'react';
import { X, Upload, Check, AlertCircle, Loader } from 'lucide-react';
import api from '../api/api';
import { API_CONFIG } from '../constants/api';

const UPLOAD_STATES = {
  PENDING: 'pending',
  UPLOADING: 'uploading',
  COMPLETED: 'completed',
  ERROR: 'error',
};

const BulkUploadModal = ({
  isOpen,
  onClose,
  postulacion,
  tiposDocumentoFiltrados,
  tiposDocumentoPorEtapa,
  isStudent,
  onUploadComplete,
}) => {
  const [documentoFiles, setDocumentoFiles] = useState({});
  const [uploadStates, setUploadStates] = useState({});
  const [uploadProgress, setUploadProgress] = useState(null);
  const [resumen, setResumen] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedEstado, setSelectedEstado] = useState('pendiente');

  // Inicializar estado cuando se abre el modal
  useEffect(() => {
    const documentos = Array.isArray(tiposDocumentoFiltrados)
      ? tiposDocumentoFiltrados
      : Object.values(tiposDocumentoPorEtapa || tiposDocumentoFiltrados || {}).flat();

    if (isOpen && documentos.length > 0) {
      const initialStates = {};
      documentos.forEach((tipo) => {
        initialStates[tipo.id] = UPLOAD_STATES.PENDING;
      });
      setUploadStates(initialStates);
      setDocumentoFiles({});
      setResumen(null);
      setUploadProgress(null);
    }
  }, [isOpen, tiposDocumentoFiltrados, tiposDocumentoPorEtapa]);

  if (!isOpen) return null;

  const handleFileSelect = (tipoId, file) => {
    if (file) {
      // Validar extensión
      const extensionesPermitidas = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'];
      const extension = file.name.split('.').pop().toLowerCase();
      if (!extensionesPermitidas.includes(extension)) {
        alert(`Extensión no permitida para ${file.name}`);
        return;
      }
      // Validar tamaño
      const MAX_SIZE = 25 * 1024 * 1024;
      if (file.size > MAX_SIZE) {
        alert(`El archivo ${file.name} excede 25MB`);
        return;
      }
      setDocumentoFiles((prev) => ({
        ...prev,
        [tipoId]: file,
      }));
    } else {
      setDocumentoFiles((prev) => {
        const newFiles = { ...prev };
        delete newFiles[tipoId];
        return newFiles;
      });
    }
  };

  const getFileStatus = (tipoId) => {
    if (documentoFiles[tipoId]) {
      return 'ready';
    }
    return 'pending';
  };

  const getDocumentosDisponibles = () => {
    if (Array.isArray(tiposDocumentoFiltrados)) {
      return [['Todos', tiposDocumentoFiltrados]];
    }

    const grouped = tiposDocumentoPorEtapa || tiposDocumentoFiltrados || {};
    return Object.entries(grouped).filter(([, documentos]) => Array.isArray(documentos));
  };

  const handleUploadAll = async () => {
    const archivosSeleccionados = Object.entries(documentoFiles);
    if (archivosSeleccionados.length === 0) {
      alert('Por favor selecciona al menos un archivo');
      return;
    }

    setIsUploading(true);
    setUploadProgress({
      total: archivosSeleccionados.length,
      current: 0,
    });

    const resultados = {
      exitosos: 0,
      errores: 0,
      detalles: [],
    };

    const documentosDisponibles = getDocumentosDisponibles().flatMap(([, documentos]) => documentos);

    for (let i = 0; i < archivosSeleccionados.length; i++) {
      const [tipoId, file] = archivosSeleccionados[i];
      const tipoDocumento = documentosDisponibles.find((t) => t.id === parseInt(tipoId, 10));

      setUploadProgress({
        total: archivosSeleccionados.length,
        current: i + 1,
      });

      setUploadStates((prev) => ({
        ...prev,
        [tipoId]: UPLOAD_STATES.UPLOADING,
      }));

      try {
        const payload = new FormData();
        payload.append('postulacion', postulacion);
        payload.append('tipo_documento', tipoId);
        payload.append('archivo', file);
        payload.append('estado', isStudent ? 'pendiente' : selectedEstado);

        const result = await api.create(API_CONFIG.ENDPOINTS.DOCUMENTOS, payload, {
          suppressErrorToast: true,
        });

        if (result.success) {
          setUploadStates((prev) => ({
            ...prev,
            [tipoId]: UPLOAD_STATES.COMPLETED,
          }));
          resultados.exitosos += 1;
          resultados.detalles.push({
            tipo: tipoDocumento.label,
            estado: 'exitoso',
          });
        } else {
          setUploadStates((prev) => ({
            ...prev,
            [tipoId]: UPLOAD_STATES.ERROR,
          }));
          resultados.errores += 1;
          resultados.detalles.push({
            tipo: tipoDocumento.label,
            estado: 'error',
            error: result.error,
          });
        }
      } catch (error) {
        setUploadStates((prev) => ({
          ...prev,
          [tipoId]: UPLOAD_STATES.ERROR,
        }));
        resultados.errores += 1;
        resultados.detalles.push({
          tipo: tipoDocumento.label,
          estado: 'error',
          error: error.message,
        });
      }
    }

    setIsUploading(false);
    setUploadProgress(null);
    setResumen(resultados);
    onUploadComplete(resultados);
  };

  const handleClose = () => {
    if (!isUploading && resumen) {
      // Si ya mostró resumen, cierra
      onClose();
    } else if (!isUploading) {
      // Si no está subiendo y no hay resumen, permite cerrar
      onClose();
    }
  };

  const documentosParaMostrar = getDocumentosDisponibles();
  const archivosSeleccionados = Object.keys(documentoFiles).length;
  const totalDocumentos = documentosParaMostrar.reduce((acc, [, tipos]) => acc + tipos.length, 0);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="relative w-full max-w-3xl rounded-3xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-900">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4 dark:border-gray-700">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Carga Masiva de Documentos</h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Se cargarán todos los requisitos de la modalidad, agrupados por etapa solo para visualización.
            </p>
          </div>
          <button
            onClick={handleClose}
            disabled={isUploading}
            className="rounded-lg p-1 text-gray-500 transition hover:bg-gray-100 hover:text-gray-900 disabled:opacity-50 dark:hover:bg-gray-800 dark:hover:text-white"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Content */}
        <div className="max-h-[60vh] overflow-y-auto px-6 py-6">
          {resumen ? (
            // Mostrar resumen
            <div className="space-y-6">
              <div className="rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-50 p-6 dark:from-blue-900/20 dark:to-indigo-900/20">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Resumen de Carga</h3>
                
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="rounded-xl bg-white p-4 dark:bg-gray-800">
                    <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Total</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {resumen.exitosos + resumen.errores}
                    </p>
                  </div>
                  <div className="rounded-xl bg-green-50 p-4 dark:bg-green-900/20">
                    <p className="text-xs text-green-600 dark:text-green-400 mb-1">Cargados</p>
                    <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                      {resumen.exitosos}
                    </p>
                  </div>
                  <div className="rounded-xl bg-red-50 p-4 dark:bg-red-900/20">
                    <p className="text-xs text-red-600 dark:text-red-400 mb-1">Con Error</p>
                    <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                      {resumen.errores}
                    </p>
                  </div>
                </div>

                {resumen.detalles.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Detalles:</p>
                    {resumen.detalles.map((detalle, idx) => (
                      <div
                        key={idx}
                        className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400"
                      >
                        {detalle.estado === 'exitoso' ? (
                          <Check className="h-4 w-4 text-green-600 flex-shrink-0" />
                        ) : (
                          <AlertCircle className="h-4 w-4 text-red-600 flex-shrink-0" />
                        )}
                        <span>{detalle.tipo}</span>
                        {detalle.estado === 'error' && (
                          <span className="text-xs text-red-600 dark:text-red-400">
                            ({detalle.error})
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            // Mostrar formulario de carga
            <div className="space-y-4">
              {/* Estado selector para admins */}
              {!isStudent && (
                <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Estado de Documentos
                  </label>
                  <select
                    value={selectedEstado}
                    onChange={(e) => setSelectedEstado(e.target.value)}
                    disabled={isUploading}
                    className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-gray-900 transition focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 disabled:opacity-50 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200"
                  >
                    <option value="pendiente">Pendiente</option>
                    <option value="aprobado">Aprobado</option>
                    <option value="rechazado">Rechazado</option>
                  </select>
                </div>
              )}
              
              {totalDocumentos === 0 ? (
                <div className="flex items-center gap-3 rounded-2xl border border-yellow-200 bg-yellow-50 p-4 text-yellow-800 dark:border-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400">
                  <AlertCircle className="h-5 w-5 flex-shrink-0" />
                  <p>No hay tipos de documento configurados para esta modalidad.</p>
                </div>
              ) : (
                <>
                  {documentosParaMostrar.map(([etapaNombre, documentos]) => (
                    <div key={etapaNombre} className="space-y-3">
                      <h3 className="text-sm font-semibold uppercase tracking-wide text-gray-700 dark:text-gray-300">
                        {etapaNombre}
                      </h3>
                      <div className="overflow-x-auto rounded-xl border border-gray-200 dark:border-gray-700">
                        <table className="w-full text-sm">
                          <thead className="border-b border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-800">
                            <tr>
                              <th className="px-4 py-3 text-left font-medium text-gray-700 dark:text-gray-300">Documento</th>
                              <th className="px-4 py-3 text-left font-medium text-gray-700 dark:text-gray-300">Archivo</th>
                              <th className="px-4 py-3 text-center font-medium text-gray-700 dark:text-gray-300">Estado</th>
                            </tr>
                          </thead>
                          <tbody>
                            {documentos.map((tipo) => {
                              const fileStatus = getFileStatus(tipo.id);
                              const file = documentoFiles[tipo.id];
                              const uploadState = uploadStates[tipo.id];

                              return (
                                <tr
                                  key={tipo.id}
                                  className="border-b border-gray-200 hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800"
                                >
                                  <td className="px-4 py-3">
                                    <p className="font-medium text-gray-900 dark:text-white">{tipo.label}</p>
                                  </td>
                                  <td className="px-4 py-3">
                                    <div className="flex flex-col gap-2">
                                      <label className="flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 cursor-pointer transition hover:bg-gray-50 disabled:opacity-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700">
                                        <Upload className="h-4 w-4" />
                                        <span>{file ? 'Cambiar' : 'Seleccionar'}</span>
                                        <input
                                          type="file"
                                          onChange={(e) => handleFileSelect(tipo.id, e.target.files?.[0] || null)}
                                          accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png"
                                          className="hidden"
                                          disabled={isUploading || uploadState === UPLOAD_STATES.COMPLETED}
                                        />
                                      </label>
                                      {file && (
                                        <p className="text-xs text-gray-600 dark:text-gray-400 truncate">
                                          📄 {file.name}
                                        </p>
                                      )}
                                    </div>
                                  </td>
                                  <td className="px-4 py-3">
                                    <div className="flex items-center justify-center">
                                      {uploadState === UPLOAD_STATES.UPLOADING && (
                                        <div className="flex flex-col items-center gap-1">
                                          <Loader className="h-4 w-4 animate-spin text-blue-600" />
                                          <span className="text-xs text-blue-600 dark:text-blue-400">Subiendo...</span>
                                        </div>
                                      )}
                                      {uploadState === UPLOAD_STATES.COMPLETED && (
                                        <div className="flex flex-col items-center gap-1">
                                          <Check className="h-4 w-4 text-green-600" />
                                          <span className="text-xs text-green-600 dark:text-green-400">Completado</span>
                                        </div>
                                      )}
                                      {uploadState === UPLOAD_STATES.ERROR && (
                                        <div className="flex flex-col items-center gap-1">
                                          <AlertCircle className="h-4 w-4 text-red-600" />
                                          <span className="text-xs text-red-600 dark:text-red-400">Error</span>
                                        </div>
                                      )}
                                      {uploadState === UPLOAD_STATES.PENDING && (
                                        <div className="flex flex-col items-center gap-1">
                                          {fileStatus === 'ready' ? (
                                            <>
                                              <Check className="h-4 w-4 text-green-600" />
                                              <span className="text-xs text-green-600 dark:text-green-400">Listo</span>
                                            </>
                                          ) : (
                                            <>
                                              <AlertCircle className="h-4 w-4 text-yellow-600" />
                                              <span className="text-xs text-yellow-600 dark:text-yellow-400">Pendiente</span>
                                            </>
                                          )}
                                        </div>
                                      )}
                                    </div>
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  ))}

                  {/* Progreso */}
                  {uploadProgress && (
                    <div className="rounded-xl bg-blue-50 p-4 dark:bg-blue-900/20">
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-sm font-medium text-blue-900 dark:text-blue-200">
                          Cargando: {uploadProgress.current} de {uploadProgress.total}
                        </p>
                        <span className="text-sm text-blue-700 dark:text-blue-300">
                          {Math.round((uploadProgress.current / uploadProgress.total) * 100)}%
                        </span>
                      </div>
                      <div className="h-2 bg-blue-200 rounded-full overflow-hidden dark:bg-blue-900">
                        <div
                          className="h-full bg-blue-600 transition-all duration-300"
                          style={{
                            width: `${(uploadProgress.current / uploadProgress.total) * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 border-t border-gray-200 px-6 py-4 dark:border-gray-700">
          <button
            onClick={handleClose}
            disabled={isUploading}
            className="rounded-lg border border-gray-300 bg-white px-4 py-2 font-medium text-gray-700 transition hover:bg-gray-50 disabled:opacity-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700"
          >
            {resumen ? 'Cerrar' : 'Cancelar'}
          </button>
          {!resumen && (
            <button
              onClick={handleUploadAll}
              disabled={isUploading || archivosSeleccionados === 0}
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 font-medium text-white transition hover:bg-blue-700 disabled:opacity-50 dark:hover:bg-blue-800"
            >
              <Upload className="h-4 w-4" />
              Subir todos ({archivosSeleccionados}/{totalDocumentos})
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default BulkUploadModal;
