/**
 * 销售系统 API - 对接 /api/sales/ 前缀
 */
import request from '@/utils/request'
const prefix = '/api/sales'
const _crud = (name) => ({
  list: (params) => request.get(`${prefix}/${name}/`, { params }),
  get: (id) => request.get(`${prefix}/${name}/${id}/`),
  create: (data) => request.post(`${prefix}/${name}/`, data),
  update: (id, data) => request.put(`${prefix}/${name}/${id}/`, data),
  delete: (id) => request.delete(`${prefix}/${name}/${id}/`),
})

export const amazonListingApi = _crud('amazon-listing')
export const listingSkuMappingApi = _crud('listing-sku-mapping')
export const listingOwnerApi = _crud('listing-owner')
export const listingPerformanceApi = _crud('listing-performance')
export const listingTagApi = _crud('listing-tag')
export const listingPriceAdjustApi = _crud('listing-price-adjust')
export const listingPriceQueueApi = _crud('listing-price-queue')
export const platformProductApi = _crud('platform-product')
export const alibabaProductApi = _crud('alibaba-product')
export const shopeeProductApi = _crud('shopee-product')
export const ebayProductApi = _crud('ebay-product')
export const walmartProductApi = _crud('walmart-product')
export const listingTaskApi = _crud('listing-task')
export const listingTemplateApi = _crud('listing-template')
export const listingQueueApi = _crud('listing-queue')
export const inventorySyncTaskApi = _crud('inventory-sync-task')
export const priceInfoApi = _crud('price-info')
export const priceAdjustLogApi = _crud('price-adjust-log')
export const temuPricingApi = _crud('temu-pricing')

export default { amazonListingApi, listingSkuMappingApi, listingOwnerApi, listingTaskApi, listingTemplateApi, platformProductApi, inventorySyncTaskApi, priceInfoApi, temuPricingApi }
