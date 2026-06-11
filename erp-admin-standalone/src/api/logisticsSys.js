/**
 * 物流系统 API - 对接 /api/logistics/ 前缀
 */
import request from '@/utils/request'
const prefix = '/api/logistics'
const _crud = (name) => ({
  list: (params) => request.get(`${prefix}/${name}/`, { params }),
  get: (id) => request.get(`${prefix}/${name}/${id}/`),
  create: (data) => request.post(`${prefix}/${name}/`, data),
  update: (id, data) => request.put(`${prefix}/${name}/${id}/`, data),
  delete: (id) => request.delete(`${prefix}/${name}/${id}/`),
})

export const providerApi = _crud('provider')
export const channelApi = _crud('channel')
export const shippingOrderApi = _crud('shipping-order')
export const headOrderApi = _crud('head-order')
export const addressBookApi = _crud('address-book')
export const freightTemplateApi = _crud('freight-template')
export const declarationRuleApi = _crud('declaration-rule')
export const trackingPoolApi = _crud('tracking-pool')
export const logisticsPoolApi = _crud('logistics-pool')
export const headReconciliationApi = _crud('head-reconciliation')
export const reconciliationApi = _crud('reconciliation')

export default { providerApi, channelApi, shippingOrderApi, headOrderApi, addressBookApi, freightTemplateApi, declarationRuleApi, trackingPoolApi, logisticsPoolApi, headReconciliationApi, reconciliationApi }
