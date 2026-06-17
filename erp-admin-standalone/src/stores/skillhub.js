/**
 * SkillHub 技能商城 Pinia Store
 * 管理技能搜索、筛选、安装、卸载等状态
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  fetchSkillLabels,
  querySkills,
  downloadSkill,
  getInstalledSkills,
  saveInstalledSkill,
  removeInstalledSkill,
  isSkillInstalled,
} from '@/api/skillhub'

export const useSkillHubStore = defineStore('skillhub', () => {
  // ── 状态 ──
  const labels = ref([])           // 标签分组 [{ groupName, labels: [{id, name}] }]
  const skills = ref([])           // 当前技能列表
  const loading = ref(false)       // 列表加载中
  const installing = ref(false)    // 安装进行中
  const error = ref(null)          // 错误信息

  // 筛选条件
  const filters = ref({
    keywords: '',
    labelIds: '',
    orderBy: 'default',   // default | new | hot
    payable: undefined,   // true | false | undefined(全部)
    pageIndex: 1,
    size: 20,
  })

  // 分页
  const nextPosition = ref('')
  const totalCount = ref(0)

  // 已安装列表
  const installedSkills = ref(getInstalledSkills())

  // ── 计算属性 ──
  const installedSlugs = computed(() => {
    return new Set(installedSkills.value.map(s => s.slug))
  })

  // 按分组聚合标签（方便前端展示）
  const labelGroups = computed(() => {
    return labels.value.map(group => ({
      groupName: group.groupName,
      items: (group.labels || []).map(l => ({
        id: String(l.id),
        name: l.name,
      })),
    }))
  })

  // ── 方法 ──

  /** 加载标签分组 */
  async function loadLabels() {
    try {
      const res = await fetchSkillLabels()
      if (res && res.data) {
        labels.value = res.data
      } else if (Array.isArray(res)) {
        labels.value = res
      }
    } catch (e) {
      console.warn('[SkillHub] 加载标签失败:', e.message)
      // 不阻断流程
    }
  }

  /** 搜索/筛选技能 */
  async function searchSkills(overrideFilters = {}) {
    loading.value = true
    error.value = null
    try {
      // 合并筛选参数
      const params = { ...filters.value, ...overrideFilters }
      // 更新 filters（保持状态同步）
      if (overrideFilters.keywords !== undefined) filters.value.keywords = overrideFilters.keywords
      if (overrideFilters.labelIds !== undefined) filters.value.labelIds = overrideFilters.labelIds
      if (overrideFilters.orderBy !== undefined) filters.value.orderBy = overrideFilters.orderBy
      if (overrideFilters.payable !== undefined) filters.value.payable = overrideFilters.payable
      if (overrideFilters.pageIndex !== undefined) filters.value.pageIndex = overrideFilters.pageIndex
      if (overrideFilters.size !== undefined) filters.value.size = overrideFilters.size

      const res = await querySkills({
        keywords: params.keywords,
        labelIds: params.labelIds,
        orderBy: params.orderBy,
        payable: params.payable,
        position: params.pageIndex > 1 ? nextPosition.value : '',
        size: params.size,
        pageIndex: params.pageIndex,
      })

      if (res && res.data) {
        const data = res.data
        skills.value = data.items || data.records || []
        nextPosition.value = data.nextPosition || ''
        totalCount.value = data.total || data.totalCount || skills.value.length
      } else if (Array.isArray(res)) {
        skills.value = res
      }
    } catch (e) {
      error.value = e.message || '搜索失败'
      console.error('[SkillHub] 搜索失败:', e)
    } finally {
      loading.value = false
    }
  }

  /** 加载下一页 */
  async function loadMore() {
    if (!nextPosition.value) return
    loading.value = true
    try {
      const res = await querySkills({
        ...filters.value,
        position: nextPosition.value,
      })
      if (res && res.data) {
        const data = res.data
        const newItems = data.items || data.records || []
        skills.value = [...skills.value, ...newItems]
        nextPosition.value = data.nextPosition || ''
      }
    } catch (e) {
      console.error('[SkillHub] 加载更多失败:', e)
    } finally {
      loading.value = false
    }
  }

  /** 安装技能 */
  async function installSkill(skill) {
    installing.value = true
    try {
      // 尝试下载 ZIP 包
      const blob = await downloadSkill(skill.slug || skill.id)
      // 保存到本地已安装列表
      saveInstalledSkill({
        slug: skill.slug || skill.id,
        name: skill.name,
        description: skill.description,
        source: skill.source,
        sourceUrl: skill.sourceUrl,
        priceType: skill.priceType,
        downloaded: !!blob,
      })
      installedSkills.value = getInstalledSkills()
      return true
    } catch (e) {
      console.warn('[SkillHub] 下载失败，尝试仅记录安装:', e.message)
      // 即使下载失败，也记录安装意图（离线标记）
      saveInstalledSkill({
        slug: skill.slug || skill.id,
        name: skill.name,
        description: skill.description,
        source: skill.source,
        sourceUrl: skill.sourceUrl,
        priceType: skill.priceType,
        downloaded: false,
      })
      installedSkills.value = getInstalledSkills()
      return false
    } finally {
      installing.value = false
    }
  }

  /** 卸载技能 */
  function uninstallSkill(slug) {
    removeInstalledSkill(slug)
    installedSkills.value = getInstalledSkills()
  }

  /** 检查是否已安装 */
  function checkInstalled(slug) {
    return installedSlugs.value.has(slug)
  }

  /** 重置筛选 */
  function resetFilters() {
    filters.value = {
      keywords: '',
      labelIds: '',
      orderBy: 'default',
      payable: undefined,
      pageIndex: 1,
      size: 20,
    }
    nextPosition.value = ''
  }

  return {
    // 状态
    labels,
    skills,
    loading,
    installing,
    error,
    filters,
    nextPosition,
    totalCount,
    installedSkills,
    // 计算属性
    installedSlugs,
    labelGroups,
    // 方法
    loadLabels,
    searchSkills,
    loadMore,
    installSkill,
    uninstallSkill,
    checkInstalled,
    resetFilters,
  }
})
