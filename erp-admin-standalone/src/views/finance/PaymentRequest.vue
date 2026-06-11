<template>
  <div class="page-container">
    <el-card>
      <template #header><div class="card-header"><span>请款单</span><el-button type="primary" size="small" @click="handleCreate">新建请款单</el-button></div></template>
      <el-form :inline="true" :model="f" @submit.prevent="search">
        <el-form-item label="状态"><el-select v-model="f.status" clearable><el-option v-for="s in statuses" :key="s" :label="s" :value="s"/></el-select></el-form-item>
        <el-form-item label="应付类型"><el-select v-model="f.payable_type" clearable><el-option v-for="t in types" :key="t" :label="t" :value="t"/></el-select></el-form-item>
        <el-form-item label="搜索"><el-input v-model="f.search" placeholder="请款单号/供应商" clearable style="width:200px"/></el-form-item>
        <el-form-item><el-button type="primary" @click="search">查询</el-button><el-button @click="reset">重置</el-button></el-form-item>
      </el-form>
      <el-table :data="list" border stripe v-loading="loading">
        <el-table-column prop="request_no" label="请款单号" width="150"/>
        <el-table-column prop="supplier_name" label="供应商" width="150"/>
        <el-table-column prop="total_amount" label="请款金额" width="120"/>
        <el-table-column prop="paid_amount" label="已付金额" width="120"/>
        <el-table-column prop="payable_type" label="应付类型" width="100"/>
        <el-table-column prop="status" label="状态" width="120"><template #default="{ row }"><el-tag :type="{PENDING_APPROVAL:'warning',APPROVED:'',COMPLETED:'success',REJECTED:'danger',CANCELLED:'info'}[row.status]">{{ row.status }}</el-tag></template></el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160"/>
        <el-table-column label="操作" width="200" fixed="right"><template #default="{ row }">
          <el-button size="small" @click="handleDetail(r)">详情</el-button>
          <el-button v-if="row.status==='PENDING_APPROVAL'" size="small" type="warning" @click="handleApprove(r)">审批</el-button>
          <el-button v-if="row.status==='APPROVED'" size="small" type="success" @click="handlePay(r)">付款</el-button>
        </template></el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page.page" layout="total,prev,pager,next" :total="page.total" @current-change="load"/>
    </el-card>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getPaymentRequests, createPaymentRequest, approvePaymentRequest, payPaymentRequest } from '@/api/finance'
import { ElMessage } from 'element-plus'
const f = reactive({ status: '', payable_type: '', search: '' })
const list = ref([]); const loading = ref(false); const page = reactive({ page:1,total:0 })
const statuses = ['PENDING_APPROVAL','APPROVED','COMPLETED','REJECTED','CANCELLED']
const types = ['货款现结','货款月结','货款预付款','物流请款','其他应付款']
async function load() {
  loading.value=true
  try { const {data} = await getPaymentRequests({...f, page:page.page}); list.value=data?.results||data||[]; page.total=data?.count||0 }
  catch { ElMessage.error('加载失败') } finally { loading.value=false }
}
function search() { page.page=1; load() }
function reset() { Object.assign(f,{status:'',payable_type:'',search:''}); search() }
function handleCreate() { ElMessage.info('新建请款单功能开发中') }
function handleDetail(r) { ElMessage.info(`请款单详情: ${r.request_no}`) }
function handleApprove(r) { approvePaymentRequest(r.id,{action:'approve'}).then(()=>{ElMessage.success('审批通过');load()}) }
function handlePay(r) { ElMessage.info(`付款: ${r.request_no}`) }
onMounted(load)
</script>
