/**
 * Admin Layout Component
 * Wraps protected pages with Header and Sidebar
 * Includes global loader for HTTP requests
 * Includes global notification system (react-hot-toast)
 */

import { Toaster } from 'react-hot-toast';
import Header from '../components/Header';
import SidebarModern from '../components/SidebarModern';
import { SidebarCollapseProvider, useSidebarCollapse } from '../context/SidebarCollapseContext';
import useAuth from '../hooks/useAuth';

const AdminLayoutContent = ({ children }) => {
  const { collapsed } = useSidebarCollapse();
  const { user, logout } = useAuth();

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-slate-900">
      {/* Global Notifications */}
      <Toaster
        position="top-right"
        reverseOrder={false}
        gutter={8}
        toastOptions={{
          duration: 4000,
          // Default container style left neutral; toasts will provide their own styling
          style: {
            background: 'transparent',
            color: '#fff',
            boxShadow: 'none',
          },
        }}
      />

      {/* Sidebar */}
      <SidebarModern />

      {/* Right Content Area */}
      <div className="flex flex-col flex-1 transition-all duration-300 ease-in-out">
        {/* Header */}
        <Header user={user} onLogout={logout} />

        {/* Main Content */}
        <main className="relative flex-1 overflow-auto bg-gray-50 dark:bg-slate-900">
          <div className="px-4 py-6 max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

const AdminLayout = ({ children }) => {
  return (
    <SidebarCollapseProvider>
      <AdminLayoutContent>{children}</AdminLayoutContent>
    </SidebarCollapseProvider>
  );
};

export default AdminLayout;
