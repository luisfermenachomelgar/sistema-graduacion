import { useEffect, useState, useRef } from 'react'
import { Link } from 'react-router-dom'
import { Bell } from 'lucide-react'
import api from '../api/api'
import useAuth from '../hooks/useAuth'

function NotificationBell() {
  const { isAuthenticated } = useAuth()
  const [notifications, setNotifications] = useState([])
  const [isOpen, setIsOpen] = useState(false)
  const containerRef = useRef(null)
  const buttonRef = useRef(null)
  const panelRef = useRef(null)

  const unreadCount = notifications.filter((n) => !n.leida).length

  const loadNotifications = async () => {
    if (!isAuthenticated) return

    const result = await api.getAll('/api/notificaciones/')
    if (result.success) {
      setNotifications(result.data?.results || [])
    } else {
      console.error('Failed to fetch notifications', result.error)
      setNotifications([])
    }
  }

  useEffect(() => {
    loadNotifications()
    const interval = setInterval(loadNotifications, 60000)
    return () => clearInterval(interval)
  }, [isAuthenticated])

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (buttonRef.current && buttonRef.current.contains(event.target)) {
        return
      }

      if (panelRef.current && panelRef.current.contains(event.target)) {
        return
      }

      setIsOpen(false)
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleToggle = async () => {
    const nextState = !isOpen
    setIsOpen(nextState)

    if (nextState && unreadCount > 0) {
      const unreadIds = notifications.filter((n) => !n.leida).map((n) => n.id)
      try {
        await Promise.all(
          unreadIds.map((id) => api.create(`/api/notificaciones/${id}/marcar_leida/`, {}))
        )
        setNotifications((prev) => prev.map((n) => ({ ...n, leida: true })))
      } catch (error) {
        console.error('Failed to mark notifications as read', error)
      }
    }
  }

  const handleMarkAllAsRead = async () => {
    if (unreadCount === 0) return

    const result = await api.create('/api/notificaciones/marcar-todas-leidas/', {})
    if (result.success) {
      setNotifications((prev) => prev.map((n) => ({ ...n, leida: true })))
    } else {
      console.error('Failed to mark all as read', result.error)
    }
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="relative" ref={containerRef}>
      <button
        ref={buttonRef}
        onClick={handleToggle}
        className="relative header-action p-2 rounded-lg"
        title="Notificaciones"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 flex h-5 w-5 items-center justify-center rounded-full bg-sky-500 text-xs font-bold text-white">
            {unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div
          ref={panelRef}
          className="header-dropdown absolute right-0 top-full mt-2 w-80 rounded-xl shadow-lg border overflow-hidden"
          style={{ borderColor: '#6FD3FF14', backgroundColor: '#071740' }}
        >
          <div className="p-4 border-b" style={{ borderColor: '#6FD3FF14' }}>
            <h3 className="font-semibold text-white">Notificaciones</h3>
          </div>
          <div className="max-h-96 overflow-y-auto">
            {notifications.length > 0 ? (
              notifications.map((n) => (
                <div
                  key={n.id}
                  className="p-4 border-b transition-colors cursor-pointer header-dropdown-item"
                  style={{ borderColor: '#6FD3FF14' }}
                >
                  {n.link ? (
                    <Link
                      to={n.link}
                      onClick={() => setIsOpen(false)}
                      className="block"
                    >
                      <p className="text-sm font-medium header-dropdown-text">{n.mensaje}</p>
                      <p className="text-xs mt-1 header-dropdown-meta">{new Date(n.fecha_creacion).toLocaleString()}</p>
                    </Link>
                  ) : (
                    <div>
                      <p className="text-sm font-medium header-dropdown-text">{n.mensaje}</p>
                      <p className="text-xs mt-1 header-dropdown-meta">{new Date(n.fecha_creacion).toLocaleString()}</p>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="p-4 text-center text-white">No hay notificaciones.</div>
            )}
          </div>
          {unreadCount > 0 && (
            <div className="p-2 border-t" style={{ borderColor: '#6FD3FF14' }}>
              <button
                onClick={handleMarkAllAsRead}
                className="w-full text-sm text-sky-200 hover:text-white"
              >
                Marcar todas como leídas
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default NotificationBell
