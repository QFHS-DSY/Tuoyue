/**
 * 卖家之家 SkillHub (Skill商城) API 接入层
 *
 * 数据来源: https://data.mjzj.com
 * API 文档: https://clawhub.ai/skills/mjzj-skillhub
 *
 * 接口概览:
 *   GET  /api/skill/groupLabels  — 标签分组（公开）
 *   GET  /api/skill/query        — 搜索/筛选技能（公开）
 *   POST /api/skillManage/applyNew — 发布技能（需 API KEY）
 *   POST /api/common/applyUploadTempFile — 上传封面（需 API KEY）
 */

import request from '@/utils/request'

// SkillHub 后端代理前缀（通过 Vite proxy → data.mjzj.com）
const SKILLHUB_PREFIX = '/api/skillhub'

// ==================== 标签分组 ====================

/**
 * 获取技能标签分组（公开接口）
 * 返回分组列表，每个分组包含 labels[].id 用于后续筛选
 */
export function fetchSkillLabels() {
  return request({
    url: `${SKILLHUB_PREFIX}/groupLabels`,
    method: 'get',
    // 公开接口不需要 auth token（但 request 拦截器会自动加，不影响）
  })
}

// ==================== 技能查询 ====================

/**
 * 搜索/筛选技能（公开接口）
 * @param {Object} params
 * @param {string}  params.keywords   - 搜索关键词
 * @param {string}  params.labelIds   - 标签ID，逗号拼接 "1001,1002"
 * @param {string}  params.orderBy    - 排序: default | new | hot
 * @param {boolean} params.payable    - true=付费 / false=免费 / 不传=全部
 * @param {string}  params.position   - 分页游标（首次传空字符串）
 * @param {number}  params.size       - 每页条数 (1-100)
 * @param {number}  params.pageIndex  - 页码
 */
export function querySkills(params = {}) {
  return request({
    url: `${SKILLHUB_PREFIX}/query`,
    method: 'get',
    params: {
      keywords: params.keywords || '',
      labelIds: params.labelIds || '',
      orderBy: params.orderBy || 'default',
      payable: params.payable,
      position: params.position || '',
      size: params.size || 20,
      pageIndex: params.pageIndex || 1,
    },
  })
}

// ==================== 技能安装 ====================

/**
 * 安装技能（下载 ZIP 包）
 * @param {string} slug - 技能标识（如 "mjzj-skillhub"）
 * @returns {Blob} ZIP 字节流
 */
export function downloadSkill(slug) {
  return request({
    url: `${SKILLHUB_PREFIX}/download/${slug}`,
    method: 'get',
    responseType: 'blob',
  })
}

// ==================== 技能发布（需认证） ====================

/**
 * 申请上传临时文件（获取 putUrl）
 * @param {Object} params
 * @param {string} params.fileName    - 文件名
 * @param {string} params.contentType - MIME 类型
 * @param {number} params.fileLength  - 文件大小（字节）
 */
export function applyUploadTempFile(params) {
  return request({
    url: `${SKILLHUB_PREFIX}/applyUploadTempFile`,
    method: 'post',
    data: params,
  })
}

/**
 * 申请发布新技能
 * @param {Object} params
 * @param {string} params.name        - 技能名称
 * @param {string} params.description - 技能描述
 * @param {string} params.sourceUrl   - 技能来源 URL
 * @param {string} params.priceType   - free | freeAndPaid | paid
 * @param {string} params.coverFile   - COS 临时路径（可选）
 * @param {string[]} params.labelIds  - 标签 ID 数组
 * @param {string[]} params.tags      - 标签数组
 */
export function applyNewSkill(params) {
  return request({
    url: `${SKILLHUB_PREFIX}/applyNew`,
    method: 'post',
    data: params,
  })
}

// ==================== 本地 Skill 管理 ====================

const INSTALLED_SKILLS_KEY = 'erp_installed_skills'

/**
 * 获取本地已安装的 Skill 列表
 */
export function getInstalledSkills() {
  try {
    const raw = localStorage.getItem(INSTALLED_SKILLS_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

/**
 * 保存本地已安装的 Skill
 */
export function saveInstalledSkill(skill) {
  const list = getInstalledSkills()
  // 去重：按 slug 覆盖
  const idx = list.findIndex(s => s.slug === skill.slug)
  if (idx >= 0) {
    list[idx] = { ...skill, installedAt: new Date().toISOString() }
  } else {
    list.push({ ...skill, installedAt: new Date().toISOString() })
  }
  localStorage.setItem(INSTALLED_SKILLS_KEY, JSON.stringify(list))
  return list
}

/**
 * 卸载本地 Skill
 */
export function removeInstalledSkill(slug) {
  const list = getInstalledSkills().filter(s => s.slug !== slug)
  localStorage.setItem(INSTALLED_SKILLS_KEY, JSON.stringify(list))
  return list
}

/**
 * 检查 Skill 是否已安装
 */
export function isSkillInstalled(slug) {
  return getInstalledSkills().some(s => s.slug === slug)
}
