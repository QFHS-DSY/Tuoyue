<template>
  <div class="panel-product-image">
    <!-- 模式切换 -->
    <div class="panel-mode-switch">
      <el-radio-group v-model="mode" size="default">
        <el-radio-button value="text2image">文生图</el-radio-button>
        <el-radio-button value="image2image">图生图</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 文生图 -->
    <template v-if="mode === 'text2image'">
      <div class="panel-section">
        <label class="panel-label">产品场景描述</label>
        <el-input
          v-model="prompt"
          type="textarea"
          :rows="4"
          placeholder="例如：一款银色蓝牙音箱放在阳光明媚的沙滩上，旁边有一杯鸡尾酒，蓝天白云，专业商业摄影，高清分辨率，亚马逊主图风格"
          maxlength="1200"
          show-word-limit
        />
      </div>

      <div class="panel-section">
        <label class="panel-label">快捷场景</label>
        <div class="quick-scenes">
          <el-tag
            v-for="s in quickScenes"
            :key="s.label"
            :type="prompt === s.prompt ? 'primary' : 'info'"
            effect="plain"
            class="scene-tag"
            @click="prompt = s.prompt"
          >
            {{ s.emoji }} {{ s.label }}
          </el-tag>
        </div>
      </div>
    </template>

    <!-- 图生图 -->
    <template v-if="mode === 'image2image'">
      <div class="panel-section">
        <label class="panel-label">上传产品图片</label>
        <el-upload
          class="image-upload-area"
          :auto-upload="false"
          :show-file-list="false"
          :on-change="handleImageChange"
          accept="image/*"
          drag
        >
          <div v-if="!uploadedImage" class="upload-empty">
            <el-icon :size="48"><Plus /></el-icon>
            <p>点击或拖拽上传产品图片</p>
            <p class="upload-hint">{{ uploadHint }}</p>
          </div>
          <img v-else :src="uploadedImage" class="upload-preview-img" />
        </el-upload>
      </div>

      <div class="panel-section">
        <label class="panel-label">场景描述（可选）</label>
        <el-input
          v-model="prompt"
          type="textarea"
          :rows="3"
          placeholder="例如：将产品放在现代化厨房台面上，自然光从窗户照入..."
          maxlength="800"
          show-word-limit
        />
      </div>
    </template>

    <!-- 配置项 -->
    <div class="panel-config">
      <div class="config-item">
        <label>比例</label>
        <el-select v-model="ratio" style="width: 170px">
          <el-option v-for="r in ratioOptions" :key="r.value" :label="r.label" :value="r.value" />
        </el-select>
      </div>
      <div class="config-item">
        <label>风格</label>
        <el-select v-model="style" style="width: 140px">
          <el-option v-for="s in styleOptions" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
      </div>
      <div class="config-item">
        <label>数量</label>
        <el-radio-group v-model="count" size="small">
          <el-radio-button :value="2">2张</el-radio-button>
          <el-radio-button :value="4">4张</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <!-- 生成按钮 -->
    <el-button
      type="primary"
      size="large"
      class="generate-btn"
      :loading="generating"
      :disabled="mode === 'text2image' ? !prompt.trim() : !uploadedImage"
      @click="handleGenerate"
    >
      <el-icon><MagicStick /></el-icon>
      {{ generating ? 'AI 正在生成中...' : '开始生成商品图' }}
    </el-button>

    <!-- 生成结果 -->
    <div v-if="results.length > 0" class="results-area">
      <div class="results-header">
        <h4>生成结果（{{ results.length }} 张）</h4>
        <el-button size="small" type="primary" text @click="downloadAll">批量下载</el-button>
      </div>
      <div class="results-grid">
        <div v-for="(img, idx) in results" :key="idx" class="result-card">
          <div class="result-img-wrap">
            <img :src="img.url || img.base64" :alt="`结果 ${idx + 1}`" />
            <div class="result-overlay">
              <el-button circle size="small" @click.stop="$emit('preview', img.url || img.base64)">
                <el-icon><ZoomIn /></el-icon>
              </el-button>
              <el-button circle size="small" @click.stop="downloadSingle(img, idx)">
                <el-icon><Download /></el-icon>
              </el-button>
            </div>
          </div>
          <span class="result-label">#{{ idx + 1 }}</span>
        </div>
      </div>
    </div>

    <!-- 加载中骨架 -->
    <div v-if="generating" class="generating-hint">
      <el-icon class="is-loading" :size="20"><Loading /></el-icon>
      <span>AI 正在为您生成高质量商品图，请稍候...</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, MagicStick, ZoomIn, Download, Loading } from '@element-plus/icons-vue'
import { textToImage, imageToImage, RATIO_OPTIONS, STYLE_OPTIONS } from '@/api/aiImage'
import { fileToBase64 } from '@/api/upload'
import { AI_IMAGE_INPUT_HINT, validateAiImageFile } from '@/utils/aiStudio'

const emit = defineEmits(['preview'])

const mode = ref('text2image')
const prompt = ref('')
const uploadedImage = ref('')
const imageFile = ref(null)
const ratio = ref('1:1')
const style = ref('photography')
const count = ref(4)
const generating = ref(false)
const results = ref([])

const ratioOptions = RATIO_OPTIONS
const styleOptions = STYLE_OPTIONS
const uploadHint = AI_IMAGE_INPUT_HINT

const quickScenes = [
  { emoji: '☀️', label: '阳光沙滩', prompt: '产品放在阳光明媚的沙滩上，蓝天白云，专业商业摄影，高清分辨率' },
  { emoji: '🏠', label: '现代家居', prompt: '产品自然摆放在现代简约家居环境中，柔和的自然光，温暖舒适的氛围，专业摄影' },
  { emoji: '⬜', label: '纯白背景', prompt: 'Amazon标准主图风格，纯白色背景(RGB:255,255,255)，产品占画面85%以上，高清晰度，无阴影' },
  { emoji: '🌿', label: '户外自然', prompt: '产品放置在户外自然环境中，绿植环绕，阳光明媚，自然清新风格，商业摄影' },
  { emoji: '🔮', label: '科技感', prompt: '深色科技感背景，蓝紫渐变光影，赛博朋克风格，突出产品科技感和高级质感' },
  { emoji: '🌸', label: '美妆精致', prompt: '美妆产品精致特写摄影，柔和的粉色背景，微距镜头展现质地，花瓣点缀，高级感' },
  { emoji: '🏃', label: '运动活力', prompt: '产品在运动场景中，动态抓拍风格，充满活力的光线，展现产品功能性，专业运动摄影' },
  { emoji: '🎄', label: '节日氛围', prompt: '产品融入节日场景，装饰元素点缀，温暖灯光，喜庆氛围，适合节日促销，商业摄影' },
]

async function handleImageChange(file) {
  const validation = validateAiImageFile(file.raw)
  if (!validation.valid) {
    ElMessage.error(validation.message)
    return
  }
  if (validation.severity === 'warning') {
    ElMessage.warning(validation.message)
  }
  imageFile.value = file.raw
  uploadedImage.value = URL.createObjectURL(file.raw)
}

async function handleGenerate() {
  generating.value = true
  results.value = []
  try {
    let res
    if (mode.value === 'text2image') {
      res = await textToImage({ prompt: prompt.value, ratio: ratio.value, style: style.value, count: count.value })
    } else {
      const base64 = await fileToBase64(imageFile.value)
      res = await imageToImage({ image: base64, prompt: prompt.value, ratio: ratio.value, count: count.value })
    }
    results.value = res.images || []
    if (results.value.length === 0) {
      ElMessage.warning('未生成图片，请尝试调整描述词')
    } else {
      ElMessage.success(`成功生成 ${results.value.length} 张图片`)
    }
  } catch (e) {
    ElMessage.error('生成失败: ' + (e.message || '网络错误'))
  } finally {
    generating.value = false
  }
}

function downloadSingle(img, idx) {
  const url = img.url || img.base64
  const a = document.createElement('a')
  a.href = url
  a.download = `product-image-${idx + 1}.png`
  a.click()
}

function downloadAll() {
  results.value.forEach((img, idx) => {
    setTimeout(() => downloadSingle(img, idx), idx * 300)
  })
  ElMessage.success('开始批量下载')
}
</script>

<style scoped>
.panel-product-image {
  padding: 8px 0;
}

.panel-mode-switch {
  margin-bottom: 20px;
}

.panel-section {
  margin-bottom: 16px;
}

.panel-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.quick-scenes {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.scene-tag {
  cursor: pointer;
  font-size: 12px;
}

.image-upload-area {
  width: 100%;
}

.upload-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px;
  color: #c0c4cc;
}

.upload-empty p {
  margin: 8px 0 0;
}

.upload-hint {
  font-size: 12px;
  color: #c0c4cc;
}

.upload-preview-img {
  max-width: 100%;
  max-height: 200px;
  border-radius: 8px;
}

.panel-config {
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
  margin-bottom: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.config-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.config-item label {
  font-size: 13px;
  color: #606266;
  white-space: nowrap;
}

.generate-btn {
  width: 100%;
  margin-bottom: 24px;
}

.results-area {
  margin-top: 8px;
}

.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.results-header h4 {
  margin: 0;
  font-size: 15px;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.result-card {
  position: relative;
}

.result-img-wrap {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  background: #f5f7fa;
}

.result-img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.result-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: rgba(0, 0, 0, 0.5);
  opacity: 0;
  transition: opacity 0.3s;
}

.result-img-wrap:hover .result-overlay {
  opacity: 1;
}

.result-label {
  display: block;
  text-align: center;
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.generating-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 24px;
  color: #909399;
  font-size: 14px;
}
</style>
