/**
 * Table Component
 * Tabla genérica reutilizable con acciones
 */

import React from 'react';

const Table = ({ columns, data, loading, onEdit, onDelete, onView }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-32">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-32 rounded-lg border bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 transition-colors">
        <p className="font-medium text-gray-500 dark:text-gray-400">No hay datos disponibles</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg shadow bg-white dark:bg-gray-800 transition-colors">
      <table className="w-full">
        <thead className="border-b bg-gray-100 dark:bg-gray-900 border-gray-200 dark:border-gray-700">
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                className={`px-6 py-3 text-left text-xs font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wider transition-colors ${
                  col.width ? `w-${col.width}` : ''
                }`}
              >
                {col.label}
              </th>
            ))}
            {(onEdit || onDelete || onView) && (
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wider transition-colors">
                Acciones
              </th>
            )}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={row.id || idx} className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition">
              {columns.map((col) => (
                <td key={`${row.id}-${col.key}`} className="px-6 py-4 text-sm text-gray-800 dark:text-gray-200 transition-colors">
                  {col.render ? col.render(row[col.key], row) : row[col.key]}
                </td>
              ))}
              {(onEdit || onDelete || onView) && (
                <td className="px-6 py-4 text-sm">
                  <div className="flex gap-2">
                    {onView && (
                      <button
                        onClick={() => onView(row)}
                        className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition text-xs font-medium"
                        title="Ver"
                      >
                        👁️
                      </button>
                    )}
                    {onEdit && (
                      <button
                        onClick={() => onEdit(row)}
                        className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded hover:bg-blue-200 dark:hover:bg-blue-900/50 transition text-xs font-medium"
                        title="Editar"
                      >
                        ✏️
                      </button>
                    )}
                    {onDelete && !row.is_superuser && (
                      <button
                        onClick={() => {
                          if (window.confirm('¿Estás seguro de que deseas eliminar?')) {
                            onDelete(row);
                          }
                        }}
                        className="px-3 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded hover:bg-red-200 dark:hover:bg-red-900/50 transition text-xs font-medium"
                        title="Eliminar"
                      >
                        🗑️
                      </button>
                    )}
                  </div>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Table;
