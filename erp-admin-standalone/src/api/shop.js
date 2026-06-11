/**
 * 店铺管理 API — 对接真实后端
 */
import request from '@/utils/request'

/** 获取店铺列表 - GET /api/shops/ */
export function getShopList() {
  return request.get('/api/shops/')
}

/** 获取平台授权 URL - GET /api/auth/{platform}/login/ */
export function getAuthUrl(platformCode) {
  return request.get(`/api/auth/${platformCode}/login/`)
}

/** 刷新授权 - POST /api/auth/{platform}/refresh/ */
export function refreshAuth(shopId) {
  return request.post('/api/auth/shop/refresh/', { shop_id: shopId })
}

/** 解绑店铺 */
export function unbindShop(shopId) {
  return request.post('/api/shops/unbind/', { shop_id: shopId })
}
