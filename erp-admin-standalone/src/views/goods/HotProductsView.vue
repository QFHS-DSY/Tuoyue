<template>
  <div class="hot-products-page">
    <!-- 页面Header -->
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">爆品推荐</h1>
        <p class="page-desc">精选各平台热销、飙升、高利润商品，支持一键采集上货</p>
      </div>
    </div>

    <!-- 五大榜单Tab -->
    <div class="rank-tabs">
      <div
        v-for="tab in tabs"
        :key="tab.id"
        :class="['rank-tab', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        <el-icon><component :is="tab.icon" /></el-icon>
        <span>{{ tab.name }}</span>
        <el-tag v-if="tab.badge" type="danger" size="small" effect="dark">{{ tab.badge }}</el-tag>
      </div>
    </div>

    <!-- 商品列表 -->
    <div class="products-grid" v-loading="loading">
      <div
        v-for="item in currentList"
        :key="item.id"
        class="product-card"
        draggable="true"
        @dragstart="onDragStart($event, item)"
        @dragend="onDragEnd"
      >
        <div class="product-image">
          <img :src="item.image" :alt="item.name" />
          <div class="platform-badge" :style="{ background: item.platformColor }">
            {{ item.platform }}
          </div>
          <div class="rank-badge" v-if="item.rank">
            #{{ item.rank }}
          </div>
        </div>
        <div class="product-info">
          <h3 class="product-name">{{ item.name }}</h3>
          <div class="product-meta">
            <span class="price">¥{{ item.price }}</span>
            <span class="sales">销量 {{ item.sales }}</span>
          </div>
          <div class="product-stats">
            <span class="stat-item" :class="item.profitRate >= 20 ? 'good' : 'normal'">
              利润率 {{ item.profitRate }}%
            </span>
            <span class="stat-item rating">
              <el-icon><Star /></el-icon>
              {{ item.rating }}
            </span>
          </div>
        </div>
        <div class="product-actions">
          <el-button type="primary" size="small" @click="handleCollect(item)">
            <el-icon><ShoppingCart /></el-icon>
            采集
          </el-button>
          <el-button type="success" size="small" @click="handleQuickList(item)">
            <el-icon><Upload /></el-icon>
            上货
          </el-button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <el-empty v-if="!loading && currentList.length === 0" description="暂无数据">
      <el-button type="primary" @click="loadData">刷新试试</el-button>
    </el-empty>

    <!-- 加载更多 -->
    <div class="load-more" v-if="currentList.length > 0">
      <el-button @click="loadMore" :loading="loadingMore">加载更多</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  TrendCharts, Money, Star, Promotion, Shop,
  ShoppingCart, Upload, Star as StarIcon, Lightning
} from '@element-plus/icons-vue'
import { fetchGoodsList } from '@/api/goods'
import request from '@/utils/request'

const activeTab = ref('hot')
const loading = ref(false)
const loadingMore = ref(false)
const products = ref([])
const currentPage = ref(1)
const pageSize = 12

// 五大榜单Tab
const tabs = [
  { id: 'hot', name: '热销榜', icon: 'Lightning', badge: null, sort: '-sales' },
  { id: 'rising', name: '飙升榜', icon: 'TrendCharts', badge: 'NEW', sort: '-growth_rate' },
  { id: 'profit', name: '高利润榜', icon: 'Money', badge: null, sort: '-profit_rate' },
  { id: 'platform', name: '平台扶持榜', icon: 'Promotion', badge: null, sort: '-platform_recommend' },
  { id: 'local', name: '辽宁产业带', icon: 'Shop', badge: 'LOCAL', sort: 'local' },
]

// 从后端 API 加载商品数据
async function loadData() {
  loading.value = true
  try {
    const tab = tabs.find(t => t.id === activeTab.value)
    const res = await fetchGoodsList({
      page: currentPage.value,
      page_size: pageSize,
      sort: tab?.sort || '-sales',
    })
    if (res && res.code === 200) {
      const list = res.data?.results || res.data || []
      products.value = list.map((item, index) => ({
        id: item.id || index + 1,
        name: item.title || item.product_name || item.name || '未知商品',
        platform: item.platform || 'TikTok',
        platformColor: getPlatformColor(item.platform),
        image: (item.images && item.images[0]) || `https://picsum.photos/200/200?random=${item.id || index}`,
        price: item.price || 0,
        sales: formatSales(item.sales_count || item.sales || 0),
        profitRate: item.profit_rate || item.profitRate || 0,
        rating: item.rating || (4 + Math.random()).toFixed(1),
        rank: item.rank || index + 1,
        growth: item.growth_rate ? `+${item.growth_rate}%` : null,
      }))
    } else {
      ElMessage.warning('暂无数据')
      products.value = []
    }
  } catch (err) {
    ElMessage.error('加载商品数据失败')
    products.value = []
  } finally {
    loading.value = false
  }
}

function getPlatformColor(platform) {
  const colors = {
    tiktok: '#FF0050',
    shein: '#000000',
    temu: '#FF6B35',
    shopee: '#FF8000',
    amazon: '#FF9900',
    '1688': '#FF6C00',
    lazada: '#F57224',
  }
  return colors[(platform || '').toLowerCase()] || '#409EFF'
}

function formatSales(count) {
  if (!count) return '0'
  if (count >= 10000) return `${(count / 10000).toFixed(1)}万+`
  if (count >= 1000) return `${(count / 1000).toFixed(1)}千+`
  return `${count}`
}

const currentList = computed(() => products.value)

// 拖拽相关
function onDragStart(e, item) {
  e.dataTransfer.setData('application/json', JSON.stringify({ type: 'goods', id: item.id, name: item.name }))
  e.dataTransfer.setData('text/plain', JSON.stringify({ type: 'goods', id: item.id, name: item.name }))
}

function onDragEnd() {
  // 拖拽结束
}

// 操作
function handleCollect(item) {
  ElMessage.success(`已将「${item.name}」加入采集待处理`)
}

function handleQuickList(item) {
  ElMessage.success(`已将「${item.name}」加入上货队列`)
}

async function loadMore() {
  loadingMore.value = true
  try {
    currentPage.value++
    await loadData()
  } finally {
    loadingMore.value = false
  }
}

// Tab 切换时重新加载
watch(activeTab, () => {
  currentPage.value = 1
  loadData()
})

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.hot-products-page {
  padding: 20px;
}

/* Tab切换 */
.rank-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.rank-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  background: var(--el-fill-color-light);
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.rank-tab:hover {
  background: var(--el-fill-color);
}

.rank-tab.active {
  background: var(--el-color-primary);
  color: #fff;
}

/* 商品网格 */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.product-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 12px;
  overflow: hidden;
  cursor: grab;
  transition: all 0.2s;
}

.product-card:hover {
  border-color: var(--el-color-primary-light-5);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.product-card:active {
  cursor: grabbing;
}

.product-image {
  position: relative;
  aspect-ratio: 1;
  background: var(--el-fill-color-light);
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.platform-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  color: #fff;
  font-weight: 600;
}

.rank-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

.product-info {
  padding: 12px;
}

.product-name {
  font-size: 14px;
  font-weight: 500;
  margin: 0 0 8px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.price {
  font-size: 16px;
  font-weight: 700;
  color: var(--el-color-danger);
}

.sales {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.product-stats {
  display: flex;
  gap: 8px;
}

.stat-item {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  background: var(--el-fill-color-light);
}

.stat-item.good {
  background: rgba(103, 194, 58, 0.1);
  color: #67C23A;
}

.stat-item.rating {
  display: flex;
  align-items: center;
  gap: 2px;
  color: #E6A23C;
}

.product-actions {
  display: flex;
  gap: 8px;
  padding: 0 12px 12px;
}

.product-actions .el-button {
  flex: 1;
}

/* 加载更多 */
.load-more {
  text-align: center;
  margin-top: 20px;
}
</style>
