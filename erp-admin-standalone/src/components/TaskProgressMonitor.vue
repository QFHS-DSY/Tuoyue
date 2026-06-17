<template>
  <Transition name="task-slide">
    <div v-if="store.tasks.length > 0" class="task-monitor" :class="{ collapsed: !store.queueVisible }">
      <!-- 折叠时的触发条 -->
      <div v-if="!store.queueVisible" class="task-monitor-trigger" @click="store.toggleQueue()">
        <el-badge :value="store.runningCount" :hidden="store.runningCount === 0">
          <el-icon :size="20"><List /></el-icon>
        </el-badge>
        <span class="trigger-text">任务队列 ({{ store.totalCount }})</span>
      </div>

      <!-- 展开面板 -->
      <div v-else class="task-monitor-panel">
        <div class="task-monitor-header" @click="store.toggleQueue()">
          <div class="tmh-left">
            <el-icon><List /></el-icon>
            <span class="tmh-title">任务队列</span>
            <el-tag size="small" type="primary" effect="plain">{{ store.totalCount }}</el-tag>
          </div>
          <div class="tmh-right">
            <span class="tmh-stat tmh-stat--running">
              <span class="stat-dot running"></span>
              {{ store.runningCount }}
            </span>
            <span class="tmh-stat tmh-stat--success">
              <span class="stat-dot success"></span>
              {{ store.successCount }}
            </span>
            <span class="tmh-stat tmh-stat--fail">
              <span class="stat-dot fail"></span>
              {{ store.failCount }}
            </span>
            <el-button link size="small" @click.stop="store.clearCompleted()">
              <el-icon><Delete /></el-icon>
            </el-button>
            <el-icon class="tmh-collapse"><ArrowDown /></el-icon>
          </div>
        </div>

        <div class="task-monitor-body">
          <div
            v-for="task in store.tasks"
            :key="task.task_id"
            class="task-item"
          >
            <div class="task-item-header">
              <span class="task-title">{{ task.title }}</span>
              <el-tag :type="statusType(task.status)" size="small">
                {{ statusLabel(task.status) }}
              </el-tag>
            </div>
            <el-progress
              :percentage="task.progress"
              :status="task.status === 'failed' ? 'exception' : task.status === 'success' ? 'success' : undefined"
              :stroke-width="6"
              :text-inside="true"
            />
            <div class="task-message">{{ task.message }}</div>
            <el-button
              v-if="task.status === 'success' || task.status === 'failed'"
              link
              size="small"
              type="danger"
              @click="store.removeTask(task.task_id)"
            >
              移除
            </el-button>
          </div>

          <div v-if="store.tasks.length === 0" class="task-empty">
            暂无任务
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { List, Delete, ArrowDown } from '@element-plus/icons-vue'
import { useTaskProgressStore } from '@/stores/useTaskProgress'

const store = useTaskProgressStore()

function statusType(status) {
  const map = { running: 'primary', success: 'success', failed: 'danger', pending: 'info', cancelled: 'warning' }
  return map[status] || 'info'
}

function statusLabel(status) {
  const map = { running: '运行中', success: '成功', failed: '失败', pending: '等待', cancelled: '已取消' }
  return map[status] || status
}
</script>

<style scoped>
.task-monitor {
  position: fixed;
  right: 16px;
  bottom: 16px;
  z-index: 999;
  font-size: 13px;
}

.task-monitor-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  cursor: pointer;
  box-shadow: 0 2px 12px rgba(0,0,0,.08);
  transition: box-shadow .2s;
}

.task-monitor-trigger:hover {
  box-shadow: 0 4px 20px rgba(0,0,0,.12);
}

.trigger-text {
  color: #606266;
  font-size: 13px;
}

.task-monitor-panel {
  width: 380px;
  max-height: 520px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.task-monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  user-select: none;
}

.tmh-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tmh-title {
  font-weight: 600;
  color: #1e293b;
}

.tmh-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tmh-stat {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.tmh-stat--running { color: #3b82f6; }
.tmh-stat--success { color: #10b981; }
.tmh-stat--fail { color: #ef4444; }

.stat-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.stat-dot.running { background: #3b82f6; animation: pulse 1.5s ease-in-out infinite; }
.stat-dot.success { background: #10b981; }
.stat-dot.fail { background: #ef4444; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.tmh-collapse {
  font-size: 12px;
  color: #909399;
}

.task-monitor-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  padding: 10px 12px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
}

.task-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.task-title {
  font-weight: 500;
  color: #1e293b;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 220px;
}

.task-message {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-empty {
  text-align: center;
  color: #c0c4cc;
  padding: 20px 0;
  font-size: 13px;
}

/* 过渡动画 */
.task-slide-enter-active,
.task-slide-leave-active {
  transition: all 0.3s ease;
}

.task-slide-enter-from,
.task-slide-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>
