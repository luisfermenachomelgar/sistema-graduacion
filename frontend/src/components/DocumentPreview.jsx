import { Download, FileText, Loader2, X } from 'lucide-react';

const PDF_EXTENSIONS = ['pdf'];

const DocumentPreview = ({
  isOpen,
  title,
  previewUrl,
  previewExtension,
  onClose,
  isLoading = false,
  renderError = '',
}) => {
  if (!isOpen) return null;

  const isPdf = PDF_EXTENSIONS.includes(previewExtension);
  const hasPreview = Boolean(previewUrl);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="relative w-full max-w-5xl rounded-3xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-900">
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h2>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-gray-500 transition hover:bg-gray-100 hover:text-gray-900 dark:hover:bg-gray-800 dark:hover:text-white"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="relative overflow-hidden rounded-b-3xl border-t border-gray-200 dark:border-gray-700">
          {hasPreview ? (
            isPdf ? (
              <div className="relative">
                <iframe
                  title={title || 'Vista previa del documento'}
                  src={previewUrl}
                  className="h-[72vh] w-full bg-neutral-100 dark:bg-neutral-950"
                />
                {isLoading && (
                  <div className="absolute inset-0 flex items-center justify-center bg-white/80 p-8 backdrop-blur-sm dark:bg-gray-950/80">
                    <div className="text-center">
                      <Loader2 className="mx-auto h-10 w-10 animate-spin text-blue-600" />
                      <p className="mt-4 text-base font-semibold text-gray-900 dark:text-white">Cargando PDF...</p>
                      <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                        Estamos obteniendo el archivo para mostrar la vista previa.
                      </p>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex min-h-[72vh] flex-col items-center justify-center gap-4 p-8 text-center">
                <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  Vista previa no disponible para este formato.
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {renderError || 'Puedes descargar el archivo para verlo en tu aplicación de escritorio.'}
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

        <div className="flex justify-end gap-3 border-t border-gray-200 px-6 py-4 dark:border-gray-700">
          <button
            onClick={onClose}
            className="rounded-lg border border-gray-300 bg-white px-4 py-2 font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700"
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentPreview;
