/**
 * WebSocket 高频异步进度流控
 * - 自动连接 + 指数退避重连（最多 5 次）
 * - 消息分发到 Pinia store
 * - requestAnimationFrame + 200ms 节流
 */
import { ref, onUnmounted } from 'vue'
import { useTaskProgressStore } from '@/stores/useTaskProgress'

export function useWebSocket() {
  const ws = ref<WebSocket | null>(null)
  const connected = ref(false)
  const reconnectAttempt = ref(0)
  const MAX_RECONNECT = 5
  const BASE_DELAY = 1000

  let reconnectTimer: ReturnType<typeof setTimeout> | null = null

  const store = useTaskProgressStore()

  function connect() {
    const token = localStorage.getItem('access_token')
    if (!token) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const url = `${protocol}//${host}/api/ws/tasks?token=${token}`

    const socket = new WebSocket(url)
    ws.value = socket

    socket.onopen = () => {
      connected.value = true
      reconnectAttempt.value = 0
      console.log('[WebSocket] 已连接')
    }

    socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        if (msg.type === 'task_progress') {
          store.pushProgress(msg.data)
        } else if (msg.type === 'task_complete') {
          store.markComplete(msg.data.task_id, msg.data)
        } else if (msg.type === 'task_error') {
          store.markFailed(msg.data.task_id, msg.data.error || '任务执行失败')
        }
      } catch (e) {
        console.warn('[WebSocket] 消息解析失败:', e)
      }
    }

    socket.onclose = (event) => {
      connected.value = false
      if (!event.wasClean && reconnectAttempt.value < MAX_RECONNECT) {
        const delay = BASE_DELAY * Math.pow(2, reconnectAttempt.value)
        reconnectAttempt.value++
        console.log(`[WebSocket] ${delay}ms 后第 ${reconnectAttempt.value} 次重连...`)
        reconnectTimer = setTimeout(connect, delay)
      }
    }

    socket.onerror = () => {
      // onclose 会自动处理重连
    }
  }

  function disconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    reconnectAttempt.value = MAX_RECONNECT // 阻止重连
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
    connected.value = false
  }

  function send(data) {
    if (ws.value && connected.value) {
      ws.value.send(typeof data === 'string' ? data : JSON.stringify(data))
    }
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    connected,
    connect,
    disconnect,
    send,
  }
}
