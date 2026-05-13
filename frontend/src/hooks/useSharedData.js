/**
 * useSharedData Hook
 * 
 * Provides a shared, in-memory cache layer for API calls with:
 * - Deduplication of in-flight requests
 * - Automatic caching of resolved data
 * - Prevention of duplicate API calls
 * - Clean error handling
 * 
 * MODO DIAGNÓSTICO: Instrumentación completa de cache hits, duración, y estado
 * 
 * Architecture:
 * - Uses a global Map to store cache entries
 * - Each cache entry contains: { data, promise, error, timestamp }
 * - Returns { data, error, isLoading, fetch, clear, clearAll }
 * - Uses axios interceptor's global loader (no local spinners)
 */

import { useState, useCallback, useRef } from 'react';
import api from '../api/api';
import diagnostics from '../utils/diagnosticsLogger';

/**
 * Global cache store for all API calls
 * Key: cacheKey (usually the endpoint)
 * Value: { data, promise, error, timestamp }
 */
const globalCache = new Map();

/**
 * Custom hook for shared data fetching with caching
 * @param {string} endpoint - API endpoint to fetch from
 * @param {object} options - Configuration options
 * @param {boolean} options.deduplicateOnly - If true, only prevents duplicate in-flight requests
 * @param {number} options.cacheTime - How long to cache data in milliseconds (0 = indefinite)
 * @returns {object} - { data, error, isLoading, fetch, clear, clearAll }
 */
export const useSharedData = (endpoint, options = {}) => {
  const {
    deduplicateOnly = false,
    cacheTime = 0, // 0 means cache forever until explicit clear
  } = options;

  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Track if component is mounted to avoid state updates on unmounted component
  const isMountedRef = useRef(true);

  /**
   * Generate a cache key from endpoint and any parameters
   * @param {string} ep - The endpoint
   * @param {object} params - Query parameters
   * @returns {string} - Cache key
   */
  const getCacheKey = (ep, params = {}) => {
    const paramStr = Object.entries(params)
      .sort(([keyA], [keyB]) => keyA.localeCompare(keyB))
      .map(([k, v]) => `${k}=${JSON.stringify(v)}`)
      .join('&');
    return `${ep}${paramStr ? '?' + paramStr : ''}`;
  };

  /**
   * Check if cache entry is still valid
   * @param {object} entry - Cache entry
   * @returns {boolean}
   */
  const isCacheValid = (entry) => {
    if (!entry) return false;
    if (cacheTime === 0) return true; // Indefinite cache
    const elapsed = Date.now() - entry.timestamp;
    return elapsed < cacheTime;
  };

  /**
   * Fetch data with intelligent caching and deduplication
   * @param {object} params - Query parameters
   * @returns {Promise}
   */
  const fetch = useCallback(
    async (params = {}) => {
      const cacheKey = getCacheKey(endpoint, params);
      const existingEntry = globalCache.get(cacheKey);
      
      // LOGS: Diagnóstico de fetch
      console.log('%c[SHARED_DATA] 🔍 fetch() called', 'color: #a78bfa; font-weight: bold', { endpoint, params });
      diagnostics.logHookInit('useSharedData.fetch', 'useSharedData', endpoint, params);
      console.log(`%c[SHARED_DATA] 🔑 Cache Key: %c${cacheKey}`, 'color: #a78bfa', 'color: #6b7280; font-family: monospace');

      // Case 1: We have a promise in-flight, wait for it (DEDUPLICATION)
      if (existingEntry?.promise) {
        console.log('%c[SHARED_DATA] ⏳ DEDUPLICATION: Promise in-flight - waiting for existing request', 'color: #f59e0b; font-weight: bold');
        diagnostics.logStateChange('useSharedData', 'deduplication-in-flight', false, true);
        try {
          const result = await existingEntry.promise;
          if (isMountedRef.current) {
            setData(result.data);
            setError(null);
            setIsLoading(false);
          }
          console.log('%c[SHARED_DATA] ✅ In-flight promise resolved (deduplicated)', 'color: #10b981; font-weight: bold');
          diagnostics.logStateChange('useSharedData', 'deduplication-resolved', false, true);
          return result;
        } catch (err) {
          if (isMountedRef.current) {
            setError(err.error || err.message || 'Error al cargar datos');
            setIsLoading(false);
          }
          console.log('%c[SHARED_DATA] ❌ In-flight promise rejected:', 'color: #ef4444; font-weight: bold', err);
          throw err;
        }
      }

      // Case 2: We have valid cached data (CACHE HIT)
      if (!deduplicateOnly && existingEntry?.data && isCacheValid(existingEntry)) {
        console.log('%c[SHARED_DATA] 💾 CACHE HIT: Using cached data (valid)', 'color: #10b981; font-weight: bold');
        console.log(`%c[SHARED_DATA] ⏱️  Cache age: ${((Date.now() - existingEntry.timestamp) / 1000).toFixed(2)}s`, 'color: #10b981');
        diagnostics.logStateChange('useSharedData', 'cache-hit', false, true);
        if (isMountedRef.current) {
          setData(existingEntry.data);
          setError(null);
          setIsLoading(false);
        }
        return { success: true, data: existingEntry.data };
      }

      // Case 3: Need to make API call (CACHE MISS)
      console.log('%c[SHARED_DATA] 🚀 CACHE MISS: Making NEW API call', 'color: #f59e0b; font-weight: bold');
      diagnostics.logStateChange('useSharedData', 'cache-miss', false, true);
      if (isMountedRef.current) {
        setIsLoading(true);
      }

      // Create the promise for the API call
      const fetchPromise = api.getAll(endpoint, params);
      const requestStartTime = performance.now();

      // Store the promise immediately to deduplicate concurrent requests
      globalCache.set(cacheKey, {
        promise: fetchPromise,
        data: null,
        error: null,
        timestamp: Date.now(),
      });

      try {
        const result = await fetchPromise;
        const requestDuration = performance.now() - requestStartTime;
        console.log(`%c[SHARED_DATA] 📦 Response received in ${requestDuration.toFixed(2)}ms`, 'color: #10b981; font-weight: bold');

        if (result.success) {
          // Update cache with resolved data
          globalCache.set(cacheKey, {
            promise: null,
            data: result.data,
            error: null,
            timestamp: Date.now(),
          });

          if (isMountedRef.current) {
            setData(result.data);
            setError(null);
          }
          console.log('%c[SHARED_DATA] ✅ Data cached and state updated', 'color: #10b981; font-weight: bold');
          diagnostics.logStateChange('useSharedData', 'data-cached', null, result.data);
        } else {
          const err = result.error || 'Error al cargar datos';
          globalCache.set(cacheKey, {
            promise: null,
            data: null,
            error: err,
            timestamp: Date.now(),
          });

          if (isMountedRef.current) {
            setError(err);
            setData(null);
          }
          console.log('%c[SHARED_DATA] ⚠️ API returned error:', 'color: #ef4444; font-weight: bold', err);
          diagnostics.logStateChange('useSharedData', 'api-error', null, err);
        }

        return result;
      } catch (err) {
        const requestDuration = performance.now() - requestStartTime;
        console.log(`%c[SHARED_DATA] ❌ Exception after ${requestDuration.toFixed(2)}ms:`, 'color: #ef4444; font-weight: bold', err);
        diagnostics.logStateChange('useSharedData', 'exception', null, err.message || err);
        
        const errorMsg = err.message || 'Error al cargar datos';
        globalCache.set(cacheKey, {
          promise: null,
          data: null,
          error: errorMsg,
          timestamp: Date.now(),
        });

        if (isMountedRef.current) {
          setError(errorMsg);
          setData(null);
        }

        throw { success: false, error: errorMsg };
      } finally {
        if (isMountedRef.current) {
          setIsLoading(false);
        }
      }
    },
    [endpoint, deduplicateOnly, cacheTime]
  );

  /**
   * Clear cache for this specific endpoint
   */
  const clear = useCallback(() => {
    globalCache.delete(getCacheKey(endpoint));
    if (isMountedRef.current) {
      setData(null);
      setError(null);
    }
  }, [endpoint]);

  /**
   * Clear all cached data
   */
  const clearAll = useCallback(() => {
    globalCache.clear();
    if (isMountedRef.current) {
      setData(null);
      setError(null);
    }
  }, []);

  /**
   * Get current cached data without loading
   */
  const getCached = useCallback(() => {
    const cacheKey = getCacheKey(endpoint);
    const entry = globalCache.get(cacheKey);
    return entry?.data || null;
  }, [endpoint]);

  // Cleanup: mark as unmounted when component unmounts
  useRef(() => {
    return () => {
      isMountedRef.current = false;
    };
  }).current;

  return {
    data,
    error,
    isLoading,
    fetch,
    clear,
    clearAll,
    getCached,
  };
};

/**
 * Debug helper to inspect global cache (development only)
 */
export const inspectCache = () => {
  if (import.meta.env.DEV) {
    console.log('Global Cache:', Object.fromEntries(globalCache));
  }
};

export default useSharedData;
