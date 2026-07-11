/**
 * Sidebar Component
 * Navigation menu for admin sections
 */

import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import useAuth from '../hooks/useAuth';

const Sidebar = () => {
  const location = useLocation();
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(true);

  const menuItems = [
    {
      label: 'Dashboard',
      href: '/dashboard',
      icon: '📊',
      roles: ['admin'],
    },
    {
      label: 'Postulantes',
      href: '/postulantes',
      icon: '👥',
      roles: ['admin'],
    },
    {
      label: 'Postulaciones',
      href: '/postulaciones',
      icon: '📋',
      roles: ['admin', 'estudiante'],
    },
    {
      label: 'Documentos',
      href: '/documentos',
      icon: '📄',
      roles: ['admin', 'estudiante'],
    },
    {
      label: 'Modalidades',
      href: '/modalidades',
      icon: '🎓',
      roles: ['admin', 'estudiante'],
    },
    {
      label: 'Usuarios',
      href: '/usuarios',
      icon: '🔐',
      roles: ['admin'],
    },
    {
      label: 'Reportes',
      href: '/reportes',
      icon: '📈',
      roles: ['admin'],
    },
  ];

  const resolveRole = () => {
    if (user?.role) return user.role;
    if (user?.is_superuser === true) return 'admin';
    return null;
  };

  const basicMenuHrefs = new Set([
    '/dashboard',
    '/postulantes',
    '/postulaciones',
    '/documentos',
  ]);

  const effectiveRole = resolveRole();

  const visibleItems = effectiveRole
    ? menuItems.filter((item) => item.roles.includes(effectiveRole))
    : menuItems.filter((item) => basicMenuHrefs.has(item.href));

  const isActive = (href) => location.pathname === href;

  return (
    <aside className={`bg-gray-800 text-white transition-all duration-300 ${isOpen ? 'w-64' : 'w-20'}`}>
      <div className="p-4">
        {/* Toggle Button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center justify-center w-full p-2 rounded hover:bg-gray-700"
        >
          {isOpen ? '←' : '→'}
        </button>

        {/* Menu Items */}
        <nav className="mt-8 space-y-2">
          {visibleItems.map((item) => (
            <Link
              key={item.href}
              to={item.href}
              className={`flex items-center space-x-3 px-4 py-2 rounded transition ${
                isActive(item.href)
                  ? 'bg-blue-600 text-white'
                  : 'hover:bg-gray-700'
              }`}
              title={!isOpen ? item.label : ''}
            >
              <span className="text-xl">{item.icon}</span>
              {isOpen && <span>{item.label}</span>}
            </Link>
          ))}
        </nav>
      </div>

      {/* User Role Badge */}
      {isOpen && (
        <div className="absolute bottom-4 left-4 right-4 bg-gray-700 p-2 rounded text-xs text-center">
          Role: <strong>{user?.role_display}</strong>
        </div>
      )}
    </aside>
  );
};

export default Sidebar;
