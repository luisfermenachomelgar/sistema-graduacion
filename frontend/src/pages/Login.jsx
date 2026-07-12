/**
 * Login Page
 * User authentication page
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth';

const BRAND_DEEP = '#071740';
const BRAND_MID = '#1E66B8';
const BRAND_AZURE = '#6FD3FF';
const TEXT_ON_DARK = '#EAF4FF';
const MUTED = '#DCEBFF';
const DIVIDER = '#6FD3FF14';
const HOVER_TINT = '#1E66B81A';
const ACTIVE_FILL = '#6FD3FF24';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(username, password);

    if (result.success) {
      const targetPath = result.user?.role === 'estudiante' ? '/postulaciones' : '/dashboard';
      navigate(targetPath);
    } else {
      setError(result.error || 'Login failed');
    }

    setLoading(false);
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center px-4 py-8"
      style={{
        background: `linear-gradient(90deg, ${BRAND_DEEP} 0%, ${BRAND_MID} 50%, ${BRAND_DEEP} 100%)`,
      }}
    >
      <div className="w-full max-w-6xl">
        <div className="grid gap-8 lg:grid-cols-2">
          <div className="rounded-[32px] border border-white/10 bg-white/5 p-10 shadow-[0_32px_120px_rgba(7,23,64,0.35)] backdrop-blur-xl text-white">
            <div className="mx-auto mb-8 flex h-[7.5rem] w-[7.5rem] items-center justify-center rounded-3xl border border-[rgba(111,211,255,0.24)] bg-[rgba(111,211,255,0.18)]">
              <img
                src="/images/uabjb.png"
                alt="Logo institucional"
                className="h-[90%] w-[90%] object-contain"
              />
            </div>
            <h1 className="text-4xl font-semibold leading-tight" style={{ color: TEXT_ON_DARK }}>
              Sistema de Graduación
            </h1>
            <p className="mt-4 max-w-xl text-base leading-7" style={{ color: MUTED }}>
              Sistema de registro y seguimiento de documentación de los postulantes para las modalidades de graduación en la carrera de ingeniería de sistemas.
            </p>

            <div className="mt-10 space-y-4">
              <div className="rounded-3xl border border-[rgba(111,211,255,0.12)] bg-[rgba(255,255,255,0.04)] p-5">
                <p className="text-sm font-semibold" style={{ color: TEXT_ON_DARK }}>Funcionalidades clave</p>
                <ul className="mt-4 space-y-3 text-sm leading-6" style={{ color: MUTED }}>
                  <li>• Control y seguimiento de Modalidades de Graduación</li>
                  <li>• Documentación digital y seguimiento administrativo</li>
                  <li>• Gestión integral del proceso de graduación</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="rounded-[32px] border border-[rgba(111,211,255,0.12)] bg-[rgba(7,23,64,0.82)] p-10 shadow-[0_32px_120px_rgba(7,23,64,0.35)] backdrop-blur-xl text-white">
            <div className="mb-8">
              <p className="text-sm uppercase tracking-[0.3em]" style={{ color: MUTED }}>Bienvenido</p>
              <h2 className="mt-3 text-3xl font-semibold" style={{ color: TEXT_ON_DARK }}>
                Accede a tu panel
              </h2>
              <p className="mt-3 max-w-xl text-sm leading-6" style={{ color: MUTED }}>
                Ingresa con tu usuario y contraseña para continuar con tus trámites de graduación.
              </p>
            </div>

            {error && (
              <div className="mb-6 rounded-3xl border border-[#FF6B6B30] bg-[#FF6B6B15] p-4 text-sm" style={{ color: '#FFEAEA' }}>
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label htmlFor="username" className="mb-3 block text-sm font-medium" style={{ color: TEXT_ON_DARK }}>
                  Usuario
                </label>
                <input
                  type="text"
                  id="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full rounded-3xl border px-5 py-4 text-sm outline-none transition"
                  placeholder="Ingresa tu usuario"
                  required
                  style={{
                    backgroundColor: ACTIVE_FILL,
                    borderColor: DIVIDER,
                    color: TEXT_ON_DARK,
                  }}
                />
              </div>

              <div>
                <label htmlFor="password" className="mb-3 block text-sm font-medium" style={{ color: TEXT_ON_DARK }}>
                  Contraseña
                </label>
                <input
                  type="password"
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-3xl border px-5 py-4 text-sm outline-none transition"
                  placeholder="Ingresa tu contraseña"
                  required
                  style={{
                    backgroundColor: ACTIVE_FILL,
                    borderColor: DIVIDER,
                    color: TEXT_ON_DARK,
                  }}
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-3xl px-5 py-4 text-sm font-semibold transition duration-200"
                style={{
                  backgroundColor: BRAND_MID,
                  color: TEXT_ON_DARK,
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = BRAND_AZURE;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = BRAND_MID;
                }}
              >
                {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
