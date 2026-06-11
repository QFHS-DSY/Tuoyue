<template>
  <el-dialog v-model="visible" :show-close="false" :close-on-click-modal="false" width="640px" class="onboard-dialog">
    <template #header>
      <div class="ob-header">
        <div class="ob-logo">🚀</div>
        <div>
          <h2>新手初始化向导</h2>
          <p>AI将带你完成基础设置，仅需3步</p>
        </div>
      </div>
    </template>

    <el-steps :active="step" align-center class="ob-steps">
      <el-step title="绑定店铺" />
      <el-step title="经营设置" />
      <el-step title="功能解锁" />
    </el-steps>

    <!-- Step 1: 绑定店铺 -->
    <div v-if="step === 0" class="ob-content">
      <p class="ob-desc">选择你要经营的平台，完成授权绑定</p>
      <div class="ob-platforms">
        <div v-for="p in platforms" :key="p.id" class="ob-platform-card" @click="startOAuth(p)">
          <div class="obp-icon" :style="{background:p.color}">{{ p.name[0] }}</div>
          <div class="obp-name">{{ p.name }}</div>
          <div class="obp-desc">{{ p.desc }}</div>
          <el-tag v-if="boundPlatforms.includes(p.id)" type="success" size="small">已绑定</el-tag>
          <el-tag v-else size="small">去绑定</el-tag>
          <div class="obp-ai-tip">{{ p.aiTip }}</div>
        </div>
      </div>
    </div>

    <!-- Step 2: 经营设置 -->
    <div v-if="step === 1" class="ob-content">
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
    <div v-if="step === 2" class="ob-content">
      <p class="ob-desc">以下核心功能已为你解锁，点击即可开始使用</p>
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
    </div>

    <template #footer>
      <div class="ob-footer">
        <el-button v-if="step > 0" @click="step--">上一步</el-button>
        <el-button v-if="step < 2" type="primary" @click="step++">下一步</el-button>
        <el-button v-else type="primary" @click="finish">进入控制台</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { MagicStick, List, Box } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['finish'])
const visible = ref(false)
const step = ref(0)
const boundPlatforms = ref([])

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
  category: '', markets: [], pricingType: 'normal', warehouse: '深圳主仓', logisticsPref: 'cheapest'
})

const aiRecommendation = ref('东南亚市场的服装和3C类目')

watch(() => settings.category, (v) => {
  if (v === '服装鞋帽') aiRecommendation.value = '东南亚市场的Oversize风格与北美市场的运动休闲风'
  else if (v === '电子产品') aiRecommendation.value = '东南亚市场的蓝牙设备与北美市场的智能家居'
  else aiRecommendation.value = '高利润、低退货率的品类优先'
})

function startOAuth(platform) {
  ElMessage.info(`正在跳转 ${platform.name} 授权页面...`)
  // 模拟OAuth绑定
  setTimeout(() => {
    boundPlatforms.value.push(platform.id)
    ElMessage.success(`${platform.name} 授权成功`)
  }, 1200)
}

function show() { visible.value = true; step.value = 0 }
function finish() {
  localStorage.setItem('onboarding_done', '1')
  visible.value = false
  emit('finish')
}

defineExpose({ show })
</script>

<style scoped>
.onboard-dialog :deep(.el-dialog__header) { padding:0 }
.ob-header { display:flex;align-items:center;gap:16px;padding:24px 24px 0 }
.ob-header h2 { margin:0;font-size:20px }
.ob-header p { margin:4px 0 0;font-size:13px;color:#909399 }
.ob-logo { font-size:40px }
.ob-steps { margin:20px 0 }
.ob-content { padding:0 24px;min-height:280px }
.ob-desc { color:#606266;margin-bottom:16px;font-size:14px }
.ob-platforms { display:grid;grid-template-columns:1fr 1fr;gap:12px }
.ob-platform-card { padding:16px;border:1px solid #e5e7eb;border-radius:12px;cursor:pointer;transition:all .2s;position:relative }
.ob-platform-card:hover { border-color:#085B9C;box-shadow:0 2px 12px rgba(8,91,156,.1) }
.obp-icon { width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:16px;margin-bottom:8px }
.obp-name { font-weight:600;font-size:15px;margin-bottom:4px }
.obp-desc { font-size:12px;color:#909399 }
.obp-ai-tip { font-size:11px;color:#E6A23C;margin-top:6px;background:#fdf6ec;padding:4px 8px;border-radius:4px }
.ob-ai-insight { display:flex;align-items:flex-start;gap:8px;padding:12px;background:#f0f9ff;border-radius:8px;margin-top:16px;font-size:13px;color:#085B9C }
.ob-features { display:flex;flex-direction:column;gap:12px }
.ob-feature { display:flex;align-items:center;gap:12px;padding:16px;background:#f5f7fa;border-radius:10px }
.ob-feature h4 { margin:0 0 4px;font-size:14px }
.ob-feature p { margin:0;font-size:12px;color:#909399 }
.obf-icon { width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0 }
.ob-footer { display:flex;justify-content:center;gap:12px }
</style>
