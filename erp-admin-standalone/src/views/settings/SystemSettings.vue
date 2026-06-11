<template>
  <div class="page-container">
    <div class="page-header"><h2>系统设置</h2></div>
    <div class="page-body">
      <el-tabs v-model="activeTab">
        <!-- 全局配置 -->
        <el-tab-pane label="全局配置" name="config">
          <div style="margin-bottom:12px"><el-button type="primary" @click="handleConfigAdd">添加配置</el-button></div>
          <el-table :data="configList" border>
            <el-table-column prop="config_key" label="配置键" width="200" />
            <el-table-column prop="config_group" label="分组" width="120" />
            <el-table-column prop="description" label="描述" />
            <el-table-column label="加密" width="80"><template #default="{ row }"><el-tag :type="r.is_encrypted?'warning':'info'">{{ row.is_encrypted ? '是' : '否' }}</el-tag></template></el-table-column>
            <el-table-column label="操作" width="160"><template #default="{row}"><el-button link type="primary" size="small" @click="handleConfigEdit(row)">编辑</el-button><el-button link type="danger" size="small" @click="handleConfigDelete(row)">删除</el-button></template></el-table-column>
          </el-table>
        </el-tab-pane>
        <!-- 标签管理 -->
        <el-tab-pane label="全局标签" name="tags">
          <div style="margin-bottom:12px"><el-button type="primary" @click="handleTagAdd">添加标签</el-button></div>
          <el-table :data="tagList" border>
            <el-table-column prop="name" label="标签名称" width="150" />
            <el-table-column prop="code" label="编码" width="120" />
            <el-table-column prop="tag_type" label="类型" width="120" />
            <el-table-column label="颜色" width="80"><template #default="{row}"><el-tag :color="row.color" style="color:#fff">{{ row.color }}</el-tag></template></el-table-column>
            <el-table-column label="自动" width="80"><template #default="{ row }"><el-tag :type="r.is_auto?'success':'info'">{{ row.is_auto?'是':'否' }}</el-tag></template></el-table-column>
            <el-table-column label="状态" width="80"><template #default="{ row }"><el-tag :type="row.status?'success':'danger'">{{row.status?'启用':'禁用'}}</el-tag></template></el-table-column>
            <el-table-column label="操作" width="160"><template #default="{row}"><el-button link type="primary" size="small" @click="handleTagEdit(row)">编辑</el-button><el-button link type="danger" size="small" @click="handleTagDelete(row)">删除</el-button></template></el-table-column>
          </el-table>
        </el-tab-pane>
        <!-- SSO配置 -->
        <el-tab-pane label="SSO配置" name="sso">
          <div style="margin-bottom:12px"><el-button type="primary" @click="handleSSOAdd">添加SSO</el-button></div>
          <el-table :data="ssoList" border>
            <el-table-column prop="sso_name" label="名称" width="160" />
            <el-table-column prop="sso_provider" label="提供商" width="120" />
            <el-table-column prop="issuer" label="签发者" />
            <el-table-column prop="signing_algorithm" label="算法" width="100" />
            <el-table-column label="状态" width="80"><template #default="{ row }"><el-tag :type="row.status?'success':'danger'">{{row.status?'启用':'禁用'}}</el-tag></template></el-table-column>
            <el-table-column label="操作" width="160"><template #default="{row}"><el-button link type="primary" size="small" @click="handleSSOEdit(row)">编辑</el-button><el-button link type="danger" size="small" @click="handleSSODelete(row)">删除</el-button></template></el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </div>
    <!-- Config Dialog -->
    <el-dialog v-model="configDialog" :title="configEdit?'编辑配置':'添加配置'" width="480px">
      <el-form ref="configFormRef" :model="configForm" label-width="90px">
        <el-form-item label="配置键"><el-input v-model="configForm.config_key" /></el-form-item>
        <el-form-item label="分组"><el-select v-model="configForm.config_group"><el-option label="通用" value="GENERAL" /><el-option label="安全" value="SECURITY" /><el-option label="通知" value="NOTIFICATION" /><el-option label="仓库" value="WAREHOUSE" /></el-select></el-form-item>
        <el-form-item label="描述"><el-input v-model="configForm.description" /></el-form-item>
        <el-form-item label="配置值"><el-input v-model="configForm.config_value_text" type="textarea" :rows="3" /></el-form-item>
      </el-form><template #footer><el-button @click="configDialog=false">取消</el-button><el-button type="primary" @click="handleConfigSubmit">确定</el-button></template>
    </el-dialog>
    <!-- Tag Dialog -->
    <el-dialog v-model="tagDialog" :title="tagEdit?'编辑标签':'添加标签'" width="480px">
      <el-form :model="tagForm" label-width="90px">
        <el-form-item label="标签名称"><el-input v-model="tagForm.name" /></el-form-item>
        <el-form-item label="编码"><el-input v-model="tagForm.code" /></el-form-item>
        <el-form-item label="类型"><el-select v-model="tagForm.tag_type"><el-option label="SKU" value="SKU" /><el-option label="订单" value="ORDER" /><el-option label="Listing" value="LISTING" /><el-option label="供应商" value="SUPPLIER" /><el-option label="仓库" value="WAREHOUSE" /></el-select></el-form-item>
        <el-form-item label="颜色"><el-color-picker v-model="tagForm.color" /></el-form-item>
        <el-form-item label="状态"><el-switch v-model="tagForm.status" /></el-form-item>
      </el-form><template #footer><el-button @click="tagDialog=false">取消</el-button><el-button type="primary" @click="handleTagSubmit">确定</el-button></template>
    </el-dialog>
    <!-- SSO Dialog -->
    <el-dialog v-model="ssoDialog" :title="ssoEdit?'编辑SSO':'添加SSO'" width="520px">
      <el-form :model="ssoForm" label-width="110px">
        <el-form-item label="名称"><el-input v-model="ssoForm.sso_name" /></el-form-item>
        <el-form-item label="提供商"><el-select v-model="ssoForm.sso_provider"><el-option label="JWT" value="JWT" /><el-option label="LDAP" value="LDAP" /><el-option label="OAuth2" value="OAUTH2" /><el-option label="SAML" value="SAML" /></el-select></el-form-item>
        <el-form-item label="签发者"><el-input v-model="ssoForm.issuer" /></el-form-item>
        <el-form-item label="算法"><el-select v-model="ssoForm.signing_algorithm"><el-option label="HS256" value="HS256" /><el-option label="RS256" value="RS256" /></el-select></el-form-item>
        <el-form-item label="Token有效期"><el-input-number v-model="ssoForm.token_lifetime_hours" :min="1" :max="720" /> 小时</el-form-item>
        <el-form-item label="状态"><el-switch v-model="ssoForm.status" /></el-form-item>
      </el-form><template #footer><el-button @click="ssoDialog=false">取消</el-button><el-button type="primary" @click="handleSSOSubmit">确定</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSystemConfigs, createSystemConfig, updateSystemConfig, deleteSystemConfig, getTags, createTag, updateTag, deleteTag, getSSOConfigs, createSSOConfig, updateSSOConfig } from '@/api/sysSettings'

const activeTab = ref('config')
// Config
const configList = ref([]); const configDialog = ref(false); const configEdit = ref(false); const configCurId = ref(null)
const configFormRef = ref(null)
const configForm = ref({ config_key: '', config_group: 'GENERAL', description: '', config_value_text: '{}' })
async function loadConfig() { const res = await getSystemConfigs(); configList.value = res.results || res }
function handleConfigAdd() { configEdit.value = false; configForm.value = { config_key: '', config_group: 'GENERAL', description: '', config_value_text: '{}' }; configDialog.value = true }
function handleConfigEdit(r) { configEdit.value = true; configCurId.value = r.id; configForm.value = { config_key: r.config_key, config_group: r.config_group, description: r.description, config_value_text: JSON.stringify(r.config_value) }; configDialog.value = true }
async function handleConfigSubmit() {
  try { JSON.parse(configForm.value.config_value_text) } catch { return ElMessage.error('配置值格式错误') }
  const p = { config_key: configForm.value.config_key, config_group: configForm.value.config_group, description: configForm.value.description, config_value: JSON.parse(configForm.value.config_value_text) }
  configEdit.value ? await updateSystemConfig(configCurId.value, p) : await createSystemConfig(p)
  ElMessage.success(configEdit.value?'更新成功':'创建成功'); configDialog.value = false; loadConfig()
}
async function handleConfigDelete(r) { await deleteSystemConfig(r.id); ElMessage.success('已删除'); loadConfig() }
// Tag
const tagList = ref([]); const tagDialog = ref(false); const tagEdit = ref(false); const tagCurId = ref(null)
const tagForm = ref({ name: '', code: '', tag_type: 'SKU', color: '#409EFF', status: true })
async function loadTag() { const res = await getTags(); tagList.value = res.results || res }
function handleTagAdd() { tagEdit.value = false; tagForm.value = { name: '', code: '', tag_type: 'SKU', color: '#409EFF', status: true }; tagDialog.value = true }
function handleTagEdit(r) { tagEdit.value = true; tagCurId.value = r.id; tagForm.value = { name: r.name, code: r.code, tag_type: r.tag_type, color: r.color, status: row.status }; tagDialog.value = true }
async function handleTagSubmit() { tagEdit.value ? await updateTag(tagCurId.value, tagForm.value) : await createTag(tagForm.value); ElMessage.success(tagEdit.value?'更新成功':'创建成功'); tagDialog.value = false; loadTag() }
async function handleTagDelete(r) { await deleteTag(r.id); ElMessage.success('已删除'); loadTag() }
// SSO
const ssoList = ref([]); const ssoDialog = ref(false); const ssoEdit = ref(false); const ssoCurId = ref(null)
const ssoForm = ref({ sso_name: '', sso_provider: 'JWT', issuer: '', signing_algorithm: 'HS256', token_lifetime_hours: 24, status: false })
async function loadSSO() { const res = await getSSOConfigs(); ssoList.value = res.results || res }
function handleSSOAdd() { ssoEdit.value = false; ssoForm.value = { sso_name: '', sso_provider: 'JWT', issuer: '', signing_algorithm: 'HS256', token_lifetime_hours: 24, status: false }; ssoDialog.value = true }
function handleSSOEdit(r) { ssoEdit.value = true; ssoCurId.value = r.id; ssoForm.value = { sso_name: r.sso_name, sso_provider: r.sso_provider, issuer: r.issuer, signing_algorithm: r.signing_algorithm, token_lifetime_hours: r.token_lifetime_hours, status: row.status }; ssoDialog.value = true }
async function handleSSOSubmit() { ssoEdit.value ? await updateSSOConfig(ssoCurId.value, ssoForm.value) : await createSSOConfig(ssoForm.value); ElMessage.success(ssoEdit.value?'更新成功':'创建成功'); ssoDialog.value = false; loadSSO() }
async function handleSSODelete(r) { ElMessage.warning('暂未提供删除接口') }

onMounted(() => { loadConfig(); loadTag(); loadSSO() })
</script>
