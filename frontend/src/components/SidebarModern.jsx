import React, { useState } from 'react';
import { LayoutDashboard, Users, FileCheck, BarChart3, ChevronRight, ChevronLeft, Clipboard, BookOpen, Shield } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import { useSidebarCollapse } from '../context/SidebarCollapseContext';

const Sidebar = () => {
  // Paleta local al componente (no toca configuraciones globales)
  const BRAND_DEEP = '#071740';
  const BRAND_MID = '#1E66B8';
  const BRAND_AZURE = '#6FD3FF';
  const TEXT_ON_DARK = '#EAF4FF';
  const MUTED = '#DCEBFF';
  const DIVIDER = '#6FD3FF14';
  const HOVER_TINT = '#1E66B81A';
  const ACTIVE_FILL = '#6FD3FF24';
  const location = useLocation();
  const { user } = useAuth();
  const { collapsed, setCollapsed } = useSidebarCollapse();

  const navigationItems = [
    {
      icon: LayoutDashboard,
      label: 'Inicio',
      href: '/dashboard',
      badge: null,
      roles: ['admin'],
    },
    {
      icon: Users,
      label: 'Postulantes',
      href: '/postulantes',
      badge: null,
      roles: ['admin'],
    },
    {
      icon: Clipboard,
      label: 'Postulaciones',
      href: '/postulaciones',
      badge: null,
      roles: ['admin', 'estudiante'],
    },
    {
      icon: FileCheck,
      label: 'Documentos',
      href: '/documentos',
      roles: ['admin', 'estudiante'],
    },
    {
      icon: BookOpen,
      label: 'Modalidades',
      href: '/modalidades',
      badge: null,
      roles: ['admin', 'estudiante'],
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
    ? navigationItems.filter((item) => item.roles.includes(effectiveRole))
    : navigationItems.filter((item) => basicMenuHrefs.has(item.href));

  const isActive = (href) => location.pathname === href || location.pathname.startsWith(href + '/');

  return (
    <aside 
      className={`sidebar-modern fixed left-0 top-0 h-screen ${collapsed ? 'w-20' : 'w-64'} relative transition-all duration-300 ease-in-out z-50 flex flex-col shadow-xl overflow-hidden`}
    >
      {/* Local styles using la paleta definida arriba (scoped al componente) */}
      <style>{` 
        .sidebar-modern{background:linear-gradient(180deg, ${BRAND_DEEP}, ${BRAND_MID});color:${TEXT_ON_DARK};border-right:1px solid ${DIVIDER};}
        .sidebar-modern .sidebar-overlay{background:${BRAND_DEEP}8c}
        .sidebar-modern .glass-layer{backdrop-filter: blur(6px);}
        .sidebar-modern .logo-header{border-bottom:1px solid ${DIVIDER}}
        .sidebar-modern .logo-box{background: ${BRAND_DEEP}20; border:1px solid ${BRAND_AZURE}22}
        .sidebar-modern .logo-title{color:${TEXT_ON_DARK}}
        .sidebar-modern .logo-sub{color:#B3CBE6}
        .sidebar-modern .nav-wrapper{padding-left:0}
        .sidebar-modern .nav{padding-left:1rem;padding-top:.75rem;padding-bottom:1rem}
        .sidebar-modern .nav-link{display:flex;align-items:center;justify-content:space-between;padding:.5rem .75rem;border-radius:.75rem;transition:all .18s ease;color:${MUTED}}
        .sidebar-modern .nav-link .left{display:flex;align-items:center;gap:.5rem}
        .sidebar-modern .nav-link .icon{color:${MUTED};transition:all .18s ease}
        .sidebar-modern .nav-link:hover{background:${HOVER_TINT};transform:translateX(4px)}
        .sidebar-modern .nav-link:hover .icon{color:${BRAND_MID};transform:scale(1.06)}
        .sidebar-modern .nav-link-active{background:${ACTIVE_FILL};border-left:4px solid ${BRAND_AZURE};box-shadow:0 1px 3px rgba(0,0,0,0.06)}
        .sidebar-modern .nav-link-active .icon{color:${BRAND_AZURE}}
        .sidebar-modern .nav-link-active .nav-label{color:${BRAND_DEEP}}
        .sidebar-modern .item-badge{background:transparent;color:#B23A3A}
        .sidebar-modern .item-badge--active{background:${BRAND_AZURE}33;color:${BRAND_DEEP}}
        .sidebar-modern .sidebar-divider{border-top:1px solid ${DIVIDER}}
        .sidebar-modern .collapse-btn{background:${BRAND_MID}1a;color:${TEXT_ON_DARK};border-radius:9999px;padding:.375rem}
        .sidebar-modern .collapse-btn:hover{background:${BRAND_MID}2a;transform:scale(1.06)}
        .sidebar-modern .chev{color:${BRAND_AZURE}}
      `}</style>
      {/* Glass Layer (Blur Real) */}
      <div className="absolute inset-0 glass-layer bg-transparent z-0" />
      
      {/* Dark Overlay Suave */}
      <div className="absolute inset-0 sidebar-overlay backdrop-blur-sm z-0" />
      
      {/* Content Layer */}
      <div className="relative z-10 flex flex-col h-full drop-shadow-sm">
        {/* Logo */}
        {!collapsed && (
        <div className="p-4 logo-header flex flex-col items-center transition-all duration-300 ease-in-out opacity-100">
          <div className="w-24 h-24 rounded-xl overflow-hidden logo-box flex items-center justify-center mb-4 transition-all duration-300 ease-in-out">
            <img
              src="/images/uabjb.png"
              alt="Logo Universidad"
              className="w-20 h-20 object-contain transition-all duration-300 ease-in-out"
            />
          </div>
          <div className="text-center transition-all duration-300 ease-in-out">
            <h1 className="text-lg font-semibold logo-title tracking-wide transition-all duration-300 ease-in-out">Graduación</h1>
            <p className="text-xs logo-sub transition-all duration-300 ease-in-out">Sistema de Gestión</p>
          </div>
        </div>
        )}

        {/* Navegación + Separador + Configuración */}
        <div className="flex flex-col flex-1 justify-center transition-all duration-300 ease-in-out nav-wrapper">
          {/* Navegación */}
          <nav className="nav px-3 pt-1 pb-2 space-y-3 transition-all duration-300 ease-in-out">
            {visibleItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);

              return (
                <Link
                  key={item.href}
                  to={item.href}
                  className={`nav-link ${
                    active
                      ? 'nav-link-active'
                      : ''
                  } group`}
                >
                  <div className="left">
                    <Icon className="icon w-5 h-5 transition-all duration-300 ease-in-out group-hover:scale-110" />
                    {!collapsed && <span className={`nav-label font-medium tracking-wide transition-all duration-300 ease-in-out`}>{item.label}</span>}
                  </div>
                  {item.badge && (
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${active ? 'item-badge--active' : 'item-badge'}`}>
                      {item.badge}
                    </span>
                  )}
                  {active && <ChevronRight className="w-5 h-5 chev opacity-0 group-hover:opacity-100 transition-all duration-200" />}
                </Link>
              );
            })}
          </nav>
          {/* Separador */}
          <div className="mx-4 my-2 sidebar-divider transition-all duration-300 ease-in-out"></div>
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
