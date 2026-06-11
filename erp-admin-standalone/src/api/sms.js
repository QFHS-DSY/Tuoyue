/**
 * 阿里云短信服务 — 全部通过后端转发
 */
import axios from 'axios'

/** 发送短信验证码 */
export async function sendSmsCode(phone, templateCode, templateParam = {}) {
  const res = await axios.post('/api/sms/send/', {
    phone, template_code: templateCode, template_param: templateParam,
  })
  return { success: res.data?.Code === 'OK', message: res.data?.Message || '发送成功', requestId: res.data?.RequestId }
}

/** 发送验证码（简化版） */
export async function sendVerificationCode(phone) {
  const normalizedPhone = phone.startsWith('+') ? phone : `+86${phone}`
  const code = String(Math.floor(Math.random() * 900000) + 100000)
  return sendSmsCode(normalizedPhone, 'SMS_DEFAULT', { code })
}

/** 验证短信验证码 */
export async function verifySmsCode(phone, code) {
  const res = await axios.post('/api/sms/verify/', { phone, code })
  return { valid: res.data?.valid || false, message: res.data?.message || '验证失败' }
}

/** 查询短信发送状态 */
export async function querySmsStatus(phone, sendDate) {
  const res = await axios.get('/api/sms/query/', { params: { phone, send_date: sendDate } })
  return res.data?.SmsSendDetailDTOs?.SmsSendDetailDTO || []
}

/** 批量发送短信 */
export async function sendBatchSms(batch, templateCode) {
  const res = await axios.post('/api/sms/send-batch/', { batch, template_code: templateCode })
  return res.data
}

export default { sendSmsCode, sendVerificationCode, verifySmsCode, querySmsStatus, sendBatchSms }
