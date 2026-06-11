<template>
  <div class="login-page">
    <!-- 背景装饰 -->
    <div class="login-bg">
      <div class="bg-shape shape-1"></div>
      <div class="bg-shape shape-2"></div>
      <div class="bg-shape shape-3"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <!-- Logo区 -->
      <div class="login-logo">
        <img src="@/assets/logo.png" alt="辽宁跨境宝盒" class="logo-img" />
        <h1 class="logo-title">辽宁跨境宝盒</h1>
        <p class="logo-subtitle">跨境电商ERP管理系统</p>
      </div>

      <!-- 双模式切换（醒目大卡片） -->
      <div class="mode-selector">
        <div
          :class="['mode-card', 'beginner', { active: loginMode === 'beginner' }]"
          @click="loginMode = 'beginner'"
        >
          <div class="mode-card-icon">🌟</div>
          <div class="mode-card-content">
            <div class="mode-card-title">小白模式</div>
            <div class="mode-card-desc">AI全程带路 · 一键铺货 · 简单高效</div>
          </div>
          <div v-if="loginMode === 'beginner'" class="mode-card-check">✓</div>
        </div>

        <div
          :class="['mode-card', 'expert', { active: loginMode === 'expert' }]"
          @click="loginMode = 'expert'"
        >
          <div class="mode-card-icon">⚡</div>
          <div class="mode-card-content">
            <div class="mode-card-title">资深模式</div>
            <div class="mode-card-desc">全量功能 · 全平台适配 · 精细运营</div>
          </div>
          <div v-if="loginMode === 'expert'" class="mode-card-check">✓</div>
        </div>
      </div>

      <!-- 登录方式切换 -->
      <el-tabs v-model="loginTab" class="login-tabs" @tab-click="handleTabSwitch">
        <el-tab-pane label="短信登录" name="sms">
          <el-form
            ref="smsFormRef"
            :model="loginForm"
            :rules="smsRules"
            class="login-form"
            @submit.prevent="handleLogin"
          >
            <el-form-item prop="phone">
              <el-input
                v-model="loginForm.phone"
                placeholder="请输入手机号"
                size="large"
                :prefix-icon="Phone"
                clearable
              />
            </el-form-item>

            <el-form-item prop="code">
              <el-input
                v-model="loginForm.code"
                placeholder="请输入验证码"
                size="large"
                :prefix-icon="Message"
                maxlength="6"
                style="width: calc(100% - 130px)"
              >
                <template #append>
                  <el-button 
                    :disabled="countdown > 0" 
                    @click="handleSendCode"
                    class="send-code-btn"
                  >
                    {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
                  </el-button>
                </template>
              </el-input>
            </el-form-item>

            <div class="form-options">
              <el-checkbox v-model="rememberMe">记住手机号</el-checkbox>
            </div>

            <el-button
              type="primary"
              size="large"
              :loading="loading"
              class="login-btn"
              @click="handleLogin"
            >
              登 录
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
                placeholder="请输入用户名"
                size="large"
                :prefix-icon="User"
                clearable
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="pwdForm.password"
                :type="showPwd ? 'text' : 'password'"
                placeholder="请输入密码"
                size="large"
                :prefix-icon="Lock"
                show-password
                @click:append="showPwd = !showPwd"
              />
            </el-form-item>

            <div class="form-options">
              <el-button text size="small" @click="fillTestAccount">一键填入测试账号</el-button>
            </div>

            <el-button
              type="primary"
              size="large"
              :loading="pwdLoading"
              class="login-btn"
              @click="handlePwdLogin"
            >
              登 录
            </el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <!-- 底部 -->
      <div class="login-footer">
        <span class="footer-text">还没有账号？</span>
        <el-link type="primary" :underline="'never'" @click="$router.push('/register')">立即注册</el-link>
      </div>
    </div>

    <!-- 版本信息 -->
    <div class="version-info">
      <span>v1.0.0</span>
      <span class="divider">|</span>
      <span>跨境电商ERP系统</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Phone, Message, User, Lock } from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/useAppStore'
import { sendSmsCode, mobileLogin, login as pwdLogin, getCurrentUser } from '@/api/auth'

const router = useRouter()
const appStore = useAppStore()
const smsFormRef = ref(null)
const pwdFormRef = ref(null)
const loading = ref(false)
const pwdLoading = ref(false)
const rememberMe = ref(false)
const countdown = ref(0)
let countdownTimer = null

// 登录方式切换
const loginTab = ref('sms')

// 短信登录表单
const loginForm = reactive({
  phone: '',
  code: '',
})

// 密码登录表单
const pwdForm = reactive({
  username: '',
  password: '',
})
const showPwd = ref(false)

// ── 双模式切换 ────────────────────────────────────────────
// 'beginner': 小白模式（一键铺货，AI全程带路）
// 'expert':   资深模式（全量功能，全平台适配）
const loginMode = ref(appStore.mode || 'beginner')

const smsRules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' },
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { pattern: /^\d{4,6}$/, message: '验证码为4-6位数字', trigger: 'blur' },
  ],
}

const pwdRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 4, message: '密码长度不少于4位', trigger: 'blur' },
  ],
}

// 发送验证码（真实短信通道）
async function handleSendCode() {
  if (countdown.value > 0) return
  
  // 验证手机号格式
  const phonePattern = /^1[3-9]\d{9}$/
  
  if (!loginForm.phone || !phonePattern.test(loginForm.phone)) {
    ElMessage.warning('请输入正确的手机号')
    return
  }
  
  try {
    const res = await sendSmsCode(loginForm.phone, '86')
    if (res && res.code === 200) {
      // 检查是否为开发通道
      if (res.data?.is_development) {
        ElMessage.success(`验证码已生成（开发模式）：${res.data?.code || ''}`)
        // 开发模式自动填充验证码
        if (res.data?.code) {
          loginForm.code = res.data.code
        }
      } else {
        ElMessage.success('验证码已发送，请注意查收短信')
      }
    } else if (res && res.code === 429) {
      // 频率限制
      ElMessage.warning(res.message || '发送过于频繁，请60秒后再试')
      return
    } else if (res && res.data?.error_code) {
      // 后端返回了具体错误码
      const errMap = {
        'CONFIG_MISSING': '短信服务未配置，请联系管理员',
        'CONFIG_INVALID': '短信密钥配置异常，请联系管理员',
        'SDK_NOT_INSTALLED': '短信SDK未安装，请联系管理员',
        'BALANCE_INSUFFICIENT': '短信账户余额不足，请联系管理员充值',
        'RATE_LIMITED': '发送频率过高，请稍后再试',
        'AUTH_FAILED': '短信鉴权失败，请联系管理员检查密钥',
        'TEMPLATE_ERROR': '短信模板配置错误，请联系管理员',
        'NETWORK_ERROR': '短信服务网络异常，请稍后重试',
        'ALL_PROVIDERS_FAILED': '所有短信通道不可用，请稍后重试',
      }
      ElMessage.error(errMap[res.data.error_code] || res.message || '发送失败')
      return
    } else {
      ElMessage.warning(res?.message || '发送失败，请稍后重试')
      return
    }
  } catch (err) {
    const msg = err?.response?.data?.message || err?.message || '网络异常，请检查连接后重试'
    ElMessage.error(msg)
    return
  }
  
  // 开始倒计时
  countdown.value = 60
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(countdownTimer)
      countdownTimer = null
    }
  }, 1000)
}

// 切换登录 Tab 时重置表单
function handleTabSwitch() {
  if (loginTab.value === 'sms') {
    smsFormRef.value?.clearValidate()
  } else {
    pwdFormRef.value?.clearValidate()
  }
}

// 一键填入测试账号
function fillTestAccount() {
  pwdForm.username = 'admin'
  pwdForm.password = '123456'
  showPwd.value = false
  ElMessage.success('已填入测试账号，点击登录即可')
}

// 密码登录
async function handlePwdLogin() {
  if (!pwdFormRef.value) return
  await pwdFormRef.value.validate(async (valid) => {
    if (!valid) return
    pwdLoading.value = true
    try {
      const res = await pwdLogin({ username: pwdForm.username, password: pwdForm.password })
      if (res && res.code === 200) {
        const accessToken = res.data?.access || res.data?.access_token
        const refreshToken = res.data?.refresh || res.data?.refresh_token
        if (accessToken) {
          localStorage.setItem('access_token', accessToken)
          localStorage.setItem('refresh_token', refreshToken)
        }
        try {
          const userRes = await getCurrentUser()
          if (userRes?.data) {
            localStorage.setItem('user_info', JSON.stringify(userRes.data))
          }
        } catch (_) {}
        appStore.setMode(loginMode.value)
        ElMessage.success(`登录成功，欢迎使用${appStore.modeLabel}！`)
        router.push('/')
      } else {
        ElMessage.error(res?.message || '用户名或密码错误')
      }
    } catch (err) {
      const msg = err?.response?.data?.message || err?.message || '登录失败，请检查用户名和密码'
      ElMessage.error(msg)
    } finally {
      pwdLoading.value = false
    }
  })
}

// 登录（真实手机号验证码登录）
async function handleLogin() {
  if (!smsFormRef.value) return
  
  await smsFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    
    try {
      // 调用真实手机号验证码登录接口
      const res = await mobileLogin({
        phone: loginForm.phone,
        code: loginForm.code,
        country_code: '86',
        agreed_privacy: true,
      })
      
      if (res && res.code === 200) {
        // 保存 JWT Token
        const accessToken = res.data?.access || res.data?.access_token
        const refreshToken = res.data?.refresh || res.data?.refresh_token
        if (accessToken) {
          localStorage.setItem('access_token', accessToken)
          localStorage.setItem('refresh_token', refreshToken)
          localStorage.setItem('user_phone', loginForm.phone)
        }
        
        if (rememberMe.value) {
          localStorage.setItem('remembered_phone', loginForm.phone)
        }
        
        // 获取用户信息
        try {
          const userRes = await getCurrentUser()
          if (userRes?.data) {
            localStorage.setItem('user_info', JSON.stringify(userRes.data))
          }
        } catch (_) {
          // 用户信息获取失败不阻断登录
        }

        // 保存选择的模式
        appStore.setMode(loginMode.value)

        ElMessage.success(`登录成功，欢迎使用${appStore.modeLabel}！`)
        router.push('/')
      } else {
        ElMessage.error(res?.message || '登录失败，请检查验证码')
      }
    } catch (err) {
      const status = err?.response?.status
      const msg = err?.response?.data?.message
      if (status === 400) {
        ElMessage.error(msg || '验证码错误或已过期，请重新获取')
      } else if (status === 403) {
        ElMessage.error(msg || '登录已被限制，请稍后再试')
      } else if (status === 429) {
        ElMessage.warning(msg || '操作过于频繁，请稍后再试')
      } else {
        ElMessage.error(msg || '登录失败，请稍后重试')
      }
    } finally {
      loading.value = false
    }
  })
}

// 页面加载时恢复记住的手机号
const savedPhone = localStorage.getItem('remembered_phone')
if (savedPhone) {
  loginForm.phone = savedPhone
  rememberMe.value = true
}

// 组件卸载时清理定时器
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
}

/* 背景装饰 - 蓝绿配色 */
.login-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.bg-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
}

.shape-1 {
  width: 600px;
  height: 600px;
  background: #085B9C;
  top: -200px;
  right: -100px;
}

.shape-2 {
  width: 400px;
  height: 400px;
  background: #2ead3e;
  bottom: -150px;
  left: -100px;
}

.shape-3 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #085B9C 0%, #2ead3e 100%);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* 登录卡片 */
.login-card {
  position: relative;
  z-index: 10;
  width: 400px;
  background: #fff;
  border-radius: 16px;
  padding: 48px 40px;
  box-shadow: 
    0 4px 6px -1px rgba(0, 0, 0, 0.05),
    0 10px 15px -3px rgba(0, 0, 0, 0.08),
    0 20px 25px -5px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

/* 顶部蓝绿装饰条 */
.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #085B9C 0%, #2ead3e 100%);
}

/* Logo区 */
.login-logo {
  text-align: center;
  margin-bottom: 16px;
}

.logo-img {
  width: 80px;
  height: 80px;
  object-fit: contain;
  margin: 0 auto 16px;
  border-radius: 16px;
}

/* 双模式大卡片选择器 */
.mode-selector {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.mode-card {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 12px;
  border: 2px solid var(--el-border-color-light);
  cursor: pointer;
  transition: all 0.25s ease;
  position: relative;
  user-select: none;
  background: var(--el-fill-color-light);
  overflow: hidden;
}

.mode-card:hover {
  border-color: var(--el-color-primary-light-5);
  background: var(--el-fill-color-lighter);
}

.mode-card.active.beginner {
  border-color: #2ead3e;
  background: linear-gradient(135deg, rgba(46, 173, 62, 0.08) 0%, rgba(8, 91, 156, 0.05) 100%);
  box-shadow: 0 0 0 3px rgba(46, 173, 62, 0.15);
}

.mode-card.active.expert {
  border-color: #085B9C;
  background: linear-gradient(135deg, rgba(8, 91, 156, 0.08) 0%, rgba(46, 173, 62, 0.05) 100%);
  box-shadow: 0 0 0 3px rgba(8, 91, 156, 0.15);
}

.mode-card-icon {
  font-size: 28px;
  line-height: 1;
}

.mode-card-content {
  flex: 1;
}

.mode-card-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  margin-bottom: 2px;
}

.mode-card-desc {
  font-size: 11px;
  color: var(--el-text-color-secondary);
  white-space: normal;
  word-break: break-all;
  line-height: 1.4;
}

.mode-card-check {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}

.mode-card.active.beginner .mode-card-check {
  background: #2ead3e;
}

.mode-card.active.expert .mode-card-check {
  background: #085B9C;
}

.logo-title {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 6px;
  letter-spacing: -0.02em;
}

.logo-subtitle {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

/* 登录 Tab 切换 */
.login-tabs {
  margin-top: 4px;
}
.login-tabs :deep(.el-tabs__header) {
  margin: 0 0 12px;
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
  padding: 0;
  height: 36px;
  line-height: 36px;
}
.login-tabs :deep(.el-tabs__active-bar) {
  height: 3px;
  border-radius: 2px;
  background: linear-gradient(90deg, #085B9C, #2ead3e);
}

/* 表单 */
.login-form {
  margin-top: 8px;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px #e2e8f0;
  transition: all 0.2s;
}

.login-form :deep(.el-input__wrapper:hover),
.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px #085B9C;
}

.login-form :deep(.el-input__prefix) {
  color: #94a3b8;
}

.login-form :deep(.el-input-group__append) {
  border-radius: 0 10px 10px 0;
  padding: 0;
  border-left: none;
}

.login-form :deep(.el-input__wrapper:has(.el-input-group__append)) {
  border-radius: 10px 0 0 10px;
}

.send-code-btn {
  height: 38px;
  padding: 0 16px;
  font-size: 13px;
  color: #085B9C;
  font-weight: 500;
  background: transparent;
  border: none;
  white-space: nowrap;
}

.send-code-btn:not(:disabled):hover {
  color: #2ead3e;
  background: #f0fff4;
}

.send-code-btn:disabled {
  color: #94a3b8;
  cursor: not-allowed;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.form-options :deep(.el-checkbox__label) {
  color: #64748b;
  font-size: 13px;
}

.login-btn {
  width: 100%;
  height: 44px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.05em;
  background: linear-gradient(135deg, #085B9C 0%, #2ead3e 100%);
  border: none;
  box-shadow: 0 4px 14px rgba(8, 91, 156, 0.3);
  transition: all 0.2s;
}

.login-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(8, 91, 156, 0.4);
}

.login-btn:active {
  transform: translateY(0);
}

/* 底部 */
.login-footer {
  margin-top: 28px;
  text-align: center;
  padding-top: 24px;
  border-top: 1px solid #f1f5f9;
}

.footer-text {
  color: #64748b;
  font-size: 13px;
}

/* 版本信息 */
.version-info {
  position: absolute;
  bottom: 24px;
  color: #94a8b8;
  font-size: 12px;
  display: flex;
  gap: 8px;
}

.version-info .divider {
  color: #cbd5e1;
}
</style>
