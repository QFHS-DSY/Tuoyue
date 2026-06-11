/**
 * 产品系统 API - 对接 /api/product-sys/ 前缀
 */
import request from '@/utils/request'
const prefix = '/api/product-sys'
const _crud = (name) => ({
  list: (params) => request.get(`${prefix}/${name}/`, { params }),
  get: (id) => request.get(`${prefix}/${name}/${id}/`),
  create: (data) => request.post(`${prefix}/${name}/`, data),
  update: (id, data) => request.put(`${prefix}/${name}/${id}/`, data),
  delete: (id) => request.delete(`${prefix}/${name}/${id}/`),
})

export const productApi = _crud('product')
export const productSkuApi = _crud('product-sku')
export const spuInfoApi = _crud('spu-info')
export const developmentTaskApi = _crud('development-task')
export const bundleProductApi = _crud('bundle-product')
export const accessoryApi = _crud('accessory')
export const upcCodeApi = _crud('upc-code')
export const transparencyAccountApi = _crud('transparency-account')
export const transparencyProductApi = _crud('transparency-product')
export const brandApi = _crud('brand')
export const categoryApi = _crud('category')
export const attributeApi = _crud('attribute')
export const qualityTemplateApi = _crud('quality-template')
export const platformMatchApi = _crud('platform-match')
export const matchRuleApi = _crud('match-rule')
export const alibabaMatchApi = _crud('alibaba-match')

export default { productApi, spuInfoApi, developmentTaskApi, bundleProductApi, accessoryApi, upcCodeApi, transparencyAccountApi, brandApi, categoryApi, attributeApi, qualityTemplateApi, platformMatchApi, matchRuleApi, alibabaMatchApi }
