/**
 * 采购系统 API - 对接 /api/purchase/ 前缀
 */
import request from '@/utils/request'
const prefix = '/api/purchase'
const _crud = (name) => ({
  list: (params) => request.get(`${prefix}/${name}/`, { params }),
  get: (id) => request.get(`${prefix}/${name}/${id}/`),
  create: (data) => request.post(`${prefix}/${name}/`, data),
  update: (id, data) => request.put(`${prefix}/${name}/${id}/`, data),
  delete: (id) => request.delete(`${prefix}/${name}/${id}/`),
})

export const supplierApi = _crud('supplier')
export const purchasePlanApi = _crud('purchase-plan')
export const purchaseOrderApi = _crud('purchase-order')
export const outsourcingOrderApi = _crud('outsourcing-order')
export const changeOrderApi = _crud('change-order')
export const returnOrderApi = _crud('return-order')
export const processPlanApi = _crud('process-plan')
export const order1688Api = _crud('order-1688')
export const supplierReconciliationApi = _crud('supplier-reconciliation')
export const transferOrderApi = _crud('transfer-order')
export const supplierPortalConfigApi = _crud('supplier-portal-config')
export const supplierDeliveryOrderApi = _crud('supplier-delivery-order')
export const account1688AuthApi = _crud('account-1688-auth')
export const sku1688MappingApi = _crud('sku-1688-mapping')
export const supplierMessageApi = _crud('supplier-message')

export default { supplierApi, purchasePlanApi, purchaseOrderApi, outsourcingOrderApi, changeOrderApi, returnOrderApi, processPlanApi, order1688Api, supplierReconciliationApi, transferOrderApi, supplierPortalConfigApi, supplierDeliveryOrderApi }
