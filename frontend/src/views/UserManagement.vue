<template>
  <div class="user-management">
    <div class="page-header">
      <div class="card-header">
        <h2>用户管理</h2>
        <button class="btn btn-primary" @click="showAddDialog = true">
          添加用户
        </button>
      </div>
    </div>

    <!-- 用户列表 -->
    <div class="user-list">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>用户名</th>
              <th>角色</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.id }}</td>
              <td>{{ user.username }}</td>
              <td>
                <span :class="['role-tag', user.role]">
                  {{ user.role === 'admin' ? '管理员' : '普通用户' }}
                </span>
              </td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td>
                <button class="btn btn-small" @click="editUser(user)">编辑</button>
                <button class="btn btn-small" @click="resetPassword(user)">重置密码</button>
                <button v-if="user.role !== 'admin'" class="btn btn-small btn-danger" @click="deleteUser(user)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 添加用户对话框 -->
    <div v-if="showAddDialog" class="dialog-overlay" @click="showAddDialog = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>添加用户</h3>
          <button class="close-btn" @click="showAddDialog = false">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>用户名</label>
            <input v-model="userForm.username" placeholder="请输入用户名" />
          </div>
          <div class="form-group">
            <label>密码</label>
            <input v-model="userForm.password" type="password" placeholder="请输入密码" />
          </div>
          <div class="form-group">
            <label>邮箱</label>
            <input v-model="userForm.email" type="email" placeholder="请输入邮箱" />
          </div>
          <!-- 角色字段已删除，只能创建普通用户 -->
        </div>
        <div class="dialog-footer">
          <button class="btn" @click="showAddDialog = false">取消</button>
          <button class="btn btn-primary" @click="saveUser">确定</button>
        </div>
      </div>
    </div>

    <!-- 编辑用户对话框 -->
    <div v-if="showEditDialog" class="dialog-overlay" @click="showEditDialog = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>编辑用户</h3>
          <button class="close-btn" @click="showEditDialog = false">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>用户名</label>
            <input v-model="editForm.username" placeholder="请输入用户名" />
          </div>
          <div class="form-group">
            <label>邮箱</label>
            <input v-model="editForm.email" placeholder="请输入邮箱" />
          </div>
          <!-- 角色字段已删除，不允许修改角色 -->
          <div class="form-group">
            <label>新密码（可选）</label>
            <input v-model="editForm.password" type="password" placeholder="留空表示不修改密码" />
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn" @click="showEditDialog = false">取消</button>
          <button class="btn btn-primary" @click="saveEdit">确定</button>
        </div>
      </div>
    </div>

    <!-- 重置密码对话框 -->
    <div v-if="showResetDialog" class="dialog-overlay" @click="showResetDialog = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>重置密码</h3>
          <button class="close-btn" @click="showResetDialog = false">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>用户名</label>
            <input v-model="resetForm.username" readonly />
          </div>
          <div class="form-group">
            <label>新密码</label>
            <input v-model="resetForm.password" type="password" placeholder="请输入新密码" />
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn" @click="showResetDialog = false">取消</button>
          <button class="btn btn-primary" @click="savePassword">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
// 移除Element Plus依赖，使用原生JavaScript
import { userApi } from '@/api'

// 响应式数据
const loading = ref(false)
const users = ref([])
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const showResetDialog = ref(false)

const userForm = ref({
  username: '',
  password: '',
  email: ''
  // 角色固定为user，不需要在表单中设置
})

const editForm = ref({
  id: null,
  username: '',
  email: '',
  password: ''
  // 角色不允许修改
})

const resetForm = ref({
  username: '',
  password: ''
})

// 生命周期
onMounted(() => {
  loadUsers()
})

// 方法
const loadUsers = async () => {
  try {
    loading.value = true
    const response = await userApi.getUsers()
    if (response.code === 0) {
      users.value = response.data || []
    } else {
      alert('加载用户列表失败: ' + (response.msg || ''))
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
    alert('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const saveUser = async () => {
  try {
    const response = await userApi.addUser(userForm.value)
    console.log(response)
    if (response.code === 0) {
      alert('用户添加成功')
      showAddDialog.value = false
      userForm.value = { username: '', password: '', email: '' }
      loadUsers()
    } else {
      alert('用户添加失败: ' + (response.msg || ''))
    }
  } catch (error) {
    console.error('添加用户失败:', error)
    alert('添加用户失败')
  }
}

const editUser = (user) => {
  editForm.value = {
    id: user.id,
    username: user.username,
    email: user.email || '',
    password: ''
    // 角色不允许修改
  }
  showEditDialog.value = true
}

const saveEdit = async () => {
  try {
    const response = await userApi.updateUser(editForm.value.id, editForm.value)
    if (response.code === 0) {
      alert('用户更新成功')
      showEditDialog.value = false
      editForm.value = { id: null, username: '', email: '', role: 'user', password: '' }
      loadUsers()
    } else {
      alert('用户更新失败: ' + (response.msg || ''))
    }
  } catch (error) {
    console.error('更新用户失败:', error)
    alert('更新用户失败')
  }
}

const resetPassword = (user) => {
  resetForm.value = {
    username: user.username,
    password: ''
  }
  showResetDialog.value = true
}

const savePassword = async () => {
  try {
    const response = await userApi.resetPassword(resetForm.value.username, resetForm.value.password)
    if (response.code === 0) {
      alert('密码重置成功')
      showResetDialog.value = false
      resetForm.value = { username: '', password: '' }
    } else {
      alert('密码重置失败: ' + (response.msg || ''))
    }
  } catch (error) {
    console.error('重置密码失败:', error)
    alert('重置密码失败')
  }
}

const deleteUser = async (user) => {
  if (confirm('确定要删除用户 ' + user.username + ' 吗？')) {
    try {
      const response = await userApi.deleteUser(user.id)
      if (response.code === 0) {
        alert('用户删除成功')
        loadUsers()
      } else {
        alert('用户删除失败: ' + (response.msg || ''))
      }
    } catch (error) {
      console.error('删除用户失败:', error)
      alert('删除用户失败')
    }
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}
</script>

<style scoped>
.user-management {
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

.user-list {
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

.role-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.role-tag.admin {
  background: #f0f9ff;
  color: #409eff;
}

.role-tag.user {
  background: #f5f7fa;
  color: #909399;
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
  width: 400px;
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

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #409eff;
}

.dialog-footer {
  padding: 20px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>