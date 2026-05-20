/**
 * Generic API Service
 * Handles CRUD operations for all resources
 */

import axiosInstance from './axios';
import { API_CONFIG } from '../constants/api';

class ApiService {
  /**
   * GET - Fetch all items
   * @param {string} endpoint
   * @param {object} params - Query parameters
   * @returns {Promise}
   */
  async getAll(endpoint, params = {}, requestConfig = {}) {
    try {
      const response = await axiosInstance.get(endpoint, { params, ...requestConfig });
      return { success: true, data: response.data };
    } catch (error) {
      return this._handleError(error);
    }
  }

  /**
   * GET - Fetch single item by ID
   * @param {string} endpoint
   * @returns {Promise}
   */
  async getById(endpoint) {
    try {
      const response = await axiosInstance.get(endpoint);
      return { success: true, data: response.data };
    } catch (error) {
      return this._handleError(error);
    }
  }

  /**
   * POST - Create new item
   * @param {string} endpoint
   * @param {object} data
   * @returns {Promise}
   */
  async create(endpoint, data, requestConfig = {}) {
    try {
      const response = await axiosInstance.post(endpoint, data, requestConfig);
      return { success: true, data: response.data };
    } catch (error) {
      return this._handleError(error);
    }
  }

  /**
   * PUT - Update entire item
   * @param {string} endpoint
   * @param {object} data
   * @returns {Promise}
   */
  async update(endpoint, data, requestConfig = {}) {
    try {
      const response = await axiosInstance.put(endpoint, data, requestConfig);
      return { success: true, data: response.data };
    } catch (error) {
      return this._handleError(error);
    }
  }

  /**
   * PATCH - Partial update
   * @param {string} endpoint
   * @param {object} data
   * @returns {Promise}
   */
  async patch(endpoint, data, requestConfig = {}) {
    try {
      const response = await axiosInstance.patch(endpoint, data, requestConfig);
      return { success: true, data: response.data };
    } catch (error) {
      return this._handleError(error);
    }
  }

  /**
   * DELETE - Remove item
   * @param {string} endpoint
   * @returns {Promise}
   */
  async delete(endpoint, requestConfig = {}) {
    try {
      await axiosInstance.delete(endpoint, requestConfig);
      return { success: true };
    } catch (error) {
      return this._handleError(error);
    }
  }

  /**
   * Handle errors consistently
   * @private
   */
  _handleError(error) {
    const data = error.response?.data;
    let message = 'An error occurred';

    const stringifyFieldErrors = (errors, prefix = '') => {
      if (!errors || typeof errors !== 'object' || Array.isArray(errors)) {
        return [];
      }

      return Object.entries(errors).flatMap(([key, value]) => {
        const fieldName = prefix ? `${prefix}.${key}` : key;

        if (Array.isArray(value)) {
          return value.map((item) => `${fieldName}: ${item}`);
        }

        if (value && typeof value === 'object') {
          return stringifyFieldErrors(value, fieldName);
        }

        return [`${fieldName}: ${value}`];
      });
    };

    // Prefer serializer field errors if present
    if (data && typeof data === 'object' && !Array.isArray(data)) {
      const fieldSource = data.field_errors || data;
      const fieldMessages = stringifyFieldErrors(fieldSource).filter((entry) => {
        return !entry.startsWith('success:') && !entry.startsWith('error:') && !entry.startsWith('timestamp:');
      });

      if (fieldMessages.length > 0) {
        message = fieldMessages.join(' | ');
      }
    }

    if (message === 'An error occurred') {
      message =
        data?.error ||
        data?.detail ||
        data?.message ||
        (Array.isArray(data?.non_field_errors) ? data.non_field_errors[0] : data?.non_field_errors) ||
        error.message ||
        'An error occurred';
    }

    console.error('API Error:', message);

    return {
      success: false,
      error: message,
      status: error.response?.status,
    };
  }
}

export default new ApiService();
