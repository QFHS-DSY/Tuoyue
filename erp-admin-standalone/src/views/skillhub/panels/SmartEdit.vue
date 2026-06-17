<template>
  <div class="panel-smart-edit">
    <!-- 上传 -->
    <div class="panel-section">
      <label class="panel-label">上传需要处理的图片</label>
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
          <p>上传图片进行智能处理</p>
          <p class="upload-hint">{{ uploadHint }}</p>
        </div>
        <img v-else :src="uploadedImage" class="upload-preview-img" />
      </el-upload>
    </div>

    <!-- 处理功能 -->
    <div class="panel-section">
      <label class="panel-label">选择处理功能</label>
      <div class="edit-func-grid">
        <div
          v-for="f in editFuncs"
          :key="f.id"
          class="edit-func-card"
          :class="{ 'edit-func-card--active': selectedFunc === f.id }"
          @click="selectedFunc = f.id"
        >
          <span class="func-emoji">{{ f.emoji }}</span>
          <span class="func-name">{{ f.name }}</span>
          <span class="func-desc">{{ f.desc }}</span>
        </div>
      </div>
    </div>

    <!-- 配置项 -->
    <div v-if="selectedFunc === 'enhance'" class="panel-config">
      <div class="config-item">
        <label>增强级别</label>
        <el-slider v-model="enhanceLevel" :min="1" :max="4" :marks="{1:'轻度',2:'标准',3:'高清',4:'极致'}" style="width: 200px" />
      </div>
    </div>

    <div v-if="selectedFunc === 'expand'" class="panel-config">
      <div class="config-item">
        <label>扩图比例</label>
        <el-select v-model="expandRatio" style="width: 150px">
          <el-option label="1.5x 小扩" :value="1.5" />
          <el-option label="2x 标准" :value="2" />
          <el-option label="3x 大扩" :value="3" />
          <el-option label="4x 超大" :value="4" />
        </el-select>
      </div>
    </div>

    <div v-if="selectedFunc === 'upscale'" class="panel-config">
      <div class="config-item">
        <label>放大倍数</label>
        <el-select v-model="upscaleFactor" style="width: 150px">
          <el-option label="2x" :value="2" />
          <el-option label="4x" :value="4" />
          <el-option label="8x" :value="8" />
        </el-select>
      </div>
    </div>

    <el-button
      type="primary"
      size="large"
      class="generate-btn"
      :loading="processing"
      :disabled="!uploadedImage || !selectedFunc"
      @click="handleProcess"
    >
      <el-icon><MagicStick /></el-icon>
      {{ processing ? 'AI 正在处理...' : getButtonText() }}
    </el-button>

    <!-- 对比结果 -->
    <div v-if="processedImage" class="compare-area">
      <h4>处理结果对比</h4>
      <div class="compare-grid">
        <div class="compare-item">
          <span class="compare-label">原图</span>
          <img :src="uploadedImage" class="compare-img" />
        </div>
        <div class="compare-item">
          <span class="compare-label">处理后</span>
          <img :src="processedImage" class="compare-img" @click="$emit('preview', processedImage)" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, MagicStick } from '@element-plus/icons-vue'
import { editImage } from '@/api/ai'
import { fileToBase64 } from '@/api/upload'
import { AI_IMAGE_INPUT_HINT, validateAiImageFile } from '@/utils/aiStudio'

const emit = defineEmits(['preview'])

const uploadedImage = ref('')
const imageFile = ref(null)
const selectedFunc = ref('')
const processing = ref(false)
const processedImage = ref('')
const enhanceLevel = ref(2)
const expandRatio = ref(2)
const upscaleFactor = ref(4)
const uploadHint = AI_IMAGE_INPUT_HINT

const editFuncs = [
  { id: 'remove-bg', emoji: '✂️', name: '一键去背景', desc: 'AI自动识别主体，去除背景输出PNG' },
  { id: 'enhance', emoji: '✨', name: '画质增强', desc: 'AI提升图片清晰度和色彩质感' },
  { id: 'expand', emoji: '🔲', name: '智能扩图', desc: 'AI自动扩展图片边缘内容' },
  { id: 'upscale', emoji: '🔍', name: '高清放大', desc: '无损放大2-8倍，保持细节清晰' },
  { id: 'watermark', emoji: '🧹', name: '去水印', desc: 'AI智能识别并去除图片水印' },
]

function getButtonText() {
  const map = {
    'remove-bg': '开始去背景',
    'enhance': '开始增强画质',
    'expand': '开始智能扩图',
    'upscale': '开始高清放大',
    'watermark': '开始去水印',
  }
  return map[selectedFunc.value] || '开始处理'
}

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
  processedImage.value = ''
}

async function handleProcess() {
  processing.value = true
  processedImage.value = ''
  try {
    const base64 = await fileToBase64(imageFile.value)

    const promptMap = {
      'remove-bg': '去除图片背景，保留主体，输出纯透明背景PNG格式',
      'enhance': `将图片画质增强到${['','轻度','标准','高清','极致'][enhanceLevel.value]}级别，提升清晰度、色彩饱和度和细节表现`,
      'expand': `将图片边缘向外扩展${expandRatio.value}倍，AI智能填充扩展区域，保持画面一致性`,
      'upscale': `将图片分辨率无损放大${upscaleFactor.value}倍，保持所有细节清晰锐利`,
      'watermark': '智能识别并去除图片中的所有水印、文字和LOGO，保持背景自然',
    }

    const res = await editImage(promptMap[selectedFunc.value], base64)
    processedImage.value = res.imageUrl || res.imageBase64 || ''
    if (processedImage.value) {
      ElMessage.success('处理完成')
    } else {
      ElMessage.warning('处理完成但未返回图片')
    }
  } catch (e) {
    ElMessage.error('处理失败: ' + (e.message || '网络错误'))
  } finally {
    processing.value = false
  }
}
</script>

<style scoped>
.panel-smart-edit { padding: 8px 0; }
.panel-section { margin-bottom: 16px; }
.panel-label { display: block; font-size: 14px; font-weight: 600; color: #303133; margin-bottom: 8px; }
.image-upload-area { width: 100%; }
.upload-empty { display: flex; flex-direction: column; align-items: center; padding: 24px; color: #c0c4cc; }
.upload-empty p { margin: 8px 0 0; }
.upload-hint { font-size: 12px; color: #c0c4cc; }
.upload-preview-img { max-width: 100%; max-height: 180px; border-radius: 8px; }

.edit-func-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.edit-func-card { display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 16px 10px; border: 2px solid #ebeef5; border-radius: 10px; cursor: pointer; transition: all 0.2s; text-align: center; }
.edit-func-card:hover { border-color: #a18cd1; background: #faf8ff; }
.edit-func-card--active { border-color: #a18cd1; background: linear-gradient(135deg, #faf8ff, #f3e8ff); }
.func-emoji { font-size: 28px; }
.func-name { font-size: 13px; font-weight: 600; color: #303133; }
.func-desc { font-size: 11px; color: #909399; }

.panel-config { display: flex; align-items: center; gap: 24px; margin-bottom: 20px; padding: 16px; background: #f5f7fa; border-radius: 8px; }
.config-item { display: flex; align-items: center; gap: 12px; }
.config-item label { font-size: 13px; color: #606266; white-space: nowrap; }
.generate-btn { width: 100%; margin-bottom: 20px; }

.compare-area { margin-top: 16px; }
.compare-area h4 { margin: 0 0 12px; font-size: 15px; }
.compare-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.compare-item { text-align: center; }
.compare-label { display: block; font-size: 13px; color: #909399; margin-bottom: 8px; font-weight: 600; }
.compare-img { width: 100%; max-height: 300px; object-fit: contain; border-radius: 8px; border: 1px solid #ebeef5; }
.compare-item:last-child .compare-img { cursor: pointer; }
</style>
