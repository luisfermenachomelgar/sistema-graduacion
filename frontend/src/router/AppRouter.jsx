/**
 * App Router Configuration
 * Defines all application routes
 */

import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from '../components/ProtectedRoute';
import AdminLayout from '../layouts/AdminLayout';
import useAuth from '../hooks/useAuth';

// Pages
import Login from '../pages/Login';
import Dashboard from '../pages/Dashboard';
import Postulantes from '../pages/Postulantes';
import Postulaciones from '../pages/Postulaciones';
import Documentos from '../pages/Documentos';
import Modalidades from '../pages/Modalidades';
import ModalidadDetalle from '../pages/ModalidadDetalle';
import Usuarios from '../pages/Usuarios';
import Reportes from '../pages/Reportes';

const InitialRedirect = () => {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) {
    return null;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  const userRole = user?.role || (user?.is_superuser ? 'admin' : null);
  return <Navigate to={userRole === 'estudiante' ? '/postulaciones' : '/dashboard'} replace />;
};

const AppRouter = () => {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />

        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <AdminLayout>
                <Dashboard />
              </AdminLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/postulantes"
          element={
            <ProtectedRoute>
              <AdminLayout>
                <Postulantes />
              </AdminLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/postulaciones"
          element={
            <ProtectedRoute>
              <AdminLayout>
                <Postulaciones />
              </AdminLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/documentos"
          element={
            <ProtectedRoute>
              <AdminLayout>
                <Documentos />
              </AdminLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/modalidades"
          element={
            <ProtectedRoute requiredRole={['admin', 'estudiante']}>
              <AdminLayout>
                <Modalidades />
              </AdminLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/modalidades/:id"
          element={
            <ProtectedRoute>
              <AdminLayout>
                <ModalidadDetalle />
              </AdminLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/usuarios"
          element={
            <ProtectedRoute requiredRole={['admin']}>
              <AdminLayout>
                <Usuarios />
              </AdminLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/reportes"
          element={
            <ProtectedRoute requiredRole={['admin']}>
              <AdminLayout>
                <Reportes />
              </AdminLayout>
            </ProtectedRoute>
          }
        />

        {/* Redirect root based on role */}
        <Route path="/" element={<InitialRedirect />} />

        {/* 404 Not Found */}
        <Route path="*" element={<InitialRedirect />} />
      </Routes>
    </Router>
  );
};

export default AppRouter;
