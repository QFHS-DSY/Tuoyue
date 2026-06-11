<template>
  <div class="page">
    <!-- 页面Header -->
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">商品管理</h1>
        <p class="page-desc">管理已采集的商品，支持批量上下架、导入导出</p>
      </div>
      <div class="page-header-right">
        <el-button @click="handleExport">
          <el-icon><Upload /></el-icon>
          导出
        </el-button>
        <el-button @click="handleImport">
          <el-icon><Download /></el-icon>
          导入
        </el-button>
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新增商品
        </el-button>
      </div>
    </div>

    <!-- 搜索筛选 -->
    <el-card class="filter-card">
      <el-form :model="searchForm" inline @submit.prevent="handleSearch">
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="商品名称 / SKU编号"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="平台">
          <el-select v-model="searchForm.platform" placeholder="全部平台" clearable style="width: 140px">
            <el-option label="1688" value="1688" />
            <el-option label="TikTok" value="tiktok" />
            <el-option label="Amazon" value="amazon" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="上架" value="active" />
            <el-option label="下架" value="offline" />
            <el-option label="库存预警" value="warning" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 批量操作栏 -->
    <div v-if="selectedRows.length > 0" class="batch-bar">
      <span class="batch-tip">已选 {{ selectedRows.length }} 项</span>
      <el-button size="small" @click="handleBatchOnline">批量上架</el-button>
      <el-button size="small" @click="handleBatchOffline">批量下架</el-button>
      <el-button size="small" type="danger" @click="handleBatchDelete">批量删除</el-button>
      <el-button size="small" text @click="selectedRows = []">取消选择</el-button>
    </div>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="list"
        border
        stripe
        @selection-change="selectedRows = $event"
        style="width: 100%"
      >
        <el-table-column type="selection" width="40" />
        <el-table-column label="商品信息" min-width="260">
          <template #default="{ row }">
            <div class="goods-info">
              <el-image :src="row.images?.[0]" fit="cover" class="goods-img" />
              <div class="goods-detail">
                <div class="goods-name">{{ row.name }}</div>
                <div class="goods-id">ID: {{ row.id }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="platform" label="平台" width="100">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.platform }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="售价" width="100">
          <template #default="{ row }">
            <span class="price">¥{{ row.price }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="cost" label="成本" width="100">
          <template #default="{ row }">
            <span class="cost">¥{{ row.cost || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="100">
          <template #default="{ row }">
            <span :class="{ 'stock-warn': row.stock < 10 }">{{ row.stock }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">
              {{ statusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="入库时间" width="120" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" plain @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadData"
        @current-change="loadData"
        style="margin-top: 16px"
      />
    </el-card>

    <!-- 编辑/新增弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新增商品' : '编辑商品'"
      width="600px"
      destroy-on-close
    >
      <el-form :model="dialogForm" label-width="80px">
        <el-form-item label="商品名称">
          <el-input v-model="dialogForm.name" placeholder="请输入商品名称" />
        </el-form-item>
        <el-form-item label="SKU编号">
          <el-input v-model="dialogForm.sku_code" placeholder="自动生成或手动填写" />
        </el-form-item>
        <el-form-item label="商品条码">
          <el-input v-model="dialogForm.barcode" placeholder="扫描枪录入或手动填写（选填）" clearable />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="售价">
              <el-input-number v-model="dialogForm.price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="成本">
              <el-input-number v-model="dialogForm.cost" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="库存">
          <el-input-number v-model="dialogForm.stock" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="来源链接">
          <el-input v-model="dialogForm.source_url" placeholder="原始商品链接" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="dialogLoading" @click="handleDialogSubmit">
          确认
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { fetchSkuList, createSku, updateSku, deleteSku, batchDeleteSku, batchOnlineSku, batchOfflineSku } from '@/api/sku'

// ==================== 列表 ====================
const loading = ref(false)
const list = ref([])
const selectedRows = ref([])
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })
const searchForm = reactive({ keyword: '', platform: '', status: '' })

async function loadData() {
  loading.value = true
  try {
    const res = await fetchSkuList({
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm,
    })
    list.value = res.data?.results || res.data?.items || res.data || []
    pagination.total = res.data?.count ?? res.data?.total ?? 0
  } catch {
    // request.js 统一处理
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  loadData()
}

function handleReset() {
  searchForm.keyword = ''
  searchForm.platform = ''
  searchForm.status = ''
  pagination.page = 1
  loadData()
}

// ==================== 状态 ====================
function statusType(status) {
  const map = { active: 'success', offline: 'info', warning: 'danger' }
  return map[status] || 'info'
}
function statusText(status) {
  const map = { active: '上架', offline: '下架', warning: '库存预警' }
  return map[status] || status
}

// ==================== 批量操作 ====================
async function handleBatchOnline() {
  const ids = selectedRows.value.map(r => r.id)
  await batchOnlineSku(ids)
  ElMessage.success(`已上架 ${ids.length} 件商品`)
  selectedRows.value = []
  loadData()
}

async function handleBatchOffline() {
  const ids = selectedRows.value.map(r => r.id)
  await batchOfflineSku(ids)
  ElMessage.success(`已下架 ${ids.length} 件商品`)
  selectedRows.value = []
  loadData()
}

async function handleBatchDelete() {
  const ids = selectedRows.value.map(r => r.id)
  await ElMessageBox.confirm(`确认删除选中的 ${ids.length} 件商品？`, '批量删除', { type: 'warning' })
  await batchDeleteSku(ids)
  ElMessage.success('删除成功')
  selectedRows.value = []
  loadData()
}

// ==================== 单条操作 ====================
function handleCreate() {
  dialogMode.value = 'create'
  dialogForm.name = ''
  dialogForm.sku_code = ''
  dialogForm.barcode = ''
  dialogForm.price = 0
  dialogForm.cost = 0
  dialogForm.stock = 0
  dialogForm.source_url = ''
  dialogVisible.value = true
}

function handleEdit(row) {
  dialogMode.value = 'edit'
  dialogForm.id = row.id
  dialogForm.name = row.name
  dialogForm.sku_code = row.sku_code || ''
  dialogForm.barcode = row.barcode || ''
  dialogForm.price = row.price
  dialogForm.cost = row.cost || 0
  dialogForm.stock = row.stock
  dialogForm.source_url = row.source_url || ''
  dialogVisible.value = true
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除商品「${row.name}」？`, '删除确认', { type: 'warning' })
  await deleteSku(row.id)
  ElMessage.success('删除成功')
  loadData()
}

// ==================== 弹窗 ====================
const dialogVisible = ref(false)
const dialogLoading = ref(false)
const dialogMode = ref('create')
const dialogForm = reactive({ id: null, name: '', sku_code: '', barcode: '', price: 0, cost: 0, stock: 0, source_url: '' })

async function handleDialogSubmit() {
  if (!dialogForm.name) {
    ElMessage.warning('请填写商品名称')
    return
  }
  dialogLoading.value = true
  try {
    if (dialogMode.value === 'create') {
      await createSku(dialogForm)
      ElMessage.success('创建成功')
    } else {
      await updateSku(dialogForm.id, dialogForm)
      ElMessage.success('更新成功')
    }
    dialogVisible.value = false
    loadData()
  } finally {
    dialogLoading.value = false
  }
}

// ==================== 导入导出 ====================
function handleImport() {
  ElMessage.info('导入功能：创建上传组件或调用 POST /api/v1/sku/import/')
}

function handleExport() {
  ElMessage.info('导出功能：调用 POST /api/v1/sku/export/ 生成导出文件')
}

onMounted(() => loadData())
</script>

<style scoped>
.page {
  padding: 28px 32px;
  max-width: 1600px;
}

/* 筛选卡片 */
.filter-card { margin-bottom: 16px; }

/* 批量操作栏 */
.batch-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  background: var(--brand-light);
  border: 1px solid rgba(37,99,235,.2);
  border-radius: var(--r-md);
  margin-bottom: 12px;
  font-size: 13px;
}
.batch-tip { color: var(--brand); font-weight: 500; margin-right: 4px; }

/* 表格 */
.goods-info { display: flex; align-items: center; gap: 12px; }
.goods-img { width: 52px; height: 52px; border-radius: var(--r-sm); border: 1px solid var(--border); flex-shrink: 0; }
.goods-name { font-size: 13.5px; color: var(--text-primary); font-weight: 500; }
.goods-id { font-size: 12px; color: var(--text-muted); margin-top: 3px; }
.price { color: var(--danger); font-weight: 600; }
.cost { color: var(--text-secondary); }
.stock-warn { color: var(--danger); font-weight: 600; }
</style>
