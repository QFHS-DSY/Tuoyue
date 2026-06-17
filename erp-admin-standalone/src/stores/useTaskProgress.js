/**
 * 任务进度状态管理
 * - _rawProgress 缓冲区
 * - requestAnimationFrame + 200ms 固定周期节流
 * - 右下角浮动侧边任务队列
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useTaskProgressStore = defineStore('taskProgress', () => {
  // 原始进度缓冲区
  const _rawProgress = ref({})

  // 渲染层数据（经过节流）
  const tasks = ref([])
  const queueVisible = ref(false)

  // 节流控制
  let rafId = null
  let lastFlush = 0
  const FLUSH_INTERVAL = 200 // ms

  function scheduleFlush() {
    if (rafId !== null) return
    rafId = requestAnimationFrame(() => {
      const now = Date.now()
      if (now - lastFlush >= FLUSH_INTERVAL) {
        flushProgress()
        lastFlush = now
      }
      rafId = null
      // 如果还有数据没刷新，继续调度
      if (Object.keys(_rawProgress.value).length > 0) {
        scheduleFlush()
      }
    })
  }

  function flushProgress() {
    const data = Object.values(_rawProgress.value)
    _rawProgress.value = {}
    if (data.length === 0) return

    // 合并到 tasks 列表
    data.forEach((item) => {
      const idx = tasks.value.findIndex(t => t.task_id === item.task_id)
      if (idx >= 0) {
        tasks.value[idx] = { ...tasks.value[idx], ...item }
      } else {
        tasks.value.push(item)
      }
    })

    // 自动展开
    if (data.some((d) => d.status === 'running')) {
      queueVisible.value = true
    }
  }

  function pushProgress(data) {
    _rawProgress.value[data.task_id] = data
    scheduleFlush()
  }

  function markComplete(taskId, data) {
    const idx = tasks.value.findIndex(t => t.task_id === taskId)
    if (idx >= 0) {
      tasks.value[idx] = { ...tasks.value[idx], status: 'success', progress: 100, ...data }
    }
  }

  function markFailed(taskId, error) {
    const idx = tasks.value.findIndex(t => t.task_id === taskId)
    if (idx >= 0) {
      tasks.value[idx] = { ...tasks.value[idx], status: 'failed', message: error }
    }
  }

  function addTask(task) {
    tasks.value.push({
      task_id: task.task_id || `task_${Date.now()}`,
      title: task.title || '未命名任务',
      status: task.status || 'pending',
      progress: task.progress || 0,
      message: task.message || '等待执行...',
    })
    queueVisible.value = true
  }

  function removeTask(taskId) {
    tasks.value = tasks.value.filter(t => t.task_id !== taskId)
  }

  function clearCompleted() {
    tasks.value = tasks.value.filter(t => t.status === 'running' || t.status === 'pending')
  }

  function toggleQueue() {
    queueVisible.value = !queueVisible.value
  }

  // 计算属性
  const runningCount = computed(() => tasks.value.filter(t => t.status === 'running').length)
  const successCount = computed(() => tasks.value.filter(t => t.status === 'success').length)
  const failCount = computed(() => tasks.value.filter(t => t.status === 'failed').length)
  const hasActiveTask = computed(() => runningCount.value > 0)
  const totalCount = computed(() => tasks.value.length)

  return {
    tasks,
    queueVisible,
    runningCount,
    successCount,
    failCount,
    hasActiveTask,
    totalCount,
    pushProgress,
    markComplete,
    markFailed,
    addTask,
    removeTask,
    clearCompleted,
    toggleQueue,
  }
})
