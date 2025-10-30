import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { monitorApi } from '@/api'

export const useMonitorStore = defineStore('monitor', () => {
  // 状态
  const cpuData = ref([])
  const memData = ref([])
  const diskData = ref([])
  const loading = ref(false)
  const error = ref(null)

  // 计算属性 - 转换为前端需要的格式
  const latestCpuData = computed(() => {
    const latest = cpuData.value[cpuData.value.length - 1]
    if (!latest) return null
    return {
      id: latest.id,
      name: latest.server?.server_name || 'Unknown',
      usage: parseFloat(String(latest.cpu_value)) || 0,
      cores: 'N/A', // 后端没有核心数字段
      frequency: 'N/A', // 后端没有频率字段
      time: latest.recorded_at
    }
  })

  const latestMemData = computed(() => {
    const latest = memData.value[memData.value.length - 1]
    if (!latest) return null
    return {
      id: latest.id,
      name: latest.server?.server_name || 'Unknown',
      usage: parseFloat(String(latest.memory_value)) || 0,
      total: 0, // 后端没有总量字段
      used: 0, // 后端没有使用量字段
      free: 0, // 后端没有空闲量字段
      time: latest.recorded_at
    }
  })

  const latestDiskData = computed(() => {
    const latest = diskData.value[diskData.value.length - 1]
    if (!latest) return null
    return {
      id: latest.id,
      name: latest.server?.server_name || 'Unknown',
      usage: parseFloat(String(latest.disk_value)) || 0,
      total: 0, // 后端没有总量字段
      used: 0, // 后端没有使用量字段
      free: 0, // 后端没有空闲量字段
      path: '/', // 默认路径
      time: latest.recorded_at
    }
  })

  // 获取监控数据
  const fetchMonitorData = async (params) => {
    try {
      loading.value = true
      error.value = null
      const response = await monitorApi.getMonitorData(params)
      // 后端返回格式: { code: 0, msg: "success", data: [...] }
      const allData = response.data || []
      
      // 现在后端返回的是合并的数据，每个记录包含所有指标
      // 直接使用所有数据，前端组件会根据需要选择特定指标
      cpuData.value = allData
      memData.value = allData
      diskData.value = allData
    } catch (err) {
      error.value = err.message || '获取监控数据失败'
      console.error('获取监控数据失败:', err)
    } finally {
      loading.value = false
    }
  }

  // 获取CPU数据（兼容性方法）
  const fetchCpuData = async (params) => {
    await fetchMonitorData(params)
  }

  // 获取内存数据（兼容性方法）
  const fetchMemData = async (params) => {
    await fetchMonitorData(params)
  }

  // 获取磁盘数据（兼容性方法）
  const fetchDiskData = async (params) => {
    await fetchMonitorData(params)
  }

  // 获取所有监控数据
  const fetchAllData = async () => {
    await fetchMonitorData()
  }

  // CRUD操作
  const addMonitorData = async (data) => {
    try {
      loading.value = true
      await monitorApi.addMonitorData(data)
      await fetchMonitorData() // 刷新数据
    } catch (err) {
      error.value = err.message || '添加监控数据失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 兼容性方法
  const addCpuData = addMonitorData
  const addMemData = addMonitorData
  const addDiskData = addMonitorData

  return {
    // 状态
    cpuData,
    memData,
    diskData,
    loading,
    error,
    // 计算属性
    latestCpuData,
    latestMemData,
    latestDiskData,
    // 查询方法
    fetchMonitorData,
    fetchCpuData,
    fetchMemData,
    fetchDiskData,
    fetchAllData,
    // CRUD方法
    addMonitorData,
    addCpuData,
    addMemData,
    addDiskData
  }
})
