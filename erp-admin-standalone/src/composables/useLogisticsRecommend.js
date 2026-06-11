/**
 * 物流推荐 composable
 * 根据目标平台 + 商品特征推荐最优物流方案
 */
import { ref } from 'vue'

/** 各平台推荐物流方案 */
const LOGISTICS_PLANS = {
  tiktok: [
    { id: 'tiktok_fulfill', name: 'TikTok 本地仓发货', desc: '平台仓储+履约，时效1-3天', fee: '平台代收', days: '1-3天', recommended: true, suitable: '已提前备货到TikTok海外仓' },
    { id: 'yunexpress', name: '云途专线（小包）', desc: '小包直发，TikTok专属绿色通道', fee: '¥35-55/kg', days: '8-12天', recommended: false, suitable: '轻小件（<2kg），日销50单以内' },
    { id: 'yanwen', name: '燕文追踪小包', desc: '价格优，适合普货', fee: '¥28-45/kg', days: '12-18天', recommended: false, suitable: '低价普货，不着急补货' },
  ],
  shopee: [
    { id: 'shopee_sls', name: 'SLS 物流（Shopee推荐）', desc: '平台整合物流，覆盖东南亚全境', fee: '¥25-50/kg', days: '5-10天', recommended: true, suitable: 'Shopee马来/越南/菲律宾主力渠道' },
    { id: 'bestexpress', name: '百世跨境', desc: '东南亚专线，覆盖广', fee: '¥30-48/kg', days: '6-12天', recommended: false, suitable: 'Shopee泰国/印尼路线' },
    { id: 'singapore_post', name: '新加坡小包', desc: '时效稳定，清关能力强', fee: '¥40-60/kg', days: '7-10天', recommended: false, suitable: '高价值商品，清关风险高地区' },
  ],
  temu: [
    { id: 'temu_fulfill', name: 'Temu 半托管/全托管', desc: '平台负责仓储和配送', fee: '平台定价', days: '1-5天', recommended: true, suitable: 'Temu全托管：工厂型卖家走 JIT 补货模式' },
    { id: 'dehao', name: '德豪专线（小包）', desc: 'Temu合作服务商，时效快', fee: '¥32-50/kg', days: '7-12天', recommended: false, suitable: 'Temu半托管：自己负责头程物流' },
  ],
  shein: [
    { id: 'shein_fulfill', name: 'SHEIN 直发', desc: '供应商直发，时效宽松', fee: '¥20-40/kg', days: '10-20天', recommended: true, suitable: 'SHEIN专属供货商，走平台指定物流' },
  ],
  aliexpress: [
    { id: 'ali_standard', name: 'AliExpress Standard Shipping', desc: '平台标准物流，覆盖全球', fee: '¥28-50/kg', days: '10-25天', recommended: true, suitable: 'AliExpress主力渠道，适合普货' },
    { id: 'cainiao', name: '菜鸟特货专线', desc: '阿里系物流，清关能力强', fee: '¥30-55/kg', days: '8-15天', recommended: false, suitable: '高价值商品，欧洲路线优先' },
  ],
  amazon: [
    { id: 'fba', name: 'FBA（Fulfillment by Amazon）', desc: '亚马逊仓储+配送，Buy Box权重高', fee: 'FBA费用表', days: '1-3天', recommended: true, suitable: '北美/欧洲站，必须FBA才能拿Buy Box' },
    { id: 'seller_fulfilled', name: '自发货（MFN）', desc: '自己找物流商，灵活但权重低', fee: '自选', days: '7-20天', recommended: false, suitable: '大件商品或已有海外仓' },
  ],
  ebay: [
    { id: 'ebay_gsp', name: 'GSP 全球运输计划', desc: '平台中转，卖家只发国内', fee: 'ebay代收', days: '10-20天', recommended: true, suitable: 'ebay新手，不想处理国际物流' },
    { id: 'dhl_express', name: 'DHL Express', desc: '快时效，清关能力强', fee: '¥80-150/kg', days: '3-7天', recommended: false, suitable: '高价值商品（>$50），美国/欧洲' },
  ],
  lazada: [
    { id: 'lazada_ship', name: 'Lazada 跨境物流（LGS）', desc: 'Lazada官方物流，整合头程+清关+尾程', fee: '¥25-45/kg', days: '7-12天', recommended: true, suitable: 'Lazada全站点，标准跨境渠道' },
    { id: 'sjlogistics', name: '森鸿/递四方', desc: '东南亚专线，覆盖 Lazada 核心市场', fee: '¥28-42/kg', days: '8-14天', recommended: false, suitable: '印尼/泰国路线' },
  ],
  mercado: [
    { id: 'mercado_correo', name: 'Mercado Envíos Flex', desc: '平台物流，巴西本地配送', fee: '平台定价', days: '1-3天（本地）', recommended: true, suitable: '已在巴西本地有库存' },
    { id: 'brazil_post', name: '巴西邮政小包', desc: '覆盖广，价格低，清关较慢', fee: '¥35-55/kg', days: '20-40天', recommended: false, suitable: '低价普货，不着急到货' },
  ],
  ozon: [
    { id: 'ozon_fulfill', name: 'Ozon Fulfillment', desc: '平台仓储发货，配送快', fee: 'Ozon仓储费', days: '1-3天', recommended: true, suitable: 'Ozon俄罗斯主力，FBO模式' },
    { id: 'russian_post', name: '俄罗斯邮政小包', desc: '偏远地区覆盖全', fee: '¥30-50/kg', days: '15-30天', recommended: false, suitable: '俄罗斯偏远地区' },
  ],
  allegro: [
    { id: 'allegro_one', name: 'Allegro One', desc: '波兰平台物流，欧洲覆盖', fee: '平台定价', days: '1-3天（本地）', recommended: true, suitable: 'Allegro波兰站，已在欧盟备货' },
    { id: 'dhl_polska', name: 'DHL 波兰', desc: '西欧-中东欧专线', fee: '¥50-80/kg', days: '3-7天', recommended: false, suitable: '高价值商品' },
  ],
}

export function useLogisticsRecommend() {
  /**
   * 获取某平台推荐的物流方案
   */
  function getRecommended(platformId, goods = {}) {
    const ids = Array.isArray(platformId) ? platformId : [platformId]
    const allPlans = []
    const seen = new Set()

    for (const id of ids) {
      const plans = LOGISTICS_PLANS[id] || []
      for (const plan of plans) {
        if (!seen.has(plan.id)) {
          seen.add(plan.id)
          allPlans.push(plan)
        }
      }
    }

    allPlans.sort((a, b) => (b.recommended ? 1 : 0) - (a.recommended ? 1 : 0))
    return allPlans
  }

  /**
   * 快速推荐：最适合新卖家的方案
   */
  function getBestForNewSeller(platformId) {
    const plans = LOGISTICS_PLANS[platformId] || []
    return plans.find(p => p.recommended) || plans[0] || null
  }

  return { getRecommended, getBestForNewSeller }
}
