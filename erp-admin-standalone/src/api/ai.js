/**
 * AI 接口封装
 * 使用共享 request 实例（统一 auth token + Vite 代理）
 */
import request from '@/utils/request'

// ===================== 核心接口 =====================

/**
 * 为商品生成标题（吸引点击）
 */
export async function generateTitle(goodsInfo) {
  const { name, category, material, style, features, targetMarket } = goodsInfo
  const res = await request.post('/api/ai/generate-title/', {
    name,
    category,
    material: material || '',
    style: style || '',
    features: features || '',
    target_market: targetMarket || '跨境电商通用',
  })
  return res?.data?.title || res?.title || ''
}

/**
 * 为商品生成描述（促进转化）
 * @returns {{ description: string, description_cn: string }}
 */
export async function generateDescription(goodsInfo) {
  const { name, category, material, style, features, specs, targetMarket } = goodsInfo
  const res = await request.post('/api/ai/generate-description/', {
    name,
    category,
    material: material || '',
    style: style || '',
    features: features || '',
    specs: specs || '',
    target_market: targetMarket || '跨境电商通用',
  })
  const data = res?.data || res || {}
  return {
    description: data.description || '',
    description_cn: data.description_cn || ''
  }
}

/**
 * 改写/调整商品描述
 * @param {string} originalDesc - 原始英文描述
 * @param {string} adjustment - 调整方向（如"更短一些"、"更促销"、"突出材质"等中文描述）
 * @returns {{ description: string, description_cn: string }}
 */
export async function refineDescription(originalDesc, adjustment) {
  const res = await request.post('/api/ai/refine-description/', {
    original_desc: originalDesc,
    adjustment: adjustment,
  })
  const data = res?.data || res || {}
  return {
    description: data.description || '',
    description_cn: data.description_cn || ''
  }
}

/**
 * 多语言翻译
 */
export async function translate(text, targetLang) {
  const res = await request.post('/api/ai/translate/', {
    text,
    target_lang: targetLang,
  })
  return res?.data?.translation || res?.translation || ''
}

/**
 * AI 文生图（图片链接提取 / 文本提示词增强）
 * @param {string} prompt - 图像描述
 * @returns {{ imageUrl: string, imageBase64: string, prompts: string[] }}
 */
export async function generateImage(prompt) {
  const res = await request.post('/api/ai/image/generate/', { prompt })
  const data = res?.data || res || {}
  return {
    imageUrl: data.image_url || '',
    imageBase64: data.image_base64 || '',
    prompts: data.prompts || [],
  }
}

/**
 * AI 图生图（Nanobanana / Gemini）
 * @param {string} prompt - 图像修改指令
 * @param {string} imageBase64 - 原始图片 base64（data:image/xxx;base64,...）
 * @returns {{ imageUrl: string, imageBase64: string }}
 */
export async function editImage(prompt, imageBase64) {
  const res = await request.post('/api/ai/image/edit/', { prompt, image_base64: imageBase64 })
  const data = res?.data || res || {}
  return {
    imageUrl: data.image_url || '',
    imageBase64: data.image_base64 || '',
  }
}

/**
 * 为商品生成核心卖点（3-5条）
 * @param {object} goodsInfo - { name, category, ... }
 * @returns {Array<{icon, title, desc}>}
 */
export async function generateFeatures(goodsInfo) {
  const { name, category, material, style } = goodsInfo
  const res = await request.post('/api/ai/generate-features/', {
    name,
    category: category || '',
    material: material || '',
    style: style || '',
  })
  return res?.data?.features || res?.features || []
}

// ===================== 拓跃AI对话（走后端代理，避免CORS）=====================
/**
 * 拓跃AI对话（通过Django后端代理）
 * @param {string[]} messages - 对话历史 [{role, content}, ...]
 * @param {string} systemPrompt - 系统提示词
 * @returns {Promise<string>} AI 回复文本
 */
export async function tuoyueChat(messages, systemPrompt = '') {
  console.log('[tuoyueChat] 调用 Django 后端代理...')

  try {
    const res = await request.post('/api/ai/chat/', {
      messages,
      system_prompt: systemPrompt,
      temperature: 0.7,
      max_tokens: 800,
    }, { timeout: 90000 })  // AI 调用需要更长超时

    // 后端 success_response 返回 { code:200, data:{ reply:"..." } }
    const reply = res?.data?.reply || res?.reply || ''
    console.log('[tuoyueChat] 回复长度:', reply.length)
    return reply
  } catch (err) {
    console.error('[tuoyueChat] 请求失败:', err.message)
    throw err
  }
}

export default {
  generateTitle,
  generateDescription,
  translate,
  generateImage,
  editImage,
  generateFeatures,
  tuoyueChat,
}
