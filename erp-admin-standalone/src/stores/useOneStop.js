// 一站式上货状态管理
import { defineStore } from 'pinia'
import { ref, computed, reactive } from 'vue'

// 定价规则模板
export const PRICING_TEMPLATES = [
  { id: 'normal', label: '普通定价', rate: 1.5 },
  { id: 'promotion', label: '活动价', rate: 1.3 },
  { id: 'premium', label: '高端定价', rate: 2.0 },
  { id: 'cost_plus', label: '成本加成', rate: 1.2 },
]

export const useOneStopStore = defineStore('oneStop', () => {
  // ── 核心状态 ──
  const taskList = ref([])
  const listingResults = ref([])
  const batchMode = ref(false)
  const activePricingTemplate = ref('normal')

  // AI 评估结果 { [goodsId]: { grade, profit, reason, platformFit } }
  const aiEvaluations = ref({})

  // 集采模式
  const collectionModeEnabled = ref(false)

  // 待评估商品队列
  const pendingGoods = ref([])
  const pendingCount = computed(() => pendingGoods.value.length)

  // 已选中商品 ID 列表
  const selectedGoods = ref([])

  // 已评估的商品列表（有完整评估数据）
  const evaluatedGoods = ref([])

  // 集采配置
  const collectConfig = reactive({
    targetPlatforms: ['tiktok', 'shopee'],
    pricing: {
      multiplier: 1.5,
      platformCommission: 15,
      logisticsCost: 10,
    },
    filter: {
      mode: 'profit_rate',
      minProfit: 10,
      minProfitRate: 15,
    },
  })

  // 批量进度
  const batchRunning = ref(false)
  const batchProgress = ref(0)
  const batchSuccess = ref(0)
  const batchFail = ref(0)
  const batchTotal = ref(0)

  // ── 按等级分组（用于 UI 展示）──
  const goodsByGrade = computed(() => {
    const map = { recommend: [], okay: [], not_recommended: [] }
    pendingGoods.value.forEach(g => {
      const ev = aiEvaluations.value[g.id] || {}
      const grade = ev.grade || 'okay'
      if (grade === 'recommend') map.recommend.push(g)
      else if (grade === 'not_recommended') map.not_recommended.push(g)
      else map.okay.push(g)
    })
    return map
  })

  const selectedGoodsDetail = computed(() => {
    return selectedGoods.value
      .map(id => evaluatedGoods.value.find(g => g.id === id) || pendingGoods.value.find(g => g.id === id))
      .filter(Boolean)
  })

  // ── 应用定价模板 ──
  function applyPricingTemplate(id) {
    activePricingTemplate.value = id
  }

  // ── 计算单个商品利润 ──
  function calcProfit(goods) {
    const cost = parseFloat(goods.cost || goods.cost_price || 0)
    const freight = parseFloat(goods.freight || 0)
    const tpl = PRICING_TEMPLATES.find(t => t.id === activePricingTemplate.value) || PRICING_TEMPLATES[0]
    const salePrice = cost * tpl.rate
    const profit = salePrice - cost - freight
    const profitRate = cost > 0 ? (profit / cost) * 100 : 0
    return { cost, freight, salePrice, profit, profitRate, template: tpl.label, rate: tpl.rate }
  }

  // ── 评估商品等级 ──
  function evaluateGoods(goods) {
    const profit = calcProfit(goods)
    let grade = 'okay'
    let reason = '符合基本要求'
    if (profit.profit < 5) {
      grade = 'not_recommended'
      reason = `利润过低（仅 ¥${profit.profit.toFixed(2)}），扣除运费后几乎无盈利空间`
    } else if (profit.profit >= 20 && profit.profitRate >= 30) {
      grade = 'recommend'
      reason = `利润空间良好（¥${profit.profit.toFixed(2)}），毛利率 ${profit.profitRate.toFixed(1)}%，建议优先上架`
    } else if (profit.profit >= 10) {
      grade = 'okay'
      reason = '利润处于合理区间，可以上架'
    }
    const platformFit = {}
    ;['tiktok', 'shopee', 'temu', 'shein', 'amazon'].forEach(p => {
      platformFit[p] = profit.profitRate >= 40 ? 'high' : profit.profitRate >= 20 ? 'medium' : 'low'
    })
    aiEvaluations.value[goods.id] = { grade, profit, reason, platformFit }
    return aiEvaluations.value[goods.id]
  }

  function evaluateBatch(goodsList) {
    return goodsList.map(g => evaluateGoods(g))
  }

  // ── 集采工作流 ──
  function addPendingGoods(goods) {
    if (!pendingGoods.value.find(g => g.id === goods.id)) {
      pendingGoods.value.push(goods)
    }
  }

  async function batchEvaluate() {
    evaluatedGoods.value = [...pendingGoods.value]
    evaluatedGoods.value.forEach(g => evaluateGoods(g))
  }

  function toggleSelectGoods(id) {
    const idx = selectedGoods.value.indexOf(id)
    if (idx === -1) selectedGoods.value.push(id)
    else selectedGoods.value.splice(idx, 1)
  }

  function filterByProfitAmount(min) {
    selectedGoods.value = evaluatedGoods.value
      .filter(g => (calcProfit(g).profit || 0) >= min)
      .map(g => g.id)
  }

  function filterByProfitRate(min) {
    selectedGoods.value = evaluatedGoods.value
      .filter(g => (calcProfit(g).profitRate || 0) >= min)
      .map(g => g.id)
  }

  // ── 批量上架 ──
  function startBatch(total) {
    batchRunning.value = true
    batchProgress.value = 0
    batchSuccess.value = 0
    batchFail.value = 0
    batchTotal.value = total
  }

  function updateBatchProgress(success) {
    if (success) batchSuccess.value++
    else batchFail.value++
    batchProgress.value = Math.round(((batchSuccess.value + batchFail.value) / batchTotal.value) * 100)
    if (batchSuccess.value + batchFail.value >= batchTotal.value) {
      batchRunning.value = false
    }
  }

  function markListed(results) {
    listingResults.value = results
  }

  function resetCollectFlow() {
    pendingGoods.value = []
    selectedGoods.value = []
    evaluatedGoods.value = []
    aiEvaluations.value = {}
    listingResults.value = []
    batchProgress.value = 0
    batchSuccess.value = 0
    batchFail.value = 0
    batchTotal.value = 0
    batchRunning.value = false
  }

  function reset() {
    taskList.value = []
    resetCollectFlow()
  }

  return {
    taskList, listingResults, batchMode, activePricingTemplate, aiEvaluations,
    collectionModeEnabled, pendingGoods, pendingCount, selectedGoods, selectedGoodsDetail,
    evaluatedGoods, collectConfig, batchRunning, batchProgress, batchSuccess, batchFail,
    batchTotal, goodsByGrade,
    applyPricingTemplate, calcProfit, evaluateGoods, evaluateBatch,
    addPendingGoods, batchEvaluate, toggleSelectGoods,
    filterByProfitAmount, filterByProfitRate,
    startBatch, updateBatchProgress, markListed,
    resetCollectFlow, reset, PRICING_TEMPLATES,
  }
})
