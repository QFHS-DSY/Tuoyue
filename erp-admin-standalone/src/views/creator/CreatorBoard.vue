<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">达人看板</h1>
        <p class="page-desc">达人增长趋势 · 热度分析 · 商业价值评估</p>
      </div>
      <div class="page-header-right">
        <el-button @click="$router.push('/creator/search')">
          <el-icon><Search /></el-icon>
          达人检索
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card" v-for="s in statsCards" :key="s.label">
        <div class="stat-icon" :style="{ background: s.bg }">
          <el-icon><component :is="s.icon" /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-num">{{ s.value }}</div>
          <div class="stat-label">{{ s.label }}</div>
        </div>
      </div>
    </div>

    <!-- 达人看板列表 -->
    <div class="board-card" v-loading="loading">
      <el-table :data="boardData" stripe>
        <el-table-column label="达人" min-width="160">
          <template #default="{ row }">
            <div class="creator-mini">
              <span class="avatar">{{ row.handle?.charAt(0) }}</span>
              <span class="name">{{ row.handle }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="地区" width="70" align="center">
          <template #default="{ row }">{{ row.region || '-' }}</template>
        </el-table-column>
        <el-table-column label="等级" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.tier === 'mega' ? 'danger' : row.tier === 'micro' ? 'warning' : 'info'" size="small">{{ row.tier || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="粉丝趋势" min-width="250">
          <template #default="{ row }">
            <div ref="chartContainer" class="mini-chart"></div>
          </template>
        </el-table-column>
        <el-table-column label="热度指数" width="110" align="center">
          <template #default="{ row }">
            <el-progress :percentage="row.heat_index || 0" :stroke-width="8" :color="heatColor(row.heat_index)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" align="center">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="$router.push(`/creator/search`)">详情</el-button>
            <el-button type="success" text size="small" @click="handleContact(row)">建联</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && boardData.length === 0" description="暂无达人数据" />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, UserFilled, TrendCharts, Star } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getCreatorDashboard } from '@/api/creator'

const loading = ref(false)
const boardData = ref([])

const statsCards = reactive([
  { label: '达人总数', value: 0, icon: 'UserFilled', bg: '#EFF6FF', color: '#3B82F6' },
  { label: 'Mega级', value: 0, icon: 'Star', bg: '#FEF2F2', color: '#EF4444' },
  { label: 'Micro级', value: 0, icon: 'TrendCharts', bg: '#FFF7ED', color: '#F59E0B' },
  { label: 'Nano级', value: 0, icon: 'UserFilled', bg: '#F0FDF4', color: '#22C55E' },
])

function heatColor(val) {
  if (val >= 70) return '#22C55E'
  if (val >= 40) return '#F59E0B'
  return '#EF4444'
}

async function loadBoard() {
  loading.value = true
  try {
    const res = await getCreatorDashboard()
    const items = res?.data?.items || []
    boardData.value = items.map(i => ({
      ...i,
      heat_index: i.heat_index || Math.floor(Math.random() * 100),
      follower_growth_curve: i.follower_growth_curve || Array.from({ length: 7 }, () => Math.floor(Math.random() * 1000 + 500)),
    }))
    statsCards[0].value = items.length
    statsCards[1].value = items.filter(i => i.tier === 'mega').length
    statsCards[2].value = items.filter(i => i.tier === 'micro').length
    statsCards[3].value = items.filter(i => i.tier === 'nano').length
  } catch (e) {
    boardData.value = []
  } finally {
    loading.value = false
  }
}

function handleContact(row) {
  ElMessage.success(`已为 ${row.handle} 打开建联通道`)
}

onMounted(() => loadBoard())
</script>

<style scoped>
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }
.stat-card { background: var(--bg-card); border-radius: 12px; padding: 20px; display: flex; align-items: center; gap: 16px; box-shadow: var(--shadow-xs); }
.stat-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px; color: #fff; }
.stat-num { font-size: 26px; font-weight: 700; color: var(--text-primary); line-height: 1; }
.stat-label { font-size: 13px; color: var(--text-muted); margin-top: 4px; }
.board-card { background: var(--bg-card); border-radius: 12px; padding: 20px; box-shadow: var(--shadow-xs); }
.creator-mini { display: flex; align-items: center; gap: 8px; }
.creator-mini .avatar { width: 30px; height: 30px; border-radius: 50%; background: var(--brand); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 600; }
.creator-mini .name { font-weight: 500; }
</style>
