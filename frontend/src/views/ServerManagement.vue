<template>
  <div class="server-management">
    <div class="page-header">
      <div class="card-header">
        <h2>服务器管理</h2>
        <button class="btn btn-primary" @click="showAddDialog = true">
          添加服务器
        </button>
      </div>
    </div>

    <!-- 服务器列表 -->
    <div class="server-list">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>服务器名称</th>
              <th>IP地址</th>
              <th>端口</th>
              <!-- 状态列已删除 -->
              <th>关联用户</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="server in servers" :key="server.id">
              <td>{{ server.id }}</td>
              <td>{{ server.server_name }}</td>
              <td>{{ server.ip_address }}</td>
              <td>{{ server.port }}</td>
              <!-- 状态列已删除 -->
              <td>
                <span v-for="user in server.users" :key="user.id" class="user-tag">
                  {{ user.username }}
                </span>
              </td>
              <td>{{ formatDate(server.created_at) }}</td>
              <td>
                <button class="btn btn-small" @click="editServer(server)">编辑</button>
                <button class="btn btn-small" @click="manageUsers(server)">管理用户</button>
                <button class="btn btn-small btn-danger" @click="deleteServer(server)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 添加/编辑服务器对话框 -->
    <div v-if="showAddDialog" class="dialog-overlay" @click="showAddDialog = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>{{ editingServer ? '编辑服务器' : '添加服务器' }}</h3>
          <button class="close-btn" @click="showAddDialog = false">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>服务器名称</label>
            <input v-model="serverForm.server_name" placeholder="请输入服务器名称" />
          </div>
          <div class="form-group">
            <label>IP地址</label>
            <input v-model="serverForm.ip_address" placeholder="请输入IP地址" />
          </div>
          <div class="form-group">
            <label>端口</label>
            <input v-model="serverForm.port" type="number" placeholder="请输入端口" />
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn" @click="showAddDialog = false">取消</button>
          <button class="btn btn-primary" @click="saveServer">确定</button>
        </div>
      </div>
    </div>

    <!-- 管理用户对话框 -->
    <div v-if="showUserDialog" class="dialog-overlay" @click="showUserDialog = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>管理用户 - {{ currentServer?.server_name }}</h3>
          <button class="close-btn" @click="showUserDialog = false">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="user-list">
            <div v-for="user in allUsers" :key="user.id" class="user-item">
              <label>
                <input 
                  type="checkbox" 
                  :value="user.id" 
                  v-model="selectedUserIds"
                />
                {{ user.username }}
              </label>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn" @click="showUserDialog = false">取消</button>
          <button class="btn btn-primary" @click="saveUsers">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
// 移除Element Plus依赖，使用原生JavaScript
import { serverApi, userApi } from '@/api'

// 响应式数据
const loading = ref(false)
const servers = ref([])
const allUsers = ref([])
const showAddDialog = ref(false)
const showUserDialog = ref(false)
const editingServer = ref(null)
const currentServer = ref(null)
const selectedUserIds = ref([])

const serverForm = ref({
  server_name: '',
  ip_address: '',
  port: 22
})

// 计算属性
const serverRules = computed(() => ({
  server_name: [{ required: true, message: '请输入服务器名称', trigger: 'blur' }],
  ip_address: [{ required: true, message: '请输入IP地址', trigger: 'blur' }],
  port: [{ required: true, message: '请输入端口', trigger: 'blur' }]
}))

// 生命周期
onMounted(() => {
  loadServers()
  loadUsers()
})

// 方法
const loadServers = async () => {
  try {
    loading.value = true
    const response = await serverApi.getServers()
    if (response.code === 0) {
      servers.value = response.data || []
    } else {
      alert('加载服务器列表失败: ' + (response.msg || ''))
    }
  } catch (error) {
    console.error('加载服务器列表失败:', error)
    alert('加载服务器列表失败')
  } finally {
    loading.value = false
  }
}

const loadUsers = async () => {
  try {
    const response = await userApi.getUsers()
    if (response.code === 0) {
      allUsers.value = response.data || []
    } else {
      console.error('加载用户列表失败:', response.msg)
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
  }
}

const editServer = (server) => {
  editingServer.value = server
  serverForm.value = {
    server_name: server.server_name,
    ip_address: server.ip_address,
    port: server.port
  }
  showAddDialog.value = true
}

const saveServer = async () => {
  try {
    if (editingServer.value) {
      // 编辑服务器
      const response = await serverApi.updateServer(editingServer.value.id, serverForm.value)
      if (response.code === 0) {
        alert('服务器更新成功')
        showAddDialog.value = false
        loadServers()
      } else {
        alert('服务器更新失败: ' + (response.msg || ''))
      }
    } else {
      // 添加服务器
      const response = await serverApi.addServer(serverForm.value)
      if (response.code === 0) {
        alert('服务器添加成功')
        showAddDialog.value = false
        loadServers()
      } else {
        alert('服务器添加失败: ' + (response.msg || ''))
      }
    }
  } catch (error) {
    console.error('保存服务器失败:', error)
    alert('保存服务器失败')
  }
}

const deleteServer = async (server) => {
  if (confirm('确定要删除服务器 ' + server.server_name + ' 吗？')) {
    try {
      const response = await serverApi.deleteServer(server.id)
      if (response.code === 0) {
        alert('服务器删除成功')
        loadServers()
      } else {
        alert('服务器删除失败: ' + (response.msg || ''))
      }
    } catch (error) {
      console.error('删除服务器失败:', error)
      alert('删除服务器失败')
    }
  }
}

const manageUsers = (server) => {
  currentServer.value = server
  selectedUserIds.value = server.users.map(user => user.id)
  showUserDialog.value = true
}

const saveUsers = async () => {
  try {
    // 使用 updateServer 提交用户关联
    const response = await serverApi.updateServer(currentServer.value.id, { user_ids: selectedUserIds.value })
    if (response.code === 0) {
      alert('用户关联更新成功')
      showUserDialog.value = false
      loadServers()
    } else {
      alert('用户关联更新失败: ' + (response.msg || ''))
    }
  } catch (error) {
    console.error('更新用户关联失败:', error)
    alert('更新用户关联失败')
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}
</script>

<style scoped>
.server-management {
  padding: 20px;
}

.page-header {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  color: #303133;
}

.server-list {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  overflow: hidden;
}

.loading {
  padding: 40px;
  text-align: center;
  color: #909399;
}

.table-container {
  overflow-x: auto;
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
  font-weight: 500;
  color: #909399;
}

.data-table tr:hover {
  background: #f5f7fa;
}

/* 状态样式已删除 */

.user-tag {
  display: inline-block;
  background: #f0f9ff;
  color: #409eff;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
  margin-right: 4px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
  margin-right: 8px;
}

.btn-primary {
  background: #409eff;
  color: white;
}

.btn-primary:hover {
  background: #66b1ff;
}

.btn-small {
  padding: 4px 8px;
  font-size: 12px;
}

.btn-danger {
  background: #f56c6c;
  color: white;
}

.btn-danger:hover {
  background: #f78989;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
}

.dialog-header {
  padding: 20px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-header h3 {
  margin: 0;
  color: #303133;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #909399;
}

.dialog-body {
  padding: 20px;
  max-height: 400px;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #606266;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus {
  outline: none;
  border-color: #409eff;
}

.user-list {
  max-height: 200px;
  overflow-y: auto;
}

.user-item {
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.user-item label {
  display: flex;
  align-items: center;
  cursor: pointer;
  margin: 0;
}

.user-item input[type="checkbox"] {
  margin-right: 8px;
}

.dialog-footer {
  padding: 20px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>