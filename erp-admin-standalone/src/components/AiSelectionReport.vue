/**
 * AI选品决策报告弹窗
 * 集采模式步骤3必经拦截节点
 * 功能：
 *   - 左侧：已采集商品列表，支持勾选
 *   - 右侧：AI「小辽」选品评估报告，含等级/利润/风险
 *   - 底部：「暂不上货」/「下一步」决策按钮
 *   - 支持按利润额/利润率一键筛选
 *
 * Props:
 *   modelValue: boolean - 弹窗显示状态
 *   goodsList: Array - 待评估商品列表
 *   config: Object - 集采配置（定价规则等）
 *
 * Events:
 *   update:modelValue - 关闭弹窗
 *   confirm - 用户确认选中的商品ID列表
 *   toDraft - 用户选择暂不上货
 */
<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title=""
    width="900px"
    :close-on-click-modal="false"
    class="ai-selection-report-dialog"
    destroy-on-close
  >
    <!-- 自定义Header -->
    <template #header>
      <div class="dialog-header">
        <div class="dialog-header-left">
          <div class="xiao-liao-avatar">
            <span class="avatar-face">🤖</span>
            <div class="avatar-bubble">小辽正在分析...</div>
          </div>
          <div class="dialog-title-group">
            <h3 class="dialog-title">AI 选品决策报告</h3>
            <p class="dialog-subtitle">已完成 {{ goodsList.length }} 款商品评估，点击右侧了解详情</p>
          </div>
        </div>
        <div class="dialog-header-right">
          <el-tag type="success" size="small">
            <el-icon><Check /></el-icon>
            建议上架 {{ recommendCount }} 款
          </el-tag>
        </div>
      </div>
    </template>

    <div class="report-layout">
      <!-- 左侧：商品列表 -->
      <div class="report-left">
        <!-- 筛选工具栏 -->
        <div class="filter-toolbar">
          <div class="filter-tabs">
            <el-radio-group v-model="filterMode" size="small">
              <el-radio value="all">全部 ({{ goodsList.length }})</el-radio>
              <el-radio value="recommend">推荐 ({{ goodsByGrade.recommend?.length || 0 }})</el-radio>
              <el-radio value="okay">可上架 ({{ goodsByGrade.okay?.length || 0 }})</el-radio>
              <el-radio value="not_recommended" type="danger">不建议 ({{ goodsByGrade.not_recommended?.length || 0 }})</el-radio>
            </el-radio-group>
          </div>
          <div class="filter-quick">
            <span class="filter-label">快速筛选：</span>
            <el-input-number
              v-if="filterMode !== 'profit_rate'"
              v-model="minProfitInput"
              :min="0"
              :max="10000"
              :precision="2"
              size="small"
              controls-position="right"
              placeholder="利润≥"
              @change="onQuickFilter('profit_amount')"
            />
            <el-input-number
              v-else
              v-model="minProfitRateInput"
              :min="0"
              :max="100"
              :precision="1"
              size="small"
              controls-position="right"
              placeholder="利润率≥"
              @change="onQuickFilter('profit_rate')"
            />
            <el-button size="small" @click="filterMode = 'all'">重置</el-button>
          </div>
          <div class="selection-actions">
            <el-button size="small" @click="onSelectAll">全选</el-button>
            <el-button size="small" @click="onDeselectAll">取消</el-button>
          </div>
        </div>

        <!-- 商品列表 -->
        <div class="goods-list">
          <div
            v-for="goods in filteredGoods"
            :key="goods.id"
            :class="['goods-item', {
              'is-selected': selectedIds.includes(goods.id),
              'is-not-recommended': getGrade(goods.id) === 'not_recommended',
              'is-recommend': getGrade(goods.id) === 'recommend',
            }]"
            @click="onToggleGoods(goods.id)"
          >
            <!-- 选择框 -->
            <el-checkbox
              :model-value="selectedIds.includes(goods.id)"
              :disabled="getGrade(goods.id) === 'not_recommended'"
              @click.stop
              @change="onToggleGoods(goods.id)"
            />

            <!-- 商品信息 -->
            <div class="goods-info">
              <div class="goods-name">{{ goods.title || goods.name }}</div>
              <div class="goods-meta">
                <span class="goods-cost">成本 ¥{{ goods.cost }}</span>
                <span v-if="getProfit(goods.id)">→ 售价 ¥{{ getProfit(goods.id).salePrice?.toFixed(2) }}</span>
              </div>
            </div>

            <!-- 等级标签 -->
            <div class="goods-grade">
              <el-tag v-if="getGrade(goods.id) === 'recommend'" type="success" size="small" effect="dark">
                优先推荐
              </el-tag>
              <el-tag v-else-if="getGrade(goods.id) === 'not_recommended'" type="danger" size="small" effect="plain">
                不建议
              </el-tag>
              <el-tag v-else type="info" size="small">可上架</el-tag>
            </div>

            <!-- 利润信息 -->
            <div v-if="getProfit(goods.id)" class="goods-profit">
              <span class="profit-amount" :class="{ 'low': getProfit(goods.id).profit < 20 }">
                ¥{{ getProfit(goods.id).profit?.toFixed(2) }}
              </span>
              <span class="profit-rate">
                {{ getProfit(goods.id).profitRate?.toFixed(1) }}%
              </span>
            </div>
          </div>

          <div v-if="filteredGoods.length === 0" class="empty-list">
            <el-icon><Goods /></el-icon>
            <span>无匹配商品</span>
          </div>
        </div>
      </div>

      <!-- 右侧：AI 报告 -->
      <div class="report-right">
        <!-- 小辽评估摘要 -->
        <div class="xiao-liao-summary">
          <div class="xiao-liao-header">
            <span class="xiao-liao-face">🤖</span>
            <span class="xiao-liao-name">小辽评估</span>
          </div>

          <div class="summary-content">
            <p class="summary-intro">{{ summaryText }}</p>

            <!-- 汇总数据 -->
            <div class="summary-stats">
              <div class="stat-item">
                <span class="stat-value success">{{ goodsByGrade.recommend?.length || 0 }}</span>
                <span class="stat-label">优先推荐</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ goodsByGrade.okay?.length || 0 }}</span>
                <span class="stat-label">可上架</span>
              </div>
              <div class="stat-item">
                <span class="stat-value danger">{{ goodsByGrade.not_recommended?.length || 0 }}</span>
                <span class="stat-label">不建议</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 当前选中商品的详细报告 -->
        <div v-if="currentReportGoods" class="goods-detail-report">
          <div class="detail-header">
            <span class="detail-title">📊 {{ currentReportGoods.title || currentReportGoods.name }}</span>
          </div>

          <div class="detail-body">
            <!-- 利润测算 -->
            <div class="detail-section">
              <div class="detail-section-title">💰 利润测算</div>
              <div class="profit-table">
                <div class="profit-row">
                  <span class="profit-key">成本价</span>
                  <span class="profit-val">¥{{ currentReportGoods.cost }}</span>
                </div>
                <div class="profit-row">
                  <span class="profit-key">建议售价</span>
                  <span class="profit-val highlight">¥{{ getProfit(currentReportGoods.id)?.salePrice?.toFixed(2) }}</span>
                </div>
                <div class="profit-row">
                  <span class="profit-key">预估利润</span>
                  <span class="profit-val success">¥{{ getProfit(currentReportGoods.id)?.profit?.toFixed(2) }}</span>
                </div>
                <div class="profit-row">
                  <span class="profit-key">毛利率</span>
                  <span class="profit-val success">{{ getProfit(currentReportGoods.id)?.profitRate?.toFixed(1) }}%</span>
                </div>
              </div>
            </div>

            <!-- 评估结论 -->
            <div class="detail-section">
              <div class="detail-section-title">📋 评估结论</div>
              <div class="grade-badge" :class="'grade-' + getGrade(currentReportGoods.id)">
                <span v-if="getGrade(currentReportGoods.id) === 'recommend'">✅ 优先推荐上架</span>
                <span v-else-if="getGrade(currentReportGoods.id) === 'not_recommended'">❌ 不建议上架</span>
                <span v-else>✅ 可上架</span>
              </div>
              <p class="grade-reason">{{ getReason(currentReportGoods.id) }}</p>
            </div>

            <!-- 平台适配 -->
            <div v-if="getPlatformFit(currentReportGoods.id)" class="detail-section">
              <div class="detail-section-title">🏪 平台适配性</div>
              <div class="platform-fit-tags">
                <el-tag
                  v-for="(fit, platform) in getPlatformFit(currentReportGoods.id)"
                  :key="platform"
                  :type="fit === 'high' ? 'success' : fit === 'medium' ? 'warning' : 'info'"
                  size="small"
                >
                  {{ getPlatformName(platform) }}: {{ fit === 'high' ? '高' : fit === 'medium' ? '中' : '低' }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="no-selection-hint">
          <el-icon><Pointer /></el-icon>
          <span>点击左侧商品查看详细评估</span>
        </div>
      </div>
    </div>

    <!-- 底部操作栏 -->
    <template #footer>
      <div class="dialog-footer">
        <div class="footer-left">
          <span class="selected-count">已选 {{ selectedIds.length }} 款商品</span>
        </div>
        <div class="footer-right">
          <el-button @click="$emit('toDraft')">
            <el-icon><FolderOpened /></el-icon>
            暂不上货，存入草稿箱
          </el-button>
          <el-button type="primary" :disabled="selectedIds.length === 0" @click="onConfirm">
            <el-icon><ArrowRight /></el-icon>
            下一步，筛选商品
            <el-badge v-if="selectedIds.length > 0" :value="selectedIds.length" type="warning" />
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Check, Goods, Pointer, FolderOpened, ArrowRight } from '@element-plus/icons-vue'
import { useOneStopStore } from '@/stores/useOneStop'

const props = defineProps({
  modelValue: Boolean,
  goodsList: { type: Array, default: () => [] },
  config: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['update:modelValue', 'confirm', 'toDraft'])

const oneStop = useOneStopStore()

// ── 状态 ────────────────────────────────────────────────────
const filterMode = ref('all')
const minProfitInput = ref(0)
const minProfitRateInput = ref(0)
const selectedIds = ref([])
const currentReportGoods = ref(null)

// ── 评估数据 ────────────────────────────────────────────────
const evaluations = computed(() => {
  return Object.fromEntries(
    props.goodsList.map(g => [g.id, oneStop.aiEvaluations[g.id] || {}])
  )
})

const goodsByGrade = computed(() => {
  const map = { recommend: [], okay: [], not_recommended: [] }
  props.goodsList.forEach(g => {
    const ev = evaluations.value[g.id] || {}
    const grade = ev.grade || 'okay'
    if (grade === 'recommend') map.recommend.push(g)
    else if (grade === 'not_recommended') map.not_recommended.push(g)
    else map.okay.push(g)
  })
  return map
})

const filteredGoods = computed(() => {
  if (filterMode.value === 'recommend') return goodsByGrade.value.recommend
  if (filterMode.value === 'okay') return goodsByGrade.value.okay
  if (filterMode.value === 'not_recommended') return goodsByGrade.value.not_recommended
  return props.goodsList
})

const recommendCount = computed(() => goodsByGrade.value.recommend?.length || 0)

const summaryText = computed(() => {
  const total = props.goodsList.length
  const rec = recommendCount.value
  if (total === 0) return '暂无待评估商品'
  if (rec >= total * 0.6) return `本次采集的商品整体质量不错，建议重点关注优先推荐款，可优先上架。`
  if (rec >= total * 0.3) return `有 ${rec} 款商品符合利润要求，建议优先上架，其余可存入草稿箱观察。`
  return `建议提高定价倍率或降低筛选门槛，目前符合条件的商品较少。`
})

// ── 商品评估辅助 ─────────────────────────────────────────────
function getGrade(goodsId) {
  return evaluations.value[goodsId]?.grade || 'okay'
}

function getProfit(goodsId) {
  const ev = evaluations.value[goodsId]
  if (ev?.profit) return ev.profit
  const goods = props.goodsList.find(g => g.id === goodsId)
  if (goods) return oneStop.calcProfit(goods)
  return null
}

function getReason(goodsId) {
  return evaluations.value[goodsId]?.reason || '符合基本要求'
}

function getPlatformFit(goodsId) {
  return evaluations.value[goodsId]?.platformFit || null
}

function getPlatformName(key) {
  const names = {
    tiktok: 'TikTok',
    shopee: 'Shopee',
    temu: 'Temu',
    shein: 'Shein',
    amazon: 'Amazon',
    ebay: 'eBay',
  }
  return names[key] || key
}

// ── 交互 ────────────────────────────────────────────────────
function onToggleGoods(id) {
  const grade = getGrade(id)
  if (grade === 'not_recommended') return
  const idx = selectedIds.value.indexOf(id)
  if (idx === -1) selectedIds.value.push(id)
  else selectedIds.value.splice(idx, 1)
  currentReportGoods.value = props.goodsList.find(g => g.id === id) || null
}

function onSelectAll() {
  selectedIds.value = filteredGoods.value
    .filter(g => getGrade(g.id) !== 'not_recommended')
    .map(g => g.id)
}

function onDeselectAll() {
  selectedIds.value = []
}

function onQuickFilter(mode) {
  if (mode === 'profit_amount' && minProfitInput.value > 0) {
    filterMode.value = 'all'
    selectedIds.value = props.goodsList
      .filter(g => (getProfit(g.id)?.profit || 0) >= minProfitInput.value)
      .map(g => g.id)
  } else if (mode === 'profit_rate' && minProfitRateInput.value > 0) {
    filterMode.value = 'all'
    selectedIds.value = props.goodsList
      .filter(g => (getProfit(g.id)?.profitRate || 0) >= minProfitRateInput.value)
      .map(g => g.id)
  }
}

function onConfirm() {
  emit('confirm', [...selectedIds.value])
}

// 弹窗打开时，同步选中推荐商品
watch(() => props.modelValue, (val) => {
  if (val) {
    selectedIds.value = (goodsByGrade.value.recommend || []).map(g => g.id)
    if (props.goodsList.length > 0 && !currentReportGoods.value) {
      currentReportGoods.value = props.goodsList[0]
    }
  }
})
</script>

<style scoped>
/* 自定义Header */
.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 4px 0;
}
.dialog-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.xiao-liao-avatar {
  position: relative;
  display: inline-flex;
}
.avatar-face {
  font-size: 28px;
  line-height: 1;
}
.avatar-bubble {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  background: #1d4ed8;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 8px;
  white-space: nowrap;
  animation: bubble-pulse 2s ease-in-out infinite;
}
@keyframes bubble-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
.dialog-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
  color: var(--el-text-color-primary);
}
.dialog-subtitle {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin: 0;
}

/* 布局 */
.report-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  height: 480px;
}

/* 左侧商品列表 */
.report-left {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow: hidden;
}
.filter-toolbar {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex-shrink: 0;
}
.filter-tabs :deep(.el-radio) {
  margin-right: 4px;
}
.filter-quick {
  display: flex;
  align-items: center;
  gap: 6px;
}
.filter-label { font-size: 12px; color: var(--el-text-color-secondary); }
.filter-quick .el-input-number { width: 100px; }
.selection-actions {
  display: flex;
  gap: 4px;
}
.goods-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.goods-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
  background: white;
}
.goods-item:hover { background: #f9fafb; border-color: #d1d5db; }
.goods-item.is-selected { border-color: #22c55e; background: rgba(34,197,94,.04); }
.goods-item.is-not-recommended { opacity: 0.5; cursor: not-allowed; background: #f9f9f9; }
.goods-item.is-recommend { border-color: #22c55e; border-width: 1.5px; }
.goods-info {
  flex: 1;
  min-width: 0;
}
.goods-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.goods-meta {
  font-size: 11px;
  color: var(--el-text-color-secondary);
  margin-top: 2px;
}
.goods-grade { flex-shrink: 0; }
.goods-profit {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  flex-shrink: 0;
}
.profit-amount {
  font-size: 13px;
  font-weight: 700;
  color: #22c55e;
}
.profit-amount.low { color: #f59e0b; }
.profit-rate {
  font-size: 11px;
  color: var(--el-text-color-secondary);
}
.empty-list {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  padding: 40px 0;
}

/* 右侧 AI 报告 */
.report-right {
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
}
.xiao-liao-summary {
  background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
  border-radius: 12px;
  padding: 14px;
  color: white;
  flex-shrink: 0;
}
.xiao-liao-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.xiao-liao-face { font-size: 20px; }
.xiao-liao-name { font-weight: 700; font-size: 14px; }
.summary-content { }
.summary-intro {
  font-size: 13px;
  line-height: 1.6;
  margin: 0 0 10px;
  opacity: 0.95;
}
.summary-stats {
  display: flex;
  gap: 16px;
}
.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.stat-value {
  font-size: 20px;
  font-weight: 800;
  line-height: 1;
}
.stat-value.success { color: #4ade80; }
.stat-value.danger { color: #fca5a5; }
.stat-label {
  font-size: 10px;
  opacity: 0.8;
  text-align: center;
}

/* 商品详情报告 */
.goods-detail-report {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  flex: 1;
}
.detail-header {
  padding: 10px 14px;
  background: white;
  border-bottom: 1px solid #f0f0f0;
}
.detail-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
}
.detail-body { padding: 12px 14px; }
.detail-section { margin-bottom: 14px; }
.detail-section:last-child { margin-bottom: 0; }
.detail-section-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}
.profit-table { display: flex; flex-direction: column; gap: 4px; }
.profit-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 8px;
  background: white;
  border-radius: 6px;
  font-size: 13px;
}
.profit-key { color: var(--el-text-color-secondary); }
.profit-val { font-weight: 600; color: var(--el-text-color-primary); }
.profit-val.highlight { color: #1d4ed8; }
.profit-val.success { color: #22c55e; }
.grade-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 6px;
}
.grade-recommend { background: rgba(34,197,94,.1); color: #15803d; }
.grade-not_recommended { background: rgba(239,68,68,.1); color: #dc2626; }
.grade-okay { background: rgba(107,114,128,.1); color: #4b5563; }
.platform-fit-tags { display: flex; flex-wrap: wrap; gap: 4px; }
.no-selection-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  height: 100%;
}

/* 底部 */
.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}
.footer-left { display: flex; align-items: center; gap: 8px; }
.selected-count {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  font-weight: 500;
}
.footer-right { display: flex; align-items: center; gap: 8px; }
</style>
