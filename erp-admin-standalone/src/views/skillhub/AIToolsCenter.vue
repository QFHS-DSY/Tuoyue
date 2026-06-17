<template>
  <div class="ai-tools-center">
    <!-- ========== 顶部标题栏 ========== -->
    <header class="tools-header">
      <div class="tools-header-left">
        <h2 class="tools-title">
          <el-icon><MagicStick /></el-icon>
          AI 创意工作室
        </h2>
        <span class="tools-subtitle">AI驱动的跨境电商视觉与内容创作平台</span>
      </div>
    </header>

    <div class="studio-notice">
      <div class="studio-notice__main">
        <strong>输入规范</strong>
        <span>{{ aiImageInputHint }}</span>
      </div>
      <span class="studio-notice__sub">文案工具预计 1 积分 / 次，图片工具预计 10-20 积分 / 张。</span>
    </div>

    <!-- ========== 工具分类标签 ========== -->
    <div class="category-tabs">
      <el-radio-group v-model="activeCategory" size="default">
        <el-radio-button value="all">全部工具</el-radio-button>
        <el-radio-button value="image">🖼️ 图片生成</el-radio-button>
        <el-radio-button value="video">🎬 视频创作</el-radio-button>
        <el-radio-button value="copy">📝 文案工坊</el-radio-button>
      </el-radio-group>
    </div>

    <!-- ========== 工具卡片网格 ========== -->
    <div class="tools-grid">
      <div
        v-for="tool in filteredTools"
        :key="tool.id"
        class="tool-card"
        :class="{
          'tool-card--active': activeTool === tool.id,
          'tool-card--disabled': tool.enabled === false
        }"
        @click="openTool(tool)"
      >
        <div class="tool-card-icon" :style="{ background: tool.gradient }">
          <span class="tool-emoji">{{ tool.emoji }}</span>
        </div>
        <div class="tool-card-body">
          <h3 class="tool-card-name">{{ tool.name }}</h3>
          <p class="tool-card-desc">{{ tool.desc }}</p>
          <div class="tool-card-tags">
            <el-tag v-for="tag in tool.tags" :key="tag" size="small" type="info" effect="plain">
              {{ tag }}
            </el-tag>
          </div>
          <div class="tool-card-meta">
            <span class="tool-card-cost">{{ tool.costLabel }}</span>
            <el-tag v-if="tool.enabled === false" size="small" type="warning" effect="dark">
              待开通
            </el-tag>
          </div>
        </div>
        <div class="tool-card-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <!-- ========== 工具操作面板（弹窗） ========== -->
    <el-dialog
      v-model="dialogVisible"
      :title="currentTool ? currentTool.name : ''"
      width="900px"
      top="5vh"
      :close-on-click-modal="false"
      destroy-on-close
      class="tool-dialog"
    >
      <template #header>
        <div class="dialog-header-custom">
          <span class="dialog-emoji">{{ currentTool?.emoji }}</span>
          <span>{{ currentTool?.name }}</span>
        </div>
      </template>

      <div v-if="currentToolMeta" class="tool-meta-banner">
        <span class="tool-meta-chip">{{ currentToolMeta.costLabel }}</span>
        <span v-if="currentTool.acceptsImage" class="tool-meta-note">{{ aiImageInputHint }}</span>
      </div>

      <!-- === 商品图生成 === -->
      <div v-if="currentTool?.id === 'product-image'" class="tool-panel">
        <ProductImageGen ref="productImageRef" @preview="showPreview" />
      </div>

      <!-- === 场景替换 === -->
      <div v-if="currentTool?.id === 'scene-replace'" class="tool-panel">
        <SceneReplace ref="sceneReplaceRef" @preview="showPreview" />
      </div>

      <!-- === 模特换装 === -->
      <div v-if="currentTool?.id === 'model-dress'" class="tool-panel">
        <ModelDress ref="modelDressRef" @preview="showPreview" />
      </div>

      <!-- === 视频生成 === -->
      <div v-if="currentTool?.id === 'video-gen'" class="tool-panel">
        <VideoGen ref="videoGenRef" />
      </div>

      <!-- === 效果图/3D === -->
      <div v-if="currentTool?.id === 'effect-render'" class="tool-panel">
        <EffectRender ref="effectRenderRef" @preview="showPreview" />
      </div>

      <!-- === 智能修图 === -->
      <div v-if="currentTool?.id === 'smart-edit'" class="tool-panel">
        <SmartEdit ref="smartEditRef" @preview="showPreview" />
      </div>

      <!-- === 标题生成 === -->
      <div v-if="currentTool?.id === 'title-gen'" class="tool-panel">
        <TitleGen ref="titleGenRef" />
      </div>

      <!-- === 描述生成 === -->
      <div v-if="currentTool?.id === 'desc-gen'" class="tool-panel">
        <DescriptionGen ref="descGenRef" />
      </div>

      <!-- === 卖点提炼 === -->
      <div v-if="currentTool?.id === 'features-gen'" class="tool-panel">
        <FeaturesGen ref="featuresGenRef" />
      </div>

      <!-- === 多语言翻译 === -->
      <div v-if="currentTool?.id === 'translate'" class="tool-panel">
        <TranslateTool ref="translateRef" />
      </div>
    </el-dialog>

    <!-- ========== 图片预览弹窗 ========== -->
    <el-dialog v-model="previewVisible" title="图片预览" width="80%" top="3vh">
      <div class="preview-container" v-if="previewImage">
        <img :src="previewImage" class="preview-img" />
        <div class="preview-actions">
          <el-button type="primary" @click="downloadPreview">
            <el-icon><Download /></el-icon> 下载图片
          </el-button>
          <el-button @click="copyPreviewUrl">
            <el-icon><CopyDocument /></el-icon> 复制链接
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import { ArrowRight, Download, CopyDocument, MagicStick } from '@element-plus/icons-vue'
import {
  AI_IMAGE_INPUT_HINT,
  AI_VIDEO_ENABLED,
  AI_VIDEO_UNAVAILABLE_MESSAGE,
  getAiToolMeta,
} from '@/utils/aiStudio'

// 子组件（工具面板）
import ProductImageGen from './panels/ProductImageGen.vue'
import SceneReplace from './panels/SceneReplace.vue'
import ModelDress from './panels/ModelDress.vue'
import VideoGen from './panels/VideoGen.vue'
import EffectRender from './panels/EffectRender.vue'
import SmartEdit from './panels/SmartEdit.vue'
import TitleGen from './panels/TitleGen.vue'
import DescriptionGen from './panels/DescriptionGen.vue'
import FeaturesGen from './panels/FeaturesGen.vue'
import TranslateTool from './panels/TranslateTool.vue'

// ==================== 工具定义 ====================
const aiImageInputHint = AI_IMAGE_INPUT_HINT

function withToolMeta(tool) {
  return {
    enabled: true,
    acceptsImage: false,
    ...tool,
    ...getAiToolMeta(tool.id),
  }
}

const tools = [
  // 图片生成类
  withToolMeta({
    id: 'product-image',
    name: 'AI 商品图生成',
    emoji: '🖼️',
    desc: '输入描述或上传参考图，AI一键生成高转化商品主图、白底图、场景图',
    category: 'image',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    acceptsImage: true,
    tags: ['文生图', '图生图', '白底图', '场景图'],
  }),
  withToolMeta({
    id: 'scene-replace',
    name: 'AI 场景替换',
    emoji: '🔄',
    desc: '上传产品图，AI自动替换背景为沙滩/厨房/办公等场景，3秒出图',
    category: 'image',
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    acceptsImage: true,
    tags: ['换背景', '场景融合', '批量处理'],
  }),
  withToolMeta({
    id: 'model-dress',
    name: 'AI 模特换装',
    emoji: '👗',
    desc: '上传服装平铺图，AI自动生成真人模特穿着效果，支持多肤色/多姿势',
    category: 'image',
    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    acceptsImage: true,
    tags: ['虚拟模特', '换装', '多肤色', '多姿势'],
  }),
  withToolMeta({
    id: 'effect-render',
    name: 'AI 效果图渲染',
    emoji: '✨',
    desc: '产品3D渲染、光影特效、水花飞溅、烟雾效果，视觉冲击力MAX',
    category: 'image',
    gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    acceptsImage: true,
    tags: ['3D渲染', '特效', '光影', '动态'],
  }),
  withToolMeta({
    id: 'smart-edit',
    name: 'AI 智能修图',
    emoji: '🔧',
    desc: '一键去背景、智能扩图、画质增强、水印去除、图片高清放大',
    category: 'image',
    gradient: 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)',
    acceptsImage: true,
    tags: ['去背景', '扩图', '增强', '去水印'],
  }),

  // 视频创作类
  withToolMeta({
    id: 'video-gen',
    name: 'AI 视频生成',
    emoji: '🎬',
    desc: '上传产品图或输入描述，AI自动生成5-30秒商品展示短视频',
    category: 'video',
    gradient: 'linear-gradient(135deg, #f6d365 0%, #fda085 100%)',
    acceptsImage: true,
    enabled: AI_VIDEO_ENABLED,
    disabledReason: AI_VIDEO_UNAVAILABLE_MESSAGE,
    tags: ['产品视频', '动效', 'TikTok', '短视频'],
  }),

  // 文案工坊类
  withToolMeta({
    id: 'title-gen',
    name: 'AI 标题生成',
    emoji: '📋',
    desc: '根据产品信息，一键生成Amazon/TikTok/Shopee等多平台高转化标题',
    category: 'copy',
    gradient: 'linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%)',
    tags: ['SEO', '多平台', '关键词优化'],
  }),
  withToolMeta({
    id: 'desc-gen',
    name: 'AI 描述生成',
    emoji: '📝',
    desc: 'AI自动撰写产品描述，支持多语言、多风格，符合各平台Listing规范',
    category: 'copy',
    gradient: 'linear-gradient(135deg, #fccb90 0%, #d57eeb 100%)',
    tags: ['多语言', 'SEO', 'Listing'],
  }),
  withToolMeta({
    id: 'features-gen',
    name: 'AI 卖点提炼',
    emoji: '💎',
    desc: 'AI分析产品特性，自动提炼3-7条核心卖点，带图标和场景化描述',
    category: 'copy',
    gradient: 'linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%)',
    tags: ['卖点', 'Bullet Points', '多语言'],
  }),
  withToolMeta({
    id: 'translate',
    name: 'AI 多语言翻译',
    emoji: '🌐',
    desc: '支持中/英/日/韩/德/法/西/意等20+语种互译，保留电商专业术语',
    category: 'copy',
    gradient: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
    tags: ['多语种', '术语保留', '批量翻译'],
  }),
]

// ==================== 状态 ====================
const activeCategory = ref('all')
const activeTool = ref(null)
const currentTool = ref(null)
const dialogVisible = ref(false)
const previewVisible = ref(false)
const previewImage = ref('')

// 子组件引用
const productImageRef = ref(null)
const sceneReplaceRef = ref(null)
const modelDressRef = ref(null)
const videoGenRef = ref(null)
const effectRenderRef = ref(null)
const smartEditRef = ref(null)
const titleGenRef = ref(null)
const descGenRef = ref(null)
const featuresGenRef = ref(null)
const translateRef = ref(null)

// ==================== 计算属性 ====================
const filteredTools = computed(() => {
  if (activeCategory.value === 'all') return tools
  return tools.filter(t => t.category === activeCategory.value)
})
const currentToolMeta = computed(() => (
  currentTool.value ? getAiToolMeta(currentTool.value.id) : null
))

// ==================== 方法 ====================
function openTool(tool) {
  if (tool.enabled === false) {
    ElNotification({
      title: '功能待开通',
      message: tool.disabledReason || AI_VIDEO_UNAVAILABLE_MESSAGE,
      type: 'info',
      duration: 3500,
    })
    return
  }
  activeTool.value = tool.id
  currentTool.value = tool
  dialogVisible.value = true
}

function downloadPreview() {
  if (!previewImage.value) return
  const a = document.createElement('a')
  a.href = previewImage.value
  a.download = `ai-generated-${Date.now()}.png`
  a.click()
  ElMessage.success('开始下载')
}

function copyPreviewUrl() {
  if (!previewImage.value) return
  navigator.clipboard.writeText(previewImage.value).then(() => {
    ElMessage.success('图片链接已复制')
  })
}

// 暴露给子组件使用的方法
function showPreview(url) {
  previewImage.value = url
  previewVisible.value = true
}

defineExpose({ showPreview })
</script>

<style scoped>
.ai-tools-center {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

/* ========== 头部 ========== */
.tools-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.studio-notice {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 10px 16px;
  padding: 14px 16px;
  margin-bottom: 24px;
  border: 1px solid #dbeafe;
  border-radius: 14px;
  background: linear-gradient(135deg, #f7fbff 0%, #eef7ff 100%);
}

.studio-notice__main {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  color: #36526c;
  font-size: 13px;
}

.studio-notice__main strong {
  color: #085b9c;
}

.studio-notice__sub {
  font-size: 12px;
  color: #6b7c93;
}

.tools-header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.tools-title {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.tools-subtitle {
  font-size: 14px;
  color: #909399;
}

/* ========== 分类标签 ========== */
.category-tabs {
  margin-bottom: 24px;
}

/* ========== 工具网格 ========== */
.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 16px;
}

.tool-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  border: 2px solid #ebeef5;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tool-card:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
}

.tool-card--disabled {
  opacity: 0.72;
  cursor: not-allowed;
}

.tool-card--disabled:hover {
  border-color: #ebeef5;
  transform: none;
  box-shadow: none;
}

.tool-card--active {
  border-color: #667eea;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
}

.tool-card-icon {
  width: 60px;
  height: 60px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.tool-emoji {
  font-size: 28px;
}

.tool-card-body {
  flex: 1;
  min-width: 0;
}

.tool-card-name {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 6px 0;
}

.tool-card-desc {
  font-size: 13px;
  color: #909399;
  margin: 0 0 8px 0;
  line-height: 1.5;
}

.tool-card-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tool-card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 10px;
}

.tool-card-cost {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 999px;
  background: #eef6ff;
  color: #085b9c;
  font-size: 12px;
  font-weight: 600;
}

.tool-card-arrow {
  color: #c0c4cc;
  font-size: 18px;
  flex-shrink: 0;
}

/* ========== 弹窗 ========== */
.dialog-header-custom {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
}

.dialog-emoji {
  font-size: 24px;
}

.tool-meta-banner {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  margin-bottom: 18px;
  padding: 12px 14px;
  border-radius: 12px;
  background: #f5f7fa;
}

.tool-meta-chip {
  display: inline-flex;
  align-items: center;
  padding: 5px 10px;
  border-radius: 999px;
  background: #e8f4fc;
  color: #085b9c;
  font-size: 12px;
  font-weight: 700;
}

.tool-meta-note {
  font-size: 12px;
  color: #606266;
}

.tool-panel {
  min-height: 400px;
}

/* ========== 预览弹窗 ========== */
.preview-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.preview-img {
  max-width: 100%;
  max-height: 70vh;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.preview-actions {
  display: flex;
  gap: 12px;
}

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .ai-tools-center {
    padding: 12px;
  }

  .tools-grid {
    grid-template-columns: 1fr;
  }

  .tools-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
