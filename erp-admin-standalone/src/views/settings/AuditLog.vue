<template>
  <div class="page-container">
    <div class="page-header"><h2>审计日志</h2></div>
    <div class="page-body">
      <el-row :gutter="12" style="margin-bottom:12px">
        <el-col :span="4"><el-select v-model="filters.audit_type" placeholder="审计类型" clearable @change="loadData"><el-option label="登录" value="LOGIN" /><el-option label="登出" value="LOGOUT" /><el-option label="权限变更" value="PERM_CHANGE" /><el-option label="角色变更" value="ROLE_CHANGE" /><el-option label="配置变更" value="CONFIG_CHANGE" /><el-option label="数据导出" value="DATA_EXPORT" /><el-option label="安全事件" value="SECURITY" /></el-select></el-col>
        <el-col :span="4"><el-input v-model="filters.search" placeholder="搜索动作/目标" clearable @input="loadData" /></el-col>
      </el-row>
      <el-table :data="auditList" border>
        <el-table-column prop="user_name" label="用户" width="120" />
        <el-table-column label="类型" width="100"><template #default="{row}"><el-tag size="small">{{ row.audit_type }}</el-tag></template></el-table-column>
        <el-table-column prop="action" label="动作" width="150" />
        <el-table-column prop="target" label="目标" width="180" />
        <el-table-column prop="ip_address" label="IP" width="140" />
        <el-table-column label="结果" width="80"><template #default="{ row }"><el-tag :type="r.result==='SUCCESS'?'success':'danger'">{{ row.result }}</el-tag></template></el-table-column>
        <el-table-column prop="created_at" label="时间" width="170" />
      </el-table>
      <el-pagination v-model:current-page="page" :total="total" layout="total,prev,pager,next" @current-change="loadData" style="margin-top:12px" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAuditLogs } from '@/api/sysSettings'

const auditList = ref([])
const page = ref(1); const total = ref(0)
const filters = ref({ audit_type: '', search: '' })

async function loadData() {
  const res = await getAuditLogs({ page: page.value, ...filters.value })
  auditList.value = res.results || res; total.value = res.count || 0
}

onMounted(loadData)
</script>
