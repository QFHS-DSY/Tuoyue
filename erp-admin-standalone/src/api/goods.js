/**
 * 商品管理 API
 * 接口前缀：/api/v1/goods/
 */

import request from '@/utils/request'

/** 商品列表 */
export function fetchGoodsList(params) {
  return request.get('/api/v1/goods/list', { params })
}

/** 商品详情 */
export function fetchGoodsDetail(id) {
  return request.get(`/api/v1/goods/detail/${id}/`)
}

/** 上架商品到目标平台
 * POST /api/v1/goods/listing/
 * @param {Object} payload - { goods_id, platform, title, description, price, images }
 */
export function listingGoods(payload) {
  return request.post('/api/v1/goods/listing/', payload)
}

/** 批量上架
 * POST /api/v1/goods/listing/batch/
 */
export function listingGoodsBatch(payload) {
  return request.post('/api/v1/goods/listing/batch/', payload)
}
