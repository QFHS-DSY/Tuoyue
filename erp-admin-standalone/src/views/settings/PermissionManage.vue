<template>
  <div class="page-container">
    <div class="page-header"><h2>权限管理</h2><el-button type="primary" @click="handleAdd(null)">新建权限</el-button></div>
    <div class="page-body">
      <el-table :data="tableData" row-key="id" border default-expand-all :tree-props="{children:'children'}">
        <el-table-column prop="name" label="权限名称" min-width="200" />
        <el-table-column prop="code" label="权限编码" width="180" />
        <el-table-column label="类型" width="100"><template #default="{row}"><el-tag size="small">{{ row.perm_type }}</el-tag></template></el-table-column>
        <el-table-column prop="resource_path" label="资源路径" width="200" />
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{row}">
            <el-button link type="primary" size="small" @click="handleAdd(row)">添加子权限</el-button>
            <el-button link type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <el-dialog v-model="dialogVisible" :title="isEdit?'编辑权限':'新建权限'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="权限名称" prop="name"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="权限编码" prop="code"><el-input v-model="form.code" /></el-form-item>
        <el-form-item label="权限类型"><el-select v-model="form.perm_type"><el-option label="菜单权限" value="MENU" /><el-option label="接口权限" value="API" /><el-option label="数据权限" value="DATA" /><el-option label="按钮权限" value="BUTTON" /></el-select></el-form-item>
        <el-form-item label="上级权限"><el-tree-select v-model="form.parent" :data="permOptions" check-strictly :props="{label:'name',value:'id'}" clearable placeholder="无(根权限)" style="width:100%" /></el-form-item>
        <el-form-item label="资源路径"><el-input v-model="form.resource_path" placeholder="/api/settings/departments/" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
        <el-form-item label="状态"><el-switch v-model="form.status" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSubmit">确定</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPermissionTree, createPermission, updatePermission, deletePermission } from '@/api/sysSettings'

const tableData = ref([])
const permOptions = ref([])
const dialogVisible = ref(false); const isEdit = ref(false); const curId = ref(null)
const formRef = ref(null)
const form = ref({ name: '', code: '', perm_type: 'API', parent: null, resource_path: '', sort_order: 0, status: true })
const rules = { name: [{ required: true }], code: [{ required: true }] }

async function load() {
  const res = await getPermissionTree()
  tableData.value = res.results || res
  permOptions.value = res.results || res
}

function handleAdd(row) {
  isEdit.value = false; curId.value = null
  form.value = { name: '', code: '', perm_type: 'API', parent: row?.id || null, resource_path: '', sort_order: 0, status: true }
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true; curId.value = row.id
  form.value = { name: row.name, code: row.code, perm_type: row.perm_type, parent: row.parent, resource_path: row.resource_path, sort_order: row.sort_order, status: row.status }
  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value.validate()
  isEdit.value ? await updatePermission(curId.value, form.value) : await createPermission(form.value)
  ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
  dialogVisible.value = false; load()
}

async function handleDelete(row) {
  await ElMessageBox.confirm('确定删除?', '确认', { type: 'warning' })
  await deletePermission(row.id)
  ElMessage.success('已删除'); load()
}

onMounted(load)
</script>
