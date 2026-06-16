import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Bell, User, LogOut, Settings, Moon, Sun, HelpCircle } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import Modal from './Modal';
import HelpCenter from './HelpCenter';

const Header = ({ user, onLogout }) => {
  // Paleta corporativa (reutiliza exactamente la del Sidebar)
  const BRAND_DEEP = '#071740';
  const BRAND_MID = '#1E66B8';
  const BRAND_AZURE = '#6FD3FF';
  const TEXT_ON_DARK = '#EAF4FF';
  const MUTED = '#DCEBFF';
  const DIVIDER = '#6FD3FF14';
  const HOVER_TINT = '#1E66B81A';
  const ACTIVE_FILL = '#6FD3FF24';

  const navigate = useNavigate();
  const { isDark, toggleTheme } = useTheme();
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  
  const notificationsRef = useRef(null);
  const notificationsButtonRef = useRef(null);
  const userMenuRef = useRef(null)
  const userMenuButtonRef = useRef(null)

  useEffect(() => {
    const handleClickOutside = (event) => {
      // Cerrar notificaciones si hace clic fuera
      if (
        notificationsRef.current &&
        notificationsButtonRef.current &&
        !notificationsRef.current.contains(event.target) &&
        !notificationsButtonRef.current.contains(event.target)
      ) {
        setShowNotifications(false)
      }

      // Cerrar menú de usuario si hace clic fuera
      if (
        userMenuRef.current &&
        userMenuButtonRef.current &&
        !userMenuRef.current.contains(event.target) &&
        !userMenuButtonRef.current.contains(event.target)
      ) {
        setShowUserMenu(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <>
    <header className="sticky top-0 z-40 border-b transition-all duration-300" style={{ 
      background: `linear-gradient(90deg, ${BRAND_DEEP} 0%, ${BRAND_MID} 50%, ${BRAND_DEEP} 100%)`,
      backdropFilter: 'blur(12px)',
      borderColor: DIVIDER
    }}>
      <style>{`
        .header-dropdown {
          /* Reutiliza gradiente corporativo del Sidebar */
          background: linear-gradient(180deg, ${BRAND_DEEP}, ${BRAND_MID});
          /* Fallback sólido para garantizar opacidad sobre contenido detrás */
          background-color: ${BRAND_DEEP};
          -webkit-backdrop-filter: blur(16px);
          backdrop-filter: blur(16px);
        }

        .header-search {
          border-color: ${DIVIDER};
          background-color: ${BRAND_DEEP};
          color: ${BRAND_MID};
        }

        .header-search:focus {
          outline: none;
          border-color: ${BRAND_AZURE};
          box-shadow: 0 0 0 2px ${BRAND_AZURE};
        }

        .header-search::placeholder {
          color: ${MUTED};
        }

        .header-action {
          color: ${MUTED};
          transition: color .18s ease, background .18s ease;
        }

        .header-action:hover {
          color: ${BRAND_AZURE};
          background-color: ${HOVER_TINT};
        }

        .header-dropdown-item:hover {
          background-color: ${HOVER_TINT};
        }

        .header-dropdown-text {
          color: ${TEXT_ON_DARK};
        }

        .header-dropdown-meta {
          color: ${MUTED};
        }

        .header-user-name {
          color: ${MUTED};
        }

        .header-logout-button:hover {
          background-color: ${HOVER_TINT};
        }
      `}</style>
      <div className="px-6 py-4">
        <div className="flex items-center justify-between gap-4">
          {/* Buscador */}
          <div className="flex-1 max-w-md">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: MUTED }} />
              <input
                type="text"
                placeholder="Buscar postulantes, documentos..."
                className="header-search w-full pl-10 pr-4 py-2 rounded-lg border transition-all duration-200"
                style={{
                  caretColor: BRAND_MID
                }}
              />
            </div>
          </div>

          {/* Acciones derechas */}
          <div className="flex items-center gap-4">
            {/* Botón Ayuda */}
            <button
              onClick={() => setShowHelp(true)}
              className="header-action p-2 rounded-lg"
              title="Ayuda"
            >
              <HelpCircle className="w-5 h-5" />
            </button>

            {/* Toggle Tema */}
            <button
              onClick={toggleTheme}
              className="header-action p-2 rounded-lg"
              title={isDark ? 'Modo claro' : 'Modo oscuro'}
            >
              {isDark ? (
                <Sun className="w-5 h-5" />
              ) : (
                <Moon className="w-5 h-5" />
              )}
            </button>

            {/* Notificaciones */}
            <div className="relative">
              <button
                ref={notificationsButtonRef}
                onClick={() => setShowNotifications(!showNotifications)}
                className="relative header-action p-2 rounded-lg"
              >
                <Bell className="w-5 h-5" />
                <span className="absolute top-1 right-1 w-2 h-2 rounded-full" style={{ backgroundColor: BRAND_AZURE }}></span>
              </button>

              {showNotifications && (
                <div 
                  ref={notificationsRef}
                  className="header-dropdown absolute right-0 mt-2 w-80 rounded-xl shadow-lg border overflow-hidden"
                  style={{ borderColor: DIVIDER, backgroundColor: BRAND_DEEP }}
                >
                  <div className="p-4 border-b" style={{ borderColor: DIVIDER, color: TEXT_ON_DARK }}>
                    <h3 className="font-semibold">Notificaciones</h3>
                  </div>
                  <div className="max-h-96 overflow-y-auto">
                    {[1, 2, 3].map((i) => (
                      <div
                        key={i}
                        className="p-4 border-b transition-colors cursor-pointer header-dropdown-item"
                        style={{ borderColor: DIVIDER }}
                      >
                        <p className="text-sm font-medium header-dropdown-text">
                          Documento pendiente de revisión
                        </p>
                        <p className="text-xs mt-1 header-dropdown-meta">
                          Hace 2 horas
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Perfil Usuario */}
            <div className="relative">
              <button
                ref={userMenuButtonRef}
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-3 p-2 rounded-lg header-action"
              >
                <div className="w-8 h-8 bg-gradient-to-br rounded-lg flex items-center justify-center" style={{ backgroundImage: `linear-gradient(135deg, ${BRAND_MID}, ${BRAND_AZURE})` }}>
                  <User className="w-5 h-5" style={{ color: TEXT_ON_DARK }} />
                </div>
                <span className="hidden md:inline text-sm font-medium header-user-name">
                  {user?.username || 'Usuario'}
                </span>
              </button>

              {showUserMenu && (
                <div 
                  ref={userMenuRef}
                  className="header-dropdown absolute right-0 mt-2 w-48 rounded-xl shadow-lg border overflow-hidden"
                  style={{ borderColor: DIVIDER, backgroundColor: BRAND_DEEP }}
                >
                  <div className="p-4 border-b" style={{ borderColor: DIVIDER, color: TEXT_ON_DARK }}>
                    <p className="text-sm font-medium">
                      {user?.email || 'usuario@ejemplo.com'}
                    </p>
                    <p className="text-xs" style={{ color: MUTED }}>
                      {user?.role || 'Administrador'}
                    </p>
                  </div>
                  <div className="p-2">
                    <button className="w-full flex items-center gap-2 px-4 py-2 text-sm rounded-lg transition-all duration-180 header-action header-dropdown-item" style={{ color: TEXT_ON_DARK }}>
                      <Settings className="w-4 h-4" style={{ color: TEXT_ON_DARK }} />
                      Configuración
                    </button>
                    <button
                      onClick={() => {
                        setShowUserMenu(false);
                        onLogout();
                        navigate('/login');
                      }}
                      className="w-full flex items-center gap-2 px-4 py-2 text-sm rounded-lg transition-all duration-180 header-logout-button"
                      style={{ color: BRAND_AZURE }}
                    >
                      <LogOut className="w-4 h-4" />
                      Cerrar sesión
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
      <Modal
        isOpen={showHelp}
        onClose={() => setShowHelp(false)}
        title="Centro de Ayuda"
        sizeClass="max-w-2xl"
      >
        <HelpCenter />
      </Modal>
    </>
  );
};

export default Header;
