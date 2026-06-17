/**
 * FormField Component
 * Campo de formulario reutilizable con validación
 */

import React from 'react';

const FormField = ({
  label,
  name,
  type = 'text',
  value,
  onChange,
  placeholder,
  required = false,
  error,
  helperText,
  disabled = false,
  readOnly = false,
  options = [], // Para select
  rows, // Para textarea
  className = '',
}) => {
  const baseInputClass =
    'w-full px-4 py-2.5 border rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition shadow-sm disabled:bg-gray-100 dark:disabled:bg-gray-600 disabled:cursor-not-allowed disabled:shadow-none';

  const inputClass = error
    ? `${baseInputClass} border-red-500 dark:border-red-800 focus:ring-red-500`
    : `${baseInputClass} border-gray-300 dark:border-gray-600`;

  const renderInput = () => {
    switch (type) {
      case 'select':
        return (
          <select
            id={name}
            name={name}
            value={value}
            onChange={onChange}
            disabled={disabled}
            className={inputClass}
          >
            <option value="">{placeholder || 'Seleccionar...'}</option>
            {options.map((opt) => (
              <option key={opt.id || opt.value} value={opt.id || opt.value}>
                {opt.label || opt.nombre || opt.name}
              </option>
            ))}
          </select>
        );

      case 'textarea':
        return (
          <textarea
            id={name}
            name={name}
            value={value}
            onChange={onChange}
            placeholder={placeholder}
            disabled={disabled}
            readOnly={readOnly}
            rows={rows || 3}
            className={`${inputClass} resize-y leading-6`}
          />
        );

      case 'checkbox':
        return (
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id={name}
              name={name}
              checked={value}
              onChange={onChange}
              disabled={disabled}
              className="w-4 h-4 border border-gray-300 dark:border-gray-600 rounded focus:ring-2 focus:ring-blue-500 cursor-pointer"
            />
            <label htmlFor={name} className="text-gray-700 dark:text-gray-300 cursor-pointer">
              {label}
            </label>
          </div>
        );

      default:
        return (
          <input
            id={name}
            type={type}
            name={name}
            value={value}
            onChange={onChange}
            placeholder={placeholder}
            disabled={disabled}
            readOnly={readOnly}
            className={inputClass}
          />
        );
    }
  };

  if (type === 'checkbox') {
    return (
      <div className={className}>
        {renderInput()}
        {error && <p className="text-red-500 dark:text-red-400 text-xs mt-1">{error}</p>}
        {helperText && <p className="text-gray-500 dark:text-gray-400 text-xs mt-1">{helperText}</p>}
      </div>
    );
  }

  return (
    <div className={className}>
      {label && (
        <label htmlFor={name} className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
          {label}
          {required && <span className="text-red-500 dark:text-red-400">*</span>}
        </label>
      )}
      {renderInput()}
      {error && <p className="text-red-500 dark:text-red-400 text-xs mt-1">{error}</p>}
      {helperText && <p className="text-gray-500 dark:text-gray-400 text-xs mt-1">{helperText}</p>}
    </div>
  );
};

export default FormField;
