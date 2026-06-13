<template>
  <div class="register-page">
    <div class="register-card">
      <div class="reg-logo">
        <h1>辽宁跨境宝盒</h1>
        <p>手机号验证码注册，注册后可直接进入系统</p>
      </div>

      <div class="reg-intro">
        <span class="intro-badge">SMS Register</span>
        <p>账号通过短信验证码完成校验，密码登录作为备用入口保留。</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="reg-form"
        @submit.prevent="handleRegister"
      >
        <el-form-item label="手机号" prop="phone">
          <el-input
            v-model="form.phone"
            placeholder="请输入 11 位手机号"
            maxlength="11"
            clearable
          />
        </el-form-item>

        <el-form-item label="验证码" prop="smsCode">
          <div class="sms-row">
            <el-input
              v-model="form.smsCode"
              placeholder="请输入短信验证码"
              maxlength="6"
            />
            <el-button
              class="sms-btn"
              :disabled="countdown > 0"
              :loading="sendingCode"
              @click="handleSendSms"
            >
              {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="登录密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入 6-20 位密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            show-password
          />
        </el-form-item>

        <div class="agreement-row">
          <el-checkbox v-model="form.agreed">
            我已阅读并同意
            <el-link type="primary" :underline="false">《用户协议》</el-link>
            和
            <el-link type="primary" :underline="false">《隐私政策》</el-link>
          </el-checkbox>
        </div>

        <div class="step-actions">
          <el-button type="primary" :loading="submitting" @click="handleRegister">
            注册并进入系统
          </el-button>
          <el-button text @click="$router.push('/login')">返回登录</el-button>
        </div>
      </el-form>

      <div class="reg-footer">
        <span>已有账号？</span>
        <el-link type="primary" :underline="false" @click="$router.push('/login')">
          去登录
        </el-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getCurrentUser, register, sendSmsCode } from '@/api/auth'

const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)
const sendingCode = ref(false)
const countdown = ref(0)
let countdownTimer = null

const validateConfirmPassword = (_rule, value, callback) => {
  if (!value) {
    callback(new Error('请再次输入密码'))
    return
  }
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
    return
  }
  callback()
}

const form = reactive({
  phone: '',
  smsCode: '',
  password: '',
  confirmPassword: '',
  agreed: false,
})

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' },
  ],
  smsCode: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { pattern: /^\d{4,6}$/, message: '验证码为 4-6 位数字', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度需为 6-20 位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
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

async function handleSendSms() {
  if (countdown.value > 0 || sendingCode.value) return

  const phonePattern = /^1[3-9]\d{9}$/
  if (!form.agreed) {
    ElMessage.warning('请先阅读并同意用户协议与隐私政策')
    return
  }
  if (!form.phone || !phonePattern.test(form.phone)) {
    ElMessage.warning('请输入正确的手机号')
    return
  }

  sendingCode.value = true
  try {
    const res = await sendSmsCode(form.phone, '86')
    if (res && res.code === 200) {
      if (res.data?.code) {
        form.smsCode = res.data.code
        ElMessage.success(`验证码已发送（开发模式）：${res.data.code}`)
      } else {
        ElMessage.success('验证码已发送，请注意查收短信')
      }
      startCountdown()
      return
    }
    ElMessage.warning(res?.message || '发送失败，请稍后重试')
  } catch (err) {
    const msg = err?.response?.data?.message || err?.message || '发送失败，请稍后重试'
    ElMessage.error(msg)
  } finally {
    sendingCode.value = false
  }
}

async function handleRegister() {
  if (!formRef.value || submitting.value) return

  const valid = await formRef.value.validate().then(() => true).catch(() => false)
  if (!valid) return

  if (!form.agreed) {
    ElMessage.warning('请先阅读并同意用户协议与隐私政策')
    return
  }

  submitting.value = true
  try {
    const res = await register({
      phone: form.phone,
      sms_code: form.smsCode,
      password: form.password,
      country_code: '86',
      agreed_privacy: true,
    })

    if (res && res.code === 200) {
      const accessToken = res.data?.access || res.data?.access_token
      const refreshToken = res.data?.refresh || res.data?.refresh_token
      if (accessToken) {
        localStorage.setItem('access_token', accessToken)
      }
      if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken)
      }
      localStorage.setItem('user_phone', form.phone)

      try {
        const userRes = await getCurrentUser()
        if (userRes?.data) {
          localStorage.setItem('user_info', JSON.stringify(userRes.data))
        }
      } catch (_) {
        // User info fetch should not block successful registration.
      }

      ElMessage.success('注册成功')
      router.push('/')
      return
    }

    ElMessage.error(res?.message || '注册失败，请稍后重试')
  } catch (err) {
    const status = err?.response?.status
    const msg = err?.response?.data?.message
    if (status === 400) {
      ElMessage.error(msg || '验证码错误、手机号已注册或参数无效')
    } else if (status === 429) {
      ElMessage.warning(msg || '操作过于频繁，请稍后再试')
    } else {
      ElMessage.error(msg || '注册失败，请稍后重试')
    }
  } finally {
    submitting.value = false
  }
}

onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
})
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(circle at top left, rgba(8, 91, 156, 0.12), transparent 32%),
    radial-gradient(circle at bottom right, rgba(46, 173, 62, 0.12), transparent 30%),
    linear-gradient(135deg, #f8fafc, #e2e8f0);
  padding: 40px 16px;
}

.register-card {
  width: 100%;
  max-width: 560px;
  background: rgba(255, 255, 255, 0.96);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.12);
  position: relative;
  overflow: hidden;
}

.register-card::before {
  content: '';
  position: absolute;
  inset: 0 0 auto;
  height: 5px;
  background: linear-gradient(90deg, #085b9c, #2ead3e);
}

.reg-logo {
  text-align: center;
  margin-bottom: 18px;
}

.reg-logo h1 {
  margin: 0 0 8px;
  font-size: 28px;
  font-weight: 700;
  color: #0f172a;
}

.reg-logo p {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

.reg-intro {
  margin-bottom: 24px;
  padding: 16px 18px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(8, 91, 156, 0.08), rgba(46, 173, 62, 0.08));
  border: 1px solid rgba(8, 91, 156, 0.08);
}

.intro-badge {
  display: inline-flex;
  align-items: center;
  height: 26px;
  padding: 0 10px;
  border-radius: 999px;
  background: #085b9c;
  color: #fff;
  font-size: 12px;
  letter-spacing: 0.04em;
}

.reg-intro p {
  margin: 10px 0 0;
  color: #334155;
  line-height: 1.6;
  font-size: 14px;
}

.reg-form {
  margin-top: 8px;
}

.sms-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 132px;
  gap: 10px;
  width: 100%;
}

.sms-btn {
  width: 132px;
}

.agreement-row {
  margin-top: 4px;
  color: #475569;
  line-height: 1.7;
}

.step-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 28px;
}

.step-actions :deep(.el-button--primary) {
  min-width: 188px;
}

.reg-footer {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  color: #64748b;
  font-size: 13px;
}

@media (max-width: 640px) {
  .register-card {
    padding: 28px 20px;
    border-radius: 18px;
  }

  .reg-logo h1 {
    font-size: 24px;
  }

  .sms-row {
    grid-template-columns: 1fr;
  }

  .sms-btn {
    width: 100%;
  }

  .step-actions {
    flex-direction: column;
  }

  .step-actions :deep(.el-button) {
    width: 100%;
    margin-left: 0;
  }
}
</style>
