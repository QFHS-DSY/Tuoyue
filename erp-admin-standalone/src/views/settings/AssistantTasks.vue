<template>
  <div class="page-container">
    <div class="page-header"><h2>助手任务管理</h2><el-button type="primary" @click="handleAdd">新建任务</el-button></div>
    <div class="page-body">
      <el-row :gutter="12" style="margin-bottom:12px">
        <el-col :span="4"><el-select v-model="filters.task_type" placeholder="任务类型" clearable @change="loadData"><el-option label="同步" value="SYNC" /><el-option label="采集" value="COLLECT" /><el-option label="监控" value="MONITOR" /><el-option label="报表" value="REPORT" /><el-option label="备份" value="BACKUP" /></el-select></el-col>
        <el-col :span="4"><el-select v-model="filters.status" placeholder="状态" clearable @change="loadData"><el-option label="空闲" value="IDLE" /><el-option label="运行中" value="RUNNING" /><el-option label="成功" value="SUCCESS" /><el-option label="失败" value="FAILED" /><el-option label="已禁用" value="DISABLED" /></el-select></el-col>
        <el-col :span="4"><el-input v-model="filters.search" placeholder="搜索任务" clearable @input="loadData" /></el-col>
      </el-row>
      <el-table :data="tableData" border>
        <el-table-column prop="task_no" label="编号" width="140" />
        <el-table-column prop="task_name" label="任务名称" min-width="180" />
        <el-table-column prop="task_type" label="类型" width="100" />
        <el-table-column prop="cron_expression" label="Cron表达式" width="140" />
        <el-table-column label="状态" width="90"><template #default="{row}"><el-tag :type="row.status==='IDLE'?'':row.status==='RUNNING'?'warning':row.status==='SUCCESS'?'success':'danger'">{{ row.status }}</el-tag></template></el-table-column>
        <el-table-column prop="last_run_at" label="上次运行" width="170" />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{row}">
            <el-button link type="primary" size="small" @click="handleRun(row)">执行</el-button>
            <el-button link type="primary" size="small" @click="handleToggle(row)">{{ row.status==='DISABLED'?'启用':'禁用' }}</el-button>
            <el-button link type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" :total="total" layout="total,prev,pager,next" @current-change="loadData" style="margin-top:12px" />
    </div>
    <el-dialog v-model="dialogVisible" :title="isEdit?'编辑任务':'新建任务'" width="540px">
      <el-form ref="formRef" :model="form" label-width="100px">
        <el-form-item label="任务名称" prop="task_name"><el-input v-model="form.task_name" /></el-form-item>
        <el-form-item label="任务类型"><el-select v-model="form.task_type"><el-option label="同步" value="SYNC" /><el-option label="采集" value="COLLECT" /><el-option label="监控" value="MONITOR" /><el-option label="报表" value="REPORT" /><el-option label="备份" value="BACKUP" /></el-select></el-form-item>
        <el-form-item label="Cron表达式"><el-input v-model="form.cron_expression" placeholder="0 */6 * * *" /></el-form-item>
        <el-form-item label="优先级"><el-input-number v-model="form.priority" :min="1" :max="10" /></el-form-item>
        <el-form-item label="任务参数"><el-input v-model="form.task_params_text" type="textarea" :rows="3" placeholder='{"key":"value"}' /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSubmit">确定</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAssistantTasks, createAssistantTask, updateAssistantTask, executeAssistantTask, toggleAssistantTask } from '@/api/sysSettings'

const tableData = ref([])
const page = ref(1); const total = ref(0)
const filters = ref({ task_type: '', status: '', search: '' })
const dialogVisible = ref(false); const isEdit = ref(false); const curId = ref(null)
const formRef = ref(null)
const form = ref({ task_name: '', task_type: 'SYNC', cron_expression: '', priority: 1, task_params_text: '{}' })

async function loadData() {
  const res = await getAssistantTasks({ page: page.value, ...filters.value })
  tableData.value = res.results || res; total.value = res.count || 0
}

function handleAdd() { isEdit.value = false; form.value = { task_name: '', task_type: 'SYNC', cron_expression: '', priority: 1, task_params_text: '{}' }; dialogVisible.value = true }
function handleEdit(r) { isEdit.value = true; curId.value = r.id; form.value = { task_name: r.task_name, task_type: r.task_type, cron_expression: r.cron_expression, priority: r.priority, task_params_text: JSON.stringify(r.task_params) }; dialogVisible.value = true }
async function handleSubmit() {
  try { JSON.parse(form.value.task_params_text) } catch { return ElMessage.error('任务参数格式错误') }
  const p = { ...form.value, task_params: JSON.parse(form.value.task_params_text) }
  delete p.task_params_text
  isEdit.value ? await updateAssistantTask(curId.value, p) : await createAssistantTask(p)
  ElMessage.success(isEdit.value ? '更新成功' : '创建成功'); dialogVisible.value = false; loadData()
}
async function handleRun(r) { await executeAssistantTask(r.id); ElMessage.success('任务已触发'); loadData() }
async function handleToggle(r) { await toggleAssistantTask(r.id); ElMessage.success('状态已切换'); loadData() }

onMounted(loadData)
</script>
