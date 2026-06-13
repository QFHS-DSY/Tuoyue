<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="bg-shape shape-1"></div>
      <div class="bg-shape shape-2"></div>
      <div class="bg-shape shape-3"></div>
    </div>

    <div class="login-card">
      <div class="login-logo">
        <img src="@/assets/logo.png" alt="拓岳科技" class="logo-img" />
        <h1 class="logo-title">拓岳科技</h1>
        <p class="logo-subtitle">跨境电商 ERP 管理系统</p>
      </div>

      <div class="mode-selector">
        <button
          type="button"
          :class="['mode-card', { active: loginMode === 'beginner' }]"
          @click="loginMode = 'beginner'"
        >
          <span class="mode-title">新手模式</span>
          <span class="mode-desc">流程更简洁，适合短信快速进入</span>
        </button>
        <button
          type="button"
          :class="['mode-card', { active: loginMode === 'expert' }]"
          @click="loginMode = 'expert'"
        >
          <span class="mode-title">专家模式</span>
          <span class="mode-desc">保留完整工作台和运营能力</span>
        </button>
      </div>

      <el-tabs v-model="loginTab" class="login-tabs" @tab-click="handleTabSwitch">
        <el-tab-pane label="短信登录" name="sms">
          <el-form
            ref="smsFormRef"
            :model="smsForm"
            :rules="smsRules"
            class="login-form"
            @submit.prevent="handleLogin"
          >
            <el-form-item prop="phone">
              <el-input
                v-model="smsForm.phone"
                placeholder="请输入手机号"
                size="large"
                :prefix-icon="Phone"
                clearable
              />
            </el-form-item>

            <el-form-item prop="code">
              <el-input
                v-model="smsForm.code"
                placeholder="请输入验证码"
                size="large"
                :prefix-icon="Message"
                maxlength="6"
              >
                <template #append>
                  <el-button class="send-code-btn" :disabled="countdown > 0" @click="handleSendCode">
                    {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
                  </el-button>
                </template>
              </el-input>
            </el-form-item>

            <div class="form-options">
              <el-checkbox v-model="rememberMe">记住手机号</el-checkbox>
            </div>

            <div class="agreement-row">
              <el-checkbox v-model="smsAgreed">
                我已阅读并同意
                <el-link type="primary" :underline="false" @click.prevent="openLegalLink(userAgreementUrl, '用户协议')">《用户协议》</el-link>
                和
                <el-link type="primary" :underline="false" @click.prevent="openLegalLink(privacyPolicyUrl, '隐私政策')">《隐私政策》</el-link>
              </el-checkbox>
            </div>

            <el-button
              type="primary"
              size="large"
              :loading="loading"
              class="login-btn"
              @click="handleLogin"
            >
              登录
            </el-button>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="密码登录" name="pwd">
          <el-form
            ref="pwdFormRef"
            :model="pwdForm"
            :rules="pwdRules"
            class="login-form"
            @submit.prevent="handlePwdLogin"
          >
            <el-form-item prop="username">
              <el-input
                v-model="pwdForm.username"
                placeholder="请输入用户名或手机号"
                size="large"
                :prefix-icon="User"
                clearable
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="pwdForm.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>

            <div v-if="isDev" class="form-options">
              <el-button text size="small" @click="fillTestAccount">一键填入测试账号</el-button>
            </div>

            <el-button
              type="primary"
              size="large"
              :loading="pwdLoading"
              class="login-btn"
              @click="handlePwdLogin"
            >
              登录
            </el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <div class="login-footer">
        <span class="footer-text">还没有账号？</span>
        <el-link type="primary" :underline="false" @click="$router.push('/register')">立即注册</el-link>
      </div>
    </div>

    <div class="version-info">
      <span>v1.0.0</span>
      <span class="divider">|</span>
      <span>手机号登录已启用真实短信通道</span>
    </div>
  </div>
</template>

<script setup>
import { onUnmounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Lock, Message, Phone, User } from '@element-plus/icons-vue'
import { getCurrentUser, login as pwdLogin, mobileLogin, sendSmsCode } from '@/api/auth'
import { useAppStore } from '@/stores/useAppStore'

const router = useRouter()
const appStore = useAppStore()

const smsFormRef = ref(null)
const pwdFormRef = ref(null)
const loading = ref(false)
const pwdLoading = ref(false)
const rememberMe = ref(false)
const countdown = ref(0)
const loginTab = ref('sms')
const loginMode = ref(appStore.mode || 'beginner')
const smsAgreed = ref(false)
const isDev = import.meta.env.DEV
const userAgreementUrl = import.meta.env.VITE_USER_AGREEMENT_URL || ''
const privacyPolicyUrl = import.meta.env.VITE_PRIVACY_POLICY_URL || ''

const smsForm = reactive({
  phone: '',
  code: '',
})

const pwdForm = reactive({
  username: '',
  password: '',
})

const smsRules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' },
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { pattern: /^\d{4,6}$/, message: '验证码为 4-6 位数字', trigger: 'blur' },
  ],
}

const pwdRules = {
  username: [
    { required: true, message: '请输入用户名或手机号', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 4, message: '密码长度不能少于 4 位', trigger: 'blur' },
  ],
}

let countdownTimer = null

function openLegalLink(url, label) {
  if (!url) {
    ElMessage.info(`${label} link is not configured yet`)
    return
  }
  window.open(url, '_blank', 'noopener')
}

function startCountdown() {
  countdown.value = 60
  countdownTimer = setInterval(() => {
    countdown.value -= 1
    if (countdown.value <= 0) {
      clearInterval(countdownTimer)
      countdownTimer = null
    }
  }, 1000)
}

async function cacheCurrentUser() {
  try {
    const userRes = await getCurrentUser()
    if (userRes?.data) {
      localStorage.setItem('user_info', JSON.stringify(userRes.data))
    }
  } catch (_) {
    // Non-blocking.
  }
}

function persistLoginState(accessToken, refreshToken, phone) {
  if (accessToken) {
    localStorage.setItem('access_token', accessToken)
  }
  if (refreshToken) {
    localStorage.setItem('refresh_token', refreshToken)
  }
  if (phone) {
    localStorage.setItem('user_phone', phone)
  }
}

async function handleSendCode() {
  if (countdown.value > 0) return
  if (!smsAgreed.value) {
    ElMessage.warning('请先阅读并同意用户协议与隐私政策')
    return
  }
  if (!smsForm.phone || !/^1[3-9]\d{9}$/.test(smsForm.phone)) {
    ElMessage.warning('请输入正确的手机号')
    return
  }

  try {
    const res = await sendSmsCode(smsForm.phone, '86')
    if (res?.code !== 200) {
      ElMessage.warning(res?.message || '验证码发送失败，请稍后重试')
      return
    }

    if (res.data?.code) {
      smsForm.code = res.data.code
      ElMessage.success(`开发环境验证码：${res.data.code}`)
    } else {
      ElMessage.success('验证码已发送，请注意查收短信')
    }

    startCountdown()
  } catch (err) {
    const msg = err?.response?.data?.message || err?.message || '验证码发送失败，请稍后重试'
    ElMessage.error(msg)
  }
}

function fillTestAccount() {
  if (!isDev) return
  pwdForm.username = 'admin'
  pwdForm.password = '123456'
  ElMessage.success('已填入开发环境测试账号')
}

function handleTabSwitch() {
  if (loginTab.value === 'sms') {
    smsFormRef.value?.clearValidate()
  } else {
    pwdFormRef.value?.clearValidate()
  }
}

async function handlePwdLogin() {
  if (!pwdFormRef.value) return

  await pwdFormRef.value.validate(async (valid) => {
    if (!valid) return
    pwdLoading.value = true

    try {
      const res = await pwdLogin({
        username: pwdForm.username.trim(),
        password: pwdForm.password,
      })

      if (res?.code !== 200) {
        ElMessage.error(res?.message || '用户名或密码错误')
        return
      }

      const accessToken = res.data?.access || res.data?.access_token
      const refreshToken = res.data?.refresh || res.data?.refresh_token
      persistLoginState(accessToken, refreshToken)
      await cacheCurrentUser()
      appStore.setMode(loginMode.value)
      ElMessage.success(`登录成功，欢迎使用${appStore.modeLabel}`)
      router.push('/')
    } catch (err) {
      const msg = err?.response?.data?.message || err?.message || '登录失败，请检查用户名和密码'
      ElMessage.error(msg)
    } finally {
      pwdLoading.value = false
    }
  })
}

async function handleLogin() {
  if (!smsFormRef.value) return
  if (!smsAgreed.value) {
    ElMessage.warning('请先阅读并同意用户协议与隐私政策')
    return
  }

  await smsFormRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true

    try {
      const res = await mobileLogin({
        phone: smsForm.phone,
        code: smsForm.code,
        country_code: '86',
        agreed_privacy: smsAgreed.value,
      })

      if (res?.code !== 200) {
        ElMessage.error(res?.message || '登录失败，请检查验证码')
        return
      }

      const accessToken = res.data?.access || res.data?.access_token
      const refreshToken = res.data?.refresh || res.data?.refresh_token
      persistLoginState(accessToken, refreshToken, smsForm.phone)

      if (rememberMe.value) {
        localStorage.setItem('remembered_phone', smsForm.phone)
      } else {
        localStorage.removeItem('remembered_phone')
      }

      await cacheCurrentUser()
      appStore.setMode(loginMode.value)
      ElMessage.success(`登录成功，欢迎使用${appStore.modeLabel}`)
      router.push('/')
    } catch (err) {
      const status = err?.response?.status
      const msg = err?.response?.data?.message

      if (status === 400) {
        ElMessage.error(msg || '验证码错误或已过期，请重新获取')
      } else if (status === 403) {
        ElMessage.error(msg || '登录已被限制，请稍后重试')
      } else if (status === 429) {
        ElMessage.warning(msg || '操作过于频繁，请稍后重试')
      } else {
        ElMessage.error(msg || '登录失败，请稍后重试')
      }
    } finally {
      loading.value = false
    }
  })
}

const savedPhone = localStorage.getItem('remembered_phone')
if (savedPhone) {
  smsForm.phone = savedPhone
  rememberMe.value = true
}

onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
})
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #f1f5f9 100%);
  position: relative;
  overflow: hidden;
  padding: 32px 16px;
}

.login-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.bg-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.12;
}

.shape-1 {
  width: 560px;
  height: 560px;
  background: #085b9c;
  top: -180px;
  right: -120px;
}

.shape-2 {
  width: 360px;
  height: 360px;
  background: #2ead3e;
  bottom: -120px;
  left: -90px;
}

.shape-3 {
  width: 260px;
  height: 260px;
  background: linear-gradient(135deg, #085b9c 0%, #2ead3e 100%);
  top: 48%;
  left: 52%;
  transform: translate(-50%, -50%);
}

.login-card {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.96);
  border-radius: 18px;
  padding: 40px 32px;
  box-shadow:
    0 8px 24px rgba(15, 23, 42, 0.08),
    0 20px 48px rgba(15, 23, 42, 0.12);
  overflow: hidden;
}

.login-card::before {
  content: '';
  position: absolute;
  inset: 0 0 auto;
  height: 4px;
  background: linear-gradient(90deg, #085b9c 0%, #2ead3e 100%);
}

.login-logo {
  text-align: center;
  margin-bottom: 22px;
}

.logo-img {
  width: 72px;
  height: 72px;
  object-fit: contain;
  margin: 0 auto 14px;
  border-radius: 14px;
}

.logo-title {
  margin: 0 0 6px;
  font-size: 24px;
  font-weight: 700;
  color: #0f172a;
}

.logo-subtitle {
  margin: 0;
  color: #64748b;
  font-size: 13px;
}

.mode-selector {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 22px;
}

.mode-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 14px;
  border-radius: 14px;
  border: 1px solid #dbe4ee;
  background: #f8fafc;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mode-card:hover {
  border-color: #8bb8da;
  background: #f3f8fc;
}

.mode-card.active {
  border-color: #085b9c;
  background: linear-gradient(135deg, rgba(8, 91, 156, 0.08), rgba(46, 173, 62, 0.08));
  box-shadow: 0 0 0 3px rgba(8, 91, 156, 0.08);
}

.mode-title {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
}

.mode-desc {
  font-size: 12px;
  line-height: 1.5;
  color: #64748b;
}

.login-tabs :deep(.el-tabs__header) {
  margin-bottom: 14px;
}

.login-tabs :deep(.el-tabs__nav) {
  width: 100%;
  display: flex;
}

.login-tabs :deep(.el-tabs__item) {
  flex: 1;
  text-align: center;
  font-size: 14px;
  font-weight: 600;
}

.login-tabs :deep(.el-tabs__active-bar) {
  height: 3px;
  border-radius: 999px;
  background: linear-gradient(90deg, #085b9c, #2ead3e);
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px #e2e8f0;
}

.login-form :deep(.el-input__wrapper:hover),
.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px #085b9c;
}

.login-form :deep(.el-input__prefix) {
  color: #94a3b8;
}

.send-code-btn {
  height: 38px;
  border: none;
  color: #085b9c;
  background: transparent;
}

.send-code-btn:not(:disabled):hover {
  color: #2ead3e;
  background: #f0fff4;
}

.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}

.agreement-row {
  margin-bottom: 22px;
  color: #64748b;
  line-height: 1.7;
}

.agreement-row :deep(.el-checkbox) {
  align-items: flex-start;
  white-space: normal;
}

.agreement-row :deep(.el-checkbox__label) {
  white-space: normal;
  line-height: 1.7;
}

.login-btn {
  width: 100%;
  height: 44px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  background: linear-gradient(135deg, #085b9c 0%, #2ead3e 100%);
  box-shadow: 0 10px 24px rgba(8, 91, 156, 0.22);
}

.login-footer {
  margin-top: 26px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
  text-align: center;
}

.footer-text {
  margin-right: 8px;
  color: #64748b;
  font-size: 13px;
}

.version-info {
  position: absolute;
  bottom: 20px;
  display: flex;
  gap: 8px;
  color: #94a3b8;
  font-size: 12px;
}

.divider {
  color: #cbd5e1;
}

@media (max-width: 640px) {
  .login-card {
    padding: 32px 20px;
  }

  .mode-selector {
    grid-template-columns: 1fr;
  }

  .version-info {
    position: static;
    margin-top: 18px;
    text-align: center;
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>
