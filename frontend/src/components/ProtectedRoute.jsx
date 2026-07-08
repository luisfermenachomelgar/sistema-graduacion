/**
 * Protected Route Component
 * Restricts access to authenticated users only
 */

import { Navigate, useLocation } from 'react-router-dom';
import useAuth from '../hooks/useAuth';

const ProtectedRoute = ({ children, requiredRole = null }) => {
  const { isAuthenticated, loading, user } = useAuth();
  const location = useLocation();

  const getUserRole = () => user?.role || (user?.is_superuser ? 'admin' : null);

  if (loading) {
    return null;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (location.pathname === '/dashboard' && getUserRole() === 'estudiante') {
    return <Navigate to="/postulaciones" replace />;
  }

  /**
   * Role-based access control (FASE 2 BLOQUE 2)
   * 
   * Security policy:
   * - Routes WITHOUT requiredRole: ANY authenticated user can access
   * - Routes WITH requiredRole: User MUST have matching role
   * 
   * Role resolution:
   * 1. First try user.role field (set by backend)
   * 2. Fallback to is_superuser (Django privilege flag)
   * 3. If both null/false: Access denied for restricted routes
   */
  if (requiredRole) {
    // Resolve user role: prefer explicit role field, fallback to Django superuser flag
    const userRole = user?.role || (user?.is_superuser ? 'admin' : null);
    const allowedRoles = Array.isArray(requiredRole) ? requiredRole : [requiredRole];
    
    // Explicit validation: deny access if user has no role assigned
    // This prevents access with null/undefined role to protected routes
    if (!userRole) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-red-600 mb-4">Acceso Denegado</h1>
            <p className="text-gray-600">Usuario sin rol asignado. Contacta al administrador.</p>
            <a href="/dashboard" className="mt-4 inline-block px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
              Volver al Dashboard
            </a>
          </div>
        </div>
      );
    }
    
    // Check if user role is in the allowed roles list
    if (!allowedRoles.includes(userRole)) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-red-600 mb-4">Acceso Denegado</h1>
            <p className="text-gray-600">No tienes permisos para acceder a esta página.</p>
            <a href="/dashboard" className="mt-4 inline-block px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
              Volver al Dashboard
            </a>
          </div>
        </div>
      );
    }
  }

  return children;
};

export default ProtectedRoute;
