import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'

const Navbar = ({ notifications, clearNotifications }) => {
  const { user } = useAuth()
  const [showNotifications, setShowNotifications] = useState(false)

  return (
    <div className="navbar">
      <div className="nav-logo">
        <span>💬</span>
        <h2>NextChat</h2>
      </div>
      <div className="nav-right">
        <div className="notification-bell" onClick={() => {
          setShowNotifications(!showNotifications)
          if (!showNotifications) clearNotifications()
        }}>
          <span>🔔</span>
          {notifications.length > 0 && (
            <span className="notification-badge">{notifications.length}</span>
          )}
          {showNotifications && (
            <div className="notification-dropdown">
              {notifications.length === 0 ? (
                <p className="no-notifications">No new notifications</p>
              ) : (
                notifications.map((notif, index) => (
                  <div key={index} className="notification-item">
                    <span className="notif-icon">💬</span>
                    <div>
                      <p className="notif-text">{notif.message}</p>
                      <small className="notif-time">{notif.time}</small>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Navbar