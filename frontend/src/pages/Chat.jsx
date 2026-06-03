import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getChannels, createChannel, getMessages, getWorkspaceMembers, uploadFile, searchMessages } from '../services/api'
import { useAuth } from '../context/AuthContext'
import wsService from '../services/websocket'
import { format } from 'date-fns'
import './Chat.css'
import Navbar from '../components/Navbar'
import '../components/Navbar.css'

const Chat = () => {
  const { workspaceId } = useParams()
  const { user, logoutUser } = useAuth()
  const navigate = useNavigate()

  const [channels, setChannels] = useState([])
  const [activeChannel, setActiveChannel] = useState(null)
  const [messages, setMessages] = useState([])
  const [members, setMembers] = useState([])
  const [onlineUsers, setOnlineUsers] = useState({})
  const [typingUsers, setTypingUsers] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [newChannelName, setNewChannelName] = useState('')
  const [showChannelForm, setShowChannelForm] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [notifications, setNotifications] = useState([])
  const messagesEndRef = useRef(null)
  const typingTimeoutRef = useRef(null)
  const fileInputRef = useRef(null)
  const token = localStorage.getItem('token')

  useEffect(() => {
    fetchChannels()
    fetchMembers()
  }, [workspaceId])

  useEffect(() => {
    if (activeChannel) {
      fetchMessages(activeChannel.id)
      wsService.connect(activeChannel.id, token)
      wsService.addListener(handleWsMessage)
    }
    return () => {
      wsService.removeListener(handleWsMessage)
    }
  }, [activeChannel])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const fetchChannels = async () => {
    try {
      const res = await getChannels(workspaceId)
      setChannels(res.data)
      if (res.data.length > 0) setActiveChannel(res.data[0])
    } catch (err) {
      console.error(err)
    }
  }

  const fetchMessages = async (channelId) => {
    try {
      const res = await getMessages(channelId)
      setMessages(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  const fetchMembers = async () => {
    try {
      const res = await getWorkspaceMembers(workspaceId)
      setMembers(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  const handleWsMessage = (data) => {
    if (data.event === 'message') {
      setMessages((prev) => [...prev, data])
      setTypingUsers((prev) => prev.filter((u) => u !== data.username))
      if (data.username !== user.username) {
        setNotifications((prev) => [...prev, {
          message: `${data.username} in #${activeChannel?.name}: ${data.content.substring(0, 40)}`,
          time: format(new Date(), 'HH:mm')
        }])
      }
    } else if (data.event === 'typing') {
      if (data.username !== user.username) {
        if (data.is_typing) {
          setTypingUsers((prev) => [...new Set([...prev, data.username])])
        } else {
          setTypingUsers((prev) => prev.filter((u) => u !== data.username))
        }
      }
    } else if (data.event === 'online_status') {
      setOnlineUsers((prev) => ({ ...prev, [data.user_id]: data.is_online }))
    }
  }

  const handleSendMessage = () => {
    if (!newMessage.trim()) return
    wsService.sendMessage(newMessage)
    setNewMessage('')
    wsService.sendTyping(false)
  }

  const handleTyping = (e) => {
    setNewMessage(e.target.value)
    wsService.sendTyping(true)
    clearTimeout(typingTimeoutRef.current)
    typingTimeoutRef.current = setTimeout(() => {
      wsService.sendTyping(false)
    }, 2000)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleCreateChannel = async (e) => {
    e.preventDefault()
    if (!newChannelName.trim()) return
    try {
      const res = await createChannel({ name: newChannelName, workspace_id: parseInt(workspaceId) })
      setChannels([...channels, res.data])
      setNewChannelName('')
      setShowChannelForm(false)
    } catch (err) {
      console.error(err)
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file || !activeChannel) return
    const formData = new FormData()
    formData.append('file', file)
    try {
      await uploadFile(activeChannel.id, formData)
    } catch (err) {
      console.error(err)
    }
  }

  const handleSearch = async (e) => {
    const q = e.target.value
    setSearchQuery(q)
    if (q.trim().length > 2) {
      try {
        const res = await searchMessages(workspaceId, q)
        setSearchResults(res.data.results)
      } catch (err) {
        console.error(err)
      }
    } else {
      setSearchResults([])
    }
  }

  const handleLogout = () => {
    wsService.disconnect()
    logoutUser()
    navigate('/login')
  }

  const formatTime = (timestamp) => {
    try {
      return format(new Date(timestamp), 'HH:mm')
    } catch {
      return ''
    }
  }

  return (
    <div className="chat-container" style={{ flexDirection: 'column' }}>
      <Navbar
        notifications={notifications}
        clearNotifications={() => setNotifications([])}
      />
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>

        {/* LEFT SIDEBAR */}
        <div className="chat-sidebar">
          <div className="sidebar-header">
            <h3>#{activeChannel?.name || 'NextChat'}</h3>
            <button className="back-btn" onClick={() => navigate('/dashboard')} title="Back to Dashboard">
              ←
            </button>
          </div>

          <div className="sidebar-section">
            <div className="sidebar-section-title">
              Channels
              <button className="add-channel-btn" onClick={() => setShowChannelForm(!showChannelForm)}>+</button>
            </div>

            {showChannelForm && (
              <form className="create-channel-form" onSubmit={handleCreateChannel}>
                <input
                  type="text"
                  placeholder="channel-name"
                  value={newChannelName}
                  onChange={(e) => setNewChannelName(e.target.value)}
                  autoFocus
                />
                <button type="submit">Add</button>
              </form>
            )}

            {channels.map((channel) => (
              <div
                key={channel.id}
                className={`channel-item ${activeChannel?.id === channel.id ? 'active' : ''}`}
                onClick={() => setActiveChannel(channel)}
              >
                <span className="channel-hash">#</span>
                {channel.name}
              </div>
            ))}
          </div>

          {/* Current user */}
          <div className="sidebar-user">
            <div className="user-avatar">
              {user?.username?.charAt(0).toUpperCase()}
            </div>
            <div className="user-info">
              <span>{user?.username}</span>
              <small>● Online</small>
            </div>
            <button className="logout-btn" onClick={handleLogout} title="Logout">⏻</button>
          </div>
        </div>

        {/* MAIN CHAT */}
        <div className="chat-main">
          <div className="chat-header">
            <div className="chat-header-left">
              <span style={{ color: 'var(--text-muted)', fontSize: '18px' }}>#</span>
              <h3>{activeChannel?.name || 'Select a channel'}</h3>
            </div>
            <div className="chat-header-right">
              <div className="search-bar">
                <span>🔍</span>
                <input
                  type="text"
                  placeholder="Search messages..."
                  value={searchQuery}
                  onChange={handleSearch}
                />
              </div>
            </div>
          </div>

          {/* Search Results */}
          {searchResults.length > 0 && (
            <div style={{
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border)',
              margin: '8px 20px',
              borderRadius: '8px',
              padding: '12px',
              maxHeight: '200px',
              overflowY: 'auto'
            }}>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>
                Search Results ({searchResults.length})
              </p>
              {searchResults.map((msg) => (
                <div key={msg.id} style={{
                  padding: '6px 8px',
                  borderRadius: '6px',
                  fontSize: '13px',
                  color: 'var(--text-secondary)',
                  borderBottom: '1px solid var(--border)'
                }}>
                  {msg.content}
                </div>
              ))}
            </div>
          )}

          {/* Messages */}
          <div className="messages-area">
            {!activeChannel ? (
              <div className="no-channel">
                <span>💬</span>
                <p>Select a channel to start chatting</p>
              </div>
            ) : messages.length === 0 ? (
              <div className="no-channel">
                <span>👋</span>
                <p>No messages yet. Say hello!</p>
              </div>
            ) : (
              messages.map((msg, index) => (
                <div key={msg.id || index} className="message-item">
                  <div className="message-avatar">
                    {(msg.username || msg.sender_id)?.toString().charAt(0).toUpperCase()}
                  </div>
                  <div className="message-body">
                    <div className="message-header">
                      <span className="message-username">{msg.username || `User ${msg.sender_id}`}</span>
                      <span className="message-time">{formatTime(msg.created_at)}</span>
                    </div>
                    <div className="message-content">{msg.content}</div>
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Typing Indicator */}
          <div className="typing-indicator">
            {typingUsers.length > 0 && `${typingUsers.join(', ')} is typing...`}
          </div>

          {/* Message Input */}
          {activeChannel && (
            <div className="message-input-area">
              <div className="message-input-box">
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileUpload}
                  style={{ display: 'none' }}
                />
                <button className="file-btn" onClick={() => fileInputRef.current.click()}>📎</button>
                <input
                  type="text"
                  placeholder={`Message #${activeChannel?.name}`}
                  value={newMessage}
                  onChange={handleTyping}
                  onKeyDown={handleKeyDown}
                />
                <button className="send-btn" onClick={handleSendMessage}>➤</button>
              </div>
            </div>
          )}
        </div>

        {/* RIGHT MEMBERS SIDEBAR */}
        <div className="members-sidebar">
          <div className="members-title">Members — {members.length}</div>
          {members.map((member) => (
            <div key={member.user_id} className="member-item">
              <div className="member-avatar">
                {member.username?.charAt(0).toUpperCase()}
                <span className={onlineUsers[member.user_id] ? 'online-dot' : 'offline-dot'}></span>
              </div>
              <div>
                <div className="member-name">{member.username}</div>
                <div className="member-role">{member.role}</div>
              </div>
            </div>
          ))}
        </div>

      </div>
    </div>
  )
}

export default Chat