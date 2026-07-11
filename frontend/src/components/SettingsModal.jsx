import React, { useEffect, useMemo, useState } from 'react';
import { UserCircle, Lock, Pencil } from 'lucide-react';
import Modal from './Modal';
import UserFormContent from './UserFormContent';
import axiosInstance from '../api/axios';
import { API_CONFIG } from '../constants/api';

const INITIAL_PROFILE = {
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  role: 'estudiante',
  is_active: true,
};

const SettingsModal = ({ isOpen, onClose, user, onUserUpdated }) => {
  const [activeView, setActiveView] = useState('edit');
  const [profile, setProfile] = useState(INITIAL_PROFILE);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [passwordForm, setPasswordForm] = useState({ current_password: '', new_password: '', confirm_password: '' });

  useEffect(() => {
    if (!isOpen) return;

    const resetProfile = (sourceUser = user) => {
      setProfile({
        ...INITIAL_PROFILE,
        username: sourceUser?.username || '',
        email: sourceUser?.email || '',
        first_name: sourceUser?.first_name || '',
        last_name: sourceUser?.last_name || '',
        role: sourceUser?.role || 'estudiante',
        is_active: sourceUser?.is_active ?? true,
      });
    };

    setActiveView('edit');
    setMessage({ type: '', text: '' });
    resetProfile();
    setPasswordForm({ current_password: '', new_password: '', confirm_password: '' });

    if (!user?.id) return;

    const loadCurrentUser = async () => {
      try {
        const response = await axiosInstance.get(API_CONFIG.ENDPOINTS.USUARIO_DETAIL(user.id));
        const currentUser = response.data;
        resetProfile({
          ...user,
          ...currentUser,
          role: currentUser.role || user.role || 'estudiante',
          is_active: currentUser.is_active ?? user.is_active ?? true,
        });
      } catch (error) {
        console.error('Error loading user profile', error);
      }
    };

    loadCurrentUser();
  }, [isOpen, user]);

  const roleLabel = useMemo(() => {
    if (user?.role_display) return user.role_display;
    return user?.role || 'Usuario';
  }, [user]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setProfile((prev) => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSaveProfile = async () => {
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      if (!user?.id) {
        throw new Error('Usuario no disponible');
      }

      const response = await axiosInstance.patch(API_CONFIG.ENDPOINTS.USUARIO_DETAIL(user.id), {
        username: profile.username,
        email: profile.email,
        first_name: profile.first_name,
        last_name: profile.last_name,
      });

      const updatedUser = response.data;
      onUserUpdated?.(updatedUser);
      setProfile((prev) => ({ ...prev, ...updatedUser }));
      setMessage({ type: 'success', text: 'Perfil actualizado correctamente.' });
    } catch (error) {
      const message = error.response?.data?.detail || error.response?.data?.error || 'No se pudo actualizar el perfil.';
      setMessage({ type: 'error', text: message });
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async () => {
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      if (!user?.id) {
        throw new Error('Usuario no disponible');
      }

      if (passwordForm.new_password !== passwordForm.confirm_password) {
        setMessage({ type: 'error', text: 'La nueva contraseña y su confirmación no coinciden.' });
        setLoading(false);
        return;
      }

      const response = await axiosInstance.patch(API_CONFIG.ENDPOINTS.USUARIO_DETAIL(user.id), {
        password: passwordForm.new_password,
      });
      setPasswordForm({ current_password: '', new_password: '', confirm_password: '' });
      setMessage({ type: 'success', text: response.data?.message || 'Contraseña actualizada correctamente.' });
    } catch (error) {
      const message = error.response?.data?.detail || error.response?.data?.error || 'No se pudo cambiar la contraseña.';
      setMessage({ type: 'error', text: message });
    } finally {
      setLoading(false);
    }
  };

  const renderOptionCards = () => (
    <div className="grid gap-3 md:grid-cols-3">
      <button
        type="button"
        onClick={() => setActiveView('edit')}
        className={`rounded-2xl border p-4 text-left transition ${activeView === 'edit' ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800'}`}
      >
        <div className="flex items-center gap-2 font-semibold text-gray-900 dark:text-white">
          <Pencil className="h-5 w-5" /> Datos personales
        </div>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">Actualiza tus datos personales y credenciales de acceso.</p>
      </button>
      <button
        type="button"
        onClick={() => setActiveView('password')}
        className={`rounded-2xl border p-4 text-left transition ${activeView === 'password' ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800'}`}
      >
        <div className="flex items-center gap-2 font-semibold text-gray-900 dark:text-white">
          <Lock className="h-5 w-5" /> Cambiar contraseña
        </div>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">Cambia tu contraseña de acceso.</p>
      </button>
      <button
        type="button"
        onClick={() => setActiveView('summary')}
        className={`rounded-2xl border p-4 text-left transition ${activeView === 'summary' ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800'}`}
      >
        <div className="flex items-center gap-2 font-semibold text-gray-900 dark:text-white">
          <UserCircle className="h-5 w-5" /> Resumen
        </div>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">Revisa tus datos generales y estado dentro del sistema.</p>
      </button>
    </div>
  );

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Configuración" sizeClass="max-w-4xl" showFooter={false}>
      <div className="space-y-5">
        {renderOptionCards()}

        {message.text ? (
          <div className={`rounded-xl border px-4 py-3 text-sm ${message.type === 'success' ? 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300' : 'border-red-200 bg-red-50 text-red-700 dark:border-red-700 dark:bg-red-900/20 dark:text-red-300'}`}>
            {message.text}
          </div>
        ) : null}

        {activeView === 'edit' && (
          <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-slate-800/80">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Editar perfil</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">Los campos de rol y estado se muestran solo como referencia.</p>
              </div>
            </div>
            <UserFormContent
              formData={profile}
              onInputChange={handleInputChange}
              isEditMode={true}
              readOnlyRole={true}
              readOnlyState={true}
              extraActions={(
                <button
                  type="button"
                  onClick={() => setActiveView('password')}
                  className="rounded-xl border border-blue-600 px-4 py-2.5 text-sm font-medium text-blue-600 transition hover:bg-blue-50 dark:border-blue-400 dark:text-blue-300 dark:hover:bg-blue-900/20"
                >
                  Cambiar contraseña
                </button>
              )}
            />
            <div className="mt-5 flex justify-end">
              <button
                type="button"
                onClick={handleSaveProfile}
                disabled={loading}
                className="rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-70"
              >
                {loading ? 'Guardando...' : 'Guardar cambios'}
              </button>
            </div>
          </div>
        )}

        {activeView === 'password' && (
          <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-slate-800/80">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Cambiar contraseña</h3>
            <div className="mt-4 space-y-4">
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Contraseña actual</label>
                <input
                  type="password"
                  value={passwordForm.current_password}
                  onChange={(e) => setPasswordForm({ ...passwordForm, current_password: e.target.value })}
                  className="w-full rounded-xl border border-gray-300 px-3 py-2.5 text-sm dark:border-gray-600 dark:bg-slate-900 dark:text-white"
                />
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Nueva contraseña</label>
                <input
                  type="password"
                  value={passwordForm.new_password}
                  onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })}
                  className="w-full rounded-xl border border-gray-300 px-3 py-2.5 text-sm dark:border-gray-600 dark:bg-slate-900 dark:text-white"
                />
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Confirmación de la nueva contraseña</label>
                <input
                  type="password"
                  value={passwordForm.confirm_password}
                  onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })}
                  className="w-full rounded-xl border border-gray-300 px-3 py-2.5 text-sm dark:border-gray-600 dark:bg-slate-900 dark:text-white"
                />
              </div>
            </div>
            <div className="mt-5 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setActiveView('edit')}
                className="rounded-xl border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
              >
                Volver
              </button>
              <button
                type="button"
                onClick={handleChangePassword}
                disabled={loading}
                className="rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-70"
              >
                {loading ? 'Procesando...' : 'Cambiar contraseña'}
              </button>
            </div>
          </div>
        )}

        {activeView === 'summary' && (
          <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-slate-800/80">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Resumen de cuenta</h3>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Usuario</label>
                <div className="rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-700 dark:border-gray-700 dark:bg-slate-900/60 dark:text-gray-200">
                  {user?.username || 'No registrado'}
                </div>
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Email</label>
                <div className="rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-700 dark:border-gray-700 dark:bg-slate-900/60 dark:text-gray-200">
                  {user?.email || 'No registrado'}
                </div>
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Nombre</label>
                <div className="rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-700 dark:border-gray-700 dark:bg-slate-900/60 dark:text-gray-200">
                  {user?.first_name || 'No registrado'}
                </div>
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Apellido</label>
                <div className="rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-700 dark:border-gray-700 dark:bg-slate-900/60 dark:text-gray-200">
                  {user?.last_name || 'No registrado'}
                </div>
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Rol</label>
                <div className="rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-700 dark:border-gray-700 dark:bg-slate-900/60 dark:text-gray-200">
                  {roleLabel}
                </div>
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">Estado</label>
                <div className="rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-700 dark:border-gray-700 dark:bg-slate-900/60 dark:text-gray-200">
                  {user?.is_active ? 'Activo' : 'Inactivo'}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
};

export default SettingsModal;
