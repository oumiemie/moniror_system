<template>
  <div id="app">
    <!-- 登录页面 -->
    <router-view v-if="!authStore.isAuthenticated" />
    
    <!-- 主应用布局 -->
    <div v-else class="app-layout">
      <!-- 顶部导航 -->
      <div class="header">
        <h2>服务器监控系统</h2>
        <div class="user-info">
          <span>欢迎，{{ authStore.user?.username }}</span>
          <button @click="logout" class="logout-btn">退出</button>
        </div>
      </div>
      
      <!-- 导航菜单 -->
      <div class="nav">
        <router-link to="/home" class="nav-item">首页</router-link>
        <router-link to="/servers" class="nav-item">服务器</router-link>
        <router-link to="/monitor" class="nav-item">监控数据</router-link>
        <router-link v-if="authStore.user?.role === 'admin'" to="/users" class="nav-item">用户管理</router-link>
      </div>
      
      <!-- 主内容 -->
      <div class="main">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const router = useRouter()
const authStore = useAuthStore()

onMounted(() => {
  // 检查本地存储的token
  const token = localStorage.getItem('token')
  if (token) {
    authStore.setToken(token)
  }
})

const logout = () => {
  if (confirm('确定要退出登录吗？')) {
    authStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: #f5f5f5;
}

.header {
  background: #409eff;
  color: white;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h2 {
  margin: 0;
  font-size: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logout-btn {
  background: #f56c6c;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
}

.logout-btn:hover {
  background: #f78989;
}

.nav {
  background: white;
  padding: 0 20px;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  gap: 0;
}

.nav-item {
  display: block;
  padding: 15px 20px;
  text-decoration: none;
  color: #606266;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
}

.nav-item:hover {
  color: #409eff;
  background: #f0f9ff;
}

.nav-item.router-link-active {
  color: #409eff;
  border-bottom-color: #409eff;
  background: #f0f9ff;
}

.main {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
</style>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.6;
  color: #333;
}

#app {
  min-height: 100vh;
}
</style>
