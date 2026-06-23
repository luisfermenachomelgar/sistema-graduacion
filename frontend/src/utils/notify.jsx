/**
 * Notification Utilities
 * Global notification helpers using react-hot-toast
 * Dark themed, consistent visual toasts for success/error/warning/info
 */

import toast from 'react-hot-toast';
import React from 'react';

const baseStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: 14,
  padding: '10px 18px', // reduced vertical padding (~15%) for slimmer toasts
  borderRadius: 16,
  boxShadow: '0 8px 24px rgba(0,0,0,0.35)',
  color: '#fff',
  maxWidth: '34rem',
};

// Shared variants: identical structure; only colors/icons differ
const variants = {
  success: {
    bg: 'linear-gradient(135deg, #052e1f 0%, #064e3b 100%)',
    iconColor: '#86efac',
    iconBg: 'rgba(134,239,172,0.08)',
    iconGlow: '0 6px 18px rgba(8,86,44,0.12)',
    border: '1px solid rgba(34,197,94,0.18)',
  },
  error: {
    bg: 'linear-gradient(135deg, #450a0a 0%, #7f1d1d 100%)',
    iconColor: '#fecaca',
    iconBg: 'rgba(255,255,255,0.04)',
    iconGlow: '0 8px 20px rgba(127,29,29,0.22)',
    border: '1px solid rgba(239,68,68,0.30)',
  },
  warning: {
    bg: 'linear-gradient(135deg, #5a2e03 0%, #92400e 100%)',
    iconColor: '#fef08a',
    iconBg: 'rgba(255,255,255,0.04)',
    iconGlow: '0 8px 20px rgba(146,64,14,0.18)',
    border: '1px solid rgba(245,158,11,0.18)',
  },
  info: {
    bg: 'linear-gradient(135deg, #0f2a66 0%, #1e3a8a 100%)',
    iconColor: '#93c5fd',
    iconBg: 'rgba(255,255,255,0.04)',
    iconGlow: '0 8px 20px rgba(30,58,138,0.16)',
    border: '1px solid rgba(59,130,246,0.16)',
  },
};

const ToastElement = ({ type = 'info', message, t }) => {
  const v = variants[type] || variants.info;
  const icon = type === 'success' ? '✓' : type === 'error' ? '×' : type === 'warning' ? '⚠️' : 'ℹ️';

  const iconContainerStyle = {
    width: 36,
    height: 36,
    borderRadius: 9999,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: v.iconBg,
    boxShadow: v.iconGlow,
    color: v.iconColor,
    fontSize: 16,
    flexShrink: 0,
  };

  const messageStyle = {
    flex: 1,
    whiteSpace: 'pre-wrap',
    color: '#ffffff',
    fontWeight: 600,
    fontSize: 15,
    lineHeight: 1.25,
    paddingTop: 2,
    paddingBottom: 2,
  };

  const closeStyle = {
    marginLeft: 14,
    background: 'transparent',
    border: 'none',
    color: 'rgba(255,255,255,0.9)',
    fontSize: 16,
    cursor: 'pointer',
    opacity: 0.7,
    transition: 'opacity 180ms ease',
  };

  return (
    <div
      role="status"
      aria-live="polite"
      className="animate-in fade-in slide-in-from-top"
      style={{ ...baseStyle, background: v.bg, border: v.border }}
    >
      <div style={iconContainerStyle}>{icon}</div>
      <div style={messageStyle}>{message}</div>
      <button
        onClick={() => toast.dismiss(t.id)}
        style={closeStyle}
        aria-label="Cerrar"
        onMouseEnter={(e) => (e.currentTarget.style.opacity = '1')}
        onMouseLeave={(e) => (e.currentTarget.style.opacity = '0.7')}
      >
        ✕
      </button>
    </div>
  );
};

const showCustom = (type, message, options = {}) => {
  return toast.custom((t) => <ToastElement type={type} message={message} t={t} />, {
    duration: options.duration ?? 4000,
    position: options.position || 'top-right',
    ...options,
  });
};

export const success = (message, options = {}) => showCustom('success', message, options);
export const error = (message, options = {}) => showCustom('error', message, options);
export const warning = (message, options = {}) => showCustom('warning', message, options);
export const info = (message, options = {}) => showCustom('info', message, options);

export const dismissAll = () => toast.remove();

export const loading = (message = 'Cargando...') => {
  return toast.loading(message, { position: 'top-right' });
};

export const updateToast = (toastId, options = {}) => {
  toast((t) => <ToastElement type={options.type || 'info'} message={options.message || ''} t={t} />, {
    id: toastId,
    duration: options.duration,
    position: options.position,
  });
};

export default {
  success,
  error,
  warning,
  info,
  dismissAll,
  loading,
  updateToast,
};
