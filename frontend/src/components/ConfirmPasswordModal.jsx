import { useEffect, useState } from 'react';
import Modal from './Modal';
import FormField from './FormField';

const ConfirmPasswordModal = ({
  isOpen,
  title,
  description,
  onClose,
  onConfirm,
  isLoading = false,
  error,
  submitText = 'Confirmar',
}) => {
  const [password, setPassword] = useState('');

  useEffect(() => {
    if (isOpen) {
      setPassword('');
    }
  }, [isOpen]);

  const handleConfirm = () => {
    onConfirm(password);
  };

  return (
    <Modal
      isOpen={isOpen}
      title={title}
      onClose={onClose}
      onSubmit={handleConfirm}
      submitText={submitText}
      isLoading={isLoading}
      sizeClass="max-w-lg"
    >
      <div className="space-y-4">
        <p className="text-sm text-gray-600 dark:text-gray-300">{description}</p>
        <FormField
          label="Contraseña"
          name="confirm_password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Ingresa tu contraseña"
          required
        />
        {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}
      </div>
    </Modal>
  );
};

export default ConfirmPasswordModal;
