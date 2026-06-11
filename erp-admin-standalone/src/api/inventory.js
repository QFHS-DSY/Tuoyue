/**
 * 库存管理 API
 * 连接到后端真实数据库操作
 */
import request from '@/utils/request'

/**
 * 库存列表
 * GET /api/goods/
 * @param {Object} params - { page, page_size, platform?, keyword?, status? }
 */
export function getInventoryList(params = {}) {
  return request.get('/api/goods/', { params })
}

/**
 * 库存预警
 * GET /api/inventory/alerts
 * @param {Object} params - { threshold? }
 */
export function getInventoryAlerts(params = {}) {
  return request.get('/api/inventory/alerts', { params })
}

/**
 * SKU 详情
 * GET /api/sku/detail/{skuCode}/
 * @param {string} sku - SKU 编码
 */
export function getSkuDetail(sku) {
  return request.get(`/api/sku/detail/${sku}/`)
}

/**
 * 手动触发库存同步
 * POST /api/inventory/sync
 */
export function triggerInventorySync() {
  return request.post('/api/inventory/sync')
}

/**
 * 库存同步日志
 * GET /api/inventory/logs
 */
export function getInventoryLogs(params = {}) {
  return request.get('/api/inventory/logs', { params })
}

/**
 * 库存调整 - 新增入库/出库记录
 * POST /api/inventory/adjust/
 * @param {Object} data - { sku, warehouse_code, adjustment_type, quantity, reason }
 */
export function adjustInventory(data) {
  return request.post('/api/inventory/adjust', data)
}

/**
 * 新增商品建档
 * POST /api/goods/
 * @param {Object} data - { title, platform_product_id, stock, platform }
 */
export function addProduct(data) {
  return request.post('/api/goods/', data)
}

/**
 * 删除商品
 * DELETE /api/goods/{id}
 * @param {number} id - 商品主键 ID
 */
export function deleteProduct(id) {
  return request.delete(`/api/goods/${id}`)
}

/**
 * 库存概览统计
 * GET /api/inventory/overview?warehouse=xxx
 * 返回: { total_stock, total_sku, alert_count, out_of_stock_count, recent_syncs }
 */
export function getInventoryOverview(warehouse) {
  const params = warehouse ? { warehouse } : {}
  return request.get('/api/inventory/overview', { params })
}

/**
 * 仓库列表（目前从前端内置，后续可从后端获取）
 */
export function getWarehouseList() {
  return request.get('/api/shops/').then(res => ({
    code: 200,
    data: res?.data || ['深圳仓', '广州仓', '海外仓(英国)'],
  })).catch(() => ({
    code: 200,
    data: ['深圳仓', '广州仓', '海外仓(英国)'],
  }))
}
