import React from 'react';
import { FormField, SectionCard } from '../components';

const USER_ROLE_OPTIONS = [
  { id: 'admin', label: 'Administrador' },
  { id: 'estudiante', label: 'Estudiante' },
];

const UserFormContent = ({
  formData,
  onInputChange,
  isEditMode = false,
  readOnlyRole = false,
  readOnlyState = false,
  extraActions = null,
}) => {
  return (
    <div className="space-y-6">
      {extraActions ? (
        <div className="flex justify-end">
          {extraActions}
        </div>
      ) : null}

      <SectionCard title="Información de acceso" description="Credenciales para ingreso al sistema.">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-5">
          <FormField
            label="Usuario"
            type="text"
            name="username"
            value={formData.username}
            onChange={onInputChange}
            required
            className="md:col-span-1"
          />
          <FormField
            label="Email"
            type="email"
            name="email"
            value={formData.email}
            onChange={onInputChange}
            required
            className="md:col-span-1"
          />
          {!isEditMode && (
            <FormField
              label="Contraseña"
              type="password"
              name="password"
              value={formData.password || ''}
              onChange={onInputChange}
              required
              className="md:col-span-2"
            />
          )}
        </div>
      </SectionCard>

      <SectionCard title="Información personal" description="Datos básicos del usuario.">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-5">
          <FormField
            label="Nombre"
            type="text"
            name="first_name"
            value={formData.first_name}
            onChange={onInputChange}
          />
          <FormField
            label="Apellido"
            type="text"
            name="last_name"
            value={formData.last_name}
            onChange={onInputChange}
          />
        </div>
      </SectionCard>

      <SectionCard title="Permisos y estado" description="Nivel de acceso y estado de habilitación.">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-5">
          <FormField
            label="Rol"
            type="select"
            name="role"
            value={formData.role || 'estudiante'}
            onChange={onInputChange}
            disabled={readOnlyRole || !!formData.is_superuser}
            options={USER_ROLE_OPTIONS}
            required
          />
          <div className="rounded-xl border border-gray-200 bg-white px-4 py-3 dark:border-gray-600 dark:bg-gray-700/60">
            <FormField
              label="Usuario activo"
              type="checkbox"
              name="is_active"
              value={!!formData.is_active}
              onChange={onInputChange}
              disabled={readOnlyState || !!formData.is_superuser}
            />
          </div>
        </div>
      </SectionCard>
    </div>
  );
};

export default UserFormContent;
