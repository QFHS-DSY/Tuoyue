<template>
  <div class="page-container">
    <!-- 页面Header -->
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">店铺管理</h1>
        <p class="page-desc">管理各平台店铺授权 &amp; 账号绑定</p>
      </div>
      <div class="page-header-right">
        <el-button type="primary" @click="handleAddShop">
          <el-icon><Plus /></el-icon>
          添加授权
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-icon" style="background:#e8f5e9">
            <el-icon style="color:#67c23a"><Shop /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ activeCount }}</div>
            <div class="stat-label">已授权店铺</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-icon" style="background:#fff8e1">
            <el-icon style="color:#e6a23c"><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ pendingCount }}</div>
            <div class="stat-label">待验证</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-icon" style="background:#ffebee">
            <el-icon style="color:#f56c6c"><WarningFilled /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ expiredCount }}</div>
            <div class="stat-label">已过期</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-icon" style="background:#f3f4f6">
            <el-icon style="color:#9ca3af"><Goods /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ totalProducts }}</div>
            <div class="stat-label">绑定商品总数</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 店铺列表 -->
    <div class="list-card">
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column label="店铺名称" min-width="180">
          <template #default="{ row }">
            <div class="shop-name">
              <span class="platform-dot" :style="{ background: row.color }"></span>
              <span class="shop-title">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="平台" width="130" align="center">
          <template #default="{ row }">
            <div class="platform-cell">
              <img
                v-if="row.icon"
                :src="row.icon"
                class="platform-logo"
                :alt="row.platformName"
              />
              <span v-else class="platform-icon" :style="{ borderColor: row.color }">
                {{ row.icon }}
              </span>
              <span class="platform-name">{{ row.platformName }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="账号" width="140">
          <template #default="{ row }">
            <span class="account-id">{{ row.account }}</span>
          </template>
        </el-table-column>
        <el-table-column label="授权状态" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="row.statusType" size="small">{{ row.statusLabel }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="绑定时间" width="120" />
        <el-table-column label="绑定商品" width="100" align="center">
          <template #default="{ row }">
            <span class="product-count">{{ row.products }}</span>
          </template>
        </el-table-column>
        <el-table-column label="今日订单" width="100" align="center">
          <template #default="{ row }">
            <span class="order-count">{{ row.todayOrders }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <template v-if="row.status === 'active'">
              <el-button text size="small" @click="handleRefresh(row)">刷新授权</el-button>
              <el-button type="danger" text size="small" @click="handleUnbind(row)">解绑</el-button>
            </template>
            <template v-else-if="row.status === 'pending'">
              <el-button type="success" plain size="small" @click="handleVerify(row)">验证</el-button>
            </template>
            <template v-else-if="row.status === 'expired'">
              <el-button type="warning" plain size="small" @click="handleReauth(row)">重新授权</el-button>
            </template>
            <template v-else>
              <el-button type="primary" plain size="small" @click="handleAuth(row)">去授权</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 添加授权弹窗 -->
    <el-dialog v-model="addVisible" title="添加店铺授权" width="480px">
      <el-form :model="addForm" label-width="100px">
        <el-form-item label="选择平台">
          <el-select v-model="addForm.platform" placeholder="请选择平台" style="width:100%">
            <el-option v-for="p in platforms" :key="p.code" :label="p.name" :value="p.code">
              <span>{{ p.icon }} {{ p.name }}</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="店铺名称">
          <el-input v-model="addForm.name" placeholder="给店铺起个名字，方便识别" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addVisible = false">取消</el-button>
        <el-button type="primary" :loading="authLoading" @click="handleConfirmAuth">
          跳转授权
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getShopList, getAuthUrl, refreshAuth, unbindShop } from '@/api/shop'
import { PLATFORM_ICONS } from '@/utils/platformIcons'

const platforms = [
  { name: 'Shopee', code: 'shopee', icon: PLATFORM_ICONS.shopee.icon },
  { name: 'Temu', code: 'temu', icon: PLATFORM_ICONS.temu.icon },
  { name: 'SHEIN', code: 'shein', icon: PLATFORM_ICONS.shein.icon },
  { name: 'TikTok Shop', code: 'tiktok', icon: PLATFORM_ICONS.tiktok.icon },
  { name: 'Amazon', code: 'amazon', icon: PLATFORM_ICONS.amazon.icon },
  { name: 'eBay', code: 'ebay', icon: PLATFORM_ICONS.ebay.icon },
  { name: '速卖通', code: 'aliexpress', icon: PLATFORM_ICONS.aliexpress.icon },
  { name: 'Lazada', code: 'lazada', icon: PLATFORM_ICONS.lazada.icon },
  { name: 'Wish', code: 'wish', icon: PLATFORM_ICONS.wish.icon },
  { name: 'Mercado', code: 'mercado', icon: PLATFORM_ICONS.mercado.icon },
  { name: 'Ozon', code: 'ozon', icon: PLATFORM_ICONS.ozon.icon },
]

const loading = ref(false)
const authLoading = ref(false)
const tableData = ref([])
const addVisible = ref(false)
const addForm = reactive({ platform: '', name: '' })

const activeCount = computed(() => tableData.value.filter((r) => row.status === 'active').length)
const pendingCount = computed(() => tableData.value.filter((r) => row.status === 'pending').length)
const expiredCount = computed(() => tableData.value.filter((r) => row.status === 'expired').length)
const totalProducts = computed(() => tableData.value.reduce((sum, r) => sum + r.products, 0))

async function loadData() {
  loading.value = true
  try {
    const res = await getShopList()
    tableData.value = (res.data || []).map(shop => ({
      id: shop.id,
      name: shop.name,
      icon: shop.avatar || PLATFORM_ICONS[shop.platform]?.icon || '',
      platformName: shop.platform_label || shop.platform,
      platform: shop.platform,
      color: PLATFORM_ICONS[shop.platform]?.color || '#999',
      status: shop.status,
      statusType: shop.status === 'active' ? 'success' : shop.status === 'inactive' ? 'info' : 'warning',
      statusLabel: shop.status_label || shop.status,
      account: shop.account || shop.name,
      products: shop.orders_count || 0,
      todayOrders: shop.orders_count || 0,
      created_at: shop.created_at,
      last_sync: shop.last_sync,
    }))
  } finally {
    loading.value = false
  }
}

function handleAddShop() {
  addForm.platform = ''
  addForm.name = ''
  addVisible.value = true
}

async function handleConfirmAuth() {
  if (!addForm.platform) {
    ElMessage.warning('请先选择平台')
    return
  }
  authLoading.value = true
  try {
    const res = await getAuthUrl(addForm.platform)
    if (res.data.url) {
      window.open(res.data.url, '_blank')
      ElMessage.success('已在新窗口打开授权页面，请完成授权后刷新状态')
    } else {
      ElMessage.info('授权功能开发中，敬请期待')
    }
    addVisible.value = false
  } finally {
    authLoading.value = false
  }
}

async function handleRefresh(row) {
  await refreshAuth(row.id)
  ElMessage.success('授权已刷新')
}

async function handleUnbind(row) {
  await ElMessageBox.confirm(`确定要解绑「${row.name}」吗？解绑后该店铺数据将保留但无法同步。`, '确认解绑', { type: 'warning' })
  await unbindShop(row.id)
  ElMessage.success('解绑成功')
  loadData()
}

function handleVerify(row) {
  ElMessage.success('验证功能开发中')
}

function handleReauth(row) {
  handleConfirmAuth()
  addForm.platform = row.code
  addForm.name = row.name
  addVisible.value = true
}

function handleAuth(row) {
  addForm.platform = row.code
  addForm.name = row.name
  addVisible.value = true
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
}
.stat-info { flex: 1; }
.stat-value { font-size: 24px; font-weight: 700; color: var(--text-primary); }
.stat-label { font-size: 13px; color: var(--text-muted); margin-top: 2px; }

.list-card { background: var(--bg-card); border-radius: var(--r-lg); padding: 20px; box-shadow: var(--shadow-xs); }

.shop-name { display: flex; align-items: center; gap: 8px; }
.platform-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.shop-title { font-weight: 600; color: var(--text-primary); }

.platform-cell { display: flex; align-items: center; justify-content: center; gap: 6px; }
.platform-logo { width: 20px; height: 20px; object-fit: contain; flex-shrink: 0; }
.platform-icon { font-size: 16px; }
.platform-name { font-size: 12.5px; color: var(--text-secondary); }

.account-id { font-family: monospace; font-size: 13px; color: var(--brand); }
.product-count { font-weight: 600; color: var(--text-primary); }
.order-count { font-weight: 600; color: var(--success); }
</style>
