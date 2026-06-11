<template>
  <div class="page-container">
    <div class="page-header"><h2>角色管理</h2><el-button type="primary" @click="handleAdd">新建角色</el-button></div>
    <div class="page-body">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-input v-model="search" placeholder="搜索角色名称" clearable @input="loadData" style="width:240px;margin-bottom:12px" />
          <el-table :data="tableData" border highlight-current-row @row-click="onRoleClick">
            <el-table-column prop="name" label="角色名称" />
            <el-table-column prop="code" label="角色编码" width="150" />
            <el-table-column label="状态" width="80"><template #default="{ row }"><el-tag :type="row.status?'success':'danger'">{{row.status?'启用':'禁用'}}</el-tag></template></el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{row}"><el-button link type="primary" size="small" @click.stop="handleEdit(row)">编辑</el-button><el-button link type="danger" size="small" @click.stop="handleDelete(row)">删除</el-button></template>
            </el-table-column>
          </el-table>
          <el-pagination v-model:current-page="page" :total="total" layout="total,prev,pager,next" @current-change="loadData" style="margin-top:12px" />
        </el-col>
        <el-col :span="12">
          <div style="padding-left:16px;border-left:1px solid #eee;min-height:400px">
            <h4 v-if="currentRole">权限分配 - {{ currentRole.name }}</h4>
            <h4 v-else>请选择一个角色</h4>
            <el-tree v-if="currentRole" ref="permTreeRef" :data="permTree" show-checkbox node-key="id" :default-checked-keys="checkedKeys" :props="{label:'name'}" />
            <el-button v-if="currentRole" type="primary" size="small" @click="savePermissions" style="margin-top:12px">保存权限</el-button>
          </div>
        </el-col>
      </el-row>
    </div>
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑角色' : '新建角色'" width="460px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="角色名称" prop="name"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="角色编码" prop="code"><el-input v-model="form.code" /></el-form-item>
        <el-form-item label="描述" prop="description"><el-input v-model="form.description" type="textarea" /></el-form-item>
        <el-form-item label="状态" prop="status"><el-switch v-model="form.status" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSubmit">确定</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getRoles, createRole, updateRole, deleteRole, getRolePermissions, setRolePermissions, getPermissionTree } from '@/api/sysSettings'

const tableData = ref([])
const search = ref('')
const page = ref(1)
const total = ref(0)
const currentRole = ref(null)
const permTree = ref([])
const checkedKeys = ref([])
const permTreeRef = ref(null)
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentRoleId = ref(null)
const formRef = ref(null)
const form = ref({ name: '', code: '', description: '', status: true })
const rules = { name: [{ required: true }], code: [{ required: true }] }

async function loadData() {
  const res = await getRoles({ page: page.value, search: search.value })
  tableData.value = res.results || res
  total.value = res.count || 0
}

async function loadPermTree() {
  const res = await getPermissionTree()
  permTree.value = res.results || res
}

async function onRoleClick(row) {
  currentRole.value = row; currentRoleId.value = row.id
  const res = await getRolePermissions(row.id)
  checkedKeys.value = res.results || res
}

async function savePermissions() {
  const keys = [...permTreeRef.value.getCheckedKeys(), ...permTreeRef.value.getHalfCheckedKeys()]
  await setRolePermissions(currentRoleId.value, { permission_ids: keys })
  ElMessage.success('权限已保存')
}

function handleAdd() { isEdit.value = false; form.value = { name: '', code: '', description: '', status: true }; dialogVisible.value = true }
function handleEdit(row) { isEdit.value = true; currentRoleId.value = row.id; form.value = { name: row.name, code: row.code, description: row.description, status: row.status }; dialogVisible.value = true }
async function handleSubmit() { await formRef.value.validate(); const p = form.value; isEdit.value ? await updateRole(currentRoleId.value, p) : await createRole(p); ElMessage.success(isEdit.value ? '更新成功' : '创建成功'); dialogVisible.value = false; loadData() }
async function handleDelete(row) { await ElMessageBox.confirm('确定删除?', '确认', { type: 'warning' }); await deleteRole(row.id); ElMessage.success('已删除'); loadData() }

onMounted(() => { loadData(); loadPermTree() })
</script>
