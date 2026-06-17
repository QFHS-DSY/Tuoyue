<template>
  <div class="panel-effect-render">
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
          <p>上传产品图片进行特效渲染</p>
          <p class="upload-hint">{{ uploadHint }}</p>
        </div>
        <img v-else :src="uploadedImage" class="upload-preview-img" />
      </el-upload>
    </div>

    <!-- 特效选择 -->
    <div class="panel-section">
      <label class="panel-label">选择特效风格</label>
      <div class="effect-grid">
        <div
          v-for="e in effects"
          :key="e.id"
          class="effect-card"
          :class="{ 'effect-card--active': selectedEffect === e.id }"
          @click="selectedEffect = e.id; customPrompt = e.prompt"
        >
          <span class="effect-emoji">{{ e.emoji }}</span>
          <span class="effect-name">{{ e.name }}</span>
        </div>
      </div>
    </div>

    <div class="panel-section">
      <label class="panel-label">渲染描述（可编辑）</label>
      <el-input
        v-model="customPrompt"
        type="textarea"
        :rows="2"
        maxlength="600"
        show-word-limit
      />
    </div>

    <div class="panel-config">
      <div class="config-item">
        <label>比例</label>
        <el-select v-model="ratio" style="width: 170px">
          <el-option v-for="r in ratioOptions" :key="r.value" :label="r.label" :value="r.value" />
        </el-select>
      </div>
      <div class="config-item">
        <label>数量</label>
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
      {{ generating ? 'AI 正在渲染...' : '生成效果图' }}
    </el-button>

    <div v-if="results.length > 0" class="results-area">
      <h4>渲染结果</h4>
      <div class="results-grid">
        <div v-for="(img, idx) in results" :key="idx" class="result-card" @click="$emit('preview', img.url || img.base64)">
          <img :src="img.url || img.base64" :alt="`效果 ${idx + 1}`" />
          <div class="result-overlay"><el-icon :size="24"><ZoomIn /></el-icon></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, MagicStick, ZoomIn } from '@element-plus/icons-vue'
import { imageToImage, RATIO_OPTIONS } from '@/api/aiImage'
import { fileToBase64 } from '@/api/upload'
import { AI_IMAGE_INPUT_HINT, validateAiImageFile } from '@/utils/aiStudio'

const emit = defineEmits(['preview'])

const uploadedImage = ref('')
const imageFile = ref(null)
const selectedEffect = ref('')
const customPrompt = ref('')
const ratio = ref('1:1')
const count = ref(2)
const generating = ref(false)
const results = ref([])
const ratioOptions = RATIO_OPTIONS
const uploadHint = AI_IMAGE_INPUT_HINT

const effects = [
  { id: '3d', emoji: '🎯', name: '3D渲染', prompt: '将产品转换为高质量3D渲染效果，逼真材质和光影，C4D风格，8K分辨率' },
  { id: 'water', emoji: '💧', name: '水花飞溅', prompt: '产品与水花飞溅效果结合，高速摄影风格，黑色背景，高对比度灯光，动态瞬间定格' },
  { id: 'smoke', emoji: '🌫️', name: '烟雾缭绕', prompt: '产品被柔和彩色烟雾环绕，梦幻氛围，渐变光影，高级感商业摄影' },
  { id: 'neon', emoji: '💜', name: '霓虹光影', prompt: '产品在霓虹灯光照射下，赛博朋克风格，紫蓝粉渐变光影，科技感十足' },
  { id: 'gold', emoji: '✨', name: '奢华金箔', prompt: '产品与金箔/金属质感元素结合，奢华高端风格，金色光影，奢侈品摄影质感' },
  { id: 'ice', emoji: '❄️', name: '冰晶冷冻', prompt: '产品被冰晶包围，冷冻效果，冷蓝色调，晶莹剔透的冰块和霜冻细节' },
  { id: 'fire', emoji: '🔥', name: '火焰炽热', prompt: '产品周围有火焰和火花效果，炽热氛围，橙红色调，动态火焰细节，视觉冲击力强' },
  { id: 'float', emoji: '🪐', name: '悬浮失重', prompt: '产品悬浮在空中，失重效果，柔和的宇宙背景，粒子环绕，科幻风格' },
  { id: 'sketch', emoji: '✏️', name: '手绘素描', prompt: '将产品转换为精美手绘素描/水彩风格，艺术感，白色背景，设计草图质感' },
  { id: 'pixel', emoji: '👾', name: '像素艺术', prompt: '将产品转换为复古像素艺术风格，8-bit游戏风格，趣味创意展示' },
  { id: 'glass', emoji: '🔮', name: '玻璃折射', prompt: '产品通过玻璃/水晶材质折射展示，透明质感，棱镜光影效果，高级感' },
  { id: 'nature', emoji: '🌿', name: '自然共生', prompt: '产品与苔藓、藤蔓、花朵等自然元素融合，生态美学风格，清新自然光' },
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
    const res = await imageToImage({
      image: base64,
      prompt: customPrompt.value,
      ratio: ratio.value,
      count: count.value,
    })
    results.value = res.images || []
    ElMessage.success(`成功生成 ${results.value.length} 张效果图`)
  } catch (e) {
    ElMessage.error('效果图生成失败: ' + (e.message || '网络错误'))
  } finally {
    generating.value = false
  }
}
</script>

<style scoped>
.panel-effect-render { padding: 8px 0; }
.panel-section { margin-bottom: 16px; }
.panel-label { display: block; font-size: 14px; font-weight: 600; color: #303133; margin-bottom: 8px; }
.image-upload-area { width: 100%; }
.upload-empty { display: flex; flex-direction: column; align-items: center; padding: 24px; color: #c0c4cc; }
.upload-empty p { margin: 8px 0 0; }
.upload-hint { font-size: 12px; color: #c0c4cc; }
.upload-preview-img { max-width: 100%; max-height: 180px; border-radius: 8px; }

.effect-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.effect-card { display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 12px 8px; border: 2px solid #ebeef5; border-radius: 10px; cursor: pointer; transition: all 0.2s; }
.effect-card:hover { border-color: #fa709a; background: #fff5f7; }
.effect-card--active { border-color: #fa709a; background: linear-gradient(135deg, #fff5f7, #fff0f3); }
.effect-emoji { font-size: 28px; }
.effect-name { font-size: 12px; color: #606266; }

.panel-config { display: flex; align-items: center; gap: 24px; margin-bottom: 20px; padding: 16px; background: #f5f7fa; border-radius: 8px; }
.config-item { display: flex; align-items: center; gap: 8px; }
.config-item label { font-size: 13px; color: #606266; }
.generate-btn { width: 100%; margin-bottom: 20px; }

.results-area { margin-top: 8px; }
.results-area h4 { margin: 0 0 12px; font-size: 15px; }
.results-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.result-card { position: relative; cursor: pointer; border-radius: 8px; overflow: hidden; aspect-ratio: 1; background: #f5f7fa; }
.result-card img { width: 100%; height: 100%; object-fit: cover; }
.result-overlay { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.4); color: #fff; opacity: 0; transition: opacity 0.3s; }
.result-card:hover .result-overlay { opacity: 1; }
</style>
