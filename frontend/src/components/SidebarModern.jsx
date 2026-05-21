import React, { useState } from 'react';
import { LayoutDashboard, Users, FileCheck, BarChart3, ChevronRight, ChevronLeft, Clipboard, BookOpen, Shield } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import { useSidebarCollapse } from '../context/SidebarCollapseContext';

const Sidebar = () => {
  const location = useLocation();
  const { user } = useAuth();
  const { collapsed, setCollapsed } = useSidebarCollapse();

  const navigationItems = [
    {
      icon: LayoutDashboard,
      label: 'Inicio',
      href: '/dashboard',
      badge: null,
      roles: ['admin', 'administ'],
    },
    {
      icon: Users,
      label: 'Postulantes',
      href: '/postulantes',
      badge: null,
      roles: ['admin', 'administ', 'estudiante'],
    },
    {
      icon: Clipboard,
      label: 'Postulaciones',
      href: '/postulaciones',
      badge: null,
      roles: ['admin', 'administ', 'estudiante'],
    },
    {
      icon: FileCheck,
      label: 'Documentos',
      href: '/documentos',
      roles: ['admin', 'administ', 'estudiante'],
    },
    {
      icon: BookOpen,
      label: 'Modalidades',
      href: '/modalidades',
      badge: null,
      roles: ['admin', 'administ'],
    },
    {
      icon: Shield,
      label: 'Usuarios',
      href: '/usuarios',
      badge: null,
      roles: ['admin'],
    },
    {
      icon: BarChart3,
      label: 'Reportes',
      href: '/reportes',
      badge: null,
      roles: ['admin', 'administ'],
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
    ? navigationItems.filter((item) => item.roles.includes(effectiveRole))
    : navigationItems.filter((item) => basicMenuHrefs.has(item.href));

  const isActive = (href) => location.pathname === href || location.pathname.startsWith(href + '/');

  return (
    <aside 
      className={`fixed left-0 top-0 h-screen ${collapsed ? 'w-20' : 'w-64'} relative text-white transition-all duration-300 ease-in-out z-50 flex flex-col shadow-xl border-r border-white/10 overflow-hidden`}
    >
      {/* Background Image Layer */}
      <div 
        className="absolute inset-0 bg-cover bg-center opacity-100 z-0"
        style={{ backgroundImage: "url('/images/universidad.jpg')" }}
      />
      
      {/* Glass Layer (Blur Real) */}
      <div className="absolute inset-0 backdrop-blur-none bg-white/0 z-0" />
      
      {/* Dark Overlay Suave */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-0" />
      
      {/* Content Layer */}
      <div className="relative z-10 flex flex-col h-full text-white drop-shadow-xl">
        {/* Logo */}
        {!collapsed && (
        <div className="p-4 border-b border-white/20 flex flex-col items-center transition-all duration-300 ease-in-out opacity-100">
          <div className="w-24 h-24 rounded-xl overflow-hidden bg-white/10 backdrop-blur flex items-center justify-center mb-4 transition-all duration-300 ease-in-out">
            <img
              src="/images/uabjb.png"
              alt="Logo Universidad"
              className="w-20 h-20 object-contain transition-all duration-300 ease-in-out"
            />
          </div>
          <div className="text-center transition-all duration-300 ease-in-out">
            <h1 className="text-lg font-semibold text-white tracking-wide transition-all duration-300 ease-in-out">Graduación</h1>
            <p className="text-xs text-gray-300 transition-all duration-300 ease-in-out">Sistema de Gestión</p>
          </div>
        </div>
        )}

        {/* Navegación + Separador + Configuración */}
        <div className="flex flex-col flex-1 justify-center transition-all duration-300 ease-in-out">
          {/* Navegación */}
          <nav className="px-3 pt-1 pb-2 space-y-3 transition-all duration-300 ease-in-out">
            {visibleItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);

              return (
                <Link
                  key={item.href}
                  to={item.href}
                  className={`flex items-center justify-between px-3 py-2 rounded-xl transition-all duration-200 ease-out group ${
                    active
                      ? 'bg-blue-500/20 bg-white/10 text-white shadow-lg shadow-inner'
                      : 'text-white hover:bg-white/5 hover:translate-x-1'
                  }`}
                >
                  <div className="flex items-center gap-2 transition-all duration-300 ease-in-out">
                    <Icon className="w-5 h-5 transition-all duration-300 ease-in-out group-hover:scale-110" />
                    {!collapsed && <span className="font-medium tracking-wide transition-all duration-300 ease-in-out">{item.label}</span>}
                  </div>
                  {item.badge && (
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                      active
                        ? 'bg-white/20 text-white'
                        : 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
                    }`}>
                      {item.badge}
                    </span>
                  )}
                  {active && <ChevronRight className="w-5 h-5 opacity-0 group-hover:opacity-100 transition-all duration-200" />}
                </Link>
              );
            })}
          </nav>
          {/* Separador */}
          <div className="mx-4 my-1 border-t border-white/20 transition-all duration-300 ease-in-out"></div>
        </div>

        {/* Botón Colapsar */}
        <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 transition-all duration-300 ease-in-out">
          <button 
            onClick={() => setCollapsed(!collapsed)}
            className="rounded-full bg-white/10 hover:bg-white/20 transition-all duration-300 ease-in-out hover:scale-110 p-1.5 text-white"
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
