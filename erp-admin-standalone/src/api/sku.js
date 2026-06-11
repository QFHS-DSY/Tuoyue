/**
 * SKU 管理 API
 * 接口前缀：/api/v1/sku/
 */
import request from '@/utils/request'

/**
 * SKU 列表
 * GET /api/v1/sku/list/
 */
export function fetchSkuList(params) {
  return request.get('/api/v1/sku/list/', { params })
}

/**
 * SKU 详情
 * GET /api/v1/sku/{id}/
 */
export function fetchSkuDetail(id) {
  return request.get(`/api/v1/sku/${id}/`)
}

/**
 * SKU 创建
 * POST /api/v1/sku/
 */
export function createSku(data) {
  return request.post('/api/v1/sku/', data)
}

/**
 * SKU 更新
 * PUT /api/v1/sku/{id}/
 */
export function updateSku(id, data) {
  return request.put(`/api/v1/sku/${id}/`, data)
}

/**
 * SKU 删除
 * DELETE /api/v1/sku/{id}/
 */
export function deleteSku(id) {
  return request.delete(`/api/v1/sku/${id}/`)
}

/**
 * SKU 批量删除
 * POST /api/v1/sku/batch/delete/
 */
export function batchDeleteSku(ids) {
  return request.post('/api/v1/sku/batch/delete/', { ids })
}

/**
 * SKU 批量上架
 * POST /api/v1/sku/batch/online/
 */
export function batchOnlineSku(ids) {
  return request.post('/api/v1/sku/batch/online/', { ids })
}

/**
 * SKU 批量下架
 * POST /api/v1/sku/batch/offline/
 */
export function batchOfflineSku(ids) {
  return request.post('/api/v1/sku/batch/offline/', { ids })
}

/**
 * SKU 导入
 * POST /api/v1/sku/import/
 */
export function importSku(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/api/v1/sku/import/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
}

/**
 * SKU 导出
 * POST /api/v1/sku/export/
 */
export function exportSku(params) {
  return request.post('/api/v1/sku/export/', {}, { params })
}

/**
 * SKU 搜索
 * GET /api/v1/sku/search/
 */
export function searchSku(keyword) {
  return request.get('/api/v1/sku/search/', { params: { keyword } })
}
