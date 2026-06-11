/**
 * 选品决策状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { searchProducts, calculateDecision } from '@/api/decision'

export const useDecisionStore = defineStore('decision', () => {
  // 当前选中的商品
  const currentProduct = ref(null)
  
  // 搜索结果列表
  const searchResults = ref([])
  
  // 用户调节的参数
  const calcParams = ref({
    promotion_cost: 1000,    // 预期宣传费用
    expected_gmv: 5000,      // 预估GMV
  })
  
  // 最近一次计算结果
  const lastResult = ref(null)
  
  // 加载状态
  const loading = ref(false)
  const calculating = ref(false)
  
  // 搜索商品（防抖由组件处理）
  async function search(keyword) {
    if (!keyword?.trim()) {
      searchResults.value = []
      return
    }
    loading.value = true
    try {
      const res = await searchProducts(keyword)
      searchResults.value = res.data || []
    } catch (e) {
      console.error('商品搜索失败', e)
      searchResults.value = []
    } finally {
      loading.value = false
    }
  }
  
  // 选择商品
  function selectProduct(product) {
    currentProduct.value = product
    // 重置参数
    calcParams.value = {
      promotion_cost: 1000,
      expected_gmv: 5000,
    }
    lastResult.value = null
  }
  
  // 执行测算
  async function calculate() {
    if (!currentProduct.value) return
    calculating.value = true
    try {
      const res = await calculateDecision({
        product_id: currentProduct.value.id,
        ...calcParams.value,
      })
      lastResult.value = res.data
      return res.data
    } catch (e) {
      console.error('测算失败', e)
      lastResult.value = null
      return null
    } finally {
      calculating.value = false
    }
  }
  
  // 重置
  function reset() {
    currentProduct.value = null
    searchResults.value = []
    calcParams.value = {
      promotion_cost: 1000,
      expected_gmv: 5000,
    }
    lastResult.value = null
  }
  
  return {
    currentProduct,
    searchResults,
    calcParams,
    lastResult,
    loading,
    calculating,
    search,
    selectProduct,
    calculate,
    reset,
  }
})
