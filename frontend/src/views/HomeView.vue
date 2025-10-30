<template>
  <div class="home">
    <!-- 欢迎信息 -->
    <div class="welcome">
      <h1>服务器监控系统</h1>
      <p>欢迎回来，{{ authStore.user?.username }}！</p>
    </div>

    <!-- 系统概览 -->
    <div class="stats">
      <div class="stat-card">
        <div class="stat-value">{{ stats.totalServers }}</div>
        <div class="stat-label">总服务器数</div>
      </div>
      <!-- 在线/离线统计已删除 -->
      <div class="stat-card">
        <div class="stat-value">{{ stats.alertCount }}</div>
        <div class="stat-label">告警数量</div>
      </div>
    </div>

    <!-- 最近监控数据 -->
    <div class="data-section">
      <div class="section-header">
        <h3>最近监控数据</h3>
        <button @click="refreshData" :disabled="loading" class="btn btn-small">
          {{ loading ? '刷新中...' : '刷新' }}
        </button>
      </div>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>服务器</th>
              <th>IP地址</th>
              <th>CPU</th>
              <th>内存</th>
              <th>磁盘</th>
              <th>记录时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in recentData" :key="row.id">
              <td>{{ row.server_name }}</td>
              <td>{{ row.ip_address }}</td>
              <td><span :class="getCpuStatus(row.cpu_value)">{{ row.cpu_value }}%</span></td>
              <td><span :class="getMemoryStatus(row.memory_value)">{{ row.memory_value }}%</span></td>
              <td><span :class="getDiskStatus(row.disk_value)">{{ row.disk_value }}%</span></td>
              <td>{{ formatTime(row.recorded_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { monitorApi, serverApi } from '@/api'

const authStore = useAuthStore()
const loading = ref(false)
const recentData = ref([])
const servers = ref([])

// 计算属性
const stats = computed(() => {
  const totalServers = servers.value.length
  
  // 计算告警数量
  const alertCount = recentData.value.filter(data => {
    return data.cpu_value >= 85 || data.memory_value >= 90 || data.disk_value >= 95
  }).length

  return {
    totalServers,
    alertCount
  }
})

// 方法
const fetchServers = async () => {
  try {
    const response = await serverApi.getServers()
    if (response.code === 0) {
      servers.value = response.data || []
    } else {
      console.error('获取服务器列表失败:', response.msg)
    }
  } catch (error) {
    console.error('获取服务器列表失败:', error)
  }
}

const fetchRecentData = async () => {
  try {
    loading.value = true
    const response = await monitorApi.getMonitorData()
    if (response.code === 0) {
      // 显示全部数据，配合容器纵向滚动
      recentData.value = response.data || []
    } else {
      console.error('获取监控数据失败:', response.msg)
    }
  } catch (error) {
    console.error('获取监控数据失败:', error)
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  fetchRecentData()
}

const getCpuStatus = (value) => {
  if (value >= 85) return 'status-danger'
  if (value >= 70) return 'status-warning'
  return 'status-success'
}

const getMemoryStatus = (value) => {
  if (value >= 90) return 'status-danger'
  if (value >= 80) return 'status-warning'
  return 'status-success'
}

const getDiskStatus = (value) => {
  if (value >= 95) return 'status-danger'
  if (value >= 85) return 'status-warning'
  return 'status-success'
}

const formatTime = (timeStr) => {
  if (!timeStr) return '--'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  fetchServers()
  fetchRecentData()
  
  // 每30秒自动刷新数据
  setInterval(() => {
    fetchRecentData()
  }, 30000)
})
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome {
  background: white;
  padding: 30px;
  border-radius: 8px;
  text-align: center;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.welcome h1 {
  color: #409eff;
  margin-bottom: 10px;
  font-size: 28px;
}

.welcome p {
  color: #606266;
  font-size: 16px;
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}


.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-primary {
  background: #409eff;
  color: white;
}

.btn-primary:hover {
  background: #66b1ff;
}

.btn-success {
  background: #409eff;
  color: white;
}

.btn-success:hover {
  background: #66b1ff;
}

.btn-warning {
  background: #409eff;
  color: white;
}

.btn-warning:hover {
  background: #66b1ff;
}

.btn-small {
  padding: 6px 12px;
  font-size: 12px;
}

.data-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h3 {
  margin: 0;
  color: #606266;
}

.table-container {
  overflow-x: auto;
  max-height: 520px;
  overflow-y: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
}

.data-table th {
  background: #f5f7fa;
  font-weight: 600;
  color: #909399;
}

.data-table tr:hover {
  background: #f5f7fa;
}

.status-success {
  color: #67c23a;
  font-weight: bold;
}

.status-warning {
  color: #e6a23c;
  font-weight: bold;
}

.status-danger {
  color: #f56c6c;
  font-weight: bold;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .action-buttons {
    justify-content: center;
  }
  
  .section-header {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
}

@media (max-width: 480px) {
  .stats {
    grid-template-columns: 1fr;
  }
}
</style>
