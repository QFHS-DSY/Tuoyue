<template>
  <el-dialog
    v-model="visible"
    title="AI智能上货确认"
    width="720px"
    :close-on-click-modal="false"
    @closed="handleClosed"
  >
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <p>AI正在校验商品合规性...</p>
    </div>

    <div v-else class="dialog-content">
      <!-- 合规校验结果 -->
      <div v-if="complianceResult" class="compliance-section">
        <el-alert
          v-if="complianceResult.hasError"
          type="error"
          :title="`发现 ${errorCount} 个错误项`"
          :description="complianceResult.summary"
          :closable="false"
          show-icon
        />
        <el-alert
          v-else-if="complianceResult.hasWarning"
          type="warning"
          :title="`发现 ${warningCount} 个警告项`"
          :description="complianceResult.summary"
          :closable="false"
          show-icon
        />
        <el-alert
          v-else
          type="success"
          title="合规检查通过"
          description="该商品已通过所有合规校验，可以正常上货"
          :closable="false"
          show-icon
        />

        <!-- 风险明细（可折叠） -->
        <div v-if="complianceResult.risks && complianceResult.risks.length > 0" class="risk-list">
          <div
            v-for="(risk, idx) in complianceResult.risks"
            :key="idx"
            :class="['risk-item', `risk-${risk.level}`]"
          >
            <el-icon>
              <Warning v-if="risk.level === 'error'" />
              <InfoFilled v-else />
            </el-icon>
            <span class="risk-msg">{{ risk.msg }}</span>
            <el-button
              v-if="risk.fixable"
              text
              size="small"
              type="primary"
              @click="applyRiskFix(risk)"
            >
              AI修复
            </el-button>
          </div>
        </div>
      </div>

      <!-- 商品信息预览 -->
      <div class="goods-preview">
        <div class="preview-header">
          <el-image
            v-if="editableGoods.main_image"
            :src="editableGoods.main_image"
            fit="cover"
            class="preview-img"
          />
          <div class="preview-info">
            <div class="preview-title">{{ editableGoods.title }}</div>
            <div class="preview-meta">
              <span>货源价：¥{{ editableGoods.cost_price }}</span>
              <span>库存：{{ editableGoods.stock }}件</span>
            </div>
          </div>
        </div>

        <!-- AI优化标记 -->
        <div v-if="aiOptimizedFields.length > 0" class="ai-badge">
          <el-icon><MagicStick /></el-icon>
          AI已优化：{{ aiOptimizedFields.join('、') }}
        </div>

        <!-- 编辑表单 -->
        <el-form label-width="90px" size="default" class="listing-form">
          <!-- 外部未传平台时显示选择器，已传则展示已选平台摘要 -->
          <el-form-item v-if="showPlatformSelect" label="目标平台">
            <PlatformSelect v-model="selectedPlatforms" />
          </el-form-item>
          <el-form-item v-else label="目标平台">
            <div class="platforms-summary">
              <el-tag
                v-for="pid in selectedPlatforms"
                :key="pid"
                size="small"
                type="success"
                effect="plain"
              >
                {{ pid }}
              </el-tag>
              <span class="platforms-hint">（来自一站式上货已选平台）</span>
            </div>
          </el-form-item>

          <el-form-item label="上架价格">
            <el-input-number
              v-model="editableGoods.price"
              :precision="2"
              :min="0.01"
              :step="0.1"
              controls-position="right"
            />
            <span class="form-hint">
              利润：¥{{ profit.toFixed(2) }}
              <span :class="profitClass">({{ profitPercent }}%)</span>
            </span>
          </el-form-item>

          <el-form-item label="上架数量">
            <el-input-number
              v-model="listingQuantity"
              :min="1"
              :max="editableGoods.stock"
              controls-position="right"
            />
            <span class="form-hint">最大可上架 {{ editableGoods.stock }} 件</span>
          </el-form-item>

          <el-form-item label="商品标题">
            <el-input
              v-model="editableGoods.title"
              placeholder="AI生成的优化标题"
              maxlength="200"
              show-word-limit
            >
              <template #append>
                <el-button @click="optimizeTitle">
                  <el-icon><MagicStick /></el-icon>
                  AI优化
                </el-button>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="商品描述">
            <el-input
              v-model="editableGoods.description"
              type="textarea"
              :rows="3"
              placeholder="AI生成的优化描述"
              maxlength="2000"
              show-word-limit
            >
              <template #append>
                <el-button @click="optimizeDescription">
                  <el-icon><MagicStick /></el-icon>
                </el-button>
              </template>
            </el-input>
          </el-form-item>

          <!-- 卖点（可选） -->
          <el-form-item v-if="editableGoods.features" label="核心卖点">
            <div class="features-list">
              <el-tag
                v-for="(f, idx) in editableGoods.features"
                :key="idx"
                size="small"
                class="feature-tag"
              >
                {{ f }}
              </el-tag>
              <el-button text size="small" @click="regenerateFeatures">
                <el-icon><RefreshRight /></el-icon>
                重新生成
              </el-button>
            </div>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- 底部操作 -->
    <template #footer>
      <div class="dialog-footer">
        <span class="footer-info">
          将上架至 {{ selectedPlatforms.length }} 个平台店铺
        </span>
        <div class="footer-actions">
          <el-button @click="visible = false">取消</el-button>
          <el-button
            :disabled="complianceResult?.hasError || selectedPlatforms.length === 0"
            :loading="submitting"
            type="primary"
            @click="confirmListing"
          >
            确认上货
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { Warning, InfoFilled, MagicStick, RefreshRight, Loading } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PlatformSelect from './PlatformSelect.vue'
import { useCompliance } from '@/composables/useCompliance'
import * as aiApi from '@/api/ai'

// ── Props & Emits ──────────────────────────────────────────
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  goods: {
    type: Object,
    default: null,
  },
  targetTab: {
    type: Object,
    default: null,
  },
  // 外部已选平台数组（来自一站式上货的 selectedTargets）
  // 传入后不再显示 PlatformSelect，直接使用这些平台
  targetPlatforms: {
    type: Array,
    default: null,
  },
})

const emit = defineEmits(['update:modelValue', 'success', 'failed'])

// ── Composable ──────────────────────────────────────────────
const { preCheck } = useCompliance()

// ── State ──────────────────────────────────────────────────
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const loading = ref(false)
const submitting = ref(false)
const complianceResult = ref(null)
const aiOptimizedFields = ref([])
const selectedPlatforms = ref([])
const listingQuantity = ref(1)

// 可编辑的商品数据（深拷贝）
const editableGoods = ref({})

// ── Computed ───────────────────────────────────────────────
const errorCount = computed(() =>
  complianceResult.value?.risks?.filter(r => r.level === 'error').length || 0
)

const warningCount = computed(() =>
  complianceResult.value?.risks?.filter(r => r.level === 'warning').length || 0
)

const profit = computed(() => {
  if (!editableGoods.value.price || !editableGoods.value.cost_price) return 0
  return editableGoods.value.price - editableGoods.value.cost_price
})

const profitPercent = computed(() => {
  if (!editableGoods.value.cost_price) return '0'
  return ((profit.value / editableGoods.value.cost_price) * 100).toFixed(1)
})

const profitClass = computed(() => {
  if (profit.value <= 0) return 'profit-loss'
  if (profit.value < 10) return 'profit-low'
  return 'profit-good'
})

// 是否显示平台选择器：外部未传 targetPlatforms 时才显示
const showPlatformSelect = computed(() => {
  return !props.targetPlatforms || props.targetPlatforms.length === 0
})

// ── 监听 goods 变化 ─────────────────────────────────────────
watch(() => props.goods, async (newGoods) => {
  if (!newGoods) return

  // 深拷贝商品数据
  editableGoods.value = JSON.parse(JSON.stringify(newGoods))
  listingQuantity.value = Math.min(newGoods.stock || 1, 10)

  // 默认选中逻辑：优先用外部传入的平台，其次当前标签页，最后商品已有平台
  if (props.targetPlatforms && props.targetPlatforms.length > 0) {
    selectedPlatforms.value = [...props.targetPlatforms]
  } else if (props.targetTab?.platformKey) {
    selectedPlatforms.value = [props.targetTab.platformKey]
  } else {
    selectedPlatforms.value = newGoods.platforms || []
  }

  // 自动触发合规预检
  await runComplianceCheck()
}, { immediate: true })

// ── 合规检查 ───────────────────────────────────────────────
async function runComplianceCheck() {
  loading.value = true
  try {
    const platforms = selectedPlatforms.value.length > 0
      ? selectedPlatforms.value
      : (props.targetTab?.platformKey ? [props.targetTab.platformKey] : [])

    complianceResult.value = await preCheck(editableGoods.value, platforms)
  } catch (err) {
    console.error('[ListingConfirm] 合规检查失败:', err)
    complianceResult.value = null
  } finally {
    loading.value = false
  }
}

// ── AI优化 ────────────────────────────────────────────────
// AI API 期望字段：name/category/material/style → editableGoods 是 title/类别/材质/风格
function toAiGoods(goods) {
  if (!goods) return {}
  return {
    name: goods.title || goods.name || '',
    category: goods.category || '',
    material: goods.material || goods.材质 || '',
    style: goods.style || goods.风格 || '',
    features: Array.isArray(goods.features)
      ? goods.features.join('；')
      : (goods.features || goods.卖点 || ''),
    specs: goods.specs || goods.规格 || '',
    targetMarket: goods.targetMarket || goods.目标市场 || '跨境电商通用',
  }
}

async function optimizeTitle() {
  if (!editableGoods.value?.title) {
    ElMessage.warning('请先填写商品名称')
    return
  }
  try {
    const result = await aiApi.generateTitle(toAiGoods(editableGoods.value))
    if (result) {
      editableGoods.value.title = result
      aiOptimizedFields.value.push('标题')
    }
  } catch (err) {
    ElMessage.error('标题优化失败：' + err.message)
  }
}

async function optimizeDescription() {
  if (!editableGoods.value?.title) {
    ElMessage.warning('请先填写商品名称')
    return
  }
  try {
    const result = await aiApi.generateDescription(toAiGoods(editableGoods.value))
    if (result) {
      // description 可能是对象 { description, description_cn } 或直接是字符串
      editableGoods.value.description = typeof result === 'string'
        ? result
        : (result.description || result.description_cn || '')
      aiOptimizedFields.value.push('描述')
    }
  } catch (err) {
    ElMessage.error('描述优化失败：' + err.message)
  }
}

async function regenerateFeatures() {
  if (!editableGoods.value?.title) {
    ElMessage.warning('请先填写商品名称')
    return
  }
  try {
    const result = await aiApi.generateFeatures(toAiGoods(editableGoods.value))
    if (result) {
      // API 可能返回数组或 { features: [...] }
      editableGoods.value.features = Array.isArray(result)
        ? result
        : (result.features || [])
      aiOptimizedFields.value.push('卖点')
    }
  } catch (err) {
    ElMessage.error('卖点生成失败：' + err.message)
  }
}

// ── 修复风险 ──────────────────────────────────────────────
function applyRiskFix(risk) {
  ElMessage.warning(`请手动修复「${risk.field}」后重新校验`)
}

// ── 确认上货 ──────────────────────────────────────────────
async function confirmListing() {
  if (!selectedPlatforms.value.length) {
    ElMessage.warning('请至少选择一个目标平台')
    return
  }

  if (complianceResult.value?.hasError) {
    ElMessage.error('存在合规错误项，请先修复后再上货')
    return
  }

  submitting.value = true
  try {
    // 调用后端批量上货接口
    const { default: request } = await import('@/utils/request')
    await request.post('/api/v1/goods/listing/batch/', { goods_ids: [editableGoods.value.id], platforms: selectedPlatforms.value })

    ElMessageBox.confirm(
      `商品「${editableGoods.value.title}」已提交上货至 ${selectedPlatforms.value.length} 个平台店铺，请等待平台审核。`,
      '上货成功',
      { type: 'success', confirmButtonText: '知道了' }
    )

    emit('success', {
      goods: editableGoods.value,
      platforms: selectedPlatforms.value,
      quantity: listingQuantity.value,
    })

    visible.value = false
  } catch (err) {
    emit('failed', err)
    ElMessage.error('上货失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

// ── 清理 ──────────────────────────────────────────────────
function handleClosed() {
  complianceResult.value = null
  aiOptimizedFields.value = []
  submitting.value = false
}
</script>

<style scoped>
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 16px;
  color: var(--el-text-color-secondary);
}

.dialog-content {
  max-height: 65vh;
  overflow-y: auto;
}

/* 合规区域 */
.compliance-section {
  margin-bottom: 20px;
}

.risk-list {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.risk-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
}

.risk-error {
  background: #fef0f0;
  color: #c45656;
}

.risk-warning {
  background: #fdf6ec;
  color: #b07d2a;
}

.risk-msg {
  flex: 1;
}

/* 商品预览 */
.goods-preview {
  background: var(--el-fill-color-light);
  border-radius: 8px;
  padding: 16px;
}

.preview-header {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.preview-img {
  width: 64px;
  height: 64px;
  border-radius: 6px;
  flex-shrink: 0;
}

.preview-info {
  flex: 1;
  min-width: 0;
}

.preview-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.preview-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

/* AI标记 */
.ai-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  padding: 2px 8px;
  border-radius: 4px;
  margin-bottom: 12px;
}

/* 表单 */
.listing-form {
  margin-top: 12px;
}

.form-hint {
  margin-left: 10px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.profit-good { color: #67c23a; font-weight: 600; }
.profit-low { color: #e6a23c; font-weight: 600; }
.profit-loss { color: #f56c6c; font-weight: 600; }

.features-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.feature-tag {
  margin: 0;
}

/* 底部操作 */
/* 已选平台摘要 */
.platforms-summary {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
}
.platforms-hint {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.footer-info {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.footer-actions {
  display: flex;
  gap: 10px;
}
</style>
