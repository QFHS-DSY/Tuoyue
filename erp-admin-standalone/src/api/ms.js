/**
 * 阿里云短信服务封装
 * 文档: https://help.aliyun.com/document_detail/101414.html
 * 说明：所有短信操作通过后端转发，密钥不暴露在前端
 */

import axios from 'axios'

// ===================== 核心接口 =====================

/**
 * 发送短信验证码
 * @param {string} phone - 手机号（如 +8613800138000 或 13800138000）
 * @param {string} templateCode - 短信模板 CODE
 * @param {object} templateParam - 模板参数（如 { code: '123456' }）
 * @returns {Promise<{success: boolean, message: string, requestId: string}>}
 */
export async function sendSmsCode(phone, templateCode, templateParam = {}) {
  const res = await axios.post('/api/sms/send/', {
    phone,
    template_code: templateCode,
    template_param: templateParam,
  })

  return {
    success: res.data?.Code === 'OK',
    message: res.data?.Message || '发送成功',
    requestId: res.data?.RequestId,
  }
}

/**
 * 发送验证码（简化版，自动使用默认模板）
 * @param {string} phone - 手机号
 * @returns {Promise<{success: boolean, message: string}>}
 */
export async function sendVerificationCode(phone) {
  const normalizedPhone = phone.startsWith('+') ? phone : `+86${phone}`
  const code = String(Math.floor(Math.random() * 900000) + 100000)
  return sendSmsCode(normalizedPhone, 'SMS_DEFAULT', { code })
}

/**
 * 验证短信验证码
 * @param {string} phone - 手机号
 * @param {string} code - 用户输入的验证码
 * @returns {Promise<{valid: boolean, message: string}>}
 */
export async function verifySmsCode(phone, code) {
  const res = await axios.post('/api/sms/verify/', {
    phone,
    code,
  })

  return {
    valid: res.data?.valid || false,
    message: res.data?.message || '验证失败',
  }
}

/**
 * 查询短信发送状态
 * @param {string} phone - 手机号
 * @param {string} sendDate - 发送日期（YYYYMMDD）
 * @returns {Promise<Array>}
 */
export async function querySmsStatus(phone, sendDate) {
  const res = await axios.get('/api/sms/query/', {
    params: { phone, send_date: sendDate },
  })

  return res.data?.SmsSendDetailDTOs?.SmsSendDetailDTO || []
}

/**
 * 批量发送短信（订单通知等）
 * @param {Array<{phone: string, param: object}>} batch - 批量数据
 * @param {string} templateCode - 模板CODE
 * @returns {Promise<{success: boolean, results: Array}>}
 */
export async function sendBatchSms(batch, templateCode) {
  const res = await axios.post('/api/sms/send-batch/', {
    batch,
    template_code: templateCode,
  })

  return res.data
}

export default {
  sendSmsCode,
  sendVerificationCode,
  verifySmsCode,
  querySmsStatus,
  sendBatchSms,
}
