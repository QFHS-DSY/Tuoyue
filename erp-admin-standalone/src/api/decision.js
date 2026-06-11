/**
 * 选品决策 API
 * 对接真实 selection_engine + goods API
 */
import axios from '@/utils/request'

/** 搜索商品 - 真实 goods API */
export const searchProducts = (keyword) =>
  axios.get('/api/goods/', { params: { keyword, page: 1, page_size: 20 } })
    .then(res => ({
      data: (res.data?.results || res.data || []).map(g => ({
        id: g.id,
        sku: (g.variants?.[0]?.sku) || `SKU-${g.id}`,
        name: g.title || g.name,
        cost_price: Number(g.price || 0),
        freight: 0,
        commission_rate: 0.08,
      }))
    }))
    .catch(() => axios.get('/api/v1/products/', { params: { search: keyword } }))

/** 计算 ROAS - 对接 selection_engine */
export const calculateDecision = (params) =>
  axios.post('/api/v1/decision/calculate/', {
    product_id: params.product_id || params.productId,
    promotion_cost: params.promotion_cost,
    estimated_revenue: params.expected_gmv,
    commission_rate: params.commission_rate || 0.08,
  })

export default { searchProducts, calculateDecision }
