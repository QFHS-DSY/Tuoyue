/**
 * 通用表格页逻辑 Composable
 * 封装分页列表的 loading、data、pagination 逻辑
 * 各业务模块可复用，减少重复代码
 *
 * 用法：
 *   const { loading, list, pagination, loadData } = useTablePage(fetchGoodsList)
 *   loadData()                  // 初始加载
 *   loadData({ keyword: 'xx' }) // 带参数搜索
 */

import { ref, reactive } from 'vue'

/**
 * @param {Function} fetchFn - 数据请求函数，接收 { page, page_size, ...extra } 参数
 * @returns {{ loading, list, pagination, loadData, reset }}
 */
export function useTablePage(fetchFn) {
  const loading = ref(false)
  const list = ref([])
  const pagination = reactive({
    page: 1,
    pageSize: 20,
    total: 0,
  })

  /**
   * 加载数据
   * @param {Object} extra - 额外查询参数
   */
  async function loadData(extra = {}) {
    loading.value = true
    try {
      const params = {
        page: pagination.page,
        page_size: pagination.pageSize,
        ...extra,
      }
      const res = await fetchFn(params)
      // 兼容不同后端返回格式：data / results / list
      list.value = res.data || res.results || res.list || []
      pagination.total = res.total || res.count || 0
    } finally {
      loading.value = false
    }
  }

  /** 重置到第一页并重新加载 */
  function reset(extra = {}) {
    pagination.page = 1
    loadData(extra)
  }

  return {
    loading,
    list,
    pagination,
    loadData,
    reset,
  }
}
