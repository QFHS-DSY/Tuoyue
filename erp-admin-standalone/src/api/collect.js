/**
 * 商品采集 API
 * 接口前缀：/api/v1/collect/
 * 接口文档：嘉瑞 Swagger 21个接口
 */
import request from '@/utils/request'

// ==================== 1688 采集 ====================

/**
 * 1688 单链接采集
 * POST /api/v1/collect/1688/single/
 */
export function collect1688Single(payload) {
  return request.post('/api/v1/collect/1688/single/', payload)
}

/**
 * 1688 批量采集
 * POST /api/v1/collect/1688/batch/
 */
export function collect1688Batch(payload) {
  return request.post('/api/v1/collect/1688/batch/', payload)
}

// ==================== 平台授权 ====================

/**
 * 1688 授权登录
 * POST /api/v1/collect/1688/auth/login/
 */
export function auth1688Login() {
  return request.post('/api/v1/collect/1688/auth/login/')
}

/**
 * 1688 授权回调
 * GET /api/v1/collect/1688/auth/callback/
 */
export function auth1688Callback(params) {
  return request.get('/api/v1/collect/1688/auth/callback/', { params })
}

/**
 * 1688 授权状态查询
 * GET /api/v1/collect/1688/auth/status/
 */
export function auth1688Status() {
  return request.get('/api/v1/collect/1688/auth/status/')
}

/**
 * 1688 登出
 * POST /api/v1/collect/1688/auth/logout/
 */
export function auth1688Logout() {
  return request.post('/api/v1/collect/1688/auth/logout/')
}

/**
 * TikTok 授权登录
 * POST /api/v1/collect/tiktok/auth/login/
 */
export function authTiktokLogin() {
  return request.post('/api/v1/collect/tiktok/auth/login/')
}

/**
 * TikTok 授权回调
 * GET /api/v1/collect/tiktok/auth/callback/
 */
export function authTiktokCallback(params) {
  return request.get('/api/v1/collect/tiktok/auth/callback/', { params })
}

/**
 * TikTok 授权状态查询
 * GET /api/v1/collect/tiktok/auth/status/
 */
export function authTiktokStatus() {
  return request.get('/api/v1/collect/tiktok/auth/status/')
}

/**
 * TikTok 登出
 * POST /api/v1/collect/tiktok/auth/logout/
 */
export function authTiktokLogout() {
  return request.post('/api/v1/collect/tiktok/auth/logout/')
}

/**
 * Amazon 授权登录
 * POST /api/v1/collect/amazon/auth/login/
 */
export function authAmazonLogin() {
  return request.post('/api/v1/collect/amazon/auth/login/')
}

/**
 * Amazon 授权回调
 * GET /api/v1/collect/amazon/auth/callback/
 */
export function authAmazonCallback(params) {
  return request.get('/api/v1/collect/amazon/auth/callback/', { params })
}

/**
 * Amazon 授权状态查询
 * GET /api/v1/collect/amazon/auth/status/
 */
export function authAmazonStatus() {
  return request.get('/api/v1/collect/amazon/auth/status/')
}

/**
 * Amazon 登出
 * POST /api/v1/collect/amazon/auth/logout/
 */
export function authAmazonLogout() {
  return request.post('/api/v1/collect/amazon/auth/logout/')
}

// ==================== 采集任务 ====================

/**
 * 创建采集任务
 * POST /api/v1/collect/task/
 */
export function createTask(payload) {
  return request.post('/api/v1/collect/task/', payload)
}

/**
 * 采集任务列表
 * GET /api/v1/collect/task/list/
 */
export function fetchTaskList(params) {
  return request.get('/api/v1/collect/task/list/', { params })
}

/**
 * 采集任务详情
 * GET /api/v1/collect/task/{id}/
 */
export function fetchTaskDetail(id) {
  return request.get(`/api/v1/collect/task/${id}/`)
}

/**
 * 采集任务状态查询
 * GET /api/v1/collect/task/{id}/status/
 */
export function fetchTaskStatus(id) {
  return request.get(`/api/v1/collect/task/${id}/status/`)
}

/**
 * 取消采集任务
 * POST /api/v1/collect/task/{id}/cancel/
 */
export function cancelTask(id) {
  return request.post(`/api/v1/collect/task/${id}/cancel/`)
}

/**
 * 删除采集任务
 * DELETE /api/v1/collect/task/{id}/
 */
export function deleteTask(id) {
  return request.delete(`/api/v1/collect/task/${id}/`)
}

/**
 * 批量采集多链接
 * POST /api/v1/collect/batch/scrape/
 */
export function batchScrape(urls, platform = '') {
  return request.post('/api/v1/collect/batch/scrape/', { urls, platform })
}

/**
 * 导出采集数据
 * POST /api/v1/collect/export/
 */
export function exportCollected(productIds, format = 'xlsx') {
  return request.post('/api/v1/collect/export/', {
    product_ids: productIds,
    format,
  }, { responseType: 'blob' })
}

// ==================== 库存同步 ====================

/**
 * 触发库存同步
 * POST /api/v1/inventory/sync/trigger/
 */
export function triggerInventorySync() {
  return request.post('/api/v1/inventory/sync/trigger/')
}

/**
 * 库存同步日志
 * GET /api/v1/inventory/sync/log/
 */
export function fetchInventoryLog(params) {
  return request.get('/api/v1/inventory/sync/log/', { params })
}
