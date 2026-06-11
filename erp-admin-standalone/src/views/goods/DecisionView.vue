<template>
  <div class="decision-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>选品决策与 ROAS 测算</h2>
      <p class="subtitle">输入商品信息与营销参数，系统自动计算 ROAS 比值并给出决策建议</p>
    </div>

    <div class="decision-layout">
      <!-- 左侧：搜索 + 参数区 -->
      <div class="left-panel">
        <!-- 商品搜索 -->
        <el-card class="search-card">
          <template #header>
            <span class="card-title">选择商品</span>
          </template>
          
          <el-select
            v-model="searchKeyword"
            filterable
            remote
            reserve-keyword
            placeholder="输入 SKU 或商品名称搜索"
            :remote-method="handleSearch"
            :loading="store.loading"
            clearable
            class="product-search"
            @change="handleSelect"
          >
            <el-option
              v-for="item in store.searchResults"
              :key="item.id"
              :label="`${item.sku} - ${item.name}`"
              :value="item.id"
            >
              <div class="product-option">
                <span class="sku">{{ item.sku }}</span>
                <span class="name">{{ item.name }}</span>
                <span class="price">¥{{ item.cost_price }}</span>
              </div>
            </el-option>
          </el-select>
        </el-card>

        <!-- 当前商品信息 -->
        <el-card v-if="store.currentProduct" class="product-info-card">
          <template #header>
            <span class="card-title">商品信息</span>
          </template>
          
          <div class="product-detail">
            <div class="info-row">
              <span class="label">SKU</span>
              <span class="value">{{ store.currentProduct.sku }}</span>
            </div>
            <div class="info-row">
              <span class="label">商品名称</span>
              <span class="value">{{ store.currentProduct.name }}</span>
            </div>
            <div class="info-row">
              <span class="label">采购价</span>
              <span class="value price">¥{{ store.currentProduct.cost_price }}</span>
            </div>
            <div class="info-row">
              <span class="label">运费</span>
              <span class="value price">¥{{ store.currentProduct.freight }}</span>
            </div>
            <div class="info-row">
              <span class="label">佣金率</span>
              <span class="value">{{ (store.currentProduct.commission_rate * 100).toFixed(0) }}%</span>
            </div>
          </div>
        </el-card>

        <!-- 动态参数区 -->
        <el-card class="params-card">
          <template #header>
            <span class="card-title">调整参数</span>
          </template>
          
          <el-form label-position="top">
            <el-form-item label="预期宣传费用 (元)">
              <el-slider
                v-model="store.calcParams.promotion_cost"
                :min="0"
                :max="10000"
                :step="100"
                :format-tooltip="val => `¥${val}`"
                @change="handleParamChange"
              />
              <div class="param-value">¥{{ store.calcParams.promotion_cost }}</div>
            </el-form-item>
            
            <el-form-item label="预估 GMV (元)">
              <el-slider
                v-model="store.calcParams.expected_gmv"
                :min="0"
                :max="50000"
                :step="500"
                :format-tooltip="val => `¥${val}`"
                @change="handleParamChange"
              />
              <div class="param-value">¥{{ store.calcParams.expected_gmv }}</div>
            </el-form-item>
          </el-form>

          <el-button
            type="primary"
            :loading="store.calculating"
            :disabled="!store.currentProduct"
            class="calc-btn"
            @click="handleCalculate"
          >
            开始测算
          </el-button>
        </el-card>
      </div>

      <!-- 右侧：结果看板 -->
      <div class="right-panel">
        <el-card class="result-card" v-if="store.lastResult">
          <template #header>
            <div class="result-header">
              <span class="card-title">测算结果</span>
              <el-tag :type="store.lastResult.decision_type" size="large" class="decision-tag">
                {{ store.lastResult.decision_text }}
              </el-tag>
            </div>
          </template>

          <!-- ROAS 核心指标 -->
          <div class="roas-display">
            <div class="roas-circle" :class="getRoasClass(store.lastResult.roas)">
              <div class="roas-value">{{ store.lastResult.roas }}</div>
              <div class="roas-label">ROAS</div>
            </div>
          </div>

          <!-- 决策灯号说明 -->
          <div class="decision-legend">
            <div class="legend-item">
              <span class="dot danger"></span>
              <span>比值 &lt; 3：高风险</span>
            </div>
            <div class="legend-item">
              <span class="dot success"></span>
              <span>3 ≤ 比值 ≤ 5：健康/推荐</span>
            </div>
            <div class="legend-item">
              <span class="dot warning"></span>
              <span>比值 &gt; 5：爆款潜力</span>
            </div>
          </div>

          <!-- 详细数据 -->
          <el-divider />
          
          <div class="result-details">
            <div class="detail-row">
              <span class="label">预估收入</span>
              <span class="value income">¥{{ store.lastResult.estimated_revenue.toLocaleString() }}</span>
            </div>
            <div class="detail-row">
              <span class="label">总投入</span>
              <span class="value expense">¥{{ store.lastResult.total_investment.toFixed(2) }}</span>
            </div>
            <el-divider direction="vertical" class="divider-vertical" />
            <div class="detail-row">
              <span class="label">固定成本</span>
              <span class="value">¥{{ store.lastResult.fixed_cost.toFixed(2) }}</span>
            </div>
            <div class="detail-row">
              <span class="label">变量成本</span>
              <span class="value">¥{{ store.lastResult.variable_cost.toFixed(2) }}</span>
            </div>
            <div class="detail-row">
              <span class="label">宣传费用</span>
              <span class="value">¥{{ store.lastResult.promotion_cost.toFixed(2) }}</span>
            </div>
          </div>
        </el-card>

        <!-- 空状态 -->
        <el-card v-else class="empty-card">
          <div class="empty-state">
            <el-icon class="empty-icon"><DataAnalysis /></el-icon>
            <p>请先选择商品并调整参数</p>
            <p class="empty-hint">输入 SKU 或商品名称开始选品决策</p>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { DataAnalysis } from '@element-plus/icons-vue'
import { useDecisionStore } from '@/stores/decision'

const store = useDecisionStore()

const searchKeyword = ref('')
let debounceTimer = null

// 防抖搜索
function handleSearch(query) {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    store.search(query)
  }, 300)
}

// 选择商品
function handleSelect(productId) {
  const product = store.searchResults.find(p => p.id === productId)
  if (product) {
    store.selectProduct(product)
    searchKeyword.value = ''
  }
}

// 参数变化时自动测算（防抖）
function handleParamChange() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    if (store.currentProduct) {
      handleCalculate()
    }
  }, 500)
}

// 执行测算
async function handleCalculate() {
  if (!store.currentProduct) {
    ElMessage.warning('请先选择商品')
    return
  }
  await store.calculate()
}

// 根据 ROAS 获取样式类
function getRoasClass(roas) {
  if (roas < 3) return 'danger'
  if (roas <= 5) return 'success'
  return 'warning'
}
</script>

<style scoped>
.decision-page {
  padding: 24px;
  min-height: calc(100vh - 120px);
  background: #f5f7fa;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px;
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
}

.subtitle {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

.decision-layout {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 24px;
}

.left-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.right-panel {
  min-height: 500px;
}

.card-title {
  font-weight: 600;
  color: #1e293b;
}

/* 搜索框 */
.product-search {
  width: 100%;
}

.product-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 0;
}

.product-option .sku {
  font-weight: 600;
  color: #3b82f6;
  min-width: 60px;
}

.product-option .name {
  flex: 1;
  color: #475569;
}

.product-option .price {
  color: #059669;
  font-weight: 500;
}

/* 商品信息 */
.product-detail {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-row .label {
  color: #64748b;
  font-size: 14px;
}

.info-row .value {
  color: #1e293b;
  font-weight: 500;
}

.info-row .value.price {
  color: #059669;
}

/* 参数区 */
.param-value {
  text-align: center;
  font-size: 24px;
  font-weight: 700;
  color: #3b82f6;
  margin-top: 8px;
}

.calc-btn {
  width: 100%;
  margin-top: 16px;
}

/* 结果看板 */
.result-card {
  height: 100%;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.decision-tag {
  font-size: 14px;
  padding: 6px 16px;
}

/* ROAS 圆形展示 */
.roas-display {
  display: flex;
  justify-content: center;
  padding: 32px 0;
}

.roas-circle {
  width: 180px;
  height: 180px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 6px solid;
  transition: all 0.3s ease;
}

.roas-circle.danger {
  border-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
}

.roas-circle.success {
  border-color: #10b981;
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
}

.roas-circle.warning {
  border-color: #f59e0b;
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
  animation: pulse-glow 2s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 20px rgba(245, 158, 11, 0.3); }
  50% { box-shadow: 0 0 40px rgba(245, 158, 11, 0.6); }
}

.roas-value {
  font-size: 48px;
  font-weight: 800;
  line-height: 1;
}

.roas-circle.danger .roas-value { color: #dc2626; }
.roas-circle.success .roas-value { color: #059669; }
.roas-circle.warning .roas-value { color: #d97706; }

.roas-label {
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* 决策图例 */
.decision-legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  padding: 16px 0;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #64748b;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.dot.danger { background: #ef4444; }
.dot.success { background: #10b981; }
.dot.warning { background: #f59e0b; }

/* 详细数据 */
.result-details {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 16px;
  position: relative;
}

.detail-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-row .label {
  font-size: 13px;
  color: #64748b;
}

.detail-row .value {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.detail-row .value.income { color: #059669; }
.detail-row .value.expense { color: #dc2626; }

.divider-vertical {
  height: auto;
  align-self: stretch;
  margin: 0 8px;
}

/* 空状态 */
.empty-card {
  height: 100%;
  min-height: 400px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
  color: #94a3b8;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state p {
  margin: 0;
  font-size: 16px;
}

.empty-hint {
  margin-top: 8px !important;
  font-size: 14px !important;
  color: #cbd5e1;
}
</style>
