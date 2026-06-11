/**
 * 仓库管理系统 API - 对接 /api/wms/ 前缀
 */
import request from '@/utils/request'
const prefix = '/api/wms'
const _crud = (name) => ({
  list: (params) => request.get(`${prefix}/${name}/`, { params }),
  get: (id) => request.get(`${prefix}/${name}/${id}/`),
  create: (data) => request.post(`${prefix}/${name}/`, data),
  update: (id, data) => request.put(`${prefix}/${name}/${id}/`, data),
  delete: (id) => request.delete(`${prefix}/${name}/${id}/`),
})

export const warehouseApi = _crud('warehouse')
export const inventoryApi = _crud('inventory')
export const inventoryBatchApi = _crud('inventory-batch')
export const receiptApi = _crud('receipt')
export const deliveryApi = _crud('delivery')
export const transferApi = _crud('transfer')
export const inventoryCheckApi = _crud('inventory-check')
export const stockFlowApi = _crud('stock-flow')
export const waveApi = _crud('wave')
export const packingTaskApi = _crud('packing-task')
export const productApi = _crud('product')
export const overseasStockingApi = _crud('overseas-stocking')

export default { warehouseApi, inventoryApi, receiptApi, deliveryApi, transferApi, inventoryCheckApi, stockFlowApi, waveApi, packingTaskApi, productApi, overseasStockingApi }
