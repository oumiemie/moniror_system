import axios from 'axios'

// 创建axios实例（默认走 Vite 代理 /api，生产可用 VITE_API_BASE 覆盖）
const apiBase = import.meta.env?.VITE_API_BASE || '/api'
const api = axios.create({
  baseURL: apiBase,
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加token到请求头
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API请求错误:', error)

    // 处理认证错误
    if (error.response?.status === 401) {
      // token过期或无效，清除本地存储并跳转到登录页
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }

    return Promise.reject(error)
  }
)

// 监控数据API - 匹配后端API结构
export const monitorApi = {
  // 获取监控数据
  getMonitorData: (params) => api.get('/monitor/data', { params }),

  // 获取监控统计
  getMonitorStats: (params) => api.get('/monitor/stats', { params }),

  // 添加监控数据（监控客户端使用）
  addMonitorData: (data) => api.post('/monitor/data', data),
}

// 用户认证API
export const authApi = {
  login: (data) => api.post('/auth/login', data)
}

// 用户管理API
export const userApi = {
  // 获取用户列表
  getUsers: () => api.get('/users'),

  // 获取指定用户信息
  getUser: (userId) => api.get(`/users/${userId}`),

  // 创建用户
  createUser: (userData) => api.post('/users', userData),

  // 添加用户（别名）
  addUser: (userData) => api.post('/users', userData),

  // 更新用户
  updateUser: (userId, userData) => api.put(`/users/${userId}`, userData),

  // 删除用户
  deleteUser: (userId) => api.delete(`/users/${userId}`),

  // 获取当前用户信息
  getProfile: () => api.get('/profile'),

  // 重置用户密码
  resetPassword: (username, password) =>
    api.put('/users/reset-password', { username, password })
}

// 服务器管理API
export const serverApi = {
  // 获取服务器列表
  getServers: () => api.get('/servers'),

  // 获取指定服务器信息
  getServer: (serverId) => api.get(`/servers/${serverId}`),

  // 添加服务器
  addServer: (serverData) => api.post('/servers', serverData),

  // 更新服务器
  updateServer: (serverId, serverData) => api.put(`/servers/${serverId}`, serverData),

  // 删除服务器
  deleteServer: (serverId) => api.delete(`/servers/${serverId}`),

  // 获取用户关联的服务器列表
  getUserServers: (userId) => api.get('/user-servers', { params: { user_id: userId } }),

  // 为服务器添加用户
  addServerUser: (serverId, userId) =>
    api.post(`/servers/${serverId}/users`, { user_id: userId }),

  // 从服务器移除用户
  removeServerUser: (serverId, userId) =>
    api.delete(`/servers/${serverId}/users/${userId}`)
}

export default api
