/**
 * useCrud Hook
 * Encapsula operaciones CRUD comunes con estado de carga y error.
 */

import { useCallback, useRef, useState } from 'react';
import api from '../api/api';

const normalizeList = (data) => (Array.isArray(data) ? data : data?.results || []);

export const useCrud = (listEndpoint) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [meta, setMeta] = useState({ count: 0, next: null, previous: null });
  const lastParamsRef = useRef({});

  const list = useCallback(
    async (params = {}, options = {}) => {
      lastParamsRef.current = params;
      setLoading(true);
      try {
        const result = await api.getAll(listEndpoint, params, options.requestConfig || {});
        if (result.success) {
          const normalized = normalizeList(result.data);
          setData(normalized);
          if (result.data && typeof result.data === 'object' && !Array.isArray(result.data)) {
            setMeta({
              count: result.data.count ?? normalized.length,
              next: result.data.next ?? null,
              previous: result.data.previous ?? null,
            });
          } else {
            setMeta({
              count: normalized.length,
              next: null,
              previous: null,
            });
          }
        } else {
          setError(result.error || options.errorMessage || 'Error al cargar');
        }
        return result;
      } catch (err) {
        const message = options.exceptionMessage || options.errorMessage || 'Error al cargar';
        setError(message);
        return { success: false, error: message };
      } finally {
        setLoading(false);
      }
    },
    [listEndpoint]
  );

  const refresh = useCallback(
    async (options = {}) => list(lastParamsRef.current || {}, options),
    [list]
  );

  const create = useCallback(async (payload, requestConfig = {}) => api.create(listEndpoint, payload, requestConfig), [listEndpoint]);
  const update = useCallback(async (endpoint, payload, requestConfig = {}) => api.update(endpoint, payload, requestConfig), []);
  const patch = useCallback(async (endpoint, payload, requestConfig = {}) => api.patch(endpoint, payload, requestConfig), []);
  const remove = useCallback(async (endpoint, requestConfig = {}) => api.delete(endpoint, requestConfig), []);

  return {
    data,
    loading,
    error,
    setError,
    meta,
    list,
    refresh,
    create,
    update,
    patch,
    remove,
  };
};

export default useCrud;
