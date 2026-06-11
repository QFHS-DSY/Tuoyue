/**
 * Ruitalk AI 接口封装
 * 对接 Ruitalk 金牌客服系统（Flask 后端，端口 5001）
 * 基于 DeepSeek 大模型，提供高情绪价值客服回复
 */

import axios from 'axios'

// ===================== 配置 =====================
const RUITALK_BASE_URL = import.meta.env.VITE_RUITALK_URL || 'http://127.0.0.1:5001'

const ruitalkClient = axios.create({
  baseURL: RUITALK_BASE_URL,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
})

ruitalkClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.message || error.message || '小辽暂时不可用'
    console.error('[Ruitalk] 请求失败:', message)
    return Promise.reject(new Error(message))
  }
)

// ===================== 会话管理 =====================
// 内存中的 session_id（实际应该持久化到 localStorage）
let currentSessionId = localStorage.getItem('ruitalk_session_id') || ''

/**
 * 开始一个新会话（需要先调用这个获取 session_id）
 * @param {string} phone - 客户手机号（可选，用于获取客户档案）
 * @param {string} name - 客户名称（可选）
 * @returns {Promise<{session_id, welcome, customer_info}>}
 */
export async function startSession(phone = '', name = 'ERP用户') {
  try {
    const res = await ruitalkClient.post('/api/customer/start', {
      phone,
      name,
    })
    if (res.success && res.session_id) {
      currentSessionId = res.session_id
      localStorage.setItem('ruitalk_session_id', currentSessionId)
    }
    return res
  } catch (err) {
    console.error('[Ruitalk] 开始会话失败:', err.message)
    throw err
  }
}

/**
 * 发送消息并获取回复
 * @param {string} message - 用户消息
 * @returns {Promise<{response, language}>}
 */
export async function sendMessage(message) {
  if (!currentSessionId) {
    // 自动开启会话
    await startSession()
  }

  try {
    const res = await ruitalkClient.post('/api/customer/chat', {
      session_id: currentSessionId,
      message: message.trim(),
    })

    if (!res.success) {
      throw new Error(res.message || '发送失败')
    }

    return {
      response: res.response,
      language: res.language || 'zh',
    }
  } catch (err) {
    console.error('[Ruitalk] 发送消息失败:', err.message)
    throw err
  }
}

/**
 * 获取历史消息（用于恢复会话）
 * @param {string} sessionId - 会话ID
 * @returns {Promise<Array>}
 */
export async function getHistory(sessionId = currentSessionId) {
  if (!sessionId) return []
  try {
    const res = await ruitalkClient.get(`/api/customer/history/${sessionId}`)
    return res.messages || []
  } catch (err) {
    console.warn('[Ruitalk] 获取历史消息失败:', err.message)
    return []
  }
}

/**
 * 清除会话（重新开始）
 */
export function clearSession() {
  currentSessionId = ''
  localStorage.removeItem('ruitalk_session_id')
}

/**
 * 翻译接口
 * @param {string} text - 待翻译文本
 * @param {string} target - 目标语言 (zh/en/ar/ru/th/vi/id/ms/tl)
 * @returns {Promise<string>}
 */
export async function translate(text, target = 'zh') {
  const res = await ruitalkClient.post('/api/translate', {
    text,
    target,
  })
  return res.translation || ''
}

export default {
  startSession,
  sendMessage,
  getHistory,
  clearSession,
  translate,
}
