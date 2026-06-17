/**
 * axios 请求封装（含 TypeScript 类型声明）
 * 所有 API 请求统一通过此模块发出
 *
 * 规范：
 * - 不走 baseURL，通过 Vite proxy 同源代理到后端
 * - 自动附加 Authorization token
 * - 401 时自动尝试 refresh token 续期（并发锁 + 挂起队列）
 * - 429 限流：解析 Retry-After 头部，倒计时提示 + 广播事件
 * - 网络错误自动重试（最大 2 次，指数退避）
 * - 统一错误处理，弹出 ElMessage 提示
 * - DEMO_MODE 降级感知：检测 [MOCK] 标识时友好提示
 * - 响应 data 透传，直接拿到业务数据
 */

import axios from 'axios'
import { ElMessage, ElNotification } from 'element-plus'
import { AI_DEFAULT_TIMEOUT_MS, AI_LONG_TIMEOUT_MS } from '@/utils/aiStudio'

const service = axios.create({
  timeout: AI_DEFAULT_TIMEOUT_MS,
  withCredentials: false,
})

// ── Token 刷新状态管理 ──
let isRefreshing = false
let failedQueue = []

function processQueue(error, token = null) {
  failedQueue.forEach(prom => {
    if (error) prom.reject(error)
    else prom.resolve(token)
  })
  failedQueue = []
}

function logout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  if (window.location.pathname !== '/login') {
    window.location.href = '/login'
  }
}

async function tryRefreshToken() {
  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) return null

  try {
    const res = await axios.post('/api/auth/refresh', {
      refresh_token: refreshToken,
    }, { timeout: 10000 })

    const payload = res.data
    const data = payload?.data || payload
    if (data?.access_token) {
      localStorage.setItem('access_token', data.access_token)
      if (data.refresh_token) {
        localStorage.setItem('refresh_token', data.refresh_token)
      }
      return data.access_token
    }
    return null
  } catch (e) {
    return null
  }
}

// ==================== 429 限流状态管理 ====================
let rateLimitTimer = null

function clearRateLimitTimer() {
  if (rateLimitTimer) {
    clearTimeout(rateLimitTimer)
    rateLimitTimer = null
  }
}

/**
 * 429 限流倒计时提示
 * 解析 Retry-After 头部，广播 rate_limit_unlock 事件供按钮禁用恢复
 */
function handleRateLimited(response) {
  const retryAfter = parseInt(response.headers['retry-after'] || response.headers['Retry-After'] || '5', 10)
  const waitSeconds = Math.min(retryAfter, 60)

  // 广播全局限流事件
  window.dispatchEvent(new CustomEvent('rate_limit_locked', {
    detail: { retryAfter: waitSeconds }
  }))

  // 倒计时提示
  let remaining = waitSeconds
  const notification = ElNotification({
    title: '请求过于频繁',
    message: `服务器限流，请等待 ${remaining} 秒后重试...`,
    type: 'warning',
    duration: 0,
    showClose: false,
  })

  clearRateLimitTimer()
  const tick = () => {
    remaining--
    if (remaining <= 0) {
      notification.close()
      window.dispatchEvent(new CustomEvent('rate_limit_unlocked'))
      clearRateLimitTimer()
    } else {
      notification.message = `服务器限流，请等待 ${remaining} 秒后重试...`
      rateLimitTimer = setTimeout(tick, 1000)
    }
  }
  rateLimitTimer = setTimeout(tick, 1000)
}

// ==================== DEMO_MODE 降级检测 ====================
function isDemoModeData(data) {
  if (typeof data === 'string' && data.startsWith('[MOCK]')) return true
  if (data && typeof data === 'object') {
    const obj = data
    if (obj._mock || obj._demo) return true
    if (typeof obj.message === 'string' && obj.message.startsWith('[MOCK]')) return true
    if (typeof obj.detail === 'string' && obj.detail.startsWith('[MOCK]')) return true
  }
  return false
}

// ==================== 请求拦截器 ====================
service.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }

    if ((config.url || '').startsWith('/api/ai/')) {
      config.timeout = Math.max(config.timeout || 0, AI_LONG_TIMEOUT_MS)
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ==================== 响应拦截器 ====================
const MAX_RETRIES = 2
const RETRY_DELAY = 1000

service.interceptors.response.use(
  (response) => {
    // 检测 DEMO_MODE 降级数据
    const data = response.data
    if (isDemoModeData(data)) {
      // DEMO 模式不报错，返回数据让调用方处理
      return { ...data, _demo: true }
    }
    return response.data
  },
  async (error) => {
    const originalRequest = error.config
    if (!originalRequest) return Promise.reject(error)

    // ── 网络错误/超时自动重试（最多2次）──
    const isNetErr = !error.response || error.code === 'ECONNABORTED' || (error.message || '').includes('Network')
    const rc = originalRequest._retryCount || 0
    if (isNetErr && rc < MAX_RETRIES) {
      originalRequest._retryCount = rc + 1
      await new Promise(r => setTimeout(r, RETRY_DELAY * (rc + 1)))
      return service(originalRequest)
    }

    // ── 429 限流处理 ──
    if (error.response?.status === 429) {
      handleRateLimited(error.response)
      return Promise.reject(error)
    }

    // ── 401 处理：尝试 Token 自动刷新 ──
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (originalRequest.url?.includes('/api/auth/refresh')) {
        logout()
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          originalRequest.headers['Authorization'] = `Bearer ${token}`
          return service(originalRequest)
        }).catch(err => {
          return Promise.reject(err)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const newToken = await tryRefreshToken()
        if (newToken) {
          processQueue(null, newToken)
          originalRequest.headers['Authorization'] = `Bearer ${newToken}`
          return service(originalRequest)
        } else {
          processQueue(new Error('refresh failed'), null)
          ElMessage.error('登录已过期，请重新登录')
          logout()
          return Promise.reject(error)
        }
      } catch (refreshError) {
        processQueue(refreshError, null)
        ElMessage.error('登录已过期，请重新登录')
        logout()
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // ── DEMO_MODE 降级感知 ──
    if (error.response?.data && isDemoModeData(error.response.data)) {
      ElMessage.info('当前为演示模式，部分功能受限')
      return { ...error.response.data, _demo: true }
    }

    // ── 通用错误处理（含解决方案指引）──
    let message = '请求失败，已自动重试2次仍失败，请检查网络或稍后重试'
    if (error.response) {
      const { status, data } = error.response
      switch (status) {
        case 400:
          if (data && typeof data === 'object' && !data.detail && !data.message) {
            const firstKey = Object.keys(data)[0]
            const firstErr = data[firstKey]
            message = Array.isArray(firstErr) ? firstErr[0] : (typeof firstErr === 'string' ? firstErr : '请求参数错误')
          } else {
            message = data?.detail || data?.message || '请求参数错误，请检查输入内容'
          }
          break
        case 401: message = '登录已过期，请重新登录'; break
        case 403: message = '没有权限执行此操作，请联系管理员开通权限'; break
        case 404: message = '接口地址不存在，请确认后端服务已启动且地址正确'; break
        case 422: message = data?.detail || '数据验证失败，请检查必填字段'; break
        case 500: message = '服务器内部错误 [500]，请查看后端日志排查原因'; break
        default: message = data?.detail || data?.message || `请求异常 [${status}]`
      }
    } else if (error.request) {
      message = '网络连接失败，请检查：① 后端服务是否启动 ② 接口地址是否正确 ③ 网络是否正常'
    } else {
      message = error.message || '请求配置错误'
    }

    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default service
