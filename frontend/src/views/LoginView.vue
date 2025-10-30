<template>
  <div class="login-container">
    <div class="login-card">
      <div class="card-header">
        <h2>服务器监控系统</h2>
        <p>请登录您的账户</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label>用户名</label>
          <input 
            v-model="loginForm.username" 
            type="text"
            placeholder="请输入用户名"
            required
            autocomplete="username"
          />
        </div>
        
        <div class="form-group">
          <label>密码</label>
          <input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="请输入密码"
            required
            autocomplete="current-password"
          />
        </div>
        
        <button type="submit" :disabled="loading" class="login-btn">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const handleLogin = async () => {
  if (!loginForm.username || !loginForm.password) {
    alert('请输入用户名和密码')
    return
  }
  
  try {
    loading.value = true
    const result = await authStore.login(loginForm)
    
    if (result.success) {
      alert('登录成功！')
      router.push('/home')
    } else {
      alert(result.message || '登录失败')
    }
  } catch (error) {
    console.error('登录错误:', error)
    alert(error.message || '登录失败')
  } finally {
    loading.value = false
  }
}

// 如果已经登录，直接跳转到首页
onMounted(() => {
  if (authStore.isLoggedIn) {
    router.push('/home')
  }
})
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.card-header {
  text-align: center;
  margin-bottom: 30px;
}

.card-header h2 {
  margin: 0 0 10px 0;
  color: #333;
  font-weight: 600;
  font-size: 24px;
}

.card-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.form-group input {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.login-btn {
  background: #409eff;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.login-btn:hover:not(:disabled) {
  background: #66b1ff;
}

.login-btn:disabled {
  background: #c0c4cc;
  cursor: not-allowed;
}
</style>

