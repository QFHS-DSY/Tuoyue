<template>
  <div class="page-container">
    <!-- 页面Header -->
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">物流追踪</h1>
        <p class="page-desc">实时包裹轨迹 · 多物流商聚合</p>
      </div>
      <div class="page-header-right">
        <el-button type="primary" @click="handleSync">
          <el-icon><Refresh /></el-icon>
          同步物流
        </el-button>
      </div>
    </div>

    <!-- 物流统计卡片 -->
    <div class="logistics-stats">
      <div class="stat-card" @click="handleStatusFilter('pending')">
        <div class="stat-icon pending"><el-icon><Clock /></el-icon></div>
        <div class="stat-info">
          <div class="stat-num">{{ stats.pending }}</div>
          <div class="stat-label">待揽收</div>
        </div>
      </div>
      <div class="stat-card" @click="handleStatusFilter('transit')">
        <div class="stat-icon transit"><el-icon><Van /></el-icon></div>
        <div class="stat-info">
          <div class="stat-num">{{ stats.transit }}</div>
          <div class="stat-label">运输中</div>
        </div>
      </div>
      <div class="stat-card" @click="handleStatusFilter('delivering')">
        <div class="stat-icon delivering"><el-icon><Location /></el-icon></div>
        <div class="stat-info">
          <div class="stat-num">{{ stats.delivering }}</div>
          <div class="stat-label">派送中</div>
        </div>
      </div>
      <div class="stat-card" @click="handleStatusFilter('delivered')">
        <div class="stat-icon delivered"><el-icon><CircleCheck /></el-icon></div>
        <div class="stat-info">
          <div class="stat-num">{{ stats.delivered }}</div>
          <div class="stat-label">已签收</div>
        </div>
      </div>
      <div class="stat-card" @click="handleStatusFilter('exception')">
        <div class="stat-icon exception"><el-icon><WarningFilled /></el-icon></div>
        <div class="stat-info">
          <div class="stat-num">{{ stats.exception }}</div>
          <div class="stat-label">异常</div>
        </div>
      </div>
    </div>

    <!-- 筛选区 -->
    <div class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="关键词">
          <el-input v-model="filterForm.keyword" placeholder="运单号/订单号" clearable @keyup.enter="loadData" style="width:180px" />
        </el-form-item>
        <el-form-item label="物流商">
          <el-select v-model="filterForm.carrier" placeholder="全部" clearable style="width:140px">
            <el-option label="全部" value="" />
            <el-option label="顺丰速运" value="顺丰速运" />
            <el-option label="圆通速递" value="圆通速递" />
            <el-option label="中通快递" value="中通快递" />
            <el-option label="韵达快递" value="韵达快递" />
            <el-option label="DHL" value="DHL" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable style="width:140px">
            <el-option label="全部" value="" />
            <el-option label="待揽收" value="pending" />
            <el-option label="运输中" value="transit" />
            <el-option label="派送中" value="delivering" />
            <el-option label="已签收" value="delivered" />
            <el-option label="异常" value="exception" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 物流列表 -->
    <div class="list-card">
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column label="运单号" width="180">
          <template #default="{ row }">
            <span class="waybill-no">{{ row.waybillNo }}</span>
          </template>
        </el-table-column>
        <el-table-column label="关联订单" width="170">
          <template #default="{ row }">
            <span class="order-ref">{{ row.orderId }}</span>
          </template>
        </el-table-column>
        <el-table-column label="物流商" width="120" align="center">
          <template #default="{ row }">
            <div class="carrier-info">
              <span class="carrier-icon">{{ row.carrierIcon }}</span>
              <span class="carrier-name">{{ row.carrier }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="收件信息" min-width="200">
          <template #default="{ row }">
            <div class="ship-info">
              <div class="from-to">
                <span class="city-tag origin">{{ row.from }}</span>
                <el-icon class="arrow-icon"><Right /></el-icon>
                <span class="city-tag dest">{{ row.to }}</span>
              </div>
              <div v-if="row.currentLoc" class="current-loc">
                <el-icon><Location /></el-icon>
                {{ row.currentLoc }}
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="费用" width="80" align="right">
          <template #default="{ row }">
            <span class="fee">¥{{ row.fee }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110" align="center">
          <template #default="{ row }">
            <el-tooltip v-if="row.status === 'exception' && row.exceptionReason" :content="row.exceptionReason" placement="top" effect="dark">
              <el-tag :type="statusTagType(row.status)" size="small" effect="light" :class="{ 'exception-tag': row.status === 'exception' }">
                {{ statusLabelMap[row.status] || row.status }}
                <el-icon v-if="row.status === 'exception'" style="margin-left:2px;font-size:12px"><WarningFilled /></el-icon>
              </el-tag>
            </el-tooltip>
            <el-tag v-else :type="statusTagType(row.status)" size="small" effect="light" :class="{ 'exception-tag': row.status === 'exception' }">
              {{ statusLabelMap[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="更新时间" width="160">
          <template #default="{ row }">
            <span class="update-time">{{ row.lastUpdate }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleTrack(row)">追踪</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="pagination.page"
          :page-size="pagination.pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadData"
        />
      </div>
    </div>

    <!-- 物流轨迹抽屉（带地图和时间轴） -->
    <el-drawer v-model="drawerVisible" title="物流轨迹详情" size="680px" direction="rtl">
      <div v-if="currentShipment" class="track-content">
        <!-- 轨迹头部 -->
        <div class="track-header">
          <div class="track-main">
            <div class="track-waybill">
              <span class="waybill-label">运单号</span>
              <span class="waybill-no">{{ currentShipment.waybillNo }}</span>
            </div>
            <div class="track-meta">
              <el-tag :type="currentShipment.statusType" size="small">{{ currentShipment.statusLabel }}</el-tag>
              <span class="carrier-text">{{ currentShipment.carrierIcon }} {{ currentShipment.carrier }}</span>
            </div>
          </div>
          <div class="track-summary">
            <div class="summary-item">
              <span class="summary-label">寄件地</span>
              <span class="summary-value">{{ currentShipment.from }}</span>
            </div>
            <div class="summary-arrow">→</div>
            <div class="summary-item">
              <span class="summary-label">收件地</span>
              <span class="summary-value">{{ currentShipment.to }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">运费</span>
              <span class="summary-value amount">¥{{ currentShipment.fee }}</span>
            </div>
          </div>
        </div>

        <!-- 地图区域 -->
        <div class="track-map">
          <div ref="mapContainer" class="map-container"></div>
          <div v-if="currentShipment.status === 'exception'" class="map-alert">
            <el-icon><WarningFilled /></el-icon>
            物流异常：{{ currentShipment.exceptionReason }}
          </div>
        </div>

        <!-- 垂直时间轴 -->
        <div class="track-timeline-section">
          <h4>
            <el-icon><Clock /></el-icon>
            物流时间轴
          </h4>
          <el-timeline>
            <el-timeline-item
              v-for="(track, idx) in currentShipment.tracks"
              :key="idx"
              :timestamp="track.time"
              :type="track.nodeType"
              :color="track.nodeColor"
              :hollow="track.nodeType === 'info'"
              size="large"
            >
              <div class="timeline-content">
                <div class="timeline-status">{{ track.status }}</div>
                <div class="timeline-location">
                  <el-icon><Location /></el-icon>
                  {{ track.location }}
                </div>
                <div v-if="track.isTimeout" class="timeline-warning">
                  <el-icon><Warning /></el-icon>
                  超时未更新
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
      <div v-else class="track-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        加载物流轨迹中...
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Clock, Van, Location, CircleCheck, WarningFilled, Right, Warning, Loading } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getShipmentList, getLogisticsStats, getShipmentTrack, syncLogistics } from '@/api/logistics'

// 地图城市坐标
const cityCoords = {
  '深圳': [114.06, 22.54], '广州': [113.26, 23.13], '杭州': [120.19, 30.27],
  '洛杉矶': [-118.24, 34.05], '芝加哥': [-87.63, 41.88], '伦敦': [-0.13, 51.51],
  '旧金山': [-122.42, 37.77], '西雅图': [-122.33, 47.61], '吉隆坡': [101.69, 3.14],
  '雅加达': [106.85, -6.21], '香港': [114.17, 22.28],
}

// ==================== 状态 ====================
const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const drawerVisible = ref(false)
const currentShipment = ref(null)
const filterForm = reactive({ keyword: '', carrier: '', status: '' })
const pagination = reactive({ page: 1, pageSize: 10 })
const mapContainer = ref(null)
let mapChart = null

const stats = ref({ pending: 0, transit: 0, delivering: 0, delivered: 0, exception: 0 })

// 物流状态 → 中文标签映射（覆盖后端 pending/in_transit/delivered/exception）
const statusLabelMap = {
  pending: '待揽收',
  in_transit: '运输中',
  transit: '运输中',
  delivering: '派送中',
  delivered: '已签收',
  exception: '异常',
}

function statusTagType(status) {
  const map = {
    pending: 'info', in_transit: 'primary', transit: 'primary',
    delivering: 'warning', delivered: 'success', exception: 'danger',
  }
  return map[status] || 'info'
}

// ==================== 方法 ====================
async function loadStats() {
  try {
    const res = await getLogisticsStats()
    if (res.code === 200) {
      stats.value = res.data
    }
  } catch (e) {
    console.error('获取物流统计失败:', e)
  }
}

async function loadData() {
  loading.value = true
  try {
    // 前端状态名 → 后端 LogisticsShipment 模型状态常量映射
    const STATUS_TO_BACKEND = {
      pending: 'pending',
      transit: 'in_transit',
      delivering: 'in_transit',
      delivered: 'delivered',
      exception: 'exception',
    }
    const params = {
      page: pagination.page,
      pageSize: pagination.pageSize,
      keyword: filterForm.keyword,
      carrier: filterForm.carrier,
      status: STATUS_TO_BACKEND[filterForm.status] || filterForm.status
    }
    const res = await getShipmentList(params)
    if (res.code === 200) {
      tableData.value = (res.data?.results || []).map(item => ({
        waybillNo: item.tracking_no || item.waybill_no,
        orderId: item.order_no || item.order_id,
        carrier: item.carrier,
        carrierIcon: getCarrierIcon(item.carrier),
        from: item.origin,
        to: item.destination,
        currentLoc: item.current_location || '',
        fee: item.fee,
        status: item.status,
        statusLabel: item.status_label || item.status_text,
        statusType: getStatusType(item.status),
        lastUpdate: item.updated_at || item.last_update,
        exceptionReason: item.abnormal_reason || item.exception_reason || '',
        itemsCount: item.items_count,
        tracks: [] // 轨迹在详情中加载
      }))
      total.value = res.data.count ?? res.data.total ?? res.total ?? 0
    }
  } catch (e) {
    ElMessage.error('获取物流列表失败')
    console.error(e)
  } finally {
    loading.value = false
  }
}

function getCarrierIcon(carrier) {
  const icons = {
    '顺丰速运': '📦',
    '圆通速递': '📮',
    '中通快递': '📬',
    '韵达快递': '📭',
    'DHL': '✈️',
    '京东物流': '🏍️'
  }
  return icons[carrier] || '🚚'
}

function getStatusType(status) {
  const map = {
    'pending': 'info',
    'shipped': 'primary',
    'in_transit': 'primary',
    'transit': 'primary',
    'delivering': 'warning',
    'delivered': 'success',
    'exception': 'danger'
  }
  return map[status] || 'info'
}

function handleStatusFilter(status) {
  filterForm.status = filterForm.status === status ? '' : status
  pagination.page = 1
  loadData()
}

function resetFilter() {
  filterForm.keyword = ''
  filterForm.carrier = ''
  filterForm.status = ''
  pagination.page = 1
  loadData()
}

async function handleTrack(row) {
  currentShipment.value = null
  drawerVisible.value = true
  
  // 获取物流轨迹
  try {
    const res = await getShipmentTrack(row.waybillNo)
    if (res.code === 200) {
      currentShipment.value = {
        ...row,
        tracks: res.data.tracks.map(t => ({
          time: t.time,
          status: t.status,
          location: t.location,
          description: t.description,
          nodeType: getTrackNodeType(t.icon),
          nodeColor: getTrackNodeColor(t.icon),
          isTimeout: t.is_overdue
        }))
      }
    }
  } catch (e) {
    // 如果轨迹接口失败，直接显示列表数据
    currentShipment.value = row
  }
  
  nextTick(() => initMap())
}

function getTrackNodeType(icon) {
  const map = {
    'completed': 'success',
    'transit': 'primary',
    'delivering': 'warning',
    'exception': 'danger',
    'pending': 'info'
  }
  return map[icon] || 'info'
}

function getTrackNodeColor(icon) {
  const map = {
    'completed': '#22C55E',
    'transit': '#3B82F6',
    'delivering': '#F59E0B',
    'exception': '#EF4444',
    'pending': '#94A3B8'
  }
  return map[icon] || '#94A3B8'
}

function initMap() {
  if (!mapContainer.value) return
  if (mapChart) mapChart.dispose()
  
  mapChart = echarts.init(mapContainer.value)
  
  const shipment = currentShipment.value
  const fromCoord = cityCoords[shipment.from] || [113, 23]
  const toCoord = cityCoords[shipment.to] || [0, 0]
  
  // 获取当前节点坐标
  const currentLoc = shipment.currentLoc
  let currentCoord = toCoord
  if (currentLoc && cityCoords[currentLoc]) {
    currentCoord = cityCoords[currentLoc]
  }
  
  const option = {
    tooltip: { trigger: 'item', formatter: (p) => p.data.name || '' },
    geo: {
      map: 'world',
      roam: false,
      silent: true,
      itemStyle: { areaColor: '#E2E8F0', borderColor: '#CBD5E1', borderWidth: 0.5 },
      emphasis: { itemStyle: { areaColor: '#BFDBFE' } }
    },
    series: [
      {
        name: '物流轨迹',
        type: 'lines',
        coordinateSystem: 'geo',
        zlevel: 2,
        effect: { show: true, period: 4, trailLength: 0.4, symbol: 'circle', symbolSize: 6, color: '#3B82F6' },
        lineStyle: { color: '#3B82F6', width: 2, curveness: 0.3, opacity: 0.8 },
        data: [{ coords: [fromCoord, toCoord], name: `${shipment.from} → ${shipment.to}` }]
      },
      {
        name: '起点',
        type: 'scatter',
        coordinateSystem: 'geo',
        zlevel: 3,
        symbol: 'circle',
        symbolSize: 12,
        itemStyle: { color: '#22C55E', shadowBlur: 10, shadowColor: 'rgba(34,197,94,0.5)' },
        data: [{ name: shipment.from, value: [...fromCoord, 1] }]
      },
      {
        name: '终点',
        type: 'scatter',
        coordinateSystem: 'geo',
        zlevel: 3,
        symbol: 'circle',
        symbolSize: 12,
        itemStyle: { color: shipment.status === 'exception' ? '#EF4444' : shipment.status === 'delivered' ? '#22C55E' : '#F59E0B', shadowBlur: 10, shadowColor: shipment.status === 'exception' ? 'rgba(239,68,68,0.5)' : 'rgba(245,158,11,0.5)' },
        data: [{ name: shipment.to, value: [...toCoord, 1] }]
      },
      {
        name: '当前位置',
        type: 'effectScatter',
        coordinateSystem: 'geo',
        zlevel: 4,
        symbol: 'circle',
        symbolSize: 10,
        rippleEffect: { brushType: 'stroke', scale: 3 },
        itemStyle: { color: shipment.status === 'exception' ? '#EF4444' : '#F59E0B' },
        data: shipment.status !== 'pending' ? [{ name: currentLoc || shipment.to, value: [...currentCoord, 1] }] : []
      }
    ]
  }
  
  mapChart.setOption(option)
}

async function handleSync() {
  try {
    const res = await syncLogistics()
    if (res.code === 200) {
      ElMessage.success('物流信息同步完成')
      loadStats()
      loadData()
    }
  } catch (e) {
    ElMessage.error('同步失败')
  }
}

onMounted(() => {
  loadStats()
  loadData()
})
</script>

<style scoped>
/* 统计卡片 */
.logistics-stats {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}
.stat-card {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: var(--shadow-xs);
  cursor: pointer;
  transition: all 0.2s;
}
.stat-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-sm); }
.stat-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}
.stat-icon.pending { background: #EFF6FF; color: #3B82F6; }
.stat-icon.transit { background: #FEF3C7; color: #D97706; }
.stat-icon.delivering { background: #DBEAFE; color: #2563EB; }
.stat-icon.delivered { background: #F0FDF4; color: #16A34A; }
.stat-icon.exception { background: #FEF2F2; color: #DC2626; }
.stat-num { font-size: 24px; font-weight: 700; color: var(--text-primary); line-height: 1; }
.stat-label { font-size: 12px; color: var(--text-muted); margin-top: 2px; }

/* 筛选区 */
.filter-card {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 16px;
  box-shadow: var(--shadow-xs);
}

/* 列表卡片 */
.list-card {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--shadow-xs);
}
.waybill-no { font-family: monospace; font-size: 13px; color: var(--brand); font-weight: 600; }
.order-ref { color: var(--text-muted); font-size: 12px; font-family: monospace; }
.carrier-info { display: flex; align-items: center; gap: 6px; }
.carrier-icon { font-size: 16px; }
.carrier-name { font-size: 12px; color: var(--text-secondary); }
.ship-info { display: flex; flex-direction: column; gap: 4px; }
.from-to { display: flex; align-items: center; gap: 6px; }
.city-tag { font-size: 12px; padding: 2px 8px; border-radius: 4px; font-weight: 500; }
.city-tag.origin { background: #EFF6FF; color: #3B82F6; }
.city-tag.dest { background: #F0FDF4; color: #16A34A; }
.arrow-icon { font-size: 12px; color: var(--text-muted); }
.current-loc { font-size: 11px; color: var(--brand); display: flex; align-items: center; gap: 2px; }
.fee { color: var(--text-muted); }
.update-time { font-size: 12px; color: var(--text-muted); }
.exception-tag { background: #FEF2F2 !important; color: #DC2626 !important; }
.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 16px; }

/* 轨迹抽屉 */
.track-content { display: flex; flex-direction: column; gap: 20px; }
.track-header { background: var(--bg-page); border-radius: 12px; padding: 16px; }
.track-main { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.waybill-label { font-size: 11px; color: var(--text-muted); display: block; }
.waybill-no { font-family: monospace; font-size: 18px; font-weight: 700; color: var(--brand); }
.track-meta { display: flex; flex-direction: column; gap: 6px; align-items: flex-end; }
.carrier-text { font-size: 12px; color: var(--text-muted); }
.track-summary { display: flex; align-items: center; gap: 12px; padding: 12px; background: #fff; border-radius: 8px; }
.summary-item { display: flex; flex-direction: column; gap: 2px; }
.summary-label { font-size: 11px; color: var(--text-muted); }
.summary-value { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.summary-value.amount { color: var(--danger); }
.summary-arrow { color: var(--text-muted); font-size: 18px; }

/* 地图 */
.track-map { border-radius: 12px; overflow: hidden; position: relative; }
.map-container { height: 220px; background: #F8FAFC; border-radius: 12px; }
.map-alert {
  position: absolute;
  bottom: 12px;
  left: 12px;
  background: #FEF2F2;
  color: #DC2626;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}

/* 时间轴 */
.track-timeline-section h4 {
  font-size: 14px;
  color: var(--text-primary);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.timeline-content { display: flex; flex-direction: column; gap: 2px; }
.timeline-status { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.timeline-location { font-size: 12px; color: var(--text-muted); display: flex; align-items: center; gap: 4px; }
.timeline-warning { font-size: 11px; color: #DC2626; display: flex; align-items: center; gap: 4px; margin-top: 2px; }
.track-loading { text-align: center; color: var(--text-muted); padding: 60px; display: flex; flex-direction: column; align-items: center; gap: 12px; font-size: 14px; }
</style>
