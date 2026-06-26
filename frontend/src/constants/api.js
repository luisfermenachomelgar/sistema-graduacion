/**
 * API Configuration for Django Backend
 * Compatible with djangorestframework-simplejwt
 */

// Detect environment
const isDevelopment = import.meta.env.DEV;

// Base URL configuration for API requests
let baseUrl;
if (isDevelopment) {
  // During development, use relative paths
  // Vite dev server (localhost:5173) has a proxy configured to forward /api to localhost:8000
  // This avoids CORS issues because requests come from the same origin
  baseUrl = '';
} else {
  // In production, use the full URL from environment or default
  baseUrl = import.meta.env.VITE_API_URL || 'http://localhost';
}

// Public server URL for accessing non-API resources (e.g., /media files)
// Must always be a full URL (http://host:port)
let publicServerUrl;
if (isDevelopment) {
  // In development, media files are served through nginx on port 80
  publicServerUrl = 'http://localhost';
} else {
  // In production, extract host from API URL and remove /api suffix
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost';
  publicServerUrl = apiUrl.replace(/\/api\/?$/, '') || 'http://localhost';
}

export const API_CONFIG = {
  // Backend URL for API requests - Adjust based on environment
  BASE_URL: baseUrl,
  
  // Public server URL for accessing resources like /media files
  PUBLIC_SERVER_URL: publicServerUrl,
  
  // Endpoints
  ENDPOINTS: {
    // Authentication
    LOGIN: '/api/auth/login/',
    REFRESH_TOKEN: '/api/auth/refresh/',
    
    // Postulantes (Applicants)
    POSTULANTES: '/api/postulantes/',
    POSTULANTE_DETAIL: (id) => `/api/postulantes/${id}/`,
    
    // Postulaciones (Applications)
    POSTULACIONES: '/api/postulaciones/',
    POSTULACION_DETAIL: (id) => `/api/postulaciones/${id}/`,
    POSTULACION_AVANZAR_ETAPA: (id) => `/api/postulaciones/${id}/avanzar-etapa/`,
    POSTULACION_HISTORIAL: (id) => `/api/postulaciones/${id}/historial/`,
    
    // Documentos (Documents)
    DOCUMENTOS: '/api/documentos/',
    DOCUMENTO_DETAIL: (id) => `/api/documentos/${id}/`,
    TIPOS_DOCUMENTO: '/api/tipos-documento/',
    
    // Modalidades (Modalities)
    MODALIDADES: '/api/modalidades/',
    MODALIDAD_DETAIL: (id) => `/api/modalidades/${id}/`,
    MODALIDAD_TIPOS_DOCUMENTO: (id) => `/api/modalidades/${id}/tipos-documento/`,
    MODALIDAD_REQUISITOS: (id) => `/api/modalidades/${id}/requisitos/`,
    MODALIDAD_REQUISITO_DETAIL: (modalidadId, requisitoId) => `/api/modalidades/${modalidadId}/requisitos/${requisitoId}/`,
    MODALIDAD_REQUISITO_DESCARGAR: (modalidadId, requisitoId) => `/api/modalidades/${modalidadId}/requisitos/${requisitoId}/descargar/`,
    MODALIDAD_REQUISITO_PREVIEW: (modalidadId, requisitoId) => `/api/modalidades/${modalidadId}/requisitos/${requisitoId}/preview/`,
    ETAPAS: '/api/etapas/',
    ETAPA_DETAIL: (id) => `/api/etapas/${id}/`,
    
    // Usuarios (Users)
    USUARIOS: '/api/usuarios/',
    USUARIO_DETAIL: (id) => `/api/usuarios/${id}/`,
    
    // Auditoria
    AUDITORIA: '/api/auditoria/',
    
    // Reportes (Reports)
    DASHBOARD_GENERAL: '/api/reportes/dashboard-general/',
    ESTADISTICAS_TUTORES: '/api/reportes/estadisticas-tutores/',
    EXPORTAR_ESTADISTICAS: '/api/reportes/estadisticas-tutores/exportar/',
    EFICIENCIA_CARRERAS: '/api/reportes/eficiencia-carreras/',
    
    // Documentation
    SCHEMA: '/api/schema/',
    DOCS: '/api/docs/',
  },

  // Token Storage Keys
  STORAGE_KEYS: {
    ACCESS_TOKEN: 'access_token',
    REFRESH_TOKEN: 'refresh_token',
    USER_INFO: 'user_info',
  },

  // Token expiration times (in seconds)
  TOKEN_EXPIRY: {
    ACCESS: 3600,      // 1 hour
    REFRESH: 604800,   // 7 days
  },

  // HTTP Status Codes
  STATUS_CODES: {
    OK: 200,
    CREATED: 201,
    BAD_REQUEST: 400,
    UNAUTHORIZED: 401,
    FORBIDDEN: 403,
    NOT_FOUND: 404,
    CONFLICT: 409,
    SERVER_ERROR: 500,
  },
};

export const ROLE_TYPES = {
  ADMIN: 'admin',
  ADMINISTRATIVO: 'administ',
  ESTUDIANTE: 'estudiante',
};

export const ESTADO_POSTULACION = {
  BORRADOR: 'borrador',
  EN_REVISION: 'en_revision',
  APROBADA: 'aprobada',
  RECHAZADA: 'rechazada',
};

export const ESTADO_DOCUMENTO = {
  PENDIENTE: 'pendiente',
  APROBADO: 'aprobado',
  RECHAZADO: 'rechazado',
};
