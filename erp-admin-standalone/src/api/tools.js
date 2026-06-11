/**
 * 工具系统 API - 对接 /api/tools/ 前缀
 */
import request from '@/utils/request'
const prefix = '/api/tools'
const _crud = (name) => ({
  list: (params) => request.get(`${prefix}/${name}/`, { params }),
  get: (id) => request.get(`${prefix}/${name}/${id}/`),
  create: (data) => request.post(`${prefix}/${name}/`, data),
  update: (id, data) => request.put(`${prefix}/${name}/${id}/`, data),
  delete: (id) => request.delete(`${prefix}/${name}/${id}/`),
})

export const walmartMonitorApi = _crud('walmart-monitor')
export const logisticsQueryApi = _crud('logistics-query')
export const aiModelTaskApi = _crud('ai-model-task')
export const aiCutoutTaskApi = _crud('ai-cutout-task')
export const aiGenerateTaskApi = _crud('ai-generate-task')
export const approvalTypeApi = _crud('approval-type')
export const approvalTaskApi = _crud('approval-task')
export const aiProductCopyApi = _crud('ai-product-copy')
export const alertRuleApi = _crud('alert-rule')
export const alertMessageApi = _crud('alert-message')
export const priceAdjustTaskApi = _crud('price-adjust-task')
export const priceAdjustRuleApi = _crud('price-adjust-rule')
export const priceAdjustLogApi = _crud('price-adjust-log')

export default { walmartMonitorApi, logisticsQueryApi, aiModelTaskApi, aiCutoutTaskApi, aiGenerateTaskApi, approvalTypeApi, approvalTaskApi, aiProductCopyApi, alertRuleApi, alertMessageApi, priceAdjustTaskApi, priceAdjustLogApi }
