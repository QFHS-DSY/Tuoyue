/**
 * 物流追踪 API
 * 对接真实后端 Django DRF
 */
import request from '@/utils/request'

/** 获取物流列表 - GET /api/logistics/shipments/ */
export function getShipmentList(params = {}) {
  return request.get('/api/logistics/shipments/', { params })
}

/** 获取物流统计（从列表数据本地计算，后端也可返回 stats） */
export function getLogisticsStats() {
  return request.get('/api/logistics/shipments/', { params: { page: 1, page_size: 1000 } })
    .then(res => {
      const results = res?.data?.results || []
      return {
        code: 200,
        data: {
          pending: results.filter(s => s.status === 'pending').length,
          transit: results.filter(s => s.status === 'in_transit').length,
          delivering: results.filter(s => s.status === 'in_transit').length,
          delivered: results.filter(s => s.status === 'delivered').length,
          exception: results.filter(s => s.status === 'exception').length,
        }
      }
    })
    .catch(() => ({ code: 200, data: { pending: 0, transit: 0, delivering: 0, delivered: 0, exception: 0 } }))
}

/** 获取物流轨迹详情 - GET /api/logistics/track/{waybill}/ */
export function getShipmentTrack(waybillNo) {
  return request.get(`/api/logistics/track/${waybillNo}`)
}

/** 同步物流信息 - POST /api/logistics/sync/ */
export function syncLogistics(waybillNos = []) {
  return request.post('/api/logistics/sync/', { waybill_nos: waybillNos })
}

/** 运费预估 - POST /api/logistics/freight-estimate */
export function estimateFreight(data) {
  return request.post('/api/logistics/freight-estimate', data)
}

/** 物流商列表 */
export function getCarrierList() {
  return request.get('/api/logistics/carriers/').then(res => ({ code: 200, data: res?.data || [] }))
    .catch(() => ({ code: 200, data: [] }))
}

/** 订阅物流轨迹 */
export function subscribeTrack(waybillNo, callbackUrl) {
  return request.post('/api/logistics/subscribe/', { waybill_no: waybillNo, callback_url: callbackUrl })
}

export default { getShipmentList, getLogisticsStats, getShipmentTrack, syncLogistics, estimateFreight, getCarrierList, subscribeTrack }
