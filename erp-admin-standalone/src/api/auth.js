/**
 * 用户认证 API — 全部对接真实后端
 */
import axios from 'axios'

const request = axios.create({
  timeout: 15000,
})

request.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
}, (error) => Promise.reject(error))

request.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const refresh = localStorage.getItem('refresh_token')
        if (!refresh) throw new Error('No refresh token')
        const res = await request.post('/api/auth/refresh', { refresh_token: refresh })
        localStorage.setItem('access_token', res.access_token)
        originalRequest.headers.Authorization = `Bearer ${res.access_token}`
        return request(originalRequest)
      } catch {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export const sendSmsCode = (phone, countryCode = '86') =>
  request.post('/api/auth/send-sms', { phone, country_code: countryCode })

export const verifySmsCode = (phone, code) =>
  request.post('/api/auth/verify-sms', { phone, code })

export const mobileLogin = (data) =>
  request.post('/api/auth/mobile/login', {
    mobile: data.phone || data.mobile,
    code: data.code,
    country_code: data.country_code || '86',
    agreed_privacy: data.agreed_privacy !== false,
  })

export const register = (data) =>
  request.post('/api/auth/register', data)

export const login = (data) =>
  request.post('/api/auth/login', data)

export const refreshToken = (data) =>
  request.post('/api/auth/refresh', data)

export const getCurrentUser = () =>
  request.get('/api/auth/me')

export default { sendSmsCode, verifySmsCode, mobileLogin, register, login, refreshToken, getCurrentUser }
