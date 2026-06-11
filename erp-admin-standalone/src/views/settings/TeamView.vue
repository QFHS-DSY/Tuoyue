<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left"><h1>团队管理</h1><p>子账号管理 · 权限分配 · 操作审计</p></div>
      <div class="page-header-right">
        <el-button @click="showAuditLog"><el-icon><Document /></el-icon> 操作日志</el-button>
        <el-button type="primary" @click="openAddDialog"><el-icon><Plus /></el-icon> 添加子账号</el-button>
      </div>
    </div>

    <el-card shadow="never">
      <el-table :data="members" v-loading="loading" stripe>
        <el-table-column prop="username" label="用户名" width="180" />
        <el-table-column label="状态" width="100">
          <template #default="{row}">
            <el-tag :type="row.is_active?'success':'danger'" size="small">{{ row.is_active?'正常':'禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="角色" width="120">
          <template #default>
            <el-tag size="small" type="info">运营</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="date_joined" label="创建时间" width="180" />
        <el-table-column label="操作" min-width="200">
          <template #default="{row}">
            <el-button size="small" @click="toggleStatus(row)">{{ row.is_active?'禁用':'启用' }}</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加子账号 -->
    <el-dialog v-model="addVisible" title="添加子账号" width="450px">
      <el-form :model="addForm" label-position="top">
        <el-form-item label="用户名(手机号)" required><el-input v-model="addForm.username" /></el-form-item>
        <el-form-item label="登录密码" required><el-input v-model="addForm.password" show-password /></el-form-item>
        <el-form-item label="角色"><el-select v-model="addForm.role" style="width:100%"><el-option v-for="r in roles" :key="r" :label="r" :value="r" /></el-select></el-form-item>
        <el-form-item label="操作权限"><el-checkbox-group v-model="addForm.permissions"><el-checkbox v-for="p in perms" :key="p" :label="p">{{p}}</el-checkbox></el-checkbox-group></el-form-item>
      </el-form>
      <template #footer><el-button @click="addVisible=false">取消</el-button><el-button type="primary" @click="submitAdd">创建</el-button></template>
    </el-dialog>

    <!-- 操作日志 -->
    <el-dialog v-model="logVisible" title="操作日志" width="650px">
      <el-table :data="logs" stripe>
        <el-table-column prop="time" label="时间" width="160" />
        <el-table-column prop="operator" label="操作人" width="100" />
        <el-table-column prop="action" label="操作内容" />
        <el-table-column prop="ip" label="IP" width="140" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, Plus } from '@element-plus/icons-vue'
import { getTeamMembers, createTeamMember, updateTeamMember, deleteTeamMember, getTeamAuditLogs } from '@/api/team'

const members = ref([]); const loading = ref(false)
const addVisible = ref(false); const logVisible = ref(false); const logs = ref([])
const roles = ['运营','财务','客服','采购']
const perms = ['商品管理','订单管理','库存查看','数据导出','店铺设置']
const addForm = reactive({ username:'', password:'Test123456', role:'运营', permissions:[] })

async function loadData() { loading.value = true; try { const r = await getTeamMembers(); members.value = r?.data?.members || [] } finally { loading.value = false } }
function openAddDialog() { addForm.username=''; addForm.password='Test123456'; addForm.permissions=[]; addVisible.value=true }
async function submitAdd() {
  if (!addForm.username) return ElMessage.warning('请输入用户名')
  try { await createTeamMember({...addForm}); ElMessage.success('创建成功'); addVisible.value = false; loadData() } catch { ElMessage.error('创建失败') }
}
async function toggleStatus(row) {
  try { await updateTeamMember(row.id, {is_active:!row.is_active}); ElMessage.success('操作成功'); loadData() } catch { ElMessage.error('操作失败') }
}
async function handleDelete(row) {
  try { await ElMessageBox.confirm(`确定删除子账号 ${row.username}？`); await deleteTeamMember(row.id); ElMessage.success('已删除'); loadData() } catch {}
}
async function showAuditLog() { logVisible.value = true; try { const r = await getTeamAuditLogs(); logs.value = r?.data?.logs || [] } catch {} }

onMounted(loadData)
</script>

<style scoped>
.page-container { padding:24px;max-width:1200px;margin:0 auto }
.page-header { display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:24px }
.page-header-left h1 { margin:0 0 4px;font-size:22px;font-weight:600 }
.page-header-left p { margin:0;color:#909399;font-size:13px }
.page-header-right { display:flex;gap:8px }
</style>
