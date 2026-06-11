<template>
  <div class="page-container">
    <div class="page-header"><h2>仓库配置</h2></div>
    <div class="page-body">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="拓岳WMS仓库" name="wms">
          <div style="margin-bottom:12px"><el-button type="primary" @click="handleWmsAdd">添加仓库</el-button></div>
          <el-table :data="wmsList" border>
            <el-table-column prop="warehouse_name" label="仓库名称" />
            <el-table-column prop="warehouse_code" label="仓库编码" width="150" />
            <el-table-column prop="warehouse_type" label="类型" width="120" />
            <el-table-column prop="country" label="国家" width="100" />
            <el-table-column label="状态" width="80"><template #default="{ row }"><el-tag :type="row.status?'success':'danger'">{{row.status?'启用':'禁用'}}</el-tag></template></el-table-column>
            <el-table-column label="操作" width="160"><template #default="{row}"><el-button link type="primary" size="small" @click="handleWmsEdit(row)">编辑</el-button><el-button link type="danger" size="small" @click="handleWmsDelete(row)">删除</el-button></template></el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="第三方海外仓" name="third">
          <div style="margin-bottom:12px"><el-button type="primary" @click="handleThirdAdd">添加海外仓</el-button></div>
          <el-table :data="thirdList" border>
            <el-table-column prop="name" label="仓库名称" />
            <el-table-column prop="provider_name" label="服务商" width="120" />
            <el-table-column prop="warehouse_code" label="仓库编码" width="150" />
            <el-table-column prop="country" label="国家" width="100" />
            <el-table-column label="状态" width="80"><template #default="{ row }"><el-tag :type="row.status?'success':'danger'">{{row.status?'启用':'禁用'}}</el-tag></template></el-table-column>
            <el-table-column label="操作" width="160"><template #default="{row}"><el-button link type="primary" size="small" @click="handleThirdEdit(row)">编辑</el-button><el-button link type="danger" size="small" @click="handleThirdDelete(row)">删除</el-button></template></el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </div>
    <!-- WMS dialog -->
    <el-dialog v-model="wmsDialog" :title="wmsEdit ? '编辑仓库' : '添加仓库'" width="500px">
      <el-form ref="wmsFormRef" :model="wmsForm" label-width="100px">
        <el-form-item label="仓库名称" prop="warehouse_name"><el-input v-model="wmsForm.warehouse_name" /></el-form-item>
        <el-form-item label="仓库编码" prop="warehouse_code"><el-input v-model="wmsForm.warehouse_code" /></el-form-item>
        <el-form-item label="仓库类型"><el-select v-model="wmsForm.warehouse_type"><el-option label="自营" value="SELF" /><el-option label="第三方" value="THIRD_PARTY" /><el-option label="FBA" value="FBA" /></el-select></el-form-item>
        <el-form-item label="国家"><el-input v-model="wmsForm.country" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="wmsForm.address" /></el-form-item>
        <el-form-item label="联系人"><el-input v-model="wmsForm.contact_name" /></el-form-item>
        <el-form-item label="联系电话"><el-input v-model="wmsForm.contact_phone" /></el-form-item>
        <el-form-item label="状态"><el-switch v-model="wmsForm.status" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="wmsDialog=false">取消</el-button><el-button type="primary" @click="handleWmsSubmit">确定</el-button></template>
    </el-dialog>
    <!-- Third-party dialog -->
    <el-dialog v-model="thirdDialog" :title="thirdEdit ? '编辑海外仓' : '添加海外仓'" width="500px">
      <el-form ref="thirdFormRef" :model="thirdForm" label-width="110px">
        <el-form-item label="仓库名称" prop="name"><el-input v-model="thirdForm.name" /></el-form-item>
        <el-form-item label="服务商"><el-select v-model="thirdForm.provider_code"><el-option label="谷仓" value="GUCANG" /><el-option label="万邑通" value="WANYITONG" /><el-option label="4PX" value="4PX" /></el-select></el-form-item>
        <el-form-item label="服务商名称"><el-input v-model="thirdForm.provider_name" /></el-form-item>
        <el-form-item label="仓库编码"><el-input v-model="thirdForm.warehouse_code" /></el-form-item>
        <el-form-item label="国家"><el-input v-model="thirdForm.country" /></el-form-item>
        <el-form-item label="API地址"><el-input v-model="thirdForm.api_endpoint" /></el-form-item>
        <el-form-item label="AppKey"><el-input v-model="thirdForm.api_app_key" /></el-form-item>
        <el-form-item label="AppSecret"><el-input v-model="thirdForm.api_app_secret" type="password" /></el-form-item>
        <el-form-item label="状态"><el-switch v-model="thirdForm.status" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="thirdDialog=false">取消</el-button><el-button type="primary" @click="handleThirdSubmit">确定</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getWarehouseConfigs, createWarehouseConfig, updateWarehouseConfig, deleteWarehouseConfig, getThirdPartyWarehouses, createThirdPartyWarehouse, updateThirdPartyWarehouse } from '@/api/sysSettings'

const activeTab = ref('wms')
const wmsList = ref([]); const thirdList = ref([])
// WMS
const wmsDialog = ref(false); const wmsEdit = ref(false); const wmsCurId = ref(null)
const wmsFormRef = ref(null)
const wmsForm = ref({ warehouse_name: '', warehouse_code: '', warehouse_type: 'SELF', country: '', address: '', contact_name: '', contact_phone: '', status: true })
async function loadWms() { const res = await getWarehouseConfigs(); wmsList.value = res.results || res }
function handleWmsAdd() { wmsEdit.value = false; wmsForm.value = { warehouse_name: '', warehouse_code: '', warehouse_type: 'SELF', country: '', address: '', contact_name: '', contact_phone: '', status: true }; wmsDialog.value = true }
function handleWmsEdit(r) { wmsEdit.value = true; wmsCurId.value = r.id; wmsForm.value = { ...r }; wmsDialog.value = true }
async function handleWmsSubmit() { wmsEdit.value ? await updateWarehouseConfig(wmsCurId.value, wmsForm.value) : await createWarehouseConfig(wmsForm.value); ElMessage.success(wmsEdit.value ? '更新成功' : '创建成功'); wmsDialog.value = false; loadWms() }
async function handleWmsDelete(r) { await ElMessageBox.confirm('确定删除?', '确认', { type: 'warning' }); await deleteWarehouseConfig(r.id); ElMessage.success('已删除'); loadWms() }
// Third-party
const thirdDialog = ref(false); const thirdEdit = ref(false); const thirdCurId = ref(null)
const thirdFormRef = ref(null)
const thirdForm = ref({ name: '', provider_code: 'GUCANG', provider_name: '', warehouse_code: '', country: '', api_endpoint: '', api_app_key: '', api_app_secret: '', status: true })
async function loadThird() { const res = await getThirdPartyWarehouses(); thirdList.value = res.results || res }
function handleThirdAdd() { thirdEdit.value = false; thirdForm.value = { name: '', provider_code: 'GUCANG', provider_name: '', warehouse_code: '', country: '', api_endpoint: '', api_app_key: '', api_app_secret: '', status: true }; thirdDialog.value = true }
function handleThirdEdit(r) { thirdEdit.value = true; thirdCurId.value = r.id; thirdForm.value = { ...r }; thirdDialog.value = true }
async function handleThirdSubmit() { thirdEdit.value ? await updateThirdPartyWarehouse(thirdCurId.value, thirdForm.value) : await createThirdPartyWarehouse(thirdForm.value); ElMessage.success(thirdEdit.value ? '更新成功' : '创建成功'); thirdDialog.value = false; loadThird() }
async function handleThirdDelete(r) { await ElMessageBox.confirm('确定删除?', '确认', { type: 'warning' }); /* no delete API for third-party yet, could add */ ElMessage.warning('暂未提供删除接口') }

onMounted(() => { loadWms(); loadThird() })
</script>
