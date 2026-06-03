import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getWorkspaces, createWorkspace, joinWorkspace } from '../services/api'
import { useAuth } from '../context/AuthContext'
import './Dashboard.css'

const Dashboard = () => {
  const [workspaces, setWorkspaces] = useState([])
  const [newWorkspace, setNewWorkspace] = useState('')
  const [joinCode, setJoinCode] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const { user, logoutUser } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    fetchWorkspaces()
  }, [])

  const fetchWorkspaces = async () => {
    try {
      const res = await getWorkspaces()
      setWorkspaces(res.data)
    } catch (err) {
      setError('Failed to load workspaces')
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    if (!newWorkspace.trim()) return
    try {
      const res = await createWorkspace({ name: newWorkspace })
      setWorkspaces([...workspaces, res.data])
      setNewWorkspace('')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create workspace')
    }
  }

  const handleJoin = async (e) => {
    e.preventDefault()
    if (!joinCode.trim()) return
    try {
      await joinWorkspace(joinCode)
      fetchWorkspaces()
      setJoinCode('')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to join workspace')
    }
  }

  const handleLogout = () => {
    logoutUser()
    navigate('/login')
  }

  return (
    <div className="dashboard-container">
      {/* Navbar */}
      <div className="dashboard-navbar">
        <div className="nav-logo">
          <span>💬</span>
          <h2>NextChat</h2>
        </div>
        <div className="nav-user">
          <span className="nav-username">👤 {user?.username}</span>
          <button className="btn-danger" onClick={handleLogout}>Logout</button>
        </div>
      </div>

      <div className="dashboard-content">
        <h2 className="dashboard-title">Your Workspaces</h2>
        {error && <div className="auth-error">{error}</div>}

        {/* Workspaces Grid */}
        {loading ? (
          <p className="loading-text">Loading workspaces...</p>
        ) : (
          <div className="workspaces-grid">
            {workspaces.length === 0 ? (
              <p className="empty-text">No workspaces yet. Create or join one!</p>
            ) : (
              workspaces.map((ws) => (
                <div
                  key={ws.id}
                  className="workspace-card"
                  onClick={() => navigate(`/chat/${ws.id}`)}
                >
                  <div className="workspace-icon">
                    {ws.name.charAt(0).toUpperCase()}
                  </div>
                  <div className="workspace-info">
                    <h3>{ws.name}</h3>
                    <p>Code: <strong>{ws.invite_code}</strong></p>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Actions */}
        <div className="dashboard-actions">
          {/* Create Workspace */}
          <div className="action-card">
            <h3>➕ Create Workspace</h3>
            <form onSubmit={handleCreate}>
              <input
                className="input-field"
                type="text"
                placeholder="Workspace name"
                value={newWorkspace}
                onChange={(e) => setNewWorkspace(e.target.value)}
              />
              <button className="btn-primary" type="submit">Create</button>
            </form>
          </div>

          {/* Join Workspace */}
          <div className="action-card">
            <h3>🔗 Join Workspace</h3>
            <form onSubmit={handleJoin}>
              <input
                className="input-field"
                type="text"
                placeholder="Enter invite code (e.g. AB12CD34)"
                value={joinCode}
                onChange={(e) => setJoinCode(e.target.value)}
              />
              <button className="btn-primary" type="submit">Join</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard