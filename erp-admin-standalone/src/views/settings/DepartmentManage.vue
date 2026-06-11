<template>
  <div class="page-container">
    <div class="page-header">
      <h2>部门管理</h2>
      <el-button type="primary" @click="handleAdd(null)">新建部门</el-button>
    </div>
    <div class="page-body">
      <el-table :data="tableData" row-key="id" border default-expand-all :tree-props="{children:'children'}">
        <el-table-column prop="name" label="部门名称" min-width="200" />
        <el-table-column prop="code" label="部门编码" width="150" />
        <el-table-column prop="level" label="层级" width="80" />
        <el-table-column prop="manager_name" label="负责人" width="120" />
        <el-table-column label="状态" width="80">
          <template #default="{row}"><el-tag :type="row.status?'success':'danger'">{{ row.status ? '启用' : '禁用' }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{row}">
            <el-button link type="primary" size="small" @click="handleAdd(row)">添加子部门</el-button>
            <el-button link type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑部门' : '新建部门'" width="520px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="部门名称" prop="name"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="部门编码" prop="code"><el-input v-model="form.code" /></el-form-item>
        <el-form-item label="上级部门" prop="parent"><el-tree-select v-model="form.parent" :data="departmentOptions" check-strictly :props="{label:'name',value:'id'}" clearable placeholder="无(根部门)" style="width:100%" /></el-form-item>
        <el-form-item label="排序" prop="sort_order"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
        <el-form-item label="状态" prop="status"><el-switch v-model="form.status" /></el-form-item>
        <el-form-item label="描述" prop="description"><el-input v-model="form.description" type="textarea" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSubmit">确定</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDepartmentTree, getDepartmentSimple, createDepartment, updateDepartment, deleteDepartment } from '@/api/sysSettings'

const tableData = ref([])
const departmentOptions = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentId = ref(null)
const formRef = ref(null)
const form = reactive({ name: '', code: '', parent: null, sort_order: 0, status: true, description: '' })
const rules = { name: [{ required: true, message: '请输入部门名称' }], code: [{ required: true, message: '请输入部门编码' }] }

async function loadData() {
  const treeRes = await getDepartmentTree()
  tableData.value = treeRes.results || treeRes
  const simpleRes = await getDepartmentSimple()
  departmentOptions.value = simpleRes.results || simpleRes
}

function handleAdd(row) {
  isEdit.value = false; currentId.value = null
  Object.assign(form, { name: '', code: '', parent: row?.id || null, sort_order: 0, status: true, description: '' })
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true; currentId.value = row.id
  Object.assign(form, { name: row.name, code: row.code, parent: row.parent, sort_order: row.sort_order, status: row.status, description: row.description })
  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value.validate()
  const payload = { ...form }
  if (isEdit.value) await updateDepartment(currentId.value, payload)
  else await createDepartment(payload)
  ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
  dialogVisible.value = false
  loadData()
}

async function handleDelete(row) {
  await ElMessageBox.confirm('确定删除该部门？', '确认删除', { type: 'warning' })
  await deleteDepartment(row.id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>
