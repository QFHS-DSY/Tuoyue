/**
 * AI 生图专用 API 模块
 * 
 * 功能：
 *   - 文生图（文本提示词 → 图片）
 *   - 图生图（上传图片 + 提示词 → 优化/场景融合图片）
 *   - 图片保存到 SKU
 *   - 生成历史记录查询
 *   - 预设模板管理
 */

import request from '@/utils/request'
import { fileToBase64 } from '@/api/upload'
import { AI_LONG_TIMEOUT_MS } from '@/utils/aiStudio'

const AI_IMAGE_REQUEST_CONFIG = { timeout: AI_LONG_TIMEOUT_MS }

// ==================== 预设模板 ====================

/** 获取系统预设的提示词模板列表 */
export async function fetchTemplates() {
  const res = await request.get('/api/ai/image/templates/')
  return res?.data || res || []
}

/** 用户自定义模板（本地存储兜底 + 远程同步） */
export async function saveUserTemplate(template) {
  const res = await request.post('/api/ai/image/templates/save/', template)
  return res?.data || res || {}
}

// ==================== 图片生成 ====================

/**
 * AI 文生图
 * @param {Object} params
 * @param {string} params.prompt - 图片描述提示词（中文或英文）
 * @param {string} [params.ratio] - 图片比例：'1:1' | '16:9' | '9:16' | '4:3' | '3:4'
 * @param {string} [params.style] - 风格：'photography' | 'illustration' | '3d' | 'realistic'
 * @param {boolean} [params.transparent] - 是否透明背景（PNG）
 * @param {number} [params.count] - 生成数量，默认4
 * @returns {Promise<{images: Array<{url: string, base64: string, seed: number}>, requestId: string}>}
 */
export async function textToImage(params) {
  const { prompt, ratio = '1:1', style = 'photography', transparent = false, count = 4 } = params
  const res = await request.post('/api/ai/image/text-to-image/', {
    action: 'text_to_image',
    prompt,
    ratio,
    style,
    transparent,
    count,
  }, AI_IMAGE_REQUEST_CONFIG)
  const data = res?.data || res || {}
  return {
    images: data.images || [],
    requestId: data.request_id || '',
  }
}

/**
 * AI 图生图（上传图片 + 提示词优化/场景融合）
 * @param {Object} params
 * @param {string|File} params.image - 图片 base64 或 File 对象
 * @param {string} params.prompt - 修改指令（如"添加阳光沙滩背景"）
 * @param {string} [params.ratio] - 输出比例
 * @param {number} [params.count] - 生成数量，默认4
 * @returns {Promise<{images: Array<{url: string, base64: string}>, requestId: string}>}
 */
export async function imageToImage(params) {
  let imageBase64 = params.image
  if (params.image instanceof File) {
    imageBase64 = await fileToBase64(params.image)
  }
  const { prompt, ratio = '1:1', count = 4 } = params
  const res = await request.post('/api/ai/image/image-to-image/', {
    action: 'image_to_image',
    image_base64: imageBase64,
    prompt,
    ratio,
    count,
  }, AI_IMAGE_REQUEST_CONFIG)
  const data = res?.data || res || {}
  return {
    images: data.images || [],
    requestId: data.request_id || '',
    enhancedPrompt: data.enhanced_prompt || '',
  }
}

/**
 * 继续编辑已生成的图片（微调）
 * @param {Object} params
 * @param {string} params.imageBase64 - 上一张图片的 base64
 * @param {string} params.prompt - 微调指令
 * @param {string} [params.ratio]
 * @param {number} [params.count] - 默认1
 */
export async function refineImage(params) {
  const { imageBase64, prompt, ratio = '1:1', count = 1 } = params
  const res = await request.post('/api/ai/image/image-to-image/', {
    action: 'image_to_image',
    image_base64: imageBase64,
    prompt,
    ratio,
    count,
  }, AI_IMAGE_REQUEST_CONFIG)
  const data = res?.data || res || {}
  return {
    images: data.images || [],
    requestId: data.request_id || '',
  }
}

/**
 * AI 视频生成
 * @param {Object} params
 * @param {File[]} params.images
 * @param {string} [params.duration]
 * @param {string} [params.style]
 * @param {string} [params.bgm]
 * @param {string} [params.description]
 */
export async function generateVideo(params) {
  const formData = new FormData()
  ;(params.images || []).forEach((file, index) => {
    formData.append(`image_${index}`, file)
  })
  formData.append('duration', params.duration || '10')
  formData.append('style', params.style || 'cinematic')
  formData.append('bgm', params.bgm || 'none')
  formData.append('description', params.description || '')

  const res = await request.post('/api/ai/video/generate/', formData, {
    ...AI_IMAGE_REQUEST_CONFIG,
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  const data = res?.data || res || {}
  return {
    videoUrl: data.video_url || data.url || '',
    requestId: data.request_id || '',
    detail: data.detail || data.message || '',
  }
}

// ==================== 图片保存与关联 ====================

/**
 * 保存生成的图片并关联到指定 SKU
 * @param {Object} params
 * @param {string} params.imageBase64 - 图片 base64
 * @param {string} [params.skuCode] - SKU 编码
 * @param {string} [params.prompt] - 使用的提示词
 * @param {string} [params.requestId] - 生成请求 ID
 */
export async function saveImageToSku(params) {
  const res = await request.post('/api/ai/image/save-to-sku/', params)
  return res?.data || res || {}
}

/**
 * 批量保存图片到 SKU
 */
export async function batchSaveImages(params) {
  const res = await request.post('/api/ai/image/batch-save/', params)
  return res?.data || res || {}
}

// ==================== 历史记录 ====================

/**
 * 获取 AI 生图历史记录
 * @param {Object} params
 * @param {number} [params.page=1]
 * @param {number} [params.pageSize=20]
 * @param {string} [params.skuCode] - 按 SKU 筛选
 * @param {string} [params.mode] - 'text2image' | 'image2image' | 'all'
 */
export async function fetchHistory(params = {}) {
  const { page = 1, pageSize = 20, skuCode, mode } = params
  const res = await request.get('/api/ai/image/history/', {
    params: { page, page_size: pageSize, sku_code: skuCode, mode }
  })
  const data = res?.data || res || {}
  return {
    items: data.items || data.results || [],
    total: data.total || data.count || 0,
  }
}

/**
 * 获取单次生成会话的完整对话记录
 * @param {string} requestId
 */
export async function fetchConversation(requestId) {
  const res = await request.get(`/api/ai/image/conversation/${requestId}/`)
  const data = res?.data || res || {}
  return data.messages || data.records || []
}

/**
 * 删除历史记录
 */
export async function deleteHistoryItem(id) {
  await request.delete(`/api/ai/image/history/${id}/`)
  return true
}

// ==================== 商品 SKU 查询（用于关联） ====================

/**
 * 搜索商品 SKU（用于图片关联时选择 SKU）
 */
export async function searchSku(keyword) {
  const res = await request.get('/api/v1/goods/sku/search/', {
    params: { keyword, page_size: 20 }
  })
  const data = res?.data || res || {}
  return data.items || data.results || []
}

// ==================== 本地预设模板（前端兜底，后端不可用时使用） ====================

export const LOCAL_TEMPLATES = [
  {
    id: 'tpl_1',
    name: '白色背景商业摄影',
    category: '通用',
    icon: 'camera',
    prompt: '专业商业产品摄影，纯白色背景，柔和均匀的影棚灯光，高分辨率，清晰展现产品细节和质感',
  },
  {
    id: 'tpl_2',
    name: '生活场景展示',
    category: '通用',
    icon: 'home',
    prompt: '产品自然地摆放在现代简约家居环境中，柔和的自然光从窗户洒入，生活化场景，温暖舒适的氛围',
  },
  {
    id: 'tpl_3',
    name: '户外自然光',
    category: '户外用品',
    icon: 'sunny',
    prompt: '产品放置在户外自然环境中，阳光明媚，绿植环绕，蓝天白云背景下展示产品，自然清新风格',
  },
  {
    id: 'tpl_4',
    name: '厨房/餐厅场景',
    category: '家居厨具',
    icon: 'dish',
    prompt: '产品摆放在现代化厨房或餐厅中，大理石台面，温暖灯光，精致的餐具搭配，美食博主风格摄影',
  },
  {
    id: 'tpl_5',
    name: '时尚模特展示',
    category: '服饰',
    icon: 'user',
    prompt: '时尚模特穿戴/使用产品，简约干净的摄影棚背景，专业时装摄影灯光，展现产品的穿着效果和版型',
  },
  {
    id: 'tpl_6',
    name: '科技感深色背景',
    category: '电子产品',
    icon: 'monitor',
    prompt: '深色科技感背景，产品被蓝色或紫色渐变光影照亮，赛博朋克风格，突出产品的科技感和高级质感',
  },
  {
    id: 'tpl_7',
    name: '美妆精致特写',
    category: '美妆',
    icon: 'star',
    prompt: '美妆产品精致特写摄影，柔和的粉色/玫瑰金背景，微距镜头展现产品质地，花瓣或水珠点缀，高级感',
  },
  {
    id: 'tpl_8',
    name: '运动活力场景',
    category: '运动户外',
    icon: 'run',
    prompt: '产品在运动场景中使用，动态抓拍风格，充满活力的光线和色彩，展现产品的功能性和运动感',
  },
  {
    id: 'tpl_9',
    name: '儿童温馨场景',
    category: '母婴用品',
    icon: 'baby',
    prompt: '柔和温馨的婴儿房/儿童房场景，柔和的粉色或浅蓝色调，毛绒玩具和柔和灯光，安全温暖的感觉',
  },
  {
    id: 'tpl_10',
    name: '办公桌面平铺',
    category: '办公用品',
    icon: 'desk',
    prompt: '产品与办公文具一起平铺在木质桌面上，俯拍视角，自然光从侧面照射，简洁专业的商务风格',
  },
  {
    id: 'tpl_11',
    name: '亚马逊主图标准',
    category: '电商平台',
    icon: 'shop',
    prompt: 'Amazon标准主图风格，纯白色背景(RGB:255,255,255)，产品占据画面85%以上，高清晰度，无阴影无文字无水印',
  },
  {
    id: 'tpl_12',
    name: '节日氛围场景',
    category: '季节性',
    icon: 'gift',
    prompt: '产品融入节日氛围场景，节日装饰元素点缀，温暖的节日灯光，喜庆欢乐的氛围，适合节日促销使用',
  },
  {
    id: 'tpl_13',
    name: '极简主义风格',
    category: '通用',
    icon: 'minimal',
    prompt: '极简主义风格摄影，单一产品居中摆放，大面积留白，极简构图，高级灰白色调，突出产品本身的设计美感',
  },
  {
    id: 'tpl_14',
    name: '水花/动态效果',
    category: '特效',
    icon: 'water',
    prompt: '产品与水花/飞溅效果结合的高速摄影风格，黑色背景，高对比度灯光，定格瞬间动态，视觉冲击力强',
  },
]

// ==================== 图片比例预设 ====================

export const RATIO_OPTIONS = [
  { label: '1:1 正方形（主图）', value: '1:1' },
  { label: '16:9 横版（横幅广告）', value: '16:9' },
  { label: '9:16 竖版（A+页面）', value: '9:16' },
  { label: '4:3 标准（附图）', value: '4:3' },
  { label: '3:4 竖版（详情图）', value: '3:4' },
]

export const STYLE_OPTIONS = [
  { label: '商业摄影', value: 'photography' },
  { label: '写实风格', value: 'realistic' },
  { label: '插画风格', value: 'illustration' },
  { label: '3D渲染', value: '3d' },
]

export default {
  textToImage,
  imageToImage,
  refineImage,
  saveImageToSku,
  batchSaveImages,
  fetchHistory,
  fetchConversation,
  deleteHistoryItem,
  searchSku,
  generateVideo,
  fetchTemplates,
  saveUserTemplate,
  LOCAL_TEMPLATES,
  RATIO_OPTIONS,
  STYLE_OPTIONS,
}
