<template>
  <div class="register-page">
    <div class="register-card">
      <div class="reg-logo">
        <h1>辽宁跨境宝盒</h1>
        <p>创建您的跨境电商账号</p>
      </div>

      <!-- 步骤条 -->
      <el-steps :active="step" align-center class="reg-steps">
        <el-step title="账号信息" />
        <el-step title="实名认证" />
        <el-step title="经营信息" />
        <el-step title="提交审核" />
      </el-steps>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="reg-form" @submit.prevent>

        <!-- Step 0: 账号信息 -->
        <div v-show="step === 0">
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="form.phone" placeholder="输入11位手机号" maxlength="11" />
          </el-form-item>
          <el-form-item label="验证码" prop="smsCode">
            <el-input v-model="form.smsCode" placeholder="输入短信验证码" maxlength="6" style="width:calc(100% - 140px)" />
            <el-button :disabled="countdown>0" @click="sendSms" style="width:130px;margin-left:10px">
              {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
            </el-button>
          </el-form-item>
          <el-form-item label="登录密码" prop="password">
            <el-input v-model="form.password" type="password" placeholder="6-16位，含数字与字母" show-password />
          </el-form-item>
          <el-form-item label="用户类型" prop="userType">
            <el-radio-group v-model="form.userType">
              <el-radio-button value="personal">个人卖家</el-radio-button>
              <el-radio-button value="enterprise">企业卖家</el-radio-button>
            </el-radio-group>
          </el-form-item>
        </div>

        <!-- Step 1: 实名认证 -->
        <div v-show="step === 1">
          <template v-if="form.userType === 'personal'">
            <el-form-item label="真实姓名" prop="realName">
              <el-input v-model="form.realName" placeholder="与身份证一致" />
            </el-form-item>
            <el-form-item label="身份证号" prop="idCard">
              <el-input v-model="form.idCard" placeholder="18位身份证号" maxlength="18" />
            </el-form-item>
            <el-form-item label="身份证正面" prop="idFront">
              <el-upload class="id-upload" :auto-upload="false" :limit="1" list-type="picture-card"
                :on-change="(f) => form.idFront = f.raw">
                <el-icon><Plus /></el-icon>
              </el-upload>
            </el-form-item>
            <el-form-item label="身份证反面" prop="idBack">
              <el-upload class="id-upload" :auto-upload="false" :limit="1" list-type="picture-card"
                :on-change="(f) => form.idBack = f.raw">
                <el-icon><Plus /></el-icon>
              </el-upload>
            </el-form-item>
          </template>
          <template v-else>
            <el-form-item label="企业名称" prop="companyName">
              <el-input v-model="form.companyName" placeholder="与营业执照一致" />
            </el-form-item>
            <el-form-item label="统一社会信用代码" prop="creditCode">
              <el-input v-model="form.creditCode" placeholder="18位统一社会信用代码" maxlength="18" />
            </el-form-item>
            <el-form-item label="营业执照" prop="license">
              <el-upload class="id-upload" :auto-upload="false" :limit="1" list-type="picture-card"
                :on-change="(f) => form.license = f.raw">
                <el-icon><Plus /></el-icon>
              </el-upload>
            </el-form-item>
            <el-form-item label="法人姓名" prop="legalPerson">
              <el-input v-model="form.legalPerson" placeholder="法人姓名" />
            </el-form-item>
          </template>
        </div>

        <!-- Step 2: 经营信息 -->
        <div v-show="step === 2">
          <el-form-item label="主营类目">
            <el-select v-model="form.category" placeholder="请选择" style="width:100%">
              <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
            </el-select>
          </el-form-item>
          <el-form-item label="目标市场">
            <el-checkbox-group v-model="form.markets">
              <el-checkbox v-for="m in markets" :key="m" :label="m" :value="m">{{ m }}</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          <el-form-item label="经营经验">
            <el-radio-group v-model="form.experience">
              <el-radio label="new">0经验新手</el-radio>
              <el-radio label="half">1年以内</el-radio>
              <el-radio label="senior">1-3年</el-radio>
              <el-radio label="expert">3年以上</el-radio>
            </el-radio-group>
          </el-form-item>
        </div>

        <!-- Step 3: 提交审核 -->
        <div v-show="step === 3">
          <div class="confirm-section">
            <el-descriptions title="请确认注册信息" :column="1" border>
              <el-descriptions-item label="手机号">{{ form.phone }}</el-descriptions-item>
              <el-descriptions-item label="用户类型">{{ form.userType === 'personal' ? '个人卖家' : '企业卖家' }}</el-descriptions-item>
              <el-descriptions-item label="姓名/企业">{{ form.realName || form.companyName }}</el-descriptions-item>
              <el-descriptions-item label="主营类目">{{ form.category || '未选择' }}</el-descriptions-item>
              <el-descriptions-item label="目标市场">{{ form.markets.join('、') || '未选择' }}</el-descriptions-item>
              <el-descriptions-item label="经营经验">{{ experienceMap[form.experience] || '未选择' }}</el-descriptions-item>
            </el-descriptions>
            <el-checkbox v-model="agreed" style="margin-top:16px">
              我已阅读并同意 <el-link type="primary">《用户协议》</el-link> 和 <el-link type="primary">《隐私政策》</el-link>
            </el-checkbox>
          </div>
        </div>

        <div class="step-actions">
          <el-button v-if="step > 0" @click="step--">上一步</el-button>
          <el-button v-if="step < 3" type="primary" @click="nextStep">下一步</el-button>
          <el-button v-else type="primary" :loading="submitting" @click="submitRegister">提交注册申请</el-button>
          <el-button text @click="$router.push('/login')" style="margin-left:12px">返回登录</el-button>
        </div>
      </el-form>

      <!-- 审核状态查询 -->
      <div class="reg-footer">
        <span>已提交申请？</span>
        <el-link type="primary" @click="showQuery = true">审核进度查询</el-link>
      </div>
    </div>

    <!-- 审核进度查询弹窗 -->
    <el-dialog v-model="showQuery" title="审核进度查询" width="400px">
      <el-form>
        <el-form-item label="注册手机号">
          <el-input v-model="queryPhone" placeholder="输入注册时的手机号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showQuery = false">取消</el-button>
        <el-button type="primary" @click="checkStatus">查询</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()
const formRef = ref(null)
const step = ref(0)
const submitting = ref(false)
const agreed = ref(false)
const countdown = ref(0)
const showQuery = ref(false)
const queryPhone = ref('')
let timer = null

const categories = ['电子产品', '服装鞋帽', '家居用品', '美妆个护', '运动户外', '箱包皮具', '母婴玩具', '汽车用品', '食品饮料', '其他']
const markets = ['东南亚', '北美', '欧洲', '中东', '拉美', '日韩', '非洲', '澳洲']
const experienceMap = { new: '0经验新手', half: '1年以内', senior: '1-3年', expert: '3年以上' }

const form = reactive({
  phone: '', smsCode: '', password: '', userType: 'personal',
  realName: '', idCard: '', idFront: null, idBack: null,
  companyName: '', creditCode: '', license: null, legalPerson: '',
  category: '', markets: [], experience: ''
})

const rules = {
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }, { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确' }],
  smsCode: [{ required: true, message: '请输入验证码' }],
  password: [{ required: true, message: '请设置密码' }, { min: 6, max: 16, message: '6-16位' }],
  userType: [{ required: true }],
  realName: [{ required: true, message: '请输入真实姓名' }],
  idCard: [{ required: true, message: '请输入身份证号' }],
  companyName: [{ required: true, message: '请输入企业名称' }],
  creditCode: [{ required: true, message: '请输入统一社会信用代码' }],
}

function sendSms() {
  if (!/^1[3-9]\d{9}$/.test(form.phone)) { ElMessage.warning('请输入正确手机号'); return }
  request.post('/api/auth/send-sms', { phone: form.phone, country_code: '86' }).then(res => {
    if (res?.data?.code) { form.smsCode = res.data.code; ElMessage.success(`验证码: ${res.data.code}`) }
    else ElMessage.success('验证码已发送')
    countdown.value = 60
    timer = setInterval(() => { countdown.value--; if (countdown.value <= 0) clearInterval(timer) }, 1000)
  }).catch(() => ElMessage.error('发送失败'))
}

function nextStep() {
  if (step.value === 0) { if (!form.phone || !form.smsCode || !form.password) { ElMessage.warning('请完善信息'); return } }
  if (step.value === 1) {
    if (form.userType === 'personal' && (!form.realName || !form.idCard)) { ElMessage.warning('请完成实名认证'); return }
    if (form.userType === 'enterprise' && (!form.companyName || !form.creditCode)) { ElMessage.warning('请完善企业信息'); return }
  }
  step.value++
}

async function submitRegister() {
  if (!agreed.value) { ElMessage.warning('请同意用户协议'); return }
  submitting.value = true
  try {
    await request.post('/api/auth/register-submit/', {
      phone: form.phone, sms_code: form.smsCode, password: form.password,
      user_type: form.userType, real_name: form.realName, id_card: form.idCard,
      company_name: form.companyName, credit_code: form.creditCode,
      legal_person: form.legalPerson, category: form.category,
      markets: form.markets, experience: form.experience,
    })
    ElMessage.success('注册申请已提交，审核结果将通过短信通知')
    router.push('/login?registered=1')
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || '提交失败')
  } finally { submitting.value = false }
}

async function checkStatus() {
  if (!queryPhone.value) { ElMessage.warning('请输入手机号'); return }
  try {
    const res = await request.get('/api/auth/register-status/', { params: { phone: queryPhone.value } })
    const d = res?.data || {}
    const statusMap = { pending: '审核中', approved: '已通过', rejected: '已驳回' }
    ElMessageBox.alert(
      `状态: ${statusMap[d.status] || d.status}\n${d.reason ? '驳回原因: ' + d.reason : ''}\n${d.message || ''}`,
      '审核进度'
    )
  } catch { ElMessage.error('查询失败') }
}

import { ElMessageBox } from 'element-plus'
</script>

<style scoped>
.register-page { min-height:100vh; display:flex; align-items:center; justify-content:center; background:linear-gradient(135deg,#f8fafc,#e2e8f0); padding:40px 0 }
.register-card { width:560px; background:#fff; border-radius:16px; padding:40px; box-shadow:0 4px 24px rgba(0,0,0,0.08); position:relative }
.register-card::before { content:''; position:absolute; top:0;left:0;right:0;height:4px; background:linear-gradient(90deg,#085B9C,#2ead3e); border-radius:16px 16px 0 0 }
.reg-logo { text-align:center; margin-bottom:24px }
.reg-logo h1 { font-size:22px;font-weight:700;color:#1e293b;margin:0 0 4px }
.reg-logo p { font-size:13px;color:#64748b;margin:0 }
.reg-steps { margin-bottom:28px }
.reg-form { margin-top:8px }
.id-upload :deep(.el-upload--picture-card) { width:100px;height:100px }
.step-actions { display:flex;align-items:center;justify-content:center;margin-top:28px;gap:12px }
.confirm-section { margin-bottom:8px }
.reg-footer { text-align:center;margin-top:24px;padding-top:20px;border-top:1px solid #f1f5f9;font-size:13px;color:#64748b }
</style>
