<template>
  <div class="page-container">
    <div class="page-header"><h2>平台授权管理</h2><el-button type="primary" @click="handleAdd">添加授权</el-button></div>
    <div class="page-body">
      <el-row :gutter="12" style="margin-bottom:12px">
        <el-col :span="4"><el-select v-model="filters.platform" placeholder="平台" clearable @change="loadData"><el-option v-for="p in platforms" :key="p.id" :label="p.platform_name" :value="p.id" /></el-select></el-col>
        <el-col :span="4"><el-select v-model="filters.status" placeholder="状态" clearable @change="loadData"><el-option label="已授权" value="ACTIVE" /><el-option label="已过期" value="EXPIRED" /><el-option label="已撤销" value="REVOKED" /></el-select></el-col>
        <el-col :span="4"><el-input v-model="filters.search" placeholder="搜索账户" clearable @input="loadData" /></el-col>
      </el-row>
      <el-table :data="tableData" border>
        <el-table-column prop="platform_name" label="平台" width="120" />
        <el-table-column prop="account_name" label="账户名称" width="160" />
        <el-table-column prop="account_id" label="账户ID" width="160" />
        <el-table-column label="状态" width="100"><template #default="{row}"><el-tag :type="row.auth_status==='ACTIVE'?'success':row.auth_status==='EXPIRED'?'warning':'danger'">{{ row.auth_status }}</el-tag></template></el-table-column>
        <el-table-column prop="token_expires_at" label="过期时间" width="180" />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{row}">
            <el-button link type="primary" size="small" @click="handleRefresh(row)">刷新Token</el-button>
            <el-button link type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" :total="total" layout="total,prev,pager,next" @current-change="loadData" style="margin-top:12px" />
    </div>
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑授权' : '添加平台授权'" width="520px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
        <el-form-item label="平台" prop="platform"><el-select v-model="form.platform" placeholder="选择平台" style="width:100%"><el-option v-for="p in platforms" :key="p.id" :label="p.platform_name" :value="p.id" /></el-select></el-form-item>
        <el-form-item label="账户名称" prop="account_name"><el-input v-model="form.account_name" /></el-form-item>
        <el-form-item label="账户ID" prop="account_id"><el-input v-model="form.account_id" /></el-form-item>
        <el-form-item label="AccessToken"><el-input v-model="form.access_token" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="RefreshToken"><el-input v-model="form.refresh_token" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="状态"><el-select v-model="form.auth_status"><el-option label="已授权" value="ACTIVE" /><el-option label="已过期" value="EXPIRED" /><el-option label="已撤销" value="REVOKED" /></el-select></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSubmit">确定</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPlatformAuths, createPlatformAuth, updatePlatformAuth, deletePlatformAuth, refreshPlatformToken, getPlatformConfigs } from '@/api/sysSettings'

const tableData = ref([])
const platforms = ref([])
const page = ref(1); const total = ref(0)
const filters = ref({ platform: null, status: '', search: '' })
const dialogVisible = ref(false); const isEdit = ref(false); const currentId = ref(null)
const formRef = ref(null)
const form = ref({ platform: null, account_name: '', account_id: '', access_token: '', refresh_token: '', auth_status: 'ACTIVE' })
const rules = { platform: [{ required: true }], account_name: [{ required: true }], account_id: [{ required: true }] }

async function loadData() {
  const res = await getPlatformAuths({ page: page.value, ...filters.value })
  tableData.value = res.results || res; total.value = res.count || 0
}

async function loadPlatforms() {
  const res = await getPlatformConfigs()
  platforms.value = res.results || res
}

function handleAdd() { isEdit.value = false; currentId.value = null; form.value = { platform: null, account_name: '', account_id: '', access_token: '', refresh_token: '', auth_status: 'ACTIVE' }; dialogVisible.value = true }
function handleEdit(row) { isEdit.value = true; currentId.value = row.id; form.value = { platform: row.platform, account_name: row.account_name, account_id: row.account_id, access_token: row.access_token, refresh_token: row.refresh_token, auth_status: row.auth_status }; dialogVisible.value = true }
async function handleSubmit() { await formRef.value.validate(); const p = form.value; isEdit.value ? await updatePlatformAuth(currentId.value, p) : await createPlatformAuth(p); ElMessage.success(isEdit.value ? '更新成功' : '创建成功'); dialogVisible.value = false; loadData() }
async function handleDelete(row) { await ElMessageBox.confirm('确定删除?', '确认', { type: 'warning' }); await deletePlatformAuth(row.id); ElMessage.success('已删除'); loadData() }
async function handleRefresh(row) { await refreshPlatformToken(row.id); ElMessage.success('刷新请求已发出'); loadData() }

onMounted(() => { loadData(); loadPlatforms() })
</script>
