import axios from 'axios'

const API_URL = 'https://nextchat-backend-nnyh.onrender.com'

const api = axios.create({
  baseURL: API_URL,
})

// Automatically attach token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auth
export const register = (data) => api.post('/auth/register', data)
export const login = (data) => api.post('/auth/login', data)
export const getMe = () => api.get('/auth/me')

// Workspaces
export const getWorkspaces = () => api.get('/workspaces/')
export const createWorkspace = (data) => api.post('/workspaces/', data)
export const deleteWorkspace = (id) => api.delete(`/workspaces/${id}`)
export const joinWorkspace = (id) => api.post(`/workspaces/${id}/join`)
export const getWorkspaceMembers = (id) => api.get(`/workspaces/${id}/members`)

// Channels
export const getChannels = (workspaceId) => api.get(`/channels/workspace/${workspaceId}`)
export const createChannel = (data) => api.post('/channels/', data)
export const deleteChannel = (id) => api.delete(`/channels/${id}`)

// Messages
export const getMessages = (channelId) => api.get(`/messages/${channelId}`)
export const searchMessages = (workspaceId, q) => api.get(`/messages/search/${workspaceId}?q=${q}`)
export const uploadFile = (channelId, formData) => api.post(`/upload/${channelId}`, formData)

// Users
export const getWorkspaceUsers = (workspaceId) => api.get(`/users/workspace/${workspaceId}`)
export const getUserProfile = (userId) => api.get(`/users/${userId}`)