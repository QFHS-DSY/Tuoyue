<template>
  <div class="panel-model-dress">
    <!-- 上传服装图片 -->
    <div class="panel-section">
      <label class="panel-label">上传服装平铺图</label>
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
          <p>上传服装平铺图或假人模特图</p>
          <p class="upload-hint">{{ uploadHint }}</p>
        </div>
        <img v-else :src="uploadedImage" class="upload-preview-img" />
      </el-upload>
    </div>

    <!-- 模特配置 -->
    <div class="panel-section">
      <label class="panel-label">AI 模特配置</label>
      <div class="model-config-grid">
        <div class="config-group">
          <span class="config-group-label">肤色</span>
          <el-radio-group v-model="skinTone" size="small">
            <el-radio-button value="fair">白皙</el-radio-button>
            <el-radio-button value="medium">自然</el-radio-button>
            <el-radio-button value="tan">小麦</el-radio-button>
            <el-radio-button value="dark">深色</el-radio-button>
          </el-radio-group>
        </div>
        <div class="config-group">
          <span class="config-group-label">性别</span>
          <el-radio-group v-model="gender" size="small">
            <el-radio-button value="female">女性</el-radio-button>
            <el-radio-button value="male">男性</el-radio-button>
          </el-radio-group>
        </div>
        <div class="config-group">
          <span class="config-group-label">姿势</span>
          <el-select v-model="pose" style="width: 140px">
            <el-option v-for="p in poses" :key="p.value" :label="p.label" :value="p.value" />
          </el-select>
        </div>
        <div class="config-group">
          <span class="config-group-label">背景</span>
          <el-select v-model="background" style="width: 140px">
            <el-option v-for="b in backgrounds" :key="b.value" :label="b.label" :value="b.value" />
          </el-select>
        </div>
      </div>
    </div>

    <!-- 数量 -->
    <div class="panel-config">
      <div class="config-item">
        <label>生成数量</label>
        <el-radio-group v-model="count" size="small">
          <el-radio-button :value="1">1张</el-radio-button>
          <el-radio-button :value="2">2张</el-radio-button>
          <el-radio-button :value="4">4张</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <el-button
      type="primary"
      size="large"
      class="generate-btn"
      :loading="generating"
      :disabled="!uploadedImage"
      @click="handleGenerate"
    >
      <el-icon><MagicStick /></el-icon>
      {{ generating ? 'AI 正在生成模特图...' : '生成模特穿着效果' }}
    </el-button>

    <!-- 结果 -->
    <div v-if="results.length > 0" class="results-area">
      <div class="results-header">
        <h4>AI 模特效果</h4>
      </div>
      <div class="results-grid model-results">
        <div v-for="(img, idx) in results" :key="idx" class="result-card model-card" @click="$emit('preview', img.url || img.base64)">
          <img :src="img.url || img.base64" :alt="`模特 ${idx + 1}`" />
          <div class="result-overlay">
            <el-icon :size="24"><ZoomIn /></el-icon>
          </div>
        </div>
      </div>
    </div>

    <!-- 提示 -->
    <el-alert
      v-if="!results.length && !generating"
      title="使用提示"
      type="info"
      :closable="false"
      show-icon
      style="margin-top: 16px;"
    >
      <template #default>
        <p style="margin:0;font-size:13px;">
          上传清晰的服装正面平铺图，AI将自动识别服装款式并生成真人模特穿着效果。<br/>
          支持上衣、连衣裙、裤子、外套等品类。
        </p>
      </template>
    </el-alert>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, MagicStick, ZoomIn } from '@element-plus/icons-vue'
import { imageToImage } from '@/api/aiImage'
import { fileToBase64 } from '@/api/upload'
import { AI_IMAGE_INPUT_HINT, validateAiImageFile } from '@/utils/aiStudio'

const emit = defineEmits(['preview'])

const uploadedImage = ref('')
const imageFile = ref(null)
const skinTone = ref('fair')
const gender = ref('female')
const pose = ref('standing')
const background = ref('studio')
const count = ref(2)
const generating = ref(false)
const results = ref([])
const uploadHint = AI_IMAGE_INPUT_HINT

const poses = [
  { label: '正面站立', value: 'standing' },
  { label: '侧面展示', value: 'side' },
  { label: '行走动态', value: 'walking' },
  { label: '坐姿休闲', value: 'sitting' },
  { label: '45度侧身', value: 'three-quarter' },
]

const backgrounds = [
  { label: '摄影棚白底', value: 'studio' },
  { label: '都市街景', value: 'street' },
  { label: '自然户外', value: 'outdoor' },
  { label: '简约室内', value: 'indoor' },
  { label: '纯色背景', value: 'solid' },
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
    const base64 = await fileToBase64(imageFile.value)
    const skinMap = { fair: '白皙肤色', medium: '自然肤色', tan: '小麦肤色', dark: '深色肤色' }
    const genderMap = { female: '女性', male: '男性' }
    const poseMap = { standing: '正面站立姿势', side: '侧面展示姿势', walking: '行走动态姿势', sitting: '坐姿休闲', 'three-quarter': '45度侧身姿势' }
    const bgMap = { studio: '白色摄影棚背景', street: '都市街景背景', outdoor: '自然户外背景', indoor: '简约室内背景', solid: '纯色背景' }

    const prompt = `虚拟${genderMap[gender.value]}模特穿着这件服装，${skinMap[skinTone.value]}，${poseMap[pose.value]}，${bgMap[background.value]}，专业时尚摄影，高清分辨率，自然光线，电商服装展示标准`

    const res = await imageToImage({
      image: base64,
      prompt,
      ratio: '3:4',
      count: count.value,
    })
    results.value = res.images || []
    ElMessage.success(`成功生成 ${results.value.length} 张模特图`)
  } catch (e) {
    ElMessage.error('模特生成失败: ' + (e.message || '网络错误'))
  } finally {
    generating.value = false
  }
}
</script>

<style scoped>
.panel-model-dress { padding: 8px 0; }
.panel-section { margin-bottom: 16px; }
.panel-label { display: block; font-size: 14px; font-weight: 600; color: #303133; margin-bottom: 8px; }
.image-upload-area { width: 100%; }
.upload-empty { display: flex; flex-direction: column; align-items: center; padding: 24px; color: #c0c4cc; }
.upload-empty p { margin: 8px 0 0; }
.upload-hint { font-size: 12px; color: #c0c4cc; }
.upload-preview-img { max-width: 100%; max-height: 180px; border-radius: 8px; }

.model-config-grid { display: flex; flex-direction: column; gap: 12px; }
.config-group { display: flex; align-items: center; gap: 12px; }
.config-group-label { font-size: 13px; color: #606266; width: 48px; flex-shrink: 0; }

.panel-config { display: flex; align-items: center; gap: 24px; margin-bottom: 20px; padding: 16px; background: #f5f7fa; border-radius: 8px; }
.config-item { display: flex; align-items: center; gap: 8px; }
.config-item label { font-size: 13px; color: #606266; }
.generate-btn { width: 100%; margin-bottom: 20px; }

.results-area { margin-top: 8px; }
.results-header { margin-bottom: 12px; }
.results-header h4 { margin: 0; font-size: 15px; }
.results-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.result-card { position: relative; cursor: pointer; border-radius: 8px; overflow: hidden; background: #f5f7fa; }
.model-card { aspect-ratio: 3/4; }
.result-card img { width: 100%; height: 100%; object-fit: cover; }
.result-overlay { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.4); color: #fff; opacity: 0; transition: opacity 0.3s; }
.result-card:hover .result-overlay { opacity: 1; }
</style>
