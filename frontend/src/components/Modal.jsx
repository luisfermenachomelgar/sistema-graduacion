/**
 * Modal Component
 * Componente reutilizable para modales genéricos
 */

import React from 'react';
import { createPortal } from 'react-dom';

const Modal = ({
  isOpen,
  title,
  children,
  onClose,
  onSubmit,
  submitText = 'Guardar',
  submitVariant = 'primary',
  isLoading = false,
  sizeClass = 'max-w-xl',
}) => {
  if (!isOpen) return null;

  const handleBackdropMouseDown = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return createPortal(
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onMouseDown={handleBackdropMouseDown}
    >
      <div
        className={`bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full ${sizeClass} max-h-[88vh] overflow-hidden flex flex-col`}
        onMouseDown={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex justify-between items-start gap-4 px-6 pt-6 pb-4 border-b border-gray-200/80 dark:border-gray-700">
          <div className="min-w-0">
            <h2 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white leading-tight">{title}</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition text-2xl w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 dark:hover:bg-gray-700/70"
            disabled={isLoading}
          >
            ✕
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 min-h-0 overflow-y-auto px-6 py-5">{children}</div>

        {/* Footer */}
        <div className="flex justify-end gap-3 px-6 py-4 border-t border-gray-200/80 dark:border-gray-700 bg-gray-50/90 dark:bg-gray-700/40">
          <button
            onClick={onClose}
            className="px-4 py-2.5 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition font-medium"
            disabled={isLoading}
          >
            Cancelar
          </button>
          <button
            onClick={onSubmit}
            disabled={isLoading}
            className={`px-4 py-2.5 text-white rounded-xl transition font-medium flex items-center gap-2 shadow-sm ${
              submitVariant === 'danger'
                ? 'bg-red-600 hover:bg-red-700 disabled:bg-red-400'
                : 'bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400'
            }`}
          >
            {isLoading && <span className="animate-spin">⏳</span>}
            {submitText}
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
};

export default Modal;
