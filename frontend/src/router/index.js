import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/home',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/servers',
      name: 'servers',
      component: () => import('../views/ServerManagement.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/monitor',
      name: 'monitor',
      component: () => import('../views/MonitorData.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/users',
      name: 'users',
      component: () => import('../views/UserManagement.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
  ],
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 初始化认证状态
  authStore.initAuth()
  
  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    if (authStore.isLoggedIn) {
      // 已登录，验证token有效性
      const isValid = await authStore.validateToken()
      if (isValid) {
        // 检查是否需要管理员权限
        if (to.meta.requiresAdmin && authStore.user?.role !== 'admin') {
          next('/home')
        } else {
          next()
        }
      } else {
        next('/login')
      }
    } else {
      // 未登录，跳转到登录页
      next('/login')
    }
  } else {
    // 不需要认证的页面
    if (to.name === 'login' && authStore.isLoggedIn) {
      // 如果已登录且访问登录页，跳转到首页
      next('/home')
    } else {
      next()
    }
  }
})

export default router
