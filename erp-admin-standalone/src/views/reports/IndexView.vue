<template>
  <div class="page-container">
    <!-- 页面Header -->
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">数据报表</h1>
        <p class="page-desc">全链路经营数据洞察</p>
      </div>
      <div class="page-header-right">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          @change="loadData"
          style="width:260px"
        />
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card stat-collect">
          <div class="stat-icon"><el-icon><ShoppingCart /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ formatNumber(report.collectCount) }}</div>
            <div class="stat-label">采集商品数</div>
            <div class="stat-trend" :class="report.collectTrend >= 0 ? 'up' : 'down'">
              <el-icon><Top v-if="report.collectTrend >= 0" /><Bottom v-else /></el-icon>
              {{ report.collectTrend >= 0 ? '+' : '' }}{{ report.collectTrend }}%
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card stat-goods">
          <div class="stat-icon"><el-icon><Goods /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ formatNumber(report.listingCount) }}</div>
            <div class="stat-label">上货商品数</div>
            <div class="stat-trend" :class="report.listingTrend >= 0 ? 'up' : 'down'">
              <el-icon><Top v-if="report.listingTrend >= 0" /><Bottom v-else /></el-icon>
              {{ report.listingTrend >= 0 ? '+' : '' }}{{ report.listingTrend }}%
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card stat-order">
          <div class="stat-icon"><el-icon><List /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ formatNumber(report.orderCount) }}</div>
            <div class="stat-label">总订单数</div>
            <div class="stat-trend" :class="report.orderTrend >= 0 ? 'up' : 'down'">
              <el-icon><Top v-if="report.orderTrend >= 0" /><Bottom v-else /></el-icon>
              {{ report.orderTrend >= 0 ? '+' : '' }}{{ report.orderTrend }}%
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card stat-sales">
          <div class="stat-icon"><el-icon><Money /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ formatSales(report.salesAmount) }}</div>
            <div class="stat-label">总销售额</div>
            <div class="stat-trend" :class="report.salesTrend >= 0 ? 'up' : 'down'">
              <el-icon><Top v-if="report.salesTrend >= 0" /><Bottom v-else /></el-icon>
              {{ report.salesTrend >= 0 ? '+' : '' }}{{ report.salesTrend }}%
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区 -->
    <el-row :gutter="16" class="chart-row">
      <!-- 销售趋势 -->
      <el-col :xs="24" :lg="16">
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">📈 销售趋势</span>
            <el-radio-group v-model="chartPeriod" size="small" @change="loadData">
              <el-radio-button value="7d">近7天</el-radio-button>
              <el-radio-button value="30d">近30天</el-radio-button>
            </el-radio-group>
          </div>
          <div class="chart-body">
            <v-chart :option="salesChartOption" autoresize style="height:280px" />
          </div>
        </div>
      </el-col>

      <!-- 平台分布 -->
      <el-col :xs="24" :lg="8">
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">🥧 平台分布</span>
          </div>
          <div class="chart-body">
            <v-chart :option="platformChartOption" autoresize style="height:280px" />
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="chart-row">
      <!-- 库存预警 -->
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">⚠️ 库存预警 TOP10</span>
          </div>
          <div class="chart-body">
            <el-table :data="alertItems" size="small" max-height="260">
              <el-table-column label="商品名称" min-width="200" show-overflow-tooltip />
              <el-table-column label="SKU" width="120">
                <template #default="{ row }">
                  <span style="font-size:12px;color:var(--brand)">{{ row.skuId }}</span>
                </template>
              </el-table-column>
              <el-table-column label="当前库存" width="90" align="center">
                <template #default="{ row }">
                  <span :style="{ color: row.status === 'out' ? 'var(--danger)' : 'var(--warning)', fontWeight: 600 }">
                    {{ row.stock }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="安全库存" width="90" align="center" />
              <el-table-column label="状态" width="80" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'out' ? 'danger' : 'warning'" size="small">
                    {{ row.status === 'out' ? '缺货' : '预警' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-col>

      <!-- 热销商品 -->
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">🏆 热销商品 TOP10</span>
          </div>
          <div class="chart-body">
            <v-chart :option="hotProductsChartOption" autoresize style="height:260px" />
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import request from '@/utils/request'

use([CanvasRenderer, LineChart, PieChart, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

const dateRange = ref([])
const chartPeriod = ref('7d')
const alertItems = ref([])
const hotProducts = ref([])

// 报表统计数据（从后端 API 加载）
const report = ref({
  collectCount: 0,
  collectTrend: 0,
  listingCount: 0,
  listingTrend: 0,
  orderCount: 0,
  orderTrend: 0,
  salesAmount: 0,
  salesTrend: 0,
})

// 数值格式化：千位分隔
function formatNumber(n) {
  if (n == null) return '0'
  return Number(n).toLocaleString('zh-CN')
}

// 销售额格式化：超过千元显示 k
function formatSales(n) {
  if (n == null) return '¥0'
  n = Number(n)
  if (n >= 1000) return '¥' + (n / 1000).toFixed(1) + 'k'
  return '¥' + n.toFixed(2)
}

const salesChartData = ref({ labels: [], values: [] })

const salesChartOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 50, right: 20, top: 20, bottom: 25 },
  xAxis: { type: 'category', data: salesChartData.value.labels },
  yAxis: { type: 'value' },
  series: [{
    type: 'line',
    data: salesChartData.value.values,
    smooth: true,
    lineStyle: { width: 2, color: '#2563eb' },
    areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(37,99,235,0.3)' }, { offset: 1, color: 'rgba(37,99,235,0.02)' }] } },
    itemStyle: { color: '#2563eb' },
  }],
}))

const platformChartData = ref([])

const platformChartOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  series: [{
    type: 'pie',
    data: platformChartData.value,
    radius: ['40%', '70%'],
    center: ['50%', '45%'],
    label: { show: true, formatter: '{b}: {c}' },
    emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.5)' } },
  }],
}))

const hotProductsChartOption = computed(() => {
  const data = hotProducts.value || []
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 100, right: 20, top: 10, bottom: 10 },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: data.map(p => p.name).reverse() },
    series: [{
      type: 'bar',
      data: data.map(p => p.sales).reverse(),
      barMaxWidth: 18,
    }],
  }
})

async function loadData() {
  try {
    const res = await request.get('/api/reports/summary/', { params: { period: chartPeriod.value } })
    const d = res?.data || {}
    report.value = {
      collectCount: d.total_products ?? d.collectCount ?? 0,
      collectTrend: d.collectTrend ?? 0,
      listingCount: d.total_products ?? d.listingCount ?? 0,
      listingTrend: d.listingTrend ?? 0,
      orderCount: d.total_orders ?? d.orderCount ?? 0,
      orderTrend: d.orderTrend ?? 0,
      salesAmount: d.total_revenue ?? d.salesAmount ?? 0,
      salesTrend: d.monthly_growth ?? d.salesTrend ?? 0,
    }
    alertItems.value = d.alerts || []
    hotProducts.value = d.hotProducts || []
    salesChartData.value = d.salesTrendChart || { labels: [], values: [] }
    platformChartData.value = d.platformChart || []
  } catch (_) {
    // API 不可用时保持零值
  }
}

onMounted(loadData)
</script>

<style scoped>
.stat-row { margin-bottom: 20px; }
.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--bg-card);
  border-radius: var(--r-lg);
  padding: 20px;
  box-shadow: var(--shadow-xs);
}
.stat-icon {
  width: 48px; height: 48px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px;
  color: #fff;
}
.stat-collect .stat-icon { background: linear-gradient(135deg, #2563eb, #1d4ed8); }
.stat-goods .stat-icon { background: linear-gradient(135deg, #7c3aed, #6d28d9); }
.stat-order .stat-icon { background: linear-gradient(135deg, #0891b2, #0e7490); }
.stat-sales .stat-icon { background: linear-gradient(135deg, #16a34a, #15803d); }
.stat-info { flex: 1; }
.stat-value { font-size: 22px; font-weight: 700; color: var(--text-primary); }
.stat-label { font-size: 13px; color: var(--text-muted); margin-top: 2px; }
.stat-trend { font-size: 12px; font-weight: 500; margin-top: 4px; display: flex; align-items: center; gap: 2px; }
.stat-trend.up { color: var(--success); }
.stat-trend.down { color: var(--danger); }

.chart-row { margin-bottom: 16px; }
.chart-card {
  background: var(--bg-card);
  border-radius: var(--r-lg);
  padding: 20px;
  box-shadow: var(--shadow-xs);
}
.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.chart-title { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.chart-body { width: 100%; }
</style>
