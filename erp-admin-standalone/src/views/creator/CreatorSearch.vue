<template>
  <div class="page-container">
    <!-- 页面Header -->
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">达人检索</h1>
        <p class="page-desc">多平台达人聚合 · AI智能匹配 · 建联闭环</p>
      </div>
      <div class="page-header-right">
        <el-button @click="tabActive = 'board'">
          <el-icon><DataLine /></el-icon>
          达人看板
        </el-button>
        <el-button type="primary" @click="showImport = true">
          <el-icon><Plus /></el-icon>
          导入达人
        </el-button>
      </div>
    </div>

    <!-- 筛选区 -->
    <div class="filter-card">
      <el-form :inline="true" :model="filters">
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="达人Handle搜索" clearable @keyup.enter="search" style="width:200px">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item label="地区">
          <el-select v-model="filters.region" placeholder="全部地区" clearable style="width:130px">
            <el-option label="全部" value="" />
            <el-option label="US" value="US" />
            <el-option label="UK" value="UK" />
            <el-option label="SEA" value="SEA" />
            <el-option label="CN" value="CN" />
            <el-option label="JP" value="JP" />
          </el-select>
        </el-form-item>
        <el-form-item label="等级">
          <el-select v-model="filters.tier" placeholder="全部等级" clearable style="width:130px">
            <el-option label="全部" value="" />
            <el-option label="Nano (1k-10k)" value="nano" />
            <el-option label="Micro (10k-100k)" value="micro" />
            <el-option label="Mega (100k+)" value="mega" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">
            <el-icon><Search /></el-icon>搜索
          </el-button>
          <el-button @click="reset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 达人列表 -->
    <div class="list-card" v-loading="loading">
      <el-table :data="tableData" stripe>
        <el-table-column label="达人" min-width="200">
          <template #default="{ row }">
            <div class="creator-cell">
              <div class="creator-avatar">{{ row.handle?.charAt(0) || '@' }}</div>
              <div class="creator-info">
                <div class="creator-name">{{ row.handle }}</div>
                <div class="creator-uid">{{ row.platform_uid }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="地区" width="80" align="center">
          <template #default="{ row }">{{ row.region || '-' }}</template>
        </el-table-column>
        <el-table-column label="等级" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="tierType(row.tier)" size="small" effect="light">{{ tierLabel(row.tier) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Email" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">{{ row.email || '-' }}</template>
        </el-table-column>
        <el-table-column label="时区" width="90" align="center">
          <template #default="{ row }">{{ row.timezone || 'UTC' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleDetail(row)">详情</el-button>
            <el-button type="success" text size="small" @click="handlePitch(row)">AI邀约</el-button>
            <el-button type="warning" text size="small" @click="handleSample(row)">寄样</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && tableData.length === 0" description="暂无达人数据，点击「导入达人」添加" />
    </div>

    <!-- 达人详情抽屉 -->
    <el-drawer v-model="showDetail" title="达人详情" size="560px">
      <div v-if="currentCreator" class="detail-wrap">
        <div class="detail-header-info">
          <div class="creator-avatar large">{{ currentCreator.handle?.charAt(0) || '@' }}</div>
          <div>
            <h3>{{ currentCreator.handle }}</h3>
            <p>{{ currentCreator.platform_uid }}</p>
          </div>
        </div>
        <el-divider />
        <div class="detail-grid">
          <div class="detail-item"><span class="label">地区</span><span class="value">{{ currentCreator.region }}</span></div>
          <div class="detail-item"><span class="label">等级</span><span class="value">{{ tierLabel(currentCreator.tier) }}</span></div>
          <div class="detail-item"><span class="label">Email</span><span class="value">{{ currentCreator.email }}</span></div>
          <div class="detail-item"><span class="label">WhatsApp</span><span class="value">{{ currentCreator.whatsapp }}</span></div>
          <div class="detail-item"><span class="label">时区</span><span class="value">{{ currentCreator.timezone }}</span></div>
        </div>
        <el-divider content-position="left">AI 分析</el-divider>
        <div v-if="aiInsight" class="ai-section">
          <div class="ai-tags">
            <span class="ai-label">内容调性：</span>
            <el-tag v-for="tag in (aiInsight.style_tags || [])" :key="tag" size="small" effect="plain" style="margin:2px">{{ tag }}</el-tag>
          </div>
          <div v-if="aiInsight.sentiment_keywords_json?.length" style="margin-top:8px">
            <span class="ai-label">评论关键词：</span>
            <el-tag v-for="kw in aiInsight.sentiment_keywords_json" :key="kw" size="small" type="info" style="margin:2px">{{ kw }}</el-tag>
          </div>
        </div>
        <div v-else class="ai-section">
          <el-button type="primary" text @click="runAIAnalysis(currentCreator.id)">触发 AI 分析</el-button>
        </div>
      </div>
    </el-drawer>

    <!-- AI邀约弹窗 -->
    <el-dialog v-model="showPitch" title="AI 多语种邀约" width="550px">
      <div v-if="pitchCreator">
        <el-form label-width="100px">
          <el-form-item label="达人">{{ pitchCreator.handle }}</el-form-item>
          <el-form-item label="目标语言">
            <el-select v-model="pitchLanguage" placeholder="选择语言">
              <el-option label="English" value="en" />
              <el-option label="中文" value="zh" />
              <el-option label="日本語" value="ja" />
              <el-option label="한국어" value="ko" />
              <el-option label="Español" value="es" />
            </el-select>
          </el-form-item>
        </el-form>
        <el-divider />
        <div v-if="pitchText" class="pitch-preview">
          <div class="pitch-label">生成的邀约信：</div>
          <el-input :model-value="pitchText" type="textarea" :rows="8" readonly />
        </div>
        <div v-else style="text-align:center;padding:40px">
          <el-button type="primary" :loading="pitchLoading" @click="doGeneratePitch">生成邀约信</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 导入达人弹窗 -->
    <el-dialog v-model="showImport" title="导入达人" width="480px" @close="resetImportForm">
      <el-form :model="importForm" label-width="100px">
        <el-form-item label="平台UID" required>
          <el-input v-model="importForm.platform_uid" placeholder="TikTok/Amazon 等平台唯一ID" />
        </el-form-item>
        <el-form-item label="Handle" required>
          <el-input v-model="importForm.handle" placeholder="@username" />
        </el-form-item>
        <el-form-item label="地区">
          <el-input v-model="importForm.region" placeholder="US/UK/SEA" />
        </el-form-item>
        <el-form-item label="等级">
          <el-select v-model="importForm.tier" placeholder="选择等级">
            <el-option label="Nano" value="nano" />
            <el-option label="Micro" value="micro" />
            <el-option label="Mega" value="mega" />
          </el-select>
        </el-form-item>
        <el-form-item label="Email">
          <el-input v-model="importForm.email" />
        </el-form-item>
        <el-form-item label="WhatsApp">
          <el-input v-model="importForm.whatsapp" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showImport = false">取消</el-button>
        <el-button type="primary" :loading="importLoading" @click="doImport">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Plus, DataLine } from '@element-plus/icons-vue'
import { searchCreators, generatePitch, importCreator, getCreatorAIInsight } from '@/api/creator'

const loading = ref(false)
const tableData = ref([])
const filters = reactive({ keyword: '', region: '', tier: '' })
const tabActive = ref('list')

// 详情
const showDetail = ref(false)
const currentCreator = ref(null)
const aiInsight = ref(null)

// AI邀约
const showPitch = ref(false)
const pitchCreator = ref(null)
const pitchLanguage = ref('en')
const pitchText = ref('')
const pitchLoading = ref(false)

// 导入
const showImport = ref(false)
const importLoading = ref(false)
const importForm = reactive({ platform_uid: '', handle: '', region: '', tier: '', email: '', whatsapp: '' })

function tierType(tier) {
  return tier === 'mega' ? 'danger' : tier === 'micro' ? 'warning' : 'info'
}
function tierLabel(tier) {
  return tier === 'mega' ? 'Mega' : tier === 'micro' ? 'Micro' : tier === 'nano' ? 'Nano' : tier || '-'
}

async function search() {
  loading.value = true
  try {
    const res = await searchCreators({ ...filters })
    tableData.value = res?.data?.items || []
  } catch (e) {
    tableData.value = []
  } finally {
    loading.value = false
  }
}

function reset() {
  filters.keyword = ''; filters.region = ''; filters.tier = ''
  search()
}

async function handleDetail(row) {
  currentCreator.value = row
  showDetail.value = true
  aiInsight.value = null
  try {
    const res = await getCreatorAIInsight(row.id)
    aiInsight.value = res?.data
  } catch (_) {}
}

async function runAIAnalysis(creatorId) {
  try {
    const { triggerContentAnalysis } = await import('@/api/creator')
    const res = await triggerContentAnalysis(creatorId)
    if (res?.code === 201 || res?.code === 200) {
      ElMessage.success('AI 分析任务已启动')
      setTimeout(() => handleDetail(currentCreator.value), 2000)
    }
  } catch (e) {
    ElMessage.error('分析启动失败')
  }
}

function handlePitch(row) {
  pitchCreator.value = row
  pitchText.value = ''
  pitchLanguage.value = 'en'
  showPitch.value = true
}

async function doGeneratePitch() {
  if (!pitchCreator.value) return
  pitchLoading.value = true
  try {
    const res = await generatePitch(pitchCreator.value.id, pitchLanguage.value)
    pitchText.value = res?.data?.pitch || '邀约信生成失败'
  } catch (e) {
    ElMessage.error('生成失败')
  } finally {
    pitchLoading.value = false
  }
}

function handleSample(row) {
  ElMessage.success(`已为 ${row.handle} 创建样品申请`)
}

async function doImport() {
  if (!importForm.platform_uid || !importForm.handle) {
    ElMessage.warning('平台UID和Handle不能为空')
    return
  }
  importLoading.value = true
  try {
    const res = await importCreator({ ...importForm })
    if (res?.code === 201 || res?.code === 200) {
      ElMessage.success('导入成功')
      showImport.value = false
      search()
    }
  } catch (e) {
    ElMessage.error('导入失败')
  } finally {
    importLoading.value = false
  }
}

function resetImportForm() {
  Object.assign(importForm, { platform_uid: '', handle: '', region: '', tier: '', email: '', whatsapp: '' })
}

onMounted(() => search())
</script>

<style scoped>
.filter-card { background: var(--bg-card); border-radius: 12px; padding: 16px 20px; margin-bottom: 16px; box-shadow: var(--shadow-xs); }
.list-card { background: var(--bg-card); border-radius: 12px; padding: 20px; box-shadow: var(--shadow-xs); min-height: 300px; }
.creator-cell { display: flex; align-items: center; gap: 12px; }
.creator-avatar { width: 36px; height: 36px; border-radius: 50%; background: var(--brand); color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 16px; flex-shrink: 0; }
.creator-avatar.large { width: 56px; height: 56px; font-size: 24px; }
.creator-info { display: flex; flex-direction: column; gap: 2px; }
.creator-name { font-weight: 600; color: var(--text-primary); }
.creator-uid { font-size: 12px; color: var(--text-muted); font-family: monospace; }
.detail-wrap { padding: 0 8px; }
.detail-header-info { display: flex; align-items: center; gap: 16px; }
.detail-header-info h3 { margin: 0 0 4px; font-size: 18px; }
.detail-header-info p { margin: 0; font-size: 13px; color: var(--text-muted); font-family: monospace; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.detail-item { display: flex; flex-direction: column; gap: 4px; }
.detail-item .label { font-size: 12px; color: var(--text-muted); }
.detail-item .value { font-size: 14px; color: var(--text-primary); font-weight: 500; }
.ai-section { padding: 8px 0; }
.ai-label { font-size: 12px; color: var(--text-muted); font-weight: 500; }
.pitch-preview { margin-top: 12px; }
.pitch-label { font-size: 13px; color: var(--text-secondary); margin-bottom: 8px; }
</style>
