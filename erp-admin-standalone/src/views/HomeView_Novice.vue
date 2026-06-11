<template>
  <div class="novice-home">
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
      <div class="stat-item" @click="goToOrders">
        <div class="stat-icon-wrapper blue">
          <el-icon><ShoppingCart /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.todayOrders }}</div>
          <div class="stat-label">今日订单</div>
        </div>
        <el-tag v-if="stats.todayOrders > 0" type="danger" size="small" effect="dark">
          待处理
        </el-tag>
      </div>

      <div class="stat-item" @click="goToSales">
        <div class="stat-icon-wrapper green">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">¥{{ formatMoney(stats.todaySales) }}</div>
          <div class="stat-label">今日销售额</div>
        </div>
        <div class="stat-trend up">
          <el-icon><ArrowUp /></el-icon>
          <span>{{ stats.salesGrowth }}</span>
        </div>
      </div>

      <div class="stat-item warning" @click="goToPendingShip">
        <div class="stat-icon-wrapper orange">
          <el-icon><Box /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.pendingShip }}</div>
          <div class="stat-label">待发货订单</div>
        </div>
        <el-tag v-if="stats.pendingShip > 5" type="warning" size="small">
          繁忙
        </el-tag>
      </div>
    </div>

    <!-- 两大核心入口按钮 -->
    <div class="main-actions">
      <div class="action-card primary" @click="handleListGoods">
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

      <div class="action-card success" @click="handleShip">
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
    <div class="ai-hint">
      <el-icon><MagicStick /></el-icon>
      <span>有疑问？试试问AI助手「小辽」</span>
    </div>

    <!-- 待办提醒（如果有） -->
    <div v-if="hasPendingTasks" class="pending-tasks">
      <div class="tasks-header">
        <el-icon><Bell /></el-icon>
        <span>待办提醒</span>
      </div>
      <div class="task-item" v-for="task in pendingTasks" :key="task.id" @click="handleTask(task)">
        <span class="task-text">{{ task.text }}</span>
        <el-tag :type="task.urgent ? 'danger' : 'warning'" size="small">{{ task.tag }}</el-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/useAppStore'
import {
  ShoppingCart, Money, Box, Upload, Van, ArrowRight, ArrowUp,
  MagicStick, Bell
} from '@element-plus/icons-vue'

const router = useRouter()
const appStore = useAppStore()

// 核心统计数据（从后端API加载）
const stats = ref({
  todayOrders: 0,
  todaySales: 0,
  salesGrowth: '--',
  pendingShip: 0
})

// 待办任务
const pendingTasks = ref([
  { id: 1, text: '有8笔订单待发货', tag: '紧急', urgent: true },
  { id: 2, text: '3个商品库存不足', tag: '提醒', urgent: false }
])

const hasPendingTasks = computed(() => pendingTasks.value.length > 0)

// 格式化金额
function formatMoney(val) {
  if (!val) return '0.00'
  return val.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// 跳转函数
function goToOrders() {
  router.push('/orders')
}

function goToSales() {
  router.push('/')
}

function goToPendingShip() {
  router.push('/orders?status=pending_ship')
}

// 主操作：上货
function handleListGoods() {
  // 引导到商品上货页面
  router.push('/goods/listing')
}

// 主操作：发货
function handleShip() {
  // 引导到订单发货页面
  router.push('/orders?action=ship')
}

// 切换到资深模式
function switchToSenior() {
  appStore.switchMode('senior')
  router.push('/')
}

// 处理待办任务
function handleTask(task) {
  if (task.id === 1) {
    goToPendingShip()
  }
}

onMounted(() => {
  // 后续对接真实API获取统计数据
})
</script>

<style scoped>
.novice-home {
  padding: 24px;
  max-width: 900px;
  margin: 0 auto;
}

/* 头部 */
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

/* 核心指标卡片 */
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

/* 两大入口按钮 */
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

/* AI提示 */
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

/* 待办提醒 */
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
</style>
