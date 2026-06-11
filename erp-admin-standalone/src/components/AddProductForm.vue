<template>
  <el-form ref="formRef" :model="form" label-width="90px" :rules="rules">
    <el-form-item label="商品名称" prop="name">
      <el-input v-model="form.name" placeholder="请输入商品名称" />
    </el-form-item>
    <el-form-item label="SKU编号" prop="sku">
      <el-input v-model="form.sku" placeholder="如：SKU-2026-001" />
    </el-form-item>
    <el-form-item label="选择仓库" prop="warehouse">
      <el-select v-model="form.warehouse" placeholder="请选择仓库" style="width:100%">
        <el-option v-for="w in warehouses" :key="w" :label="w" :value="w" />
      </el-select>
    </el-form-item>
    <el-form-item label="仓库类型" prop="warehouseType">
      <el-select v-model="form.warehouseType" placeholder="请选择仓库类型" style="width:100%">
        <el-option label="本地仓" value="本地仓" />
        <el-option label="海外仓" value="海外仓" />
        <el-option label="虚拟仓" value="虚拟仓" />
        <el-option label="在途仓" value="在途仓" />
      </el-select>
    </el-form-item>
    <el-form-item label="初始库存" prop="stock">
      <el-input-number v-model="form.stock" :min="0" :max="999999" style="width:100%" />
    </el-form-item>
    <el-form-item label="安全库存" prop="safeStock">
      <el-input-number v-model="form.safeStock" :min="0" :max="999999" style="width:100%" />
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { addProduct } from '@/api/inventory'

const emit = defineEmits(['success'])
const warehouses = ['深圳仓', '广州仓', '海外仓(英国)']

const formRef = ref(null)
const form = reactive({ name: '', sku: '', warehouse: '', warehouseType: '', stock: 0, safeStock: 0 })
const submitting = ref(false)

function gtZero(rule, value, callback) {
  if (value === null || value === undefined || value === '' || value <= 0) {
    callback(new Error(rule.message || '数值必须大于 0'))
  } else {
    callback()
  }
}

const rules = {
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  sku: [{ required: true, message: '请输入SKU编号', trigger: 'blur' }],
  warehouse: [{ required: true, message: '请选择仓库', trigger: 'change' }],
  stock: [
    { required: true, message: '请输入初始库存', trigger: 'blur' },
    { validator: gtZero, message: '初始库存必须大于 0', trigger: 'blur' },
  ],
  safeStock: [
    { required: true, message: '请输入安全库存', trigger: 'blur' },
    { validator: gtZero, message: '安全库存必须大于 0', trigger: 'blur' },
  ],
}

async function submit() {
  if (!formRef.value) return
  formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      await addProduct({
        title: form.name,
        platform_product_id: form.sku,
        stock: form.stock,
        platform: '1688',
        attributes: { warehouse: form.warehouse, warehouse_type: form.warehouseType },
      })
      ElMessage.success(`商品 ${form.name} 建档成功`)
      form.name = ''; form.sku = ''; form.warehouse = ''; form.warehouseType = ''
      form.stock = 0; form.safeStock = 0
      emit('success')
    } catch (e) {
      ElMessage.error(e?.response?.data?.message || '建档失败')
    } finally {
      submitting.value = false
    }
  })
}

function reset() {
  form.name = ''; form.sku = ''; form.warehouse = ''; form.warehouseType = ''
  form.stock = 0; form.safeStock = 0
  formRef.value?.clearValidate()
}

defineExpose({ submit, submitting, reset })
</script>
