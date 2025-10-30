import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref(localStorage.getItem('token'))
  const user = ref(null)
  const loading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const isLoggedIn = computed(() => isAuthenticated.value && !!user.value)

  // 登录
  const login = async (loginData) => {
    try {
      loading.value = true
      const response = await authApi.login(loginData)

      if (response.code === 0) {
        // 保存token和用户信息
        token.value = response.data.token
        user.value = {
          user_id: response.data.id,  // 修复字段映射
          username: response.data.username,
          email: response.data.email,
          role: response.data.role
        }

        // 持久化存储
        localStorage.setItem('token', response.data.token)
        localStorage.setItem('user', JSON.stringify(user.value))

        return { success: true, message: response.msg }
      } else {
        return { success: false, message: response.msg || '登录失败' }
      }
    } catch (error) {
      return { success: false, message: error.message || '登录失败' }
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // 外部设置 token（用于应用启动时从 localStorage 恢复）
  const setToken = (newToken) => {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('token', newToken)
    } else {
      localStorage.removeItem('token')
    }
  }

  // 初始化用户信息
  const initAuth = () => {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
      } catch (error) {
        console.error('解析用户信息失败:', error)
        logout()
      }
    }
  }

  // 验证token有效性
  const validateToken = async () => {
    if (!token.value || !user.value) return false

    try {
      // 简单验证：检查token和用户信息是否存在
      // 在实际项目中，这里可以调用后端验证接口
      return !!(token.value && user.value)
    } catch (error) {
      logout()
      return false
    }
  }

  return {
    // 状态
    token,
    user,
    loading,
    // 计算属性
    isAuthenticated,
    isLoggedIn,
    // 方法
    login,
    logout,
    initAuth,
    validateToken
    ,
    setToken
  }
})
