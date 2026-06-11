/**
 * axios 请求封装
 * 所有 API 请求统一通过此模块发出
 *
 * 规范：
 * - 不走 baseURL，通过 Vite proxy 同源代理到后端 8000
 * - 自动附加 Authorization token
 * - 401 时自动尝试 refresh token 续期
 * - 统一错误处理，弹出 ElMessage 提示
 * - 响应 data 透传，直接拿到业务数据
 */

import axios from 'axios'
import { ElMessage } from 'element-plus'

const service = axios.create({
  timeout: 15000,
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
  // 只跳转一次，避免重复触发
  if (window.location.pathname !== '/login') {
    window.location.href = '/login'
  }
}

async function tryRefreshToken() {
  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) return null

  try {
    // 用裸 axios 请求，避免进入本拦截器死循环
    const res = await axios.post('/api/auth/refresh', {
      refresh_token: refreshToken,
    }, { timeout: 10000 })

    const payload = res.data
    // 兼容两种响应格式: { code:200, data:{ access_token, refresh_token } }
    // 或 { access_token, refresh_token }
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

// ==================== 请求拦截器 ====================
service.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ==================== 响应拦截器 ====================
const MAX_RETRIES = 2; const RETRY_DELAY = 1000

service.interceptors.response.use(
  (response) => {
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

    // ── 401 处理：尝试 Token 自动刷新 ──
    if (error.response?.status === 401 && !originalRequest._retry) {
      // 不要对 refresh 请求本身重试
      if (originalRequest.url?.includes('/api/auth/refresh')) {
        logout()
        return Promise.reject(error)
      }

      if (isRefreshing) {
        // 已有刷新在进行中，将请求加入等待队列
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

    // ── 通用错误处理（含解决方案指引）──
    let message = '请求失败，已自动重试2次仍失败，请检查网络或稍后重试'
    if (error.response) {
      const { status, data } = error.response
      switch (status) {
        case 400:
          // DRF 字段级校验: {"field_name": ["error message"]}
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
        case 404: message = '接口地址不存在，请确认后端服务已启动且地址正确（开发环境: http://127.0.0.1:8000）'; break
        case 422: message = data?.detail || '数据验证失败，请检查必填字段'; break
        case 500: message = '服务器内部错误 [500]，请查看后端日志排查原因'; break
        default: message = data?.detail || data?.message || `请求异常 [${status}]`
      }
    } else if (error.request) {
      message = '网络连接失败 [ERR_CONNECTION_REFUSED]，请检查：① 后端服务是否启动 ② 接口地址是否正确 ③ 网络是否正常'
    } else {
      message = error.message || '请求配置错误'
    }

    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default service
