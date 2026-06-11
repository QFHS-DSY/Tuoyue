<template>
  <div class="page">
    <!-- 页面Header -->
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">商品采集</h1>
        <p class="page-desc">从 1688 等平台采集商品信息，支持批量采集和自动入库</p>
      </div>
      <div class="page-header-right">
        <!-- 集采模式开关 -->
        <div class="collect-mode-switch">
          <el-tooltip content="开启后，采集完成后自动进入选品评估与一站式上货流程" placement="bottom">
            <div class="switch-wrapper">
              <span class="switch-label">集采模式</span>
              <el-switch
                :model-value="oneStop.collectionModeEnabled"
                @change="onCollectionModeToggle"
                size="small"
                inline-prompt
                active-text="开"
                inactive-text="关"
                active-color="#22c55e"
              />
            </div>
          </el-tooltip>
          <el-button
            v-if="oneStop.collectionModeEnabled"
            type="primary"
            size="small"
            plain
            @click="openSelectionReport"
          >
            <el-icon><DataAnalysis /></el-icon>
            选品评估
            <el-badge v-if="oneStop.pendingCount > 0" :value="oneStop.pendingCount" class="item" type="warning" />
          </el-button>
        </div>
        <el-button v-if="!oneStop.collectionModeEnabled" text @click="showGuide = !showGuide">
          <el-icon><QuestionFilled /></el-icon>
          使用指南
        </el-button>
      </div>
    </div>

    <!-- ====== 集采模式配置面板 ====== -->
    <Transition name="slide-down">
      <el-card v-if="oneStop.collectionModeEnabled && showCollectConfig" class="collect-config-panel">
        <template #header>
          <div class="card-header">
            <div class="card-header-left">
              <el-icon><Setting /></el-icon>
              <span>集采模式配置</span>
            </div>
            <div class="config-header-right">
              <el-tag type="success" size="small">已开启 · 自动执行选品→上货流程</el-tag>
              <el-button size="small" text @click="showCollectConfig = false">收起</el-button>
            </div>
          </div>
        </template>

        <div class="config-sections">
          <!-- 配置1：目标平台 -->
          <div class="config-section">
            <div class="config-section-title">目标上架平台</div>
            <PlatformSelect
              v-model="oneStop.collectConfig.targetPlatforms"
              :max="4"
              placeholder="选择目标平台（小白模式默认展示核心平台）"
            />
            <div class="config-hint">已选 {{ oneStop.collectConfig.targetPlatforms.length }} 个平台</div>
          </div>

          <!-- 配置2：定价规则 -->
          <div class="config-section">
            <div class="config-section-title">定价规则</div>
            <div class="pricing-templates">
              <el-radio-group
                v-model="activePricingTemplate"
                size="small"
                @change="onPricingTemplateChange"
              >
                <el-radio-button
                  v-for="tpl in PRICING_TEMPLATES"
                  :key="tpl.id"
                  :value="tpl.id"
                >
                  {{ tpl.label }}
                </el-radio-button>
              </el-radio-group>
            </div>
            <el-form :model="oneStop.collectConfig.pricing" :inline="true" size="small" class="pricing-advanced">
              <el-form-item label="加价倍率">
                <el-input-number
                  v-model="oneStop.collectConfig.pricing.multiplier"
                  :min="1"
                  :max="10"
                  :precision="2"
                  controls-position="right"
                />
                <span class="input-suffix">倍</span>
              </el-form-item>
              <el-form-item label="平台佣金">
                <el-input-number
                  v-model="oneStop.collectConfig.pricing.platformCommission"
                  :min="0"
                  :max="30"
                  :precision="1"
                  controls-position="right"
                />
                <span class="input-suffix">%</span>
              </el-form-item>
              <el-form-item label="物流成本">
                <el-input-number
                  v-model="oneStop.collectConfig.pricing.logisticsCost"
                  :min="0"
                  :max="200"
                  :precision="2"
                  controls-position="right"
                />
                <span class="input-suffix">¥</span>
              </el-form-item>
            </el-form>
          </div>

          <!-- 配置3：筛选规则 -->
          <div class="config-section">
            <div class="config-section-title">筛选规则</div>
            <div class="filter-rules">
              <el-radio-group v-model="oneStop.collectConfig.filter.mode" size="small">
                <el-radio value="profit_amount">按利润额</el-radio>
                <el-radio value="profit_rate">按利润率</el-radio>
              </el-radio-group>
              <el-input-number
                v-if="oneStop.collectConfig.filter.mode === 'profit_amount'"
                v-model="oneStop.collectConfig.filter.minProfit"
                :min="0"
                :max="10000"
                :precision="2"
                placeholder="最低利润额"
              />
              <el-input-number
                v-else
                v-model="oneStop.collectConfig.filter.minProfitRate"
                :min="0"
                :max="100"
                :precision="1"
                placeholder="最低毛利率"
              />
              <span v-if="oneStop.collectConfig.filter.mode === 'profit_amount'">¥ 以上</span>
              <span v-else>% 以上</span>
            </div>
          </div>
        </div>
      </el-card>
    </Transition>

    <!-- 使用指南 -->
    <Transition name="slide-down">
      <el-card v-if="showGuide" class="guide-card">
        <template #header>
          <span>采集指南</span>
        </template>
        <el-steps :active="3" finish-status="success" align-center>
          <el-step title="复制链接" description="复制 1688 商品页链接" />
          <el-step title="粘贴采集" description="粘贴到上方输入框并点击采集" />
          <el-step title="预览确认" description="确认商品信息无误" />
          <el-step title="一键入库" description="商品自动进入管理列表" />
        </el-steps>
        <!-- AI 引导操作入口 -->
        <div class="guide-ai-entry guide-ai-entry--prominent">
          <el-button type="primary" size="large" @click="openGuideTour">
            <el-icon><MagicStick /></el-icon>
            AI 引导操作
          </el-button>
          <span class="guide-ai-hint">手把手带你完成采集</span>
        </div>
      </el-card>
    </Transition>

    <!-- AI 引导弹窗 -->
    <el-dialog
      v-model="guideDialogVisible"
      :title="guideSteps[guideStepIndex]?.title"
      width="520px"
      :close-on-click-modal="false"
      class="guide-tour-dialog"
    >
      <div v-if="guideSteps[guideStepIndex]" class="guide-tour-body">
        <!-- 进度条 -->
        <div class="guide-progress">
          <div
            class="guide-progress-bar"
            :style="{ width: ((guideStepIndex + 1) / guideSteps.length * 100) + '%' }"
          />
        </div>

        <!-- 步骤图示 -->
        <div class="guide-step-indicator">
          <span>第 {{ guideStepIndex + 1 }} / {{ guideSteps.length }} 步</span>
          <span class="guide-step-tag">{{ guideSteps[guideStepIndex].tag }}</span>
        </div>

        <!-- 步骤说明 -->
        <div class="guide-step-desc">{{ guideSteps[guideStepIndex].desc }}</div>

        <!-- 关键操作提示 -->
        <div v-if="guideSteps[guideStepIndex].tip" class="guide-step-tip">
          <el-icon><InfoFilled /></el-icon>
          {{ guideSteps[guideStepIndex].tip }}
        </div>

        <!-- 截图示意 -->
        <div v-if="guideSteps[guideStepIndex].screenshot" class="guide-step-screenshot">
          <el-image
            :src="guideSteps[guideStepIndex].screenshot"
            fit="contain"
            class="guide-screenshot-img"
          />
        </div>

        <!-- 操作区 -->
        <div class="guide-step-actions">
          <!-- 跳转按钮 -->
          <el-button
            v-if="guideSteps[guideStepIndex].externalUrl"
            type="primary"
            @click="handleGuideJump(guideStepIndex)"
          >
            <el-icon><TopRight /></el-icon>
            {{ guideSteps[guideStepIndex].jumpLabel }}
          </el-button>

          <!-- 特殊操作按钮 -->
          <el-button
            v-if="guideSteps[guideStepIndex].specialAction === 'copyUrl'"
            type="warning"
            @click="handleGuideCopy"
          >
            <el-icon><DocumentCopy /></el-icon>
            复制示例链接
          </el-button>

          <el-button
            v-if="guideSteps[guideStepIndex].specialAction === 'paste'"
            type="success"
            @click="handleGuidePaste"
          >
            <el-icon><DocumentChecked /></el-icon>
            已复制，去粘贴
          </el-button>
        </div>

        <!-- 底部导航 -->
        <div class="guide-nav">
          <el-button v-if="guideStepIndex > 0" @click="guideStepIndex--">
            <el-icon><ArrowLeft /></el-icon>
            上一步
          </el-button>
          <div class="guide-nav-space" />
          <el-button
            v-if="guideStepIndex < guideSteps.length - 1"
            type="primary"
            :disabled="!guideStepIndex"
            @click="handleGuideNext"
          >
            下一步
            <el-icon><ArrowRight /></el-icon>
          </el-button>
          <el-button
            v-if="guideStepIndex === guideSteps.length - 1"
            type="success"
            @click="handleGuideDone"
          >
            <el-icon><Check /></el-icon>
            完成，开始采集！
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 主内容 -->
    <div class="content-grid">
      <!-- 左侧：采集表单 -->
      <div class="left-panel">
        <el-card class="form-card">
          <template #header>
            <div class="card-header">
              <div class="card-header-left">
                <el-icon><Link /></el-icon>
                <span>采集入口</span>
              </div>
            </div>
          </template>

          <el-form :model="form" :rules="rules" ref="formRef" label-width="0">
            <el-form-item prop="url">
              <el-input
                v-model="form.url"
                placeholder="粘贴 1688 商品链接，如：https://detail.1688.com/offer/xxxxx.html"
                size="large"
                clearable
                @keyup.enter="handleCollect"
              >
                <template #prefix>
                  <el-icon><Link /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="loading"
                class="collect-btn"
                @click="handleCollect"
              >
                <el-icon v-if="!loading"><Search /></el-icon>
                {{ loading ? '采集中...' : '开始采集' }}
              </el-button>
            </el-form-item>
          </el-form>

          <div class="platform-tags">
            <span class="platform-label">支持平台：</span>
            <el-tag size="small" effect="plain">1688</el-tag>
            <el-tag size="small" effect="plain">淘宝</el-tag>
            <el-tag size="small" effect="plain" type="info">拼多多</el-tag>
            <el-tag size="small" effect="plain" type="info">天猫</el-tag>
          </div>
        </el-card>

        <!-- 批量导入 -->
        <el-card class="batch-import-card">
          <template #header>
            <div class="card-header">
              <div class="card-header-left">
                <el-icon><Upload /></el-icon>
                <span>批量导入</span>
              </div>
              <el-button text size="small" type="primary" @click="downloadTemplate">
                <el-icon><Download /></el-icon>
                下载 Excel 模版
              </el-button>
            </div>
          </template>
          <div class="batch-import-body">
            <el-upload
              ref="uploadRef"
              accept=".xlsx,.xls,.csv"
              :auto-upload="false"
              :show-file-list="false"
              :on-change="handleFileChange"
              :before-upload="beforeUpload"
              drag
            >
              <el-icon class="upload-icon"><UploadFilled /></el-icon>
              <div class="upload-text">将 Excel 文件拖拽到此处，或<em>点击选择</em></div>
              <div class="upload-hint">支持 .xlsx / .xls / .csv，表头须包含「商品链接」和「备注」</div>
            </el-upload>
            <div v-if="batchPreview.length > 0" class="batch-preview">
              <el-divider />
              <div class="batch-preview-header">
                <span>已读取 <b>{{ batchPreview.length }}</b> 条商品链接</span>
                <el-button size="small" type="primary" :loading="batchLoading" @click="handleBatchCollect">
                  批量采集
                </el-button>
              </div>
              <div class="batch-preview-list">
                <div v-for="(item, i) in batchPreview" :key="i" class="batch-preview-item">
                  <span class="batch-index">{{ i + 1 }}</span>
                  <span class="batch-url">{{ item.link }}</span>
                  <span v-if="item.remark" class="batch-remark">{{ item.remark }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 采集记录 -->
        <el-card class="history-card">
          <template #header>
            <div class="card-header">
              <span>采集记录</span>
              <el-link type="primary" :underline="'never'" size="small">查看全部</el-link>
            </div>
          </template>
          <div class="history-list">
            <div class="history-item" v-for="item in history" :key="item.id">
              <div class="history-info">
                <div class="history-title">{{ item.title }}</div>
                <div class="history-meta">{{ item.platform }} · {{ item.time }}</div>
              </div>
              <el-tag :type="item.status === 'success' ? 'success' : 'warning'" size="small">
                {{ item.status === 'success' ? '成功' : '失败' }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 右侧：采集结果 -->
      <div class="right-panel">
        <el-card v-if="result" class="result-card">
          <template #header>
            <div class="card-header">
              <div class="card-header-left">
                <el-icon><SuccessFilled /></el-icon>
                <span>采集结果</span>
              </div>
              <el-tag type="success" effect="light">采集成功</el-tag>
            </div>
          </template>

          <div class="result-content">
            <div class="result-title">{{ result.title }}</div>
            <el-row :gutter="16" class="result-meta">
              <el-col :span="8">
                <div class="meta-item">
                  <span class="meta-label">价格</span>
                  <span class="meta-value price">¥{{ result.price }}</span>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="meta-item">
                  <span class="meta-label">平台</span>
                  <span class="meta-value">{{ result.platform }}</span>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="meta-item">
                  <span class="meta-label">库存</span>
                  <span class="meta-value">{{ result.stock }}</span>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="meta-item">
                  <span class="meta-label">条码</span>
                  <span class="meta-value barcode-value">{{ result.barcode || '自动获取' }}</span>
                </div>
              </el-col>
            </el-row>

            <div class="result-section-title">商品图片</div>
            <div class="result-images">
              <el-image
                v-for="(img, i) in result.images"
                :key="i"
                :src="img"
                fit="cover"
                class="result-img"
                :preview-src-list="result.images"
                :initial-index="i"
              />
            </div>

            <!-- AI 智能提取 -->
            <div class="ai-extract-section">
              <div class="ai-extract-header">
                <div class="ai-extract-title">
                  <el-icon><MagicStick /></el-icon>
                  AI 智能提取优化
                </div>
                <el-tag size="small" type="warning" effect="plain">Beta</el-tag>
              </div>
              <div class="ai-extract-desc">
                基于采集到的商品信息，AI 自动生成更吸引买家的标题和描述
              </div>
              <div v-if="aiResult.title || aiResult.desc" class="ai-extract-result">
                <div class="ai-result-item">
                  <div class="ai-result-label">优化标题</div>
                  <el-input v-model="aiResult.title" type="textarea" :rows="2" placeholder="AI 将生成更吸引人的标题" />
                </div>
                <div class="ai-result-item">
                  <div class="ai-result-label">商品卖点</div>
                  <el-input v-model="aiResult.features" type="textarea" :rows="3" placeholder="AI 将提取核心卖点" />
                </div>
                <div class="ai-result-item">
                  <div class="ai-result-label">完整描述</div>
                  <el-input v-model="aiResult.desc" type="textarea" :rows="4" placeholder="AI 将生成完整的商品描述" />
                </div>
              </div>
              <div class="ai-extract-actions">
                <el-button
                  v-if="!aiResult.title && !aiResult.desc"
                  type="warning"
                  :loading="aiLoading"
                  @click="handleAiExtract"
                >
                  <el-icon><MagicStick /></el-icon>
                  一键提取优化
                </el-button>
                <el-button
                  v-if="aiResult.title || aiResult.desc"
                  size="small"
                  :loading="aiLoading"
                  @click="handleAiExtract"
                >
                  <el-icon><RefreshRight /></el-icon>
                  重新生成
                </el-button>
                <el-button
                  v-if="aiResult.title || aiResult.desc"
                  size="small"
                  type="success"
                  @click="handleApplyAi"
                >
                  <el-icon><Check /></el-icon>
                  应用到入库
                </el-button>
                <el-button
                  v-if="aiResult.title || aiResult.desc"
                  size="small"
                  @click="Object.assign(aiResult, { title: '', features: '', desc: '' })"
                >
                  清空
                </el-button>
              </div>
            </div>

            <div class="result-actions">
              <el-button type="primary" @click="handleImport">
                <el-icon><Download /></el-icon>
                一键入库
              </el-button>
              <el-button @click="handleContinue">
                <el-icon><RefreshRight /></el-icon>
                继续采集
              </el-button>
            </div>
          </div>
        </el-card>

        <!-- 无结果时 -->
        <el-card v-else class="empty-card">
          <div class="empty-state">
            <div class="empty-icon">
              <el-icon><Goods /></el-icon>
            </div>
            <div class="empty-text">粘贴商品链接即可开始采集</div>
            <div class="empty-hint">支持的平台：1688 · 淘宝 · 拼多多 · 天猫</div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- ====== AI 选品报告弹窗（步骤3必经拦截） ====== -->
    <AiSelectionReport
      v-model="showSelectionReport"
      :goods-list="reportGoodsList"
      :config="oneStop.collectConfig"
      @confirm="onReportConfirm"
      @to-draft="onReportToDraft"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { collect1688Single } from '@/api/collect'
import { generateTitle, generateDescription } from '@/api/ai'
import { useOneStopStore, PRICING_TEMPLATES } from '@/stores/useOneStop'
import PlatformSelect from '@/components/PlatformSelect.vue'
import AiSelectionReport from '@/components/AiSelectionReport.vue'

const oneStop = useOneStopStore()

const formRef = ref()
const loading = ref(false)
const result = ref(null)
const showGuide = ref(false)  // 集采模式下默认不显示引导
const aiLoading = ref(false)
let aiResult = reactive({ title: '', features: '', desc: '' })

// ── 集采模式开关 ──────────────────────────────────────────────
const showCollectConfig = ref(false)  // 配置面板默认折叠

function onCollectionModeToggle(val) {
  showCollectConfig.value = val
  if (val) {
    showGuide.value = false  // 开启集采模式时隐藏旧引导
  }
}

// ── 集采配置快捷模板 ──────────────────────────────────────────
const activePricingTemplate = ref('normal')
function onPricingTemplateChange(id) {
  activePricingTemplate.value = id
  oneStop.applyPricingTemplate(id)
}

// ── AI 选品报告弹窗 ──────────────────────────────────────────
const showSelectionReport = ref(false)
const reportGoodsList = ref([])

async function openSelectionReport() {
  // 批量评估所有待评估商品
  if (oneStop.pendingGoods.length === 0) {
    ElMessage.warning('暂无待评估商品')
    return
  }
  reportGoodsList.value = oneStop.pendingGoods
  showSelectionReport.value = true
}

function onReportConfirm(selected) {
  // 用户确认后，选中的商品进入筛选环节
  selected.forEach(id => {
    if (!oneStop.selectedGoods.includes(id)) {
      oneStop.selectedGoods.push(id)
    }
  })
  showSelectionReport.value = false
  ElMessage.success(`已确认 ${selected.length} 款商品，可前往「一站式上货」进行最终筛选与上架`)
}

function onReportToDraft() {
  // 暂不上货，全部存入草稿箱
  showSelectionReport.value = false
  ElMessage.info('商品已存入草稿箱，可在「商品管理」中随时编辑上架')
  oneStop.resetCollectFlow()
}

// ── 采集完成后 → 自动进入集采流程 ────────────────────────────
function triggerCollectWorkflow(goods) {
  if (!oneStop.collectionModeEnabled) return

  // 1. 添加到待评估队列
  oneStop.addPendingGoods(goods)

  // 2. 立即触发 AI 评估
  oneStop.evaluateGoods(goods).then(ev => {
    // 3. 自动弹出选品报告（单商品时直接显示）
    if (oneStop.pendingGoods.length >= 1) {
      showSelectionReport.value = true
    }
  })
}

// ===== AI 引导相关 =====
const guideDialogVisible = ref(false)
const guideStepIndex = ref(0)
let guideReturnTimer = null

// 引导步骤定义
const guideSteps = [
  {
    title: '第1步：打开1688',
    tag: '跳转外部',
    desc: '点击下方按钮，跳转到1688官网并登录你的账号。如果已经登录，直接搜索你要采集的商品关键词。',
    tip: '建议使用自己的1688账号登录，方便管理采集记录。',
    externalUrl: 'https://www.1688.com',
    jumpLabel: '打开 1688',
  },
  {
    title: '第2步：搜索商品',
    tag: '操作演示',
    desc: '在1688搜索栏输入商品关键词，找到你要采集的商品。建议筛选「一件代发」商品，方便后续上货。',
    tip: '找到商品后，点击进入商品详情页，准备复制链接。',
    externalUrl: 'https://www.1688.com/chanpin/list.htm?keywords=%E5%8D%8A%E8%A1%A3',
    jumpLabel: '搜索示例商品',
  },
  {
    title: '第3步：复制商品链接',
    tag: '关键操作',
    desc: '在1688商品详情页，点击浏览器地址栏复制完整链接，或右键「复制链接地址」。链接格式类似：detail.1688.com/offer/xxxxx.html',
    tip: '注意：一定要复制商品详情页的链接，不要复制搜索结果页的链接！',
    specialAction: 'copyUrl',
  },
  {
    title: '第4步：粘贴到本系统',
    tag: '回到系统',
    desc: '点击下方按钮跳回本系统，然后在「采集入口」输入框中粘贴刚才复制的链接，再点击「开始采集」。',
    tip: '粘贴后系统会自动识别1688商品并提取信息，稍等几秒即可。',
    specialAction: 'paste',
    internalJump: true,
  },
  {
    title: '第5步：确认并入库',
    tag: '最后一步',
    desc: '采集成功后，查看商品信息是否正确。可以用「AI 智能提取优化」生成更好的标题和描述，最后点击「一键入库」完成采集。',
    tip: '入库后商品会出现在「商品管理」中，可以随时编辑条码等信息。',
    specialAction: 'done',
  },
]

function openGuideTour() {
  guideStepIndex.value = 0
  guideDialogVisible.value = true
}

function handleGuideJump(index) {
  const step = guideSteps[index]
  if (step.internalJump) {
    // 回到系统 → 关闭弹窗，聚焦输入框
    guideDialogVisible.value = false
    setTimeout(() => {
      document.querySelector('.collect-btn')?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }, 300)
  } else if (step.externalUrl) {
    // 跳转外部网站
    window.open(step.externalUrl, '_blank')
    // 开始监听用户返回
    startReturnDetection(index)
  }
}

function handleGuideCopy() {
  // 复制一个示例链接供测试
  const demoUrl = 'https://detail.1688.com/offer/629584739214.html'
  navigator.clipboard.writeText(demoUrl).then(() => {
    ElMessage.success('示例链接已复制：' + demoUrl)
  }).catch(() => {
    ElMessage.info('请手动复制：' + demoUrl)
  })
}

function handleGuidePaste() {
  guideDialogVisible.value = false
  setTimeout(() => {
    const input = document.querySelector('.collect-btn')
    input?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }, 300)
}

function handleGuideNext() {
  guideStepIndex.value++
}

function handleGuideDone() {
  guideDialogVisible.value = false
  ElMessage.success('引导完成，开始你的采集之旅吧！')
}

// 监听用户从外部网站返回
function startReturnDetection(sourceIndex) {
  clearTimeout(guideReturnTimer)
  // 提示用户返回
  ElMessage.info('完成操作后，点击「下一步」继续引导')

  // 使用 Page Visibility API 检测用户返回
  const handleVisibilityChange = () => {
    if (document.visibilityState === 'visible') {
      clearTimeout(guideReturnTimer)
      document.removeEventListener('visibilitychange', handleVisibilityChange)
      // 自动进入下一步
      if (guideDialogVisible.value && guideStepIndex.value === sourceIndex) {
        guideStepIndex.value++
        ElMessage.success('检测到你已返回，可以继续下一步了！')
      }
    }
  }
  document.addEventListener('visibilitychange', handleVisibilityChange)

  // 兜底：5分钟后自动清理监听器
  guideReturnTimer = setTimeout(() => {
    document.removeEventListener('visibilitychange', handleVisibilityChange)
  }, 5 * 60 * 1000)
}

onUnmounted(() => {
  clearTimeout(guideReturnTimer)
})

const form = reactive({ url: '' })

const rules = {
  url: [
    { required: true, message: '请输入商品链接', trigger: 'blur' },
    { pattern: /1688\.com/, message: '请输入有效的 1688 商品链接', trigger: 'blur' },
  ],
}

// 模拟采集记录
const history = [
  { id: 1, title: '2024秋季新款韩版宽松连帽卫衣女', platform: '1688', time: '10分钟前', status: 'success' },
  { id: 2, title: '男士运动休闲裤宽松直筒长裤', platform: '1688', time: '30分钟前', status: 'success' },
  { id: 3, title: '韩版潮流双肩包女学生背包', platform: '淘宝', time: '1小时前', status: 'fail' },
]

async function handleCollect() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await collect1688Single({ url: form.url })
    result.value = res.data
    // 从URL提取1688商品ID作为条码保存
    const offerId = extractOfferId(form.url)
    if (offerId && !result.value.barcode) {
      result.value.barcode = offerId
    }
    // 采集新商品时清空 AI 结果
    aiResult.title = ''
    aiResult.features = ''
    aiResult.desc = ''
    ElMessage.success('采集成功')

    // 集采模式：采集完成后自动进入选品评估流程
    if (oneStop.collectionModeEnabled) {
      triggerCollectWorkflow(result.value)
    }
  } catch {
    // 错误已在 request.js 拦截器中统一处理
  } finally {
    loading.value = false
  }
}

function extractOfferId(url) {
  // 匹配 1688 offer ID: detail.1688.com/offer/xxxxx.html
  const match = url.match(/detail\.1688\.com\/offer\/(\d+)/)
  return match ? match[1] : null
}

function handleImport() {
  // 集采模式：入库后也添加到待评估队列
  if (oneStop.collectionModeEnabled && result.value) {
    triggerCollectWorkflow(result.value)
  } else {
    ElMessage.success('商品已入库')
  }
  result.value = null
  aiResult.title = ''
  aiResult.features = ''
  aiResult.desc = ''
}

function handleContinue() {
  result.value = null
  aiResult.title = ''
  aiResult.features = ''
  aiResult.desc = ''
}

async function handleAiExtract() {
  if (!result.value) {
    ElMessage.warning('请先采集商品')
    return
  }
  aiLoading.value = true
  try {
    const [title, desc] = await Promise.all([
      generateTitle({ name: result.value.title, category: '', material: '', style: '', features: '' }),
      generateDescription({ name: result.value.title, category: '', material: '', style: '', features: '' }),
    ])
    aiResult.title = title
    aiResult.desc = desc
    // 从描述中提取卖点（支持多种 bullet 格式：✨ • -）
    const lines = desc.split('\n').filter(l => /^[✨\-\•\s]/.test(l.trim()))
    aiResult.features = lines.slice(0, 3).map(l => l.replace(/^[✨\-\s]+/, '')).join('\n')
    ElMessage.success('AI 优化完成，可预览或直接入库')
  } catch (e) {
    ElMessage.error(e.message || 'AI 提取失败，请重试')
  } finally {
    aiLoading.value = false
  }
}

function handleApplyAi() {
  // 将 AI 结果应用到入库数据（扩展字段，由后端存储）
  if (result.value._ai === undefined) {
    result.value._ai = {}
  }
  result.value._ai.title = aiResult.title
  result.value._ai.features = aiResult.features
  result.value._ai.desc = aiResult.desc
  ElMessage.success('AI 内容已应用，点击"一键入库"保存')
}

// ── 批量导入 ──────────────────────────────────────────────
const uploadRef = ref(null)
const batchPreview = ref([])
const batchLoading = ref(false)

function downloadTemplate() {
  // 动态尝试引入 xlsx 库，未安装时降级为 HTML table 下载
  try {
    // eslint-disable-next-line
    const XLSX = require('xlsx') // won't work in ESM, use dynamic import
    import('xlsx').then(XLSX => {
      const wb = XLSX.utils.book_new()
      const data = [['商品链接', '备注']]
      data.push(['https://detail.1688.com/offer/629584739214.html', '示例：韩版卫衣'])
      data.push(['', '（在此粘贴你的商品链接）'])
      const ws = XLSX.utils.aoa_to_sheet(data)
      ws['!cols'] = [{ wch: 60 }, { wch: 30 }]
      XLSX.utils.book_append_sheet(wb, ws, '采集模板')
      XLSX.writeFile(wb, '批量采集模板.xlsx')
    }).catch(fallbackDownloadXLSX)
  } catch {
    fallbackDownloadXLSX()
  }
}

function fallbackDownloadXLSX() {
  // 降级方案：生成 HTML 表格（Excel 可直接打开）
  const html = `<html><body><table>
<tr><th>商品链接</th><th>备注</th></tr>
<tr><td>https://detail.1688.com/offer/629584739214.html</td><td>示例：韩版卫衣</td></tr>
<tr><td></td><td>（在此粘贴你的商品链接）</td></tr>
</table></body></html>`
  const blob = new Blob([html], { type: 'application/vnd.ms-excel' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = '批量采集模板.xls'
  a.click(); URL.revokeObjectURL(url)
}

async function handleFileChange(file) {
  if (!file.raw) return
  const reader = new FileReader()
  reader.onload = async (e) => {
    try {
      const XLSX = await import('xlsx')
      const wb = XLSX.read(e.target.result, { type: 'array' })
      const ws = wb.Sheets[wb.SheetNames[0]]
      const rows = XLSX.utils.sheet_to_json(ws, { header: 1 })
      if (rows.length < 2) { ElMessage.warning('Excel 文件为空'); return }
      const header = rows[0]
      const linkIndex = header.findIndex(h => String(h || '').includes('链接'))
      if (linkIndex === -1) { ElMessage.error('Excel 表头必须包含"商品链接"列'); return }
      const items = rows.slice(1).filter(r => r[linkIndex] && String(r[linkIndex]).trim())
      batchPreview.value = items.map(r => ({
        link: String(r[linkIndex]).trim(),
        remark: r[linkIndex + 1] ? String(r[linkIndex + 1]).trim() : '',
      }))
      ElMessage.success(`已读取 ${batchPreview.value.length} 条商品链接`)
    } catch (err) {
      if (err.message && err.message.includes('Cannot find module')) {
        ElMessage.warning('请先安装 xlsx 库: npm install xlsx')
      } else {
        ElMessage.error('文件解析失败: ' + (err.message || '格式不支持'))
      }
    }
  }
  reader.readAsArrayBuffer(file.raw)
}

function beforeUpload() { return false }

async function handleBatchCollect() {
  if (batchPreview.value.length === 0) return
  batchLoading.value = true
  for (let i = 0; i < batchPreview.value.length; i++) {
    form.url = batchPreview.value[i].link
    await handleCollect()
  }
  batchLoading.value = false
  batchPreview.value = []
  ElMessage.success('批量采集完成')
}
</script>

<style scoped>
.page {
  padding: 28px 32px;
  width: 100%;
  flex: 1;
  box-sizing: border-box;
  overflow-y: auto;
}


/* 使用指南 */
.guide-card { margin-bottom: 20px; }
.guide-ai-entry {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed #e5e7eb;
}
/* AI 引导入口 — 醒目版 */
.guide-ai-entry--prominent {
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  background: linear-gradient(135deg, #f0f3ff 0%, #fafbff 100%);
  border: 1px solid #dde3ff;
  border-radius: 12px;
  padding: 16px 20px;
  margin-top: 16px;
}
.guide-ai-entry--prominent .el-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border: none !important;
  font-size: 15px !important;
  font-weight: 600 !important;
  padding: 12px 28px !important;
  border-radius: 8px !important;
  box-shadow: 0 4px 14px rgba(102,126,234,0.35) !important;
}
.guide-ai-entry--prominent .el-button:hover {
  box-shadow: 0 6px 20px rgba(102,126,234,0.5) !important;
  transform: translateY(-1px);
}
.guide-ai-entry--prominent .el-button .el-icon {
  font-size: 16px !important;
  margin-right: 6px;
}
.guide-ai-hint { font-size: 12px; color: #9ca3af; }

/* 引导弹窗 */
.guide-tour-body { padding: 0 4px 8px; }
.guide-progress {
  height: 4px;
  background: #f0f0f0;
  border-radius: 2px;
  margin: -12px -20px 16px;
  overflow: hidden;
}
.guide-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 2px;
  transition: width 0.4s ease;
}
.guide-step-indicator {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.guide-step-indicator span { font-size: 13px; color: #6b7280; }
.guide-step-tag {
  background: #f3f4f6;
  color: #4b5563;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px !important;
  font-weight: 500;
}
.guide-step-desc {
  font-size: 14px;
  color: #374151;
  line-height: 1.7;
  margin-bottom: 12px;
}
.guide-step-tip {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 12px;
  color: #92400e;
  margin-bottom: 12px;
}
.guide-step-tip .el-icon { flex-shrink: 0; margin-top: 1px; }
.guide-step-screenshot {
  background: #f9fafb;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
  text-align: center;
}
.guide-screenshot-img {
  max-height: 160px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}
.guide-step-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
.guide-nav {
  display: flex;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}
.guide-nav-space { flex: 1; }

/* 布局 */
.content-grid {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 20px;
  align-items: start;
}

/* 表单卡片 */
.form-card .card-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1a1a2e;
}
.collect-btn {
  width: 100%;
  font-size: 15px;
  height: 44px;
}
.platform-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}
.platform-label { font-size: 12px; color: #a1a1aa; }

/* 记录列表 */
.history-list { display: flex; flex-direction: column; gap: 2px; }
.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.15s;
}
.history-item:last-child { border-bottom: none; }
.history-item:hover { background: #f8f9fc; }
.history-title { font-size: 13px; color: #1a1a2e; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 240px; }
.history-meta { font-size: 12px; color: #a1a1aa; margin-top: 2px; }
.history-info { flex: 1; }

/* 结果卡片 */
.result-card .card-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1a1a2e;
}
.result-title { font-size: 18px; font-weight: 600; color: #1a1a2e; margin-bottom: 16px; }
.result-meta { margin-bottom: 20px; }
.meta-item { display: flex; flex-direction: column; gap: 2px; }
.meta-label { font-size: 12px; color: #a1a1aa; }
.meta-value { font-size: 15px; color: #1a1a2e; font-weight: 500; }
.meta-value.price { color: #ef4444; font-size: 18px; font-weight: 700; }
.barcode-value { font-family: monospace; font-size: 13px; color: #667eea; }

.result-section-title { font-size: 13px; font-weight: 600; color: #1a1a2e; margin-bottom: 10px; }
.result-images { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
.result-img { width: 100px; height: 100px; border-radius: 8px; cursor: pointer; border: 1px solid #f0f0f0; }

.result-actions { display: flex; gap: 12px; padding-top: 16px; border-top: 1px solid #f0f0f0; }

/* AI 提取区块 */
.ai-extract-section {
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
  border: 1px solid #fde68a;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 16px;
}
.ai-extract-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}
.ai-extract-title {
  font-size: 14px;
  font-weight: 600;
  color: #92400e;
  display: flex;
  align-items: center;
  gap: 6px;
}
.ai-extract-desc {
  font-size: 12px;
  color: #a16207;
  margin-bottom: 12px;
}
.ai-result-item { margin-bottom: 10px; }
.ai-result-label {
  font-size: 12px;
  font-weight: 500;
  color: #92400e;
  margin-bottom: 4px;
}
.ai-extract-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 10px;
}

/* 空状态 */
.empty-card { min-height: 400px; display: flex; align-items: center; justify-content: center; }
.empty-state { text-align: center; padding: 40px; }
.empty-icon {
  width: 72px; height: 72px;
  background: #f5f7fa;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 16px;
  font-size: 32px;
  color: #d0d0d0;
}
.empty-text { font-size: 15px; color: #71767b; margin-bottom: 6px; }
.empty-hint { font-size: 13px; color: #a1a1aa; }

/* 通用卡片Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 动画 */
.slide-down-enter-active, .slide-down-leave-active { transition: all 0.3s ease; overflow: hidden; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-10px); max-height: 0; }
.slide-down-enter-to, .slide-down-leave-from { max-height: 200px; }

/* 集采模式开关 */
.collect-mode-switch {
  display: flex;
  align-items: center;
  gap: 10px;
}
.switch-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
}
.switch-label {
  font-size: 13px;
  color: var(--el-text-color-regular);
  font-weight: 500;
}
.config-header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 集采配置面板 */
.collect-config-panel {
  margin-bottom: 16px;
  border: 1px solid #d1fae5;
  background: linear-gradient(135deg, rgba(34,197,94,.03) 0%, rgba(16,185,129,.03) 100%);
}
.collect-config-panel :deep(.el-card__header) {
  background: rgba(34,197,94,.06);
  padding: 10px 16px;
}
.config-sections {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.config-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.config-section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  display: flex;
  align-items: center;
  gap: 6px;
}
.config-hint {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.pricing-templates {
  margin-bottom: 4px;
}
.pricing-advanced {
  margin-top: 4px;
}
.pricing-advanced .el-form-item {
  margin-bottom: 4px;
}
.input-suffix {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-left: 4px;
}
.filter-rules {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.filter-rules .el-input-number {
  width: 110px;
}

/* 批量导入 */
.batch-import-card { margin-top: 16px; }
.batch-import-body { padding: 4px 0; }
:deep(.el-upload-dragger) { padding: 20px; }
.upload-icon { font-size: 40px; color: var(--el-color-primary); margin-bottom: 8px; }
.upload-text { font-size: 14px; color: #606266; }
.upload-text em { color: var(--el-color-primary); font-style: normal; font-weight: 500; }
.upload-hint { font-size: 12px; color: #a1a1aa; margin-top: 6px; }
.batch-preview { margin-top: 8px; }
.batch-preview-header { display: flex; justify-content: space-between; align-items: center; font-size: 13px; }
.batch-preview-list { max-height: 180px; overflow-y: auto; margin-top: 8px; display: flex; flex-direction: column; gap: 4px; }
.batch-preview-item { display: flex; align-items: center; gap: 8px; font-size: 12px; padding: 4px 8px; background: #f8f9fc; border-radius: 6px; }
.batch-index { width: 20px; height: 20px; border-radius: 50%; background: var(--el-color-primary); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 11px; flex-shrink: 0; }
.batch-url { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #1a1a2e; }
.batch-remark { font-size: 11px; color: #a1a1aa; flex-shrink: 0; max-width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>
