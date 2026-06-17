<template>
  <el-dialog
    v-model="visible"
    :show-close="false"
    :close-on-click-modal="false"
    width="680px"
    class="onboard-dialog"
    top="5vh"
  >
    <template #header>
      <div class="ob-header">
        <div class="ob-logo">
          <span v-if="isDemoMode">🛡️</span>
          <span v-else>🚀</span>
        </div>
        <div>
          <h2>
            {{ isDemoMode ? '演示模式 · 新手引导' : '新手初始化向导' }}
          </h2>
          <p v-if="isDemoMode" class="ob-demo-hint">
            ⚠️ 当前为演示模式，部分数据为沙箱模拟数据，实际入驻请退出演示模式
          </p>
          <p v-else>AI将带你完成基础设置，仅需4步</p>
        </div>
      </div>
    </template>

    <el-steps :active="step" align-center class="ob-steps">
      <el-step title="绑定店铺" />
      <el-step title="企业资质" />
      <el-step title="经营设置" />
      <el-step title="功能解锁" />
    </el-steps>

    <!-- Step 0: 绑定店铺 -->
    <Transition name="step-fade" mode="out-in">
      <div v-if="step === 0" key="step0" class="ob-content">
        <p class="ob-desc">选择你要经营的平台，完成授权绑定</p>
        <div class="ob-platforms">
          <div v-for="p in platforms" :key="p.id" class="ob-platform-card" @click="startOAuth(p)">
            <div class="obp-icon" :style="{ background: p.color }">{{ p.name[0] }}</div>
            <div class="obp-name">{{ p.name }}</div>
            <div class="obp-desc">{{ p.desc }}</div>
            <el-tag v-if="boundPlatforms.includes(p.id)" type="success" size="small">已绑定</el-tag>
            <el-tag v-else size="small">去绑定</el-tag>
            <div class="obp-ai-tip">{{ p.aiTip }}</div>
          </div>
        </div>
      </div>

      <!-- Step 1: 企业资质上传（新增） -->
      <div v-else-if="step === 1" key="step1" class="ob-content">
        <p class="ob-desc">上传企业资质信息，确保合规入驻</p>

        <el-form ref="qualFormRef" :model="qualification" :rules="qualRules" label-position="top" class="qual-form">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="企业名称" prop="company_name">
                <el-input v-model="qualification.company_name" placeholder="请输入企业全称" :disabled="isDemoMode" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="统一社会信用代码" prop="credit_code">
                <el-input v-model="qualification.credit_code" placeholder="18位信用代码" :disabled="isDemoMode" maxlength="18" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="法人姓名" prop="legal_person_name">
                <el-input v-model="qualification.legal_person_name" placeholder="法人姓名" :disabled="isDemoMode" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="法人身份证号" prop="legal_person_id">
                <el-input v-model="qualification.legal_person_id" placeholder="18位身份证号" :disabled="isDemoMode" maxlength="18" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="联系电话" prop="contact_phone">
                <el-input v-model="qualification.contact_phone" placeholder="手机号码" :disabled="isDemoMode" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="联系邮箱" prop="contact_email">
                <el-input v-model="qualification.contact_email" placeholder="邮箱地址" :disabled="isDemoMode" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="营业执照" prop="business_license">
            <el-upload
              class="license-upload"
              drag
              :auto-upload="false"
              :limit="1"
              accept="image/*"
              :disabled="isDemoMode"
              :on-change="handleLicenseChange"
              :on-remove="handleLicenseRemove"
              :file-list="licenseFileList"
            >
              <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
              <div class="el-upload__text">
                拖拽营业执照到此，或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 JPG/PNG 格式，大小不超过 5MB，需清晰可辨
                </div>
              </template>
            </el-upload>
          </el-form-item>
        </el-form>

        <div v-if="isDemoMode" class="ob-demo-notice">
          <el-alert
            title="演示模式提示"
            description="当前为沙箱演示环境，企业信息已自动填充模拟数据，无需真实上传营业执照。"
            type="info"
            :closable="false"
            show-icon
          />
        </div>
      </div>

      <!-- Step 2: 经营设置 -->
      <div v-else-if="step === 2" key="step2" class="ob-content">
        <el-form label-position="top">
          <el-form-item label="主营类目">
            <el-select v-model="settings.category" placeholder="选择主营类目" style="width:100%">
              <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
            </el-select>
          </el-form-item>
          <el-form-item label="目标市场">
            <el-checkbox-group v-model="settings.markets">
              <el-checkbox v-for="m in markets" :key="m" :label="m" :value="m">{{ m }}</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          <el-form-item label="默认定价模板">
            <el-radio-group v-model="settings.pricingType">
              <el-radio-button v-for="t in pricingTemplates" :key="t.id" :value="t.id">
                {{ t.label }} (×{{ t.rate }})
              </el-radio-button>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="默认发货仓库">
            <el-select v-model="settings.warehouse" placeholder="选择仓库" style="width:100%">
              <el-option v-for="w in warehouses" :key="w" :label="w" :value="w" />
            </el-select>
          </el-form-item>
          <el-form-item label="物流偏好">
            <el-radio-group v-model="settings.logisticsPref">
              <el-radio-button value="cheapest">最便宜</el-radio-button>
              <el-radio-button value="fastest">最快</el-radio-button>
              <el-radio-button value="safest">最稳妥</el-radio-button>
            </el-radio-group>
          </el-form-item>
        </el-form>
        <div class="ob-ai-insight">
          <el-icon><MagicStick /></el-icon>
          <span>AI提示：根据你选择的类目「{{ settings.category || '未选择' }}」，推荐关注{{ aiRecommendation }}</span>
        </div>
      </div>

      <!-- Step 3: 功能解锁 -->
      <div v-else-if="step === 3" key="step3" class="ob-content">
        <p class="ob-desc">
          {{ isDemoMode ? '以下功能已在沙箱环境中解锁，可用于体验' : '以下核心功能已为你解锁，点击即可开始使用' }}
        </p>
        <div class="ob-features">
          <div class="ob-feature">
            <div class="obf-icon" style="background:rgba(8,91,156,.1);color:#085B9C">
              <el-icon><MagicStick /></el-icon>
            </div>
            <div>
              <h4>一站式采集上货</h4>
              <p>粘贴链接 → AI自动处理 → 一键上架</p>
            </div>
            <el-tag type="success" size="small">已解锁</el-tag>
          </div>
          <div class="ob-feature">
            <div class="obf-icon" style="background:rgba(46,173,62,.1);color:#2ead3e">
              <el-icon><List /></el-icon>
            </div>
            <div>
              <h4>订单管理</h4>
              <p>多平台订单聚合、智能发货</p>
            </div>
            <el-tag type="success" size="small">已解锁</el-tag>
          </div>
          <div class="ob-feature">
            <div class="obf-icon" style="background:rgba(230,162,60,.1);color:#E6A23C">
              <el-icon><Box /></el-icon>
            </div>
            <div>
              <h4>库存物流管理</h4>
              <p>多仓库存同步、预警补货</p>
            </div>
            <el-tag type="success" size="small">已解锁</el-tag>
          </div>
        </div>
        <div v-if="isDemoMode" class="ob-demo-finish-notice">
          <el-alert
            title="沙箱模式完成"
            description="演示引导流程已走完。正式使用时请退出演示模式，重新走一遍入驻流程并提交真实企业资料。"
            type="warning"
            :closable="false"
            show-icon
          />
        </div>
      </div>
    </Transition>

    <template #footer>
      <div class="ob-footer">
        <el-button v-if="step > 0" @click="prevStep">上一步</el-button>
        <el-button v-if="step < 3" type="primary" @click="nextStep">下一步</el-button>
        <el-button v-else type="primary" @click="finish">
          {{ isDemoMode ? '进入演示控制台' : '进入控制台' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { MagicStick, List, Box, UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['finish'])

const visible = ref(false)
const step = ref(0)
const boundPlatforms = ref([])
const isDemoMode = ref(false)

// ── DEMO_MODE 检测 ──
function checkDemoMode() {
  const demoFlag = localStorage.getItem('demo_mode')
  isDemoMode.value = demoFlag === '1' || demoFlag === 'true'
  if (isDemoMode.value) {
    // 预填模拟企业资质
    qualification.company_name = '辽宁跨境宝盒电子商务有限公司'
    qualification.credit_code = '91210100MA0XXXXXXX'
    qualification.legal_person_name = '张三'
    qualification.legal_person_id = '210101199001011234'
    qualification.contact_phone = '13800000000'
    qualification.contact_email = 'admin@example.com'
  }
}

// ── 企业资质 ──
const qualFormRef = ref(null)
const qualification = reactive({
  company_name: '',
  credit_code: '',
  legal_person_name: '',
  legal_person_id: '',
  contact_phone: '',
  contact_email: '',
  business_license: '',
})

const licenseFileList = ref([])

const qualRules = {
  company_name: [
    { required: true, message: '请输入企业名称', trigger: 'blur' },
    { min: 2, max: 100, message: '企业名称长度为2-100个字符', trigger: 'blur' },
  ],
  credit_code: [
    { required: true, message: '请输入统一社会信用代码', trigger: 'blur' },
    { pattern: /^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$/, message: '信用代码格式不正确（18位）', trigger: 'blur' },
  ],
  legal_person_name: [
    { required: true, message: '请输入法人姓名', trigger: 'blur' },
  ],
  legal_person_id: [
    { required: true, message: '请输入法人身份证号', trigger: 'blur' },
    { pattern: /^\d{17}[\dXx]$/, message: '身份证号格式不正确（18位）', trigger: 'blur' },
  ],
  contact_phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号码格式不正确', trigger: 'blur' },
  ],
  contact_email: [
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
}

function handleLicenseChange(file) {
  // 简单校验文件大小
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    ElMessage.error('营业执照图片大小不能超过 5MB')
    return
  }
  licenseFileList.value = [file]
  // 读取为 Base64（实际项目中应上传到OSS后获取URL）
  const reader = new FileReader()
  reader.onload = (e) => {
    qualification.business_license = e.target.result
  }
  reader.readAsDataURL(file.raw || file)
}

function handleLicenseRemove() {
  licenseFileList.value = []
  qualification.business_license = ''
}

// ── 经营设置 ──
const categories = ['电子产品', '服装鞋帽', '家居用品', '美妆个护', '运动户外', '箱包皮具', '母婴玩具', '汽车用品', '食品饮料', '其他']
const markets = ['东南亚', '北美', '欧洲', '中东', '拉美', '日韩', '非洲', '澳洲']
const warehouses = ['深圳主仓', '广州分仓', '义乌仓', '英国海外仓']
const pricingTemplates = [
  { id: 'normal', label: '普通定价', rate: '1.5' },
  { id: 'promotion', label: '活动价', rate: '1.3' },
  { id: 'premium', label: '高端定价', rate: '2.0' },
]

const platforms = [
  { id: 'shein', name: 'SHEIN', desc: '半托模式', color: '#e5004c', aiTip: '入驻门槛低，适合新手' },
  { id: 'temu', name: 'Temu', desc: '全托/半托', color: '#ff6b00', aiTip: '全托管省心，适合工厂型卖家' },
  { id: 'tiktok', name: 'TikTok Shop', desc: '内容电商', color: '#00f2ea', aiTip: '需配合短视频运营' },
  { id: 'shopee', name: 'Shopee', desc: '东南亚主流', color: '#ee4d2d', aiTip: 'Lazada的强有力竞品' },
]

const settings = reactive({
  category: '',
  markets: [],
  pricingType: 'normal',
  warehouse: '深圳主仓',
  logisticsPref: 'cheapest',
})

const aiRecommendation = ref('东南亚市场的服装和3C类目')

watch(() => settings.category, (v) => {
  if (v === '服装鞋帽') aiRecommendation.value = '东南亚市场的Oversize风格与北美市场的运动休闲风'
  else if (v === '电子产品') aiRecommendation.value = '东南亚市场的蓝牙设备与北美市场的智能家居'
  else aiRecommendation.value = '高利润、低退货率的品类优先'
})

// ── OAuth 绑定（集成 DEMO_MODE 降级）──
function startOAuth(platform) {
  if (isDemoMode.value) {
    ElMessage.info(`[沙箱模式] 模拟 ${platform.name} 授权流程...`)
    setTimeout(() => {
      boundPlatforms.value.push(platform.id)
      ElMessage.success(`[沙箱] ${platform.name} 模拟授权成功`)
    }, 800)
    return
  }

  ElMessage.info(`正在跳转 ${platform.name} 授权页面...`)
  // TODO: 真实 OAuth 跳转
  setTimeout(() => {
    boundPlatforms.value.push(platform.id)
    ElMessage.success(`${platform.name} 授权成功`)
  }, 1200)
}

// ── 步骤切换（含校验）──
async function nextStep() {
  if (step.value === 1 && !isDemoMode.value) {
    // 企业资质步骤需要校验
    if (!qualFormRef.value) return
    try {
      await qualFormRef.value.validate()
    } catch {
      ElMessage.warning('请完善企业资质信息')
      return
    }
  }
  if (step.value < 3) {
    step.value++
  }
}

function prevStep() {
  if (step.value > 0) {
    step.value--
  }
}

// ── 完成入驻 ──
function finish() {
  if (isDemoMode.value) {
    localStorage.setItem('onboarding_demo_done', '1')
  } else {
    // 保存企业资质（实际项目中调用 API）
    const qualData = { ...qualification }
    console.log('[Onboarding] 企业资质数据:', qualData)
    localStorage.setItem('onboarding_qualification', JSON.stringify(qualData))
  }
  localStorage.setItem('onboarding_done', '1')
  visible.value = false
  emit('finish')
}

// ── 公开方法 ──
function show() {
  visible.value = true
  step.value = 0
  checkDemoMode()
}

defineExpose({ show })
</script>

<style scoped>
.onboard-dialog :deep(.el-dialog__header) { padding: 0; }
.onboard-dialog :deep(.el-dialog__body) { padding: 0 0 20px; }

.ob-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px 24px 0;
}

.ob-header h2 {
  margin: 0;
  font-size: 20px;
}

.ob-header p {
  margin: 4px 0 0;
  font-size: 13px;
  color: #909399;
}

.ob-demo-hint {
  color: #e6a23c !important;
  font-weight: 500;
}

.ob-logo {
  font-size: 40px;
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f9ff;
  border-radius: 14px;
}

.ob-steps {
  margin: 20px 0;
  padding: 0 24px;
}

.ob-content {
  padding: 0 24px;
  min-height: 320px;
}

.ob-desc {
  color: #606266;
  margin-bottom: 16px;
  font-size: 14px;
}

/* ── 步骤过渡动画 ── */
.step-fade-enter-active,
.step-fade-leave-active {
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.step-fade-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.step-fade-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* ── 平台卡片 ── */
.ob-platforms {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.ob-platform-card {
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: all .2s;
  position: relative;
}

.ob-platform-card:hover {
  border-color: #085B9C;
  box-shadow: 0 2px 12px rgba(8,91,156,.1);
  transform: translateY(-2px);
}

.obp-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 16px;
  margin-bottom: 8px;
}

.obp-name {
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 4px;
}

.obp-desc {
  font-size: 12px;
  color: #909399;
}

.obp-ai-tip {
  font-size: 11px;
  color: #E6A23C;
  margin-top: 6px;
  background: #fdf6ec;
  padding: 4px 8px;
  border-radius: 4px;
}

/* ── 企业资质表单 ── */
.qual-form {
  margin-top: 8px;
}

.license-upload :deep(.el-upload-dragger) {
  padding: 20px;
}

.license-upload :deep(.el-upload__tip) {
  margin-top: 8px;
}

.ob-demo-notice {
  margin-top: 16px;
}

/* ── 经营设置 ── */
.ob-ai-insight {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  background: #f0f9ff;
  border-radius: 8px;
  margin-top: 16px;
  font-size: 13px;
  color: #085B9C;
}

/* ── 功能解锁 ── */
.ob-features {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ob-feature {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 10px;
  transition: transform .2s;
}

.ob-feature:hover {
  transform: scale(1.01);
}

.ob-feature h4 {
  margin: 0 0 4px;
  font-size: 14px;
}

.ob-feature p {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

.obf-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.ob-demo-finish-notice {
  margin-top: 16px;
}

/* ── 底部 ── */
.ob-footer {
  display: flex;
  justify-content: center;
  gap: 12px;
}
</style>
