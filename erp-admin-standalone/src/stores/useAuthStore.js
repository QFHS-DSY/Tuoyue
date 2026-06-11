/**
 * 用户认证状态管理
 * 功能：管理登录用户信息、Token、登出
 * 文档：前端开发功能与实现文档 v2.0 · 模块1
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // ── 状态 ─────────────────────────────────────────────────
  const user = ref(null)   // { id, name, role, phone, avatar }
  const token = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)

  // ── 计算属性 ─────────────────────────────────────────────
  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const userName = computed(() => user.value?.name || '未知用户')
  const userRole = computed(() => user.value?.role || 'unknown')

  // ── 操作方法 ─────────────────────────────────────────────
  function setUser(userInfo) {
    user.value = userInfo
  }

  function setToken(accessToken, refreshTokenValue) {
    token.value = accessToken
    if (accessToken) {
      localStorage.setItem('access_token', accessToken)
    }
    if (refreshTokenValue) {
      refreshToken.value = refreshTokenValue
      localStorage.setItem('refresh_token', refreshTokenValue)
    }
  }

  function logout() {
    user.value = null
    token.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  // 从登录响应数据初始化（兼容后端返回格式）
  function initFromLogin(data) {
    if (data.access_token) setToken(data.access_token, data.refresh_token)
    if (data.user) setUser(data.user)
  }

  return {
    // 状态
    user,
    token,
    refreshToken,
    // 计算
    isLoggedIn,
    userName,
    userRole,
    // 方法
    setUser,
    setToken,
    logout,
    initFromLogin,
  }
})
