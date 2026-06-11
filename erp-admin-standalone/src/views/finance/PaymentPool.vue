<template>
  <div class="page-container">
    <el-card>
      <template #header><div class="card-header"><span>请款池</span></div></template>
      <el-form :inline="true" :model="filterForm" @submit.prevent="handleSearch">
        <el-form-item label="池类型"><el-select v-model="filterForm.pool_type" clearable placeholder="全部"><el-option v-for="t in poolTypes" :key="t" :label="t" :value="t"/></el-select></el-form-item>
        <el-form-item label="来源类型"><el-select v-model="filterForm.source_type" clearable placeholder="全部"><el-option v-for="t in sourceTypes" :key="t" :label="t" :value="t"/></el-select></el-form-item>
        <el-form-item label="状态"><el-select v-model="filterForm.status" clearable placeholder="全部"><el-option v-for="t in statuses" :key="t" :label="t" :value="t"/></el-select></el-form-item>
        <el-form-item label="搜索"><el-input v-model="filterForm.search" placeholder="单据号/供应商" clearable style="width:200px"/></el-form-item>
        <el-form-item><el-button type="primary" @click="handleSearch">查询</el-button><el-button @click="handleReset">重置</el-button></el-form-item>
      </el-form>
      <el-table :data="tableData" border stripe v-loading="loading" @sort-change="handleSort">
        <el-table-column prop="source_no" label="来源单号" width="150"/>
        <el-table-column prop="pool_type" label="池类型" width="100"/>
        <el-table-column prop="supplier_name" label="供应商" width="150"/>
        <el-table-column prop="payable_amount" label="应付金额" width="120" sortable="custom"/>
        <el-table-column prop="paid_amount" label="已付金额" width="120"/>
        <el-table-column prop="unapplied_amount" label="未申请金额" width="120"/>
        <el-table-column prop="currency" label="币种" width="80"/>
        <el-table-column prop="status" label="状态" width="100"><template #default="{row}"><el-tag :type="statusType(row.status)">{{ row.status }}</el-tag></template></el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160"/>
        <el-table-column label="操作" width="150" fixed="right"><template #default="{row}"><el-button size="small" @click="handleApply(row)">申请请款</el-button></template></el-table-column>
      </el-table>
      <el-pagination v-model:current-page="pagination.page" :page-size="pagination.size" :total="pagination.total" layout="total, prev, pager, next" @current-change="loadData"/>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getPaymentPool } from '@/api/finance'
import { ElMessage } from 'element-plus'

const filterForm = reactive({ pool_type: '', source_type: '', status: '', search: '' })
const tableData = ref([])
const loading = ref(false)
const pagination = reactive({ page: 1, size: 20, total: 0 })
const poolTypes = ['现结', '月结', '预付款', '物流', '其他应付款']
const sourceTypes = ['采购单', '发货单', '备货单', '费用单']
const statuses = ['UNAPPLIED', 'APPLYING', 'PARTIAL', 'PAID']
const statusType = (s) => ({ UNAPPLIED:'info', APPLYING:'warning', PARTIAL:'warning', PAID:'success', APPLIED:'success' }[s] || 'info')

async function loadData() {
  loading.value = true
  try {
    const params = { ...filterForm, page: pagination.page, page_size: pagination.size }
    const data = await getPaymentPool(params)
    tableData.value = data?.results || data || []
    pagination.total = data?.count || 0
  } catch { ElMessage.error('加载失败') }
  finally { loading.value = false }
}
function handleSearch() { pagination.page = 1; loadData() }
function handleReset() { Object.assign(filterForm, { pool_type: '', source_type: '', status: '', search: '' }); handleSearch() }
function handleSort({ prop, order }) { /* backend sort via ordering param */ }
function handleApply(row) { ElMessage.info(`申请请款: ${row.source_no}`) }
onMounted(loadData)
</script>
