/**
 * 订单管理 API
 * 对接真实后端 Django DRF
 */
import request from '@/utils/request'

/** 获取订单列表 - GET /api/orders/ */
export function getOrderList(params = {}) {
  return request.get('/api/orders/', { params })
}

/** 获取订单状态统计 - GET /api/orders/status-counts/ */
export function getOrderStatusCounts() {
  return request.get('/api/orders/status-counts/')
}

/** 获取订单详情 - 从列表数据构建，或 GET /api/orders/{id}/ */
export function getOrderDetail(id) {
  return request.get(`/api/orders/${id}/`)
}

/** 确认订单 - POST /api/orders/{id}/confirm/ */
export function confirmOrder(id) {
  return request.post(`/api/orders/${id}/confirm/`)
}

/** 发货 - POST /api/orders/{id}/ship/ */
export function shipOrder(id, data) {
  return request.post(`/api/orders/${id}/ship/`, data)
}

/** 取消订单 - POST /api/orders/{id}/cancel/ */
export function cancelOrder(id, reason) {
  return request.post(`/api/orders/${id}/cancel/`, { reason })
}

/** 修改订单地址 - PUT /api/orders/{id}/address */
export function updateOrderAddress(id, data) {
  return request.put(`/api/orders/${id}/address`, data)
}

/** 更新订单状态 - PUT /api/orders/{id}/status */
export function updateOrderStatus(id, status) {
  return request.put(`/api/orders/${id}/status`, { status })
}

/** 添加订单备注 */
export function addOrderRemark(id, content) {
  return request.post(`/api/orders/${id}/remark/`, { content })
}

/** 导出订单 CSV - GET /api/orders/export */
export function exportOrders(params) {
  return request.get('/api/orders/export', { params, responseType: 'blob' })
}

export default { getOrderList, getOrderStatusCounts, getOrderDetail, confirmOrder, shipOrder, cancelOrder, updateOrderAddress, updateOrderStatus, addOrderRemark, exportOrders }
