/**
 * 运维与系统接口
 * 接口 27-34
 */

import axios from 'axios'

const request = axios.create({
  timeout: 15000,
})

request.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

request.interceptors.response.use((response) => response.data, (error) => Promise.reject(error))

// ===================== API 函数 =====================

/**
 * 死信队列列表（接口27）
 * GET /api/ops/dead-letter/
 * @param {Object} params - { queue?, page, page_size }
 */
export const getDeadLetterList = (params) =>
  request.get('/api/ops/dead-letter/', { params })

/**
 * 重新处理死信消息（接口27）
 * POST /api/ops/dead-letter/{id}/retry/
 * @param {number} id
 */
export const retryDeadLetter = (id) =>
  request.post(`/api/ops/dead-letter/${id}/retry/`)

/**
 * 审计日志列表（接口28）
 * GET /api/ops/audit/
 * @param {Object} params - { user?, action?, start_date?, end_date?, page, page_size }
 */
export const getAuditLog = (params) =>
  request.get('/api/ops/audit/', { params })

/**
 * 权限列表（接口29）
 * GET /api/ops/permissions/
 */
export const getPermissionList = () =>
  request.get('/api/ops/permissions/')

/**
 * 健康检查（接口31）
 * GET /api/health/
 */
export const healthCheck = () =>
  request.get('/api/health/')

/**
 * OpenAPI Schema（接口32）
 * GET /api/schema/
 */
export const getSchema = () =>
  request.get('/api/schema/')

/**
 * Swagger UI（接口33）
 * 返回 Swagger 地址
 */
export const getSwaggerUrl = () => `/api/docs`

/**
 * Redoc（接口34）
 * 返回 Redoc 地址
 */
export const getRedocUrl = () => `/api/redoc`

export default {
  getDeadLetterList,
  retryDeadLetter,
  getAuditLog,
  getPermissionList,
  healthCheck,
  getSchema,
  getSwaggerUrl,
  getRedocUrl,
}
