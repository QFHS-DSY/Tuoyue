<template>
  <!-- 新手引导向导 -->
  <OnboardingWizard ref="onboardingRef" />
  <!-- 小白模式：简洁首页 -->
  <div v-if="isNoviceMode" class="novice-home">
    <!-- 顶部：模式切换 + 欢迎语 -->
    <div class="home-header">
      <div class="welcome-section">
        <h1 class="welcome-title">欢迎回来，跨境卖家！</h1>
        <p class="welcome-sub">辽宁跨境宝盒 · 一键跨境，一屏闭环</p>
      </div>
      <div class="mode-switcher">
        <span class="mode-label">当前模式：</span>
        <el-tag type="warning" effect="dark" size="large">小白模式</el-tag>
        <el-button text @click="switchToSenior" class="switch-btn">
          切换到资深模式
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 核心指标卡片（仅3个） -->
    <div class="core-stats">
      <div class="stat-item" @click="handleOrderJump">
        <div class="stat-icon-wrapper blue">
          <el-icon><ShoppingCart /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.orderCount }}</div>
          <div class="stat-label">今日订单</div>
        </div>
        <el-tag v-if="stats.pendingOrders > 0" type="danger" size="small" effect="dark">
          待处理
        </el-tag>
      </div>

      <div class="stat-item">
        <div class="stat-icon-wrapper green">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">¥{{ formatMoney(stats.salesAmount) }}</div>
          <div class="stat-label">今日销售额</div>
        </div>
        <div class="stat-trend up">
          <el-icon><ArrowUp /></el-icon>
          <span>+8.3%</span>
        </div>
      </div>

      <div class="stat-item warning" @click="router.push('/orders?status=pending_ship')">
        <div class="stat-icon-wrapper orange">
          <el-icon><Box /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.pendingOrders }}</div>
          <div class="stat-label">待发货订单</div>
        </div>
        <el-tag v-if="stats.pendingOrders > 5" type="warning" size="small">繁忙</el-tag>
      </div>
    </div>

    <!-- 两大核心入口按钮 -->
    <div class="main-actions">
      <div class="action-card primary" @click="router.push('/goods/listing')">
        <div class="action-icon">
          <el-icon><Upload /></el-icon>
        </div>
        <div class="action-content">
          <h2 class="action-title">我要上货</h2>
          <p class="action-desc">粘贴链接/扫码/拍照，一键完成商品上架</p>
        </div>
        <div class="action-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>

      <div class="action-card success" @click="router.push('/orders?action=ship')">
        <div class="action-icon">
          <el-icon><Van /></el-icon>
        </div>
        <div class="action-content">
          <h2 class="action-title">我要发货</h2>
          <p class="action-desc">智能匹配物流，一键批量打单发货</p>
        </div>
        <div class="action-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <!-- AI助手悬浮入口 -->
    <div class="ai-hint" @click="$router.push('/goods/listing')">
      <el-icon><MagicStick /></el-icon>
      <span>有疑问？试试问AI助手「小辽」</span>
    </div>

    <!-- 待办提醒 -->
    <div v-if="stats.pendingOrders > 0 || stats.orderCount > 0" class="pending-tasks">
      <div class="tasks-header">
        <el-icon><Bell /></el-icon>
        <span>待办提醒</span>
      </div>
      <div v-if="stats.pendingOrders > 0" class="task-item" @click="router.push('/orders?status=pending_ship')">
        <span class="task-text">有 {{ stats.pendingOrders }} 笔订单待发货</span>
        <el-tag type="danger" size="small">紧急</el-tag>
      </div>
      <div class="task-item" @click="router.push('/goods/listing')">
        <span class="task-text">点击「我要上货」开始今日工作</span>
        <el-tag type="success" size="small">建议</el-tag>
      </div>
    </div>
  </div>

  <!-- 资深模式：完整Dashboard -->
  <div v-else class="dashboard-container">
    <!-- 顶部统计栏 -->
    <div class="stats-header">
      <div class="stat-card" @click="handleOrderJumpSenior">
        <div class="stat-icon blue">
          <el-icon><ShoppingCart /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">今日订单量</div>
          <div class="stat-value">
            <span class="number">{{ stats.orderCount }}</span>
            <span class="unit">单</span>
          </div>
          <div class="stat-trend up">
            <el-icon><ArrowUp /></el-icon>
            <span>+12.5%</span>
          </div>
        </div>
      </div>
      <div class="stat-card" v-loading="statsLoading" @click="router.push('/reports')">
        <div class="stat-icon green">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">今日销售额</div>
          <div class="stat-value">
            <span class="currency">¥</span>
            <span class="number">{{ formatMoney(stats.salesAmount) }}</span>
          </div>
          <div class="stat-trend up">
            <el-icon><ArrowUp /></el-icon>
            <span>+8.3%</span>
          </div>
        </div>
      </div>
      <div class="stat-card" v-loading="statsLoading" @click="router.push('/reports')">
        <div class="stat-icon orange">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">平均客单价</div>
          <div class="stat-value">
            <span class="currency">¥</span>
            <span class="number">{{ stats.avgOrderValue }}</span>
          </div>
          <div class="stat-trend down">
            <el-icon><ArrowDown /></el-icon>
            <span>-2.1%</span>
          </div>
        </div>
      </div>
      <div class="stat-card" v-loading="statsLoading" @click="router.push('/orders?status=paid')">
        <div class="stat-icon purple">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">待发货订单</div>
          <div class="stat-value">
            <span class="number">{{ stats.pendingOrders }}</span>
            <span class="unit">单</span>
          </div>
          <div class="stat-trend" :class="stats.pendingOrders > 20 ? 'down' : 'up'">
            <el-icon><ArrowUp /></el-icon>
            <span>{{ stats.pendingOrders > 20 ? '较多' : '正常' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧图表 -->
      <div class="left-panel">
        <div class="chart-card" v-loading="salesLoading">
          <div class="chart-title">
            <span class="title-icon blue"></span>
            销售额趋势
          </div>
          <div ref="salesChartRef" class="chart-container"></div>
        </div>
        <div class="chart-card">
          <div class="chart-title">
            <span class="title-icon green"></span>
            平台分布
          </div>
          <div ref="platformChartRef" class="chart-container"></div>
        </div>
      </div>

      <!-- 中间地图 -->
      <div class="center-panel">
        <div class="map-card">
          <div class="map-header">
            <div class="map-title">
              <el-icon><MapLocation /></el-icon>
              全球订单实时分布
              <span v-if="selectedRegion" class="selected-tag">
                {{ selectedRegion.name }}
              </span>
            </div>
            <div class="map-legend">
              <span class="legend-item">
                <span class="dot hot"></span> 热门区域
              </span>
              <span class="legend-item">
                <span class="dot normal"></span> 普通区域
              </span>
              <span class="legend-item">
                <span class="dot new"></span> 新订单
              </span>
            </div>
          </div>
          <div ref="worldMapRef" class="map-container"></div>
          
          <!-- 地区详情弹窗 -->
          <div v-if="selectedRegion" class="region-panel">
            <div class="region-header">
              <span class="region-name">{{ selectedRegion.name }}</span>
              <el-button size="small" text @click="selectedRegion = null">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
            <div class="region-stats">
              <div class="region-stat">
                <div class="stat-icon-small">
                  <el-icon><ShoppingCart /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-label-small">今日订单</div>
                  <div class="stat-value-small">{{ selectedRegion.orders }}</div>
                </div>
              </div>
              <div class="region-stat">
                <div class="stat-icon-small green">
                  <el-icon><Money /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-label-small">销售额</div>
                  <div class="stat-value-small">¥{{ formatMoney(selectedRegion.sales) }}</div>
                </div>
              </div>
              <div class="region-stat">
                <div class="stat-icon-small orange">
                  <el-icon><TrendCharts /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-label-small">平均客单价</div>
                  <div class="stat-value-small">¥{{ selectedRegion.avgOrder }}</div>
                </div>
              </div>
              <div class="region-stat">
                <div class="stat-icon-small purple">
                  <el-icon><Goods /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-label-small">热销品类</div>
                  <div class="stat-value-small">{{ selectedRegion.topCategory }}</div>
                </div>
              </div>
            </div>
            <div class="region-chart">
              <div ref="regionChartRef" class="mini-chart"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧实时订单 -->
      <div class="right-panel">
        <div class="order-card">
          <div class="order-header">
            <div class="order-title">
              <span class="pulse-dot"></span>
              实时订单
            </div>
            <div class="order-count">{{ realtimeOrders.length }}条</div>
          </div>
          <div class="order-list" ref="orderListRef" v-loading="ordersLoading" element-loading-text="加载订单中..."
            @mouseenter="pauseScroll" @mouseleave="resumeScroll">
            <div class="order-scroll-wrap" :style="{ transform: `translateY(-${scrollOffset}px)` }">
              <div 
                class="order-item" 
                v-for="(order, index) in scrollOrders" 
                :key="order.id + '-' + (index >= displayOrders.length ? 'dup' : '')"
                :class="{ 'new-order': index < newOrderCount }"
                @click="highlightRegion(order.country)"
              >
              <div class="order-platform" :class="order.platform">
                <img :src="getPlatformIcon(order.platform)" :alt="order.platform">
              </div>
              <div class="order-info">
                <div class="order-customer">{{ maskCustomer(order.buyer_name || order.customer || '未知买家') }}</div>
                <div class="order-location">
                  <el-icon><Location /></el-icon>
                  {{ order.city || order.country || '未知地点' }}
                </div>
              </div>
              <div class="order-amount">
                <div class="amount">¥{{ Number(order.amount).toFixed(2) }}</div>
                <div class="time">{{ order.time || '' }}</div>
              </div>
            </div>
          </div>  <!-- /order-scroll-wrap -->
        </div>
        </div>

        <div class="chart-card">
          <div class="chart-title">
            <span class="title-icon orange"></span>
            交付时效
          </div>
          <div class="delivery-stats">
            <div class="delivery-item">
              <div class="delivery-icon">
                <el-icon><Van /></el-icon>
              </div>
              <div class="delivery-info">
                <div class="delivery-label">平均交付</div>
                <div class="delivery-value">{{ deliveryStats.avgDays }}<span class="unit">天</span></div>
              </div>
            </div>
            <div class="delivery-item">
              <div class="delivery-icon green">
                <el-icon><CircleCheck /></el-icon>
              </div>
              <div class="delivery-info">
                <div class="delivery-label">准时率</div>
                <div class="delivery-value">{{ deliveryStats.onTimeRate }}<span class="unit">%</span></div>
              </div>
            </div>
            <div class="delivery-item">
              <div class="delivery-icon blue">
                <el-icon><Box /></el-icon>
              </div>
              <div class="delivery-info">
                <div class="delivery-label">在途订单</div>
                <div class="delivery-value">{{ deliveryStats.inTransit.toLocaleString() }}<span class="unit">单</span></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import OnboardingWizard from '@/components/OnboardingWizard.vue'
import { 
  ArrowUp, ArrowDown, Location, ShoppingCart, Money, User, Timer,
  MapLocation, Van, CircleCheck, Box, TrendCharts, Goods, Close,
  MagicStick, Bell, Upload, ArrowRight
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getPlatformIcon } from '@/utils/platformIcons'
import request from '@/utils/request'
import { useAppStore } from '@/stores/useAppStore'

const router = useRouter()
const appStore = useAppStore()

// 判断是否为小白模式（store 中 'beginner' 对应小白模式）
const isNoviceMode = computed(() => appStore.mode === 'beginner')

// 小白模式卡片点击路由跳转
function handleOrderJump() {
  console.log('[Dashboard] 小白模式·今日订单卡片被点击！路由对象:', router)
  router.push('/orders')
}

function handleOrderJumpSenior() {
  console.log('[Dashboard] 资深模式·今日订单量卡片被点击！')
  router.push('/orders?date=today')
}

// 小白模式切换函数
function switchToSenior() {
  appStore.setMode('expert')
}

// ==================== 加载状态 ====================
const statsLoading = ref(true)
const ordersLoading = ref(true)
const salesLoading = ref(true)

// 交付时效
const deliveryStats = reactive({ avgDays: '--', onTimeRate: '--', inTransit: 0 })

// ==================== 统计数据 ====================
const stats = reactive({
  orderCount: 0,
  salesAmount: 0,
  avgOrderValue: 0,
  pendingOrders: 0,
})

// ==================== 选中地区 ====================
const selectedRegion = ref(null)
const regionChartRef = ref(null)
let regionChart = null

// 地区数据（用于地图点击与订单高亮）
const regionData = {
  '中国': { name: '中国', orders: 456, sales: 234500, avgOrder: 514, topCategory: '电子产品', trend: [45,52,38,65,47,56,72] },
  '马来西亚': { name: '马来西亚', orders: 234, sales: 128000, avgOrder: 547, topCategory: '服装', trend: [23,31,28,35,29,40,38] },
  '美国': { name: '美国', orders: 328, sales: 189000, avgOrder: 576, topCategory: '家居用品', trend: [38,42,35,48,44,52,49] },
  '新加坡': { name: '新加坡', orders: 145, sales: 78000, avgOrder: 538, topCategory: '美妆', trend: [15,18,20,17,22,19,25] },
  '泰国': { name: '泰国', orders: 189, sales: 92000, avgOrder: 487, topCategory: '服装', trend: [20,24,22,28,26,30,32] },
  '英国': { name: '英国', orders: 156, sales: 82000, avgOrder: 526, topCategory: '电子产品', trend: [16,19,17,21,18,24,22] },
  '印尼': { name: '印尼', orders: 267, sales: 145000, avgOrder: 543, topCategory: '日用百货', trend: [28,32,30,36,33,38,35] },
}


// ==================== 实时订单 ====================
const realtimeOrders = reactive([])
const newOrderCount = ref(0)
const displayOrders = computed(() => realtimeOrders.slice(0, 8))

function maskCustomer(name) {
  if (!name) return '***'
  if (name.length <= 2) return name + '***'
  return name.slice(0, 1) + '***' + name.slice(-1)
}

// ==================== 图表引用 ====================








// ==================== 图表引用 ====================
const salesChartRef = ref(null)
const platformChartRef = ref(null)
const worldMapRef = ref(null)
let salesChart = null
let platformChart = null
let mapChart = null

// ==================== 格式化 ====================
function formatMoney(num) {
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// ==================== API 数据拉取 ====================

// 拉取统计数据
async function fetchDashboardStats() {
  try {
    const res = await request.get('/api/dashboard/stats')
    const d = res.data || {}
    Object.assign(stats, d)
    // 同时刷新交付时效（合并在同一接口中）
    deliveryStats.avgDays = d.avgDeliveryDays ?? '--'
    deliveryStats.onTimeRate = d.onTimeRate ?? '--'
    deliveryStats.inTransit = d.inTransitOrders ?? 0
  } catch (e) {
    // API 不可用，保持初始零值状态
  } finally {
    statsLoading.value = false
  }
}

// 拉取最近订单
async function fetchRecentOrders() {
  try {
    const res = await request.get('/api/dashboard/recent-orders')
    const list = res.data || []
    if (list.length) {
      realtimeOrders.splice(0, realtimeOrders.length, ...list)
    }
  } catch (e) {
    // API 不可用时保持空列表
  } finally {
    ordersLoading.value = false
  }
}

// 拉取销售趋势
async function fetchSalesTrend() {
  try {
    const res = await request.get('/api/dashboard/sales-trend')
    const data = res.data || {}
    if (data.labels && data.labels.length) return data
    return { labels: [], values: [] }
  } catch (e) {
    return { labels: [], values: [] }
  }
}

// 自动滚动：每 3 秒滚动一个订单项
const scrollOffset = ref(0)
const scrollPaused = ref(false)
let scrollTimer = null
const ITEM_HEIGHT = 72  // 每个订单项高度 px
const scrollOrders = computed(() => {
  const items = displayOrders.value
  if (items.length < 2) return items
  // 复制一份实现无缝循环：A,B,C → A,B,C,A,B
  return [...items, ...items.slice(0, 2)]
})
function startAutoScroll() {
  if (scrollTimer) clearInterval(scrollTimer)
  scrollTimer = setInterval(() => {
    if (scrollPaused.value) return
    const maxOffset = (displayOrders.value.length) * ITEM_HEIGHT
    scrollOffset.value += ITEM_HEIGHT
    if (scrollOffset.value >= maxOffset) {
      scrollOffset.value = 0
    }
  }, 3000)
}
function pauseScroll() { scrollPaused.value = true }
function resumeScroll() { scrollPaused.value = false }
onUnmounted(() => { if (scrollTimer) clearInterval(scrollTimer) })

// 在地图上闪烁气泡：接收一个订单数组，提取坐标推送到 effectScatter 临时动画
function flashMapBubble(orders) {
  const _mapChart = mapChart
  if (!_mapChart) return
  const bubbles = []
  for (const o of orders) {
    let coords = o.coords
    if (!coords || coords.length !== 2) {
      // 按城市名查不到坐标则跳过
      continue
    }
    bubbles.push({ name: o.city || o.country, value: [...coords, Math.round(o.amount || 50)] })
  }
  if (!bubbles.length) return
  _mapChart.dispatchAction({ type: 'downplay' })
  _mapChart.appendData({
    seriesIndex: 1,
    data: bubbles,
  })
  // 自动高亮首个订单对应国家
  const first = orders[0]
  if (first && (first.country || first.city)) {
    const country = first.country || first.city
    highlightRegion(country)
  }
}

// 新订单推送（WebSocket 替代轮询的后门；目前用轮询模拟）
async function pollNewOrders() {
  try {
    const res = await request.get('/api/dashboard/new-orders-since', {
      params: { since: realtimeOrders[0]?.id || 0 }
    })
    if (res.data?.length) {
      realtimeOrders.unshift(...res.data)
      if (realtimeOrders.length > 20) realtimeOrders.splice(20)
      newOrderCount.value = res.data.length
      setTimeout(() => { newOrderCount.value = 0 }, 1500)
      // 更新统计
      res.data.forEach(o => {
        stats.orderCount++
        stats.salesAmount += parseFloat(o.amount)
      })
      // 地图气泡闪烁
      flashMapBubble(res.data)
    }
  } catch (e) {
    // 静默失败，不干扰用户
  }
}

// ==================== 初始化图表 ====================
function initSalesChart(salesData) {
  if (!salesChartRef.value) return
  const labels = (salesData && salesData.labels && salesData.labels.length) ? salesData.labels : ['暂无数据']
  const values = (salesData && salesData.values && salesData.values.length) ? salesData.values : [0]
  salesChart = echarts.init(salesChartRef.value)
  const option = {
    backgroundColor: 'transparent',
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: labels,
      axisLine: { lineStyle: { color: '#e0e6ed' } },
      axisLabel: { color: '#606266', fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f0f2f5' } },
      axisLabel: { color: '#606266', fontSize: 11 }
    },
    series: [{
      data: values,
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { color: '#085B9C', width: 3 },
      itemStyle: { color: '#085B9C', borderWidth: 2, borderColor: '#fff' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(8,91,156,0.3)' },
          { offset: 1, color: 'rgba(8,91,156,0.05)' }
        ])
      }
    }]
  }
  salesChart.setOption(option)
}

function initPlatformChart() {
  if (!platformChartRef.value) return
  platformChart = echarts.init(platformChartRef.value)
  platformChart.setOption({
    backgroundColor: 'transparent',
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '50%'],
      data: [],
      label: { color: '#606266', fontSize: 12 },
      labelLine: { lineStyle: { color: '#d0d7de' } }
    }]
  })
}

// 高亮地区
function highlightRegion(country) {
  if (regionData[country]) {
    selectedRegion.value = regionData[country]
    // 高亮地图上的对应区域（用局部变量捕获，防止组件卸载后访问已 dispose 的 chart）
    const _mapChart = mapChart
    if (_mapChart) {
      const countryMap = {
        '中国': 'China',
        '马来西亚': 'Malaysia',
        '美国': 'United States',
        '新加坡': 'Singapore',
        '泰国': 'Thailand',
        '英国': 'United Kingdom',
        '印尼': 'Indonesia'
      }
      const mapName = countryMap[country]
      if (mapName) {
        _mapChart.dispatchAction({
          type: 'highlight',
          name: mapName
        })
        setTimeout(() => {
          if (_mapChart) {
            _mapChart.dispatchAction({
              type: 'downplay',
              name: mapName
            })
          }
        }, 2000)
      }
    }
    // 初始化地区图表
    setTimeout(() => {
      initRegionChart()
    }, 100)
  }
}

// 初始化地区趋势图
function initRegionChart() {
  if (!regionChartRef.value || !selectedRegion.value) return
  
  if (regionChart) {
    regionChart.dispose()
  }
  
  regionChart = echarts.init(regionChartRef.value)
  const option = {
    backgroundColor: 'transparent',
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      axisLine: { lineStyle: { color: '#e0e6ed' } },
      axisLabel: { color: '#606266', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f0f2f5' } },
      axisLabel: { color: '#606266', fontSize: 10 }
    },
    series: [{
      data: selectedRegion.value.trend,
      type: 'bar',
      barWidth: '60%',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#2ead3e' },
          { offset: 1, color: '#085B9C' }
        ]),
        borderRadius: [4, 4, 0, 0]
      }
    }]
  }
  regionChart?.setOption(option)
}

async function initWorldMap() {
  // 加载世界地图数据
  try {
    const response = await fetch('https://cdn.jsdelivr.net/npm/echarts/map/json/world.json')
    const worldJson = await response.json()
    echarts.registerMap('world', worldJson)
  } catch (e) {
    console.log('使用简化地图')
  }

  if (!worldMapRef.value) return
  mapChart = echarts.init(worldMapRef.value)

  // 从后端 API 获取真实订单分布数据
  let mapData = []
  try {
    const res = await request.get('/api/dashboard/world-map-orders/')
    mapData = (res?.data?.map_data || []).map(d => ({ name: d.name, value: d.value }))
  } catch {
    mapData = [{ name: 'China', value: 0 }]
  }

  // 空数据保护：地图无数据时不崩溃
  if (mapData.length === 0 || mapData.every(d => d.value === 0)) {
    mapData = [{ name: 'China', value: 1 }]
    const emptyOption = {
      backgroundColor: 'transparent',
      geo: {
        map: 'world',
        roam: true,
        zoom: 1.2,
        label: { show: false },
        itemStyle: { areaColor: '#e8f4fc', borderColor: '#085B9C' }
      },
      series: [{ type: 'map', geoIndex: 0, data: mapData }]
    }
    mapChart.setOption(emptyOption)
    return
  }

  const maxVal = Math.max(...mapData.map(d => d.value), 1)

  const option = {
    backgroundColor: 'transparent',
    geo: {
      map: 'world',
      roam: true,
      zoom: 1.2,
      label: { show: false },
      itemStyle: {
        areaColor: '#e8f4fc',
        borderColor: '#085B9C',
        borderWidth: 0.5
      },
      emphasis: {
        itemStyle: {
          areaColor: '#2ead3e'
        },
        label: {
          show: true,
          color: '#fff'
        }
      }
    },
    visualMap: {
      min: 0,
      max: maxVal,
      left: 'left',
      bottom: 'bottom',
      text: ['高', '低'],
      textStyle: { color: '#606266' },
      inRange: {
        color: ['#e8f4fc', '#a9cdeb', '#085B9C']
      },
      calculable: true
    },
    series: [{
      type: 'map',
      geoIndex: 0,
      data: mapData
    }, {
      type: 'effectScatter',
      coordinateSystem: 'geo',
      data: [
        { name: '深圳', value: [114.0579, 22.5431, 299] },
        { name: '吉隆坡', value: [101.6869, 3.139, 187] },
        { name: '洛杉矶', value: [-118.2437, 34.0522, 456] },
        { name: '上海', value: [121.4737, 31.2304, 128] },
        { name: '新加坡', value: [103.8198, 1.3521, 234] },
        { name: '曼谷', value: [100.5018, 13.7563, 89] },
        { name: '伦敦', value: [-0.1276, 51.5074, 567] },
        { name: '雅加达', value: [106.8456, -6.2088, 278] },
      ],
      symbolSize: function (val) {
        return val[2] / 25
      },
      rippleEffect: {
        brushType: 'stroke',
        scale: 3,
        period: 4
      },
      itemStyle: {
        color: '#2ead3e'
      }
    }]
  }
  
  mapChart.setOption(option)
  
  // 点击地图事件
  mapChart.on('click', function(params) {
    const countryMap = {
      'China': '中国',
      'Malaysia': '马来西亚',
      'United States': '美国',
      'Singapore': '新加坡',
      'Thailand': '泰国',
      'United Kingdom': '英国',
      'Indonesia': '印尼'
    }
    const cnName = countryMap[params.name]
    if (cnName && regionData[cnName]) {
      selectedRegion.value = regionData[cnName]
      setTimeout(() => {
        initRegionChart()
      }, 100)
    }
  })
}

// ==================== 真实数据轮询 ====================
let timers = []

function startRealtimeUpdate() {
  // 每 30 秒拉一次新订单
  timers.push(setInterval(() => {
    pollNewOrders()
  }, 30000))
}

// ==================== 新手引导 ====================
const onboardingRef = ref(null)
function checkOnboarding() {
  if (!localStorage.getItem('onboarding_done') && isNoviceMode.value) {
    setTimeout(() => onboardingRef.value?.show(), 500)
  }
}

// ==================== 生命周期 ====================
onMounted(async () => {
  // 0. 新手引导检查
  checkOnboarding()
  // 1. 并行拉取所有数据
  await Promise.all([
    fetchDashboardStats(),
    fetchRecentOrders(),
  ])

  // 2. 拉取销售趋势后再初始化图表
  const salesData = await fetchSalesTrend()
  salesLoading.value = false

  // 3. 初始化图表
  initSalesChart(salesData)
  initPlatformChart()
  initWorldMap()

  // 4. 启动新订单轮询
  startRealtimeUpdate()
  // 5. 启动自动滚动
  setTimeout(startAutoScroll, 4000)
  
  window.addEventListener('resize', () => {
    salesChart?.resize()
    platformChart?.resize()
    mapChart?.resize()
    regionChart?.resize()
  })
})

onUnmounted(() => {
  timers.forEach(t => clearInterval(t))
  if (salesChart) { salesChart.dispose(); salesChart = null }
  if (platformChart) { platformChart.dispose(); platformChart = null }
  if (mapChart) { mapChart.dispose(); mapChart = null }
  if (regionChart) { regionChart.dispose(); regionChart = null }
})
</script>

<style scoped>
/* ==================== 小白模式首页样式 ==================== */
.novice-home {
  padding: 24px;
  max-width: 900px;
  margin: 0 auto;
}

.home-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.welcome-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px;
}

.welcome-sub {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.mode-switcher {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mode-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.switch-btn {
  color: var(--primary);
  font-size: 13px;
}

.core-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.stat-item {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.stat-item:hover {
  border-color: var(--primary);
  box-shadow: 0 4px 12px rgba(8, 91, 156, 0.1);
}

.stat-item.warning {
  border-color: #E6A23C;
  background: #FDF6EC;
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon-wrapper.blue {
  background: rgba(64, 158, 255, 0.1);
  color: #409EFF;
}

.stat-icon-wrapper.green {
  background: rgba(103, 194, 58, 0.1);
  color: #67C23A;
}

.stat-icon-wrapper.orange {
  background: rgba(230, 162, 60, 0.1);
  color: #E6A23C;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
}

.stat-trend.up {
  color: #67C23A;
  background: rgba(103, 194, 58, 0.1);
}

.main-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 28px;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.action-card::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  opacity: 0.1;
  transform: translate(40%, -40%);
}

.action-card.primary {
  background: linear-gradient(135deg, #085B9C 0%, #0D7BD6 100%);
  color: #fff;
}

.action-card.primary::before {
  background: #fff;
}

.action-card.success {
  background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%);
  color: #fff;
}

.action-card.success::before {
  background: #fff;
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
}

.action-icon {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
}

.action-content {
  flex: 1;
}

.action-title {
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 8px;
}

.action-desc {
  font-size: 14px;
  opacity: 0.9;
  margin: 0;
  line-height: 1.4;
}

.action-arrow {
  font-size: 24px;
  opacity: 0.7;
}

.ai-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: rgba(64, 158, 255, 0.08);
  border: 1px dashed rgba(64, 158, 255, 0.3);
  border-radius: 8px;
  color: var(--primary);
  font-size: 14px;
  margin-bottom: 24px;
  cursor: pointer;
}

.ai-hint:hover {
  background: rgba(64, 158, 255, 0.12);
}

.pending-tasks {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
}

.tasks-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}

.task-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  cursor: pointer;
  transition: background 0.2s;
}

.task-item:hover {
  background: var(--bg-hover);
  margin: 0 -16px;
  padding: 10px 16px;
}

.task-text {
  font-size: 14px;
  color: var(--text-primary);
}

/* ==================== 资深模式Dashboard样式 ==================== */
.dashboard-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
}

/* 顶部统计栏 */
.stats-header {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  transition: all 0.3s;
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
}

.stat-icon.blue {
  background: linear-gradient(135deg, #085B9C, #4a8ed4);
}

.stat-icon.green {
  background: linear-gradient(135deg, #2ead3e, #5bc75e);
}

.stat-icon.orange {
  background: linear-gradient(135deg, #ee5a24, #f39c12);
}

.stat-icon.purple {
  background: linear-gradient(135deg, #8e44ad, #bb8fce);
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-value {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.stat-value .number {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.stat-value .currency {
  font-size: 16px;
  font-weight: 600;
  color: #606266;
}

.stat-value .unit {
  font-size: 14px;
  color: #909399;
  margin-left: 2px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  margin-top: 4px;
}

.stat-trend.up {
  color: #2ead3e;
}

.stat-trend.down {
  color: #f56c6c;
}

/* 主内容区 */
.main-content {
  display: grid;
  grid-template-columns: 280px 1fr 320px;
  gap: 20px;
}

/* 左侧面板 */
.left-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 右侧面板 */
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 图表卡片 */
.chart-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.title-icon {
  width: 4px;
  height: 16px;
  border-radius: 2px;
}

.title-icon.blue {
  background: #085B9C;
}

.title-icon.green {
  background: #2ead3e;
}

.title-icon.orange {
  background: #ee5a24;
}

.chart-container {
  height: 180px;
}

/* 中间地图 */
.center-panel {
  position: relative;
}

.map-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  height: 100%;
  position: relative;
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.map-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.map-title .el-icon {
  color: #085B9C;
}

.selected-tag {
  background: linear-gradient(135deg, #2ead3e, #085B9C);
  color: #fff;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.map-legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #606266;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot.hot {
  background: #2ead3e;
}

.dot.normal {
  background: #085B9C;
}

.dot.new {
  background: #ee5a24;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.map-container {
  height: calc(100% - 50px);
  min-height: 400px;
}

/* 地区详情面板 */
.region-panel {
  position: absolute;
  right: 20px;
  top: 60px;
  width: 260px;
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  z-index: 100;
}

.region-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.region-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.region-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}

.region-stat {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-icon-small {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #f0f7ff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #085B9C;
  font-size: 14px;
}

.stat-icon-small.green {
  background: #f0fff4;
  color: #2ead3e;
}

.stat-icon-small.orange {
  background: #fff7f0;
  color: #ee5a24;
}

.stat-icon-small.purple {
  background: #f9f0ff;
  color: #8e44ad;
}

.stat-content {
  flex: 1;
}

.stat-label-small {
  font-size: 11px;
  color: #909399;
  margin-bottom: 2px;
}

.stat-value-small {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

.region-chart {
  height: 100px;
}

.mini-chart {
  width: 100%;
  height: 100%;
}

/* 实时订单 */
.order-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  flex: 1;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.order-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background: #2ead3e;
  border-radius: 50%;
  animation: pulse-dot 1.5s infinite;
}

@keyframes pulse-dot {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.5); opacity: 0.5; }
  100% { transform: scale(1); opacity: 1; }
}

.order-count {
  font-size: 12px;
  color: #909399;
}

.order-list {
  max-height: 320px;
  overflow: hidden;
  position: relative;
}
.order-list:hover .order-scroll-wrap {
  animation-play-state: paused;
}

.order-scroll-wrap {
  transition: transform 0.8s cubic-bezier(0.25, 0.1, 0.25, 1);
  will-change: transform;
}

.order-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  background: #f5f7fa;
  transition: all 0.3s;
  cursor: pointer;
}

.order-item:hover {
  background: #e8f4fc;
  transform: translateX(4px);
}

.order-item.new-order {
  background: linear-gradient(90deg, #f0fff4, #e8f4fc);
  animation: slideIn 0.5s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.order-platform {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  overflow: hidden;
}

.order-platform img {
  width: 20px;
  height: 20px;
  object-fit: contain;
}

.order-info {
  flex: 1;
  min-width: 0;
}

.order-customer {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.order-location {
  font-size: 11px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 4px;
}

.order-amount {
  text-align: right;
}

.order-amount .amount {
  font-size: 14px;
  font-weight: 600;
  color: #f56c6c;
  margin-bottom: 2px;
}

.order-amount .time {
  font-size: 11px;
  color: #c0c4cc;
}

/* 交付时效 */
.delivery-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.delivery-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.delivery-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #e8f4fc;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #085B9C;
  font-size: 18px;
}

.delivery-icon.green {
  background: #f0fff4;
  color: #2ead3e;
}

.delivery-icon.blue {
  background: #f0f7ff;
  color: #085B9C;
}

.delivery-info {
  flex: 1;
}

.delivery-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 2px;
}

.delivery-value {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
}

.delivery-value .unit {
  font-size: 12px;
  font-weight: 400;
  color: #909399;
  margin-left: 2px;
}
</style>