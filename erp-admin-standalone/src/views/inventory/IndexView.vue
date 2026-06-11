<template>
  <div class="page-container">
    <!-- 页面Header -->
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">库存管理</h1>
        <p class="page-desc">动态预警与多仓协同 · 安全库存保障</p>
      </div>
      <div class="page-header-right">
        <el-button type="primary" icon="Plus" @click="handleAdd">
          新增商品
        </el-button>
        <el-button type="warning" @click="tabActive = 'alert'">
          <el-icon><Bell /></el-icon>
          预警 ({{ alertCount }})
        </el-button>
        <el-button type="primary" @click="drawerLog = true">
          <el-icon><Clock /></el-icon>
          出入库记录
        </el-button>
      </div>
    </div>

    <!-- 预警提示 -->
    <el-alert
      v-if="alertCount > 0"
      :title="`当前有 ${alertCount} 个商品库存不足，其中 ${outOfStockCount } 个已断货`"
      type="warning"
      :closable="false"
      style="margin-bottom:16px;border-radius:10px"
    >
      <template #default>
        <el-button type="warning" text size="small" @click="tabActive = 'alert'" style="margin-left:12px">
          查看预警 →
        </el-button>
      </template>
    </el-alert>

    <!-- 库存概览卡片（点击可快捷筛选） -->
    <div class="overview-cards">
      <div class="overview-card" :class="{ 'is-active': activeStatFilter === 'all' }" @click="handleStatFilter('all')">
        <div class="overview-icon blue"><el-icon><Box /></el-icon></div>
        <div class="overview-info">
          <div class="overview-num">{{ overview.totalSku }}</div>
          <div class="overview-label">商品种类</div>
        </div>
      </div>
      <div class="overview-card" :class="{ 'is-active': activeStatFilter === 'all' }" @click="handleStatFilter('all')">
        <div class="overview-icon green"><el-icon><TrendCharts /></el-icon></div>
        <div class="overview-info">
          <div class="overview-num">{{ formatNumber(overview.totalStock) }}</div>
          <div class="overview-label">总库存量</div>
        </div>
      </div>
      <div class="overview-card" :class="{ 'is-active': activeStatFilter === 'low' }" @click="handleStatFilter('low')">
        <div class="overview-icon orange"><el-icon><Warning /></el-icon></div>
        <div class="overview-info">
          <div class="overview-num">{{ alertCount }}</div>
          <div class="overview-label">预警商品</div>
        </div>
      </div>
      <div class="overview-card" :class="{ 'is-active': activeStatFilter === 'out' }" @click="handleStatFilter('out')">
        <div class="overview-icon red"><el-icon><Remove /></el-icon></div>
        <div class="overview-info">
          <div class="overview-num">{{ outOfStockCount }}</div>
          <div class="overview-label">已断货</div>
        </div>
      </div>
    </div>

    <!-- 多仓视图切换 -->
    <div class="warehouse-tabs">
      <el-tabs v-model="currentWarehouse" @tab-change="handleTabChange">
        <el-tab-pane label="全部仓库" name="all" />
        <el-tab-pane label="深圳仓" name="深圳仓">
          <template #label>
            <span class="warehouse-tab-label">
              <span>📍</span> 深圳仓
              <el-badge :value="getWarehouseAlert('深圳仓')" :hidden="getWarehouseAlert('深圳仓') === 0" type="warning" />
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="广州仓" name="广州仓">
          <template #label>
            <span class="warehouse-tab-label">
              <span>📍</span> 广州仓
              <el-badge :value="getWarehouseAlert('广州仓')" :hidden="getWarehouseAlert('广州仓') === 0" type="warning" />
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="海外仓(英国)" name="海外仓(英国)">
          <template #label>
            <span class="warehouse-tab-label">
              <span>🌍</span> 海外仓(英国)
              <el-badge :value="getWarehouseAlert('海外仓(英国)')" :hidden="getWarehouseAlert('海外仓(英国)') === 0" type="warning" />
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="在途库存" name="在途">
          <template #label>
            <span class="warehouse-tab-label">
              <span>🚚</span> 在途库存
            </span>
          </template>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 筛选区 -->
    <div class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="关键词">
          <el-input v-model="filterForm.keyword" placeholder="商品名称/SKU" clearable @keyup.enter="loadData" style="width:180px" />
        </el-form-item>
        <el-form-item label="仓库" v-if="currentWarehouse === 'all'">
          <el-select v-model="filterForm.warehouse" placeholder="全部仓库" clearable style="width:140px">
            <el-option v-for="w in warehouses" :key="w" :label="w" :value="w" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable style="width:120px">
            <el-option label="全部" value="" />
            <el-option label="正常" value="normal" />
            <el-option label="预警" value="low" />
            <el-option label="缺货" value="out" />
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

    <!-- 库存列表 -->
    <div v-if="tabActive === 'list'" class="list-card">
      <el-table :data="tableData" v-loading="loading" stripe :row-class-name="getRowClassName">
        <el-table-column label="SKU编号" width="150">
          <template #default="{ row }">
            <span class="sku-id">{{ row.skuId }}</span>
          </template>
        </el-table-column>
        <el-table-column label="商品名称" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="goods-name">
              <span>{{ row.name }}</span>
              <span v-if="row.alarmDays > 0" class="alarm-badge">
                预计 {{ row.alarmDays }} 天售完
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="仓库" width="140" align="center">
          <template #default="{ row }">
            <span class="warehouse-tag" :class="row.warehouseClass">{{ row.warehouse }}</span>
          </template>
        </el-table-column>
        <el-table-column label="当前库存" width="100" align="center">
          <template #default="{ row }">
            <span class="stock-num" :class="row.status">{{ row.stock }}</span>
          </template>
        </el-table-column>
        <el-table-column label="可用/锁定" width="100" align="center">
          <template #default="{ row }">
            <span>{{ row.available }} / {{ row.locked }}</span>
          </template>
        </el-table-column>
        <el-table-column label="安全库存" width="90" align="center">
          <template #default="{ row }">
            <span style="color: var(--text-muted)">{{ row.safeStock }}</span>
          </template>
        </el-table-column>
        <el-table-column label="库存预警" width="120" align="center">
          <template #default="{ row }">
            <el-progress
              :percentage="getStockPercent(row)"
              :color="getProgressColor(row)"
              :stroke-width="6"
              :show-text="false"
              style="width:80px;display:inline-block"
            />
            <span style="margin-left:8px;font-size:12px" :style="{ color: getProgressColor(row) }">
              {{ getStockPercent(row) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.statusType" size="small" effect="light">{{ row.statusLabel }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最近入库" width="110">
          <template #default="{ row }">
            <span class="date-cell">{{ row.lastIn }}</span>
          </template>
        </el-table-column>
        <el-table-column label="最近出库" width="110">
          <template #default="{ row }">
            <span class="date-cell">{{ row.lastOut }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="190" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleView(row)">查看</el-button>
            <el-button type="warning" text size="small" @click="handleAdjust(row)">调整</el-button>
            <el-button type="danger" text size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </div>

    <!-- 预警列表 -->
    <div v-if="tabActive === 'alert'" class="list-card">
      <div style="margin-bottom:16px;display:flex;align-items:center;gap:8px">
        <el-icon color="#f59e0b"><Bell /></el-icon>
        <span style="font-weight:600;color:#92400e">库存预警商品（{{ alertData.length }}）</span>
        <span style="color:#92400e;font-size:13px">以下商品库存低于安全库存，请及时补货</span>
      </div>
      <el-table :data="alertData" stripe :row-class-name="getRowClassName">
        <el-table-column label="SKU编号" width="150">
          <template #default="{ row }"><span class="sku-id">{{ row.skuId }}</span></template>
        </el-table-column>
        <el-table-column label="商品名称" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span>{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="仓库" width="140" align="center">
          <template #default="{ row }">
            <span class="warehouse-tag" :class="row.warehouseClass">{{ row.warehouse }}</span>
          </template>
        </el-table-column>
        <el-table-column label="当前库存" width="90" align="center">
          <template #default="{ row }">
            <span class="stock-num" :class="row.status">{{ row.stock }}</span>
          </template>
        </el-table-column>
        <el-table-column label="安全库存" width="90" align="center">
          <template #default="{ row }">
            <span style="color:var(--text-muted)">{{ row.safeStock }}</span>
          </template>
        </el-table-column>
        <el-table-column label="差额" width="90" align="center">
          <template #default="{ row }">
            <span style="color:#dc2626;font-weight:600">差 {{ Math.max(row.safeStock - row.stock, 0) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.statusType" size="small" effect="light">{{ row.statusLabel }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="center">
          <template #default="{ row }">
            <el-button type="warning" text size="small" @click="handleAlertAdjust(row)">补货</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="alertData.length === 0" description="暂无预警，库存状态良好 ✅" />
    </div>

    <!-- SKU详情弹窗 -->
    <el-dialog v-model="detailVisible" title="商品详情" width="700px">
      <div v-if="detailItem" class="sku-detail">
        <div class="detail-header">
          <div class="detail-title">
            <span class="sku-code">{{ detailItem.skuId }}</span>
            <h3>{{ detailItem.name }}</h3>
          </div>
          <el-tag :type="detailItem.statusType">{{ detailItem.statusLabel }}</el-tag>
        </div>
        <el-divider />
        <div class="detail-stats">
          <div class="stat-box">
            <span class="stat-label">当前库存</span>
            <span class="stat-value" :style="{ color: getProgressColor(detailItem) }">{{ detailItem.stock }}</span>
          </div>
          <div class="stat-box">
            <span class="stat-label">安全库存</span>
            <span class="stat-value">{{ detailItem.safeStock }}</span>
          </div>
          <div class="stat-box">
            <span class="stat-label">可用库存</span>
            <span class="stat-value">{{ detailItem.available }}</span>
          </div>
          <div class="stat-box">
            <span class="stat-label">锁定库存</span>
            <span class="stat-value">{{ detailItem.locked }}</span>
          </div>
        </div>
        <el-divider content-position="left">库存消耗趋势（近7天）</el-divider>
        <div ref="chartRef" style="height:200px"></div>
      </div>
    </el-dialog>

    <!-- 出入库记录抽屉 -->
    <el-drawer v-model="drawerLog" title="出入库记录" size="560px" direction="rtl" @open="loadLogs">
      <el-table :data="logData" size="small" max-height="600" v-loading="logLoading" stripe>
        <el-table-column label="类型" width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="row.type === 'in' ? 'success' : 'warning'" size="small">
              {{ row.type === 'in' ? '入库' : '出库' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="SKU" width="120">
          <template #default="{ row }">
            <span style="font-size:12px;color:var(--brand);font-family:monospace">{{ row.skuId }}</span>
          </template>
        </el-table-column>
        <el-table-column label="数量" width="70" align="center">
          <template #default="{ row }">
            <span :style="{ color: row.type === 'in' ? 'var(--success)' : 'var(--warning)', fontWeight: 600 }">
              {{ row.type === 'in' ? '+' : '-' }}{{ row.quantity }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作人" width="80">
          <template #default="{ row }">
            <span>{{ row.operator }}</span>
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="100" show-overflow-tooltip>
          <template #default="{ row }">
            <span style="font-size:12px;color:var(--text-muted)">{{ row.remark || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="时间" width="150">
          <template #default="{ row }">
            <span style="font-size:12px;color:var(--text-muted)">{{ row.date }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-drawer>

    <!-- 库存调整弹窗 -->
    <el-dialog v-model="adjustVisible" title="库存调整" width="420px">
      <el-form v-if="adjustItem" label-width="90px">
        <el-form-item label="商品">{{ adjustItem.name }}</el-form-item>
        <el-form-item label="SKU">
          <span style="font-family:monospace;color:var(--brand)">{{ adjustItem.skuId }}</span>
        </el-form-item>
        <el-form-item label="当前库存">{{ adjustItem.stock }}</el-form-item>
        <el-form-item label="调整类型">
          <el-radio-group v-model="adjustForm.type">
            <el-radio value="in">入库</el-radio>
            <el-radio value="out">出库</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="调整数量">
          <el-input-number v-model="adjustForm.quantity" :min="1" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="adjustForm.remark" placeholder="可选，如：补货/销售出库" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="adjustVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAdjust">确认调整</el-button>
      </template>
    </el-dialog>

    <!-- 新增商品弹窗（嵌入 AddProductForm 组件） -->
    <el-dialog v-model="addDialogVisible" title="新增商品建档" width="520px" destroy-on-close @close="addFormRefComp?.reset()">
      <AddProductForm ref="addFormRefComp" @success="onAddSuccess" />
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="addFormRefComp?.submitting" @click="addFormRefComp?.submit()">确定保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AddProductForm from '@/components/AddProductForm.vue'
import { Bell, Clock, Box, Search, Warning, Remove, TrendCharts } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getInventoryList, getInventoryOverview, getSkuDetail, adjustInventory, getInventoryLogs, addProduct, deleteProduct } from '@/api/inventory'

const warehouses = ['深圳仓', '广州仓', '海外仓(英国)']

// ==================== 状态 ====================
const loading = ref(false)
const logLoading = ref(false)
const tableData = ref([])
const total = ref(0)
const tabActive = ref('list')
const currentWarehouse = ref('all')
const alertCount = ref(0)
const outOfStockCount = ref(0)
const alertData = ref([])
const overview = ref({ totalSku: 0, totalStock: 0 })

const drawerLog = ref(false)
const logData = ref([])

const filterForm = reactive({ keyword: '', warehouse: '', status: '' })
const activeStatFilter = ref('')
const pagination = reactive({ page: 1, pageSize: 10 })

const adjustVisible = ref(false)
const adjustItem = ref(null)
const adjustForm = reactive({ type: 'in', quantity: 1, remark: '' })

const detailVisible = ref(false)

// 新增商品弹窗
const addDialogVisible = ref(false)
const addFormRef = ref(null)
const addForm = reactive({ name: '', sku: '', warehouse: '', stock: 0, safeStock: 0 })
const addRules = {
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  sku: [{ required: true, message: '请输入SKU编号', trigger: 'blur' }],
  warehouse: [{ required: true, message: '请选择仓库', trigger: 'change' }],
  stock: [{ required: true, trigger: 'blur', validator: (r, v, cb) => (v > 0 ? cb() : cb(new Error('库存必须大于 0'))) }],
  safeStock: [{ required: true, trigger: 'blur', validator: (r, v, cb) => (v > 0 ? cb() : cb(new Error('安全库存必须大于 0'))) }],
}
const addLoading = ref(false)
const detailItem = ref(null)
const chartRef = ref(null)
let chartInstance = null

// SKU详情数据
const skuDetail = ref(null)

// ==================== 方法 ====================
function getWarehouseAlert(warehouse) {
  return tableData.value.filter(i => i.warehouse === warehouse && i.status !== 'normal').length
}

function getRowClassName({ row }) {
  if (row.status === 'out') return 'row-out-of-stock'
  if (row.status === 'low') return 'row-low-stock'
  return ''
}

function getStockPercent(row) {
  if (!row.stock || !row.safeStock) return 0
  if (row.safeStock === 0) return 100
  return Math.min(Math.round((row.stock / row.safeStock) * 100), 100)
}

function getProgressColor(row) {
  if (row.status === 'out') return '#EF4444'
  if (row.status === 'low') return '#F59E0B'
  return '#22C55E'
}

function formatNumber(num) {
  return num?.toLocaleString() || '0'
}

// 仓库标签切换（防御性清洗：只剔除末尾可能混入的数字 badge）
function handleTabChange() {
  // 确保 currentWarehouse 不含多余字符（el-tabs v-model 读 name 属性，本应干净）
  const raw = currentWarehouse.value
  const clean = raw.replace(/\s?\d+$/, '').trim()
  if (clean !== raw) {
    console.warn('原始标签:', raw, ' -> 清洗后发送给后端的参数:', clean)
    currentWarehouse.value = clean === '全部仓库' ? '' : clean
  }
  loadData()
  loadOverview()
}

// 加载概览数据
async function loadOverview() {
  try {
    const warehouse = currentWarehouse.value === 'all' ? '' : currentWarehouse.value
    const res = await getInventoryOverview(warehouse)
    if (res.code === 200) {
      overview.value = {
        totalSku: res.data.total_sku,
        totalStock: res.data.total_stock
      }
      alertCount.value = res.data.alert_count
      outOfStockCount.value = res.data.out_of_stock_count
    }
  } catch (e) {
    console.error('获取库存概览失败:', e)
  }
}

async function loadData() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      pageSize: pagination.pageSize,
      warehouse: currentWarehouse.value === 'all' ? '' : currentWarehouse.value,
      keyword: filterForm.keyword,
      status: filterForm.status
    }
    console.log('🚀 发送给后端的仓库筛选参数是:', JSON.stringify(params.warehouse))
    const res = await getInventoryList(params)
    if (res.code === 200) {
      const rawList = res.data?.results || res.data?.items || res.data || []
      tableData.value = rawList.map(item => ({
        id: item.id,
        skuId: item.skuId || item.sku || item.platform_product_id,
        name: item.name,
        warehouse: item.warehouse,
        warehouseClass: getWarehouseClass(item.warehouse),
        stock: item.stock,
        available: item.available,
        locked: item.locked || 0,
        safeStock: item.safety_stock,
        status: item.status,
        statusType: item.status === 'out' ? 'danger' : item.status === 'low' ? 'warning' : 'success',
        statusLabel: item.status === 'out' ? '缺货' : item.status === 'low' ? '预警' : '正常',
        lastIn: item.last_in,
        lastOut: item.last_out,
        alarmDays: item.predicted_days,
        consumeRate: item.daily_sales
      }))
      total.value = res.data.count ?? res.data.total ?? 0
      
      // 更新预警数据
      alertData.value = tableData.value.filter(r => row.status !== 'normal')
    }
  } catch (e) {
    ElMessage.error('获取库存列表失败')
    console.error(e)
  } finally {
    loading.value = false
  }
}

function getWarehouseClass(warehouse) {
  if (!warehouse) return ''
  // 兼容"深圳仓 (本地仓)"格式
  if (warehouse.includes('深圳')) return 'sz'
  if (warehouse.includes('广州')) return 'gz'
  if (warehouse.includes('英国') || warehouse.includes('海外')) return 'uk'
  return ''
}
function getWarehouseTypeLabel(warehouse) {
  // 从"深圳仓 (本地仓)"中提取类型标签
  const m = warehouse && warehouse.match(/\((.+?)\)/)
  return m ? m[1] : ''
}

function handleStatFilter(status) {
  if (status === 'all') {
    filterForm.status = ''
    activeStatFilter.value = 'all'
  } else if (activeStatFilter.value === status) {
    filterForm.status = ''
    activeStatFilter.value = ''
  } else {
    filterForm.status = status
    activeStatFilter.value = status
  }
  pagination.page = 1
  loadData()
}

function resetFilter() {
  filterForm.keyword = ''
  filterForm.warehouse = ''
  filterForm.status = ''
  activeStatFilter.value = ''
  pagination.page = 1
  loadData()
}

async function handleView(row) {
  detailItem.value = row
  detailVisible.value = true
  
  // 获取SKU详情（含消耗趋势）
  try {
    const res = await getSkuDetail(row.skuId)
    if (res.code === 200) {
      skuDetail.value = res.data
    }
  } catch (e) {
    console.error('获取SKU详情失败:', e)
  }
  
  nextTick(() => {
    if (chartInstance) chartInstance.dispose()
    if (chartRef.value) {
      chartInstance = echarts.init(chartRef.value)
      
      // 如果有后端数据，用后端数据；否则用模拟数据
      const trendData = skuDetail.value?.consumption_trend || []
      const days = trendData.length > 0 
        ? trendData.map(d => d.date.slice(5)) // 取 MM-DD
        : ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      const stockData = trendData.length > 0
        ? trendData.map(d => d.stock)
        : (() => {
            const baseStock = row.stock + (row.consumeRate || 5) * 7
            return Array.from({length: 7}, (_, idx) => Math.max(0, baseStock - (row.consumeRate || 5) * (7 - idx)))
          })()
      
      chartInstance.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: 50, right: 20, top: 10, bottom: 30 },
        xAxis: { type: 'category', data: days, axisLine: { lineStyle: { color: '#E2E8F0' } }, axisLabel: { color: '#64748B', fontSize: 11 } },
        yAxis: { type: 'value', axisLine: { show: false }, splitLine: { lineStyle: { color: '#F1F5F9' } }, axisLabel: { color: '#64748B', fontSize: 11 } },
        series: [{
          name: '库存量',
          type: 'line',
          smooth: true,
          data: stockData,
          lineStyle: { color: row.status === 'normal' ? '#22C55E' : row.status === 'low' ? '#F59E0B' : '#EF4444', width: 3 },
          areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: row.status === 'normal' ? 'rgba(34,197,94,0.2)' : row.status === 'low' ? 'rgba(245,158,11,0.2)' : 'rgba(239,68,68,0.2)' },
            { offset: 1, color: 'rgba(255,255,255,0)' }
          ]) },
          symbol: 'circle',
          symbolSize: 6,
          itemStyle: { color: row.status === 'normal' ? '#22C55E' : row.status === 'low' ? '#F59E0B' : '#EF4444' }
        }]
      })
    }
  })
}

function handleAdjust(row) {
  adjustItem.value = row
  adjustForm.type = 'in'
  adjustForm.quantity = 1
  adjustForm.remark = ''
  adjustVisible.value = true
}

async function confirmAdjust() {
  const targetSku = adjustItem.value?.skuId || adjustItem.value?.sku || ''
  if (!targetSku) {
    ElMessage.warning('请先选择有效的商品')
    return
  }
  try {
    const res = await adjustInventory({
      sku: targetSku,
      warehouse_code: adjustItem.value.warehouse,
      adjustment_type: adjustForm.type === 'in' ? 'increase' : 'decrease',
      quantity: adjustForm.quantity,
      reason: adjustForm.remark || '库存调整',
    })
    if (res.code === 200) {
      ElMessage.success(`库存调整成功：${adjustForm.type === 'in' ? '入库' : '出库'} ${adjustForm.quantity} 件`)
      adjustVisible.value = false
      loadData()
      loadOverview()
    }
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || '库存调整失败')
  }
}

// 删除商品
async function handleDelete(row) {
  if (!row?.id) return
  try {
    await ElMessageBox.confirm('确定要删除该商品吗？此操作不可恢复', '删除确认', {
      confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning',
    })
    await deleteProduct(row.id)
    ElMessage.success('商品已删除')
    loadData()
    loadOverview()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.message || '删除失败')
  }
}

async function loadLogs() {
  logLoading.value = true
  try {
    const res = await getInventoryLogs({ page: 1, pageSize: 50 })
    if (res.code === 200) {
      logData.value = (res.data?.results || []).map(log => ({
        type: log.type,
        skuId: log.sku,
        quantity: log.quantity,
        operator: log.operator,
        remark: log.remark,
        date: log.created_at
      }))
    }
  } catch (e) {
    ElMessage.error('获取出入库记录失败')
  } finally {
    logLoading.value = false
  }
}

function handleAlertAdjust(row) {
  adjustItem.value = row
  adjustForm.type = 'in'
  adjustForm.quantity = Math.max(row.safeStock - row.stock, 1)
  adjustForm.remark = '预警补货'
  adjustVisible.value = true
}

const addFormRefComp = ref(null)

function handleAdd() {
  addDialogVisible.value = true
}

function onAddSuccess() {
  addDialogVisible.value = false
  loadData()
  loadOverview()
}

onMounted(() => {
  loadOverview()
  loadData()
})
</script>

<style scoped>
/* 概览卡片 */
.overview-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}
.overview-card {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--shadow-xs);
  cursor: pointer;
  transition: all 0.25s ease;
  border: 2px solid transparent;
}
.overview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.08);
  border-color: var(--border-hover, #d9d9d9);
}
.overview-card.is-active {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64,158,255,0.2);
}
.overview-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}
.overview-icon.blue { background: #EFF6FF; color: #3B82F6; }
.overview-icon.green { background: #F0FDF4; color: #22C55E; }
.overview-icon.orange { background: #FFF7ED; color: #F59E0B; }
.overview-icon.red { background: #FEF2F2; color: #EF4444; }
.overview-num { font-size: 26px; font-weight: 700; color: var(--text-primary); line-height: 1; }
.overview-label { font-size: 13px; color: var(--text-muted); margin-top: 4px; }

/* 多仓Tab */
.warehouse-tabs {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 0 20px;
  margin-bottom: 16px;
  box-shadow: var(--shadow-xs);
}
.warehouse-tab-label { display: flex; align-items: center; gap: 6px; }

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
.sku-id { font-family: monospace; font-size: 13px; color: var(--brand); font-weight: 600; }
.goods-name { display: flex; flex-direction: column; gap: 4px; }
.alarm-badge {
  font-size: 11px;
  color: #F59E0B;
  background: #FFF7ED;
  padding: 2px 6px;
  border-radius: 4px;
  width: fit-content;
}
.warehouse-tag {
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 4px;
  font-weight: 500;
}
.warehouse-tag.sz { background: #EFF6FF; color: #3B82F6; }
.warehouse-tag.gz { background: #F0FDF4; color: #22C55E; }
.warehouse-tag.uk { background: #FDF4FF; color: #A855F7; }
.stock-num { font-weight: 700; font-size: 15px; }
.stock-num.normal { color: var(--success); }
.stock-num.low { color: var(--warning); }
.stock-num.out { color: var(--danger); }
.date-cell { font-size: 12px; color: var(--text-muted); }
.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 16px; }

/* 预警行高亮 */
:deep(.row-low-stock) { background: #FFFBEB !important; }
:deep(.row-out-of-stock) { background: #FEF2F2 !important; }

/* SKU详情 */
.sku-detail { padding: 0 8px; }
.detail-header { display: flex; justify-content: space-between; align-items: flex-start; }
.sku-code { font-family: monospace; font-size: 12px; color: var(--brand); }
.detail-title h3 { margin: 4px 0 0; font-size: 18px; color: var(--text-primary); }
.detail-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px; }
.stat-box { display: flex; flex-direction: column; gap: 4px; text-align: center; padding: 16px; background: var(--bg-page); border-radius: 10px; }
.stat-label { font-size: 12px; color: var(--text-muted); }
.stat-value { font-size: 22px; font-weight: 700; color: var(--text-primary); }
</style>
