<template>
  <div class="panel-scene-replace">
    <!-- 上传区域 -->
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
          <p>点击或拖拽上传需要换背景的产品图片</p>
          <p class="upload-hint">{{ uploadHint }}</p>
        </div>
        <img v-else :src="uploadedImage" class="upload-preview-img" />
      </el-upload>
    </div>

    <!-- 目标场景选择 -->
    <div class="panel-section">
      <label class="panel-label">选择目标场景</label>
      <div class="scene-grid">
        <div
          v-for="s in scenes"
          :key="s.id"
          class="scene-card"
          :class="{ 'scene-card--active': selectedScene === s.id }"
          @click="selectedScene = s.id; customPrompt = s.prompt"
        >
          <span class="scene-emoji">{{ s.emoji }}</span>
          <span class="scene-name">{{ s.name }}</span>
        </div>
      </div>
    </div>

    <!-- 自定义描述 -->
    <div class="panel-section">
      <label class="panel-label">场景描述（可编辑）</label>
      <el-input
        v-model="customPrompt"
        type="textarea"
        :rows="2"
        placeholder="AI将根据此描述替换产品背景..."
        maxlength="500"
        show-word-limit
      />
    </div>

    <!-- 配置 -->
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
      :disabled="!uploadedImage || !customPrompt.trim()"
      @click="handleGenerate"
    >
      <el-icon><MagicStick /></el-icon>
      {{ generating ? 'AI 正在替换场景...' : '开始场景替换' }}
    </el-button>

    <!-- 结果 -->
    <div v-if="results.length > 0" class="results-area">
      <div class="results-header">
        <h4>替换结果</h4>
        <span class="results-compare-hint">点击图片查看大图</span>
      </div>
      <div class="results-grid">
        <div v-for="(img, idx) in results" :key="idx" class="result-card" @click="$emit('preview', img.url || img.base64)">
          <img :src="img.url || img.base64" :alt="`场景 ${idx + 1}`" />
          <div class="result-overlay">
            <el-icon :size="24"><ZoomIn /></el-icon>
          </div>
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
const selectedScene = ref('')
const customPrompt = ref('')
const ratio = ref('1:1')
const count = ref(4)
const generating = ref(false)
const results = ref([])

const ratioOptions = RATIO_OPTIONS
const uploadHint = AI_IMAGE_INPUT_HINT

const scenes = [
  { id: 'beach', emoji: '🏖️', name: '阳光沙滩', prompt: '将产品背景替换为阳光明媚的沙滩海边，蓝天白云，度假氛围，专业商业摄影，高清' },
  { id: 'kitchen', emoji: '🍳', name: '现代厨房', prompt: '将产品背景替换为现代化厨房，大理石台面，温暖灯光，精致餐具搭配，美食博主风格' },
  { id: 'living', emoji: '🛋️', name: '客厅家居', prompt: '将产品背景替换为现代简约客厅，自然光从窗户洒入，温暖舒适的家居氛围，专业摄影' },
  { id: 'office', emoji: '💼', name: '商务办公', prompt: '将产品背景替换为现代化办公环境，木质桌面，简洁专业风格，自然光照明' },
  { id: 'outdoor', emoji: '🌲', name: '户外自然', prompt: '将产品背景替换为户外自然环境，绿植环绕，阳光明媚，自然清新风格' },
  { id: 'white', emoji: '⬜', name: '纯白背景', prompt: '将产品背景替换为纯白色(RGB:255,255,255)摄影棚背景，均匀灯光，Amazon主图标准，高清' },
  { id: 'dark', emoji: '🌑', name: '深色科技', prompt: '将产品背景替换为深色科技感背景，蓝紫色渐变光影，赛博朋克风格，突出产品高级感' },
  { id: 'marble', emoji: '🪨', name: '大理石纹理', prompt: '将产品背景替换为高级大理石纹理背景，奢华质感，柔和影棚灯光，高端产品摄影' },
  { id: 'garden', emoji: '🌸', name: '花园庭院', prompt: '将产品背景替换为美丽花园庭院，鲜花盛开，阳光透过树叶洒落，浪漫清新风格' },
  { id: 'studio', emoji: '📸', name: '摄影棚', prompt: '将产品背景替换为专业摄影棚，柔和均匀灯光，渐变背景纸，商业产品摄影标准' },
  { id: 'season_xmas', emoji: '🎄', name: '圣诞节日', prompt: '将产品背景替换为圣诞节日场景，圣诞树和装饰元素，温暖灯光，节日氛围' },
  { id: 'season_cny', emoji: '🧧', name: '春节喜庆', prompt: '将产品背景替换为中国春节喜庆场景，红色装饰，灯笼，喜庆氛围' },
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
    ElMessage.success(`成功生成 ${results.value.length} 张场景图`)
  } catch (e) {
    ElMessage.error('场景替换失败: ' + (e.message || '网络错误'))
  } finally {
    generating.value = false
  }
}
</script>

<style scoped>
.panel-scene-replace { padding: 8px 0; }
.panel-section { margin-bottom: 16px; }
.panel-label { display: block; font-size: 14px; font-weight: 600; color: #303133; margin-bottom: 8px; }
.image-upload-area { width: 100%; }
.upload-empty { display: flex; flex-direction: column; align-items: center; padding: 24px; color: #c0c4cc; }
.upload-empty p { margin: 8px 0 0; }
.upload-hint { font-size: 12px; color: #c0c4cc; }
.upload-preview-img { max-width: 100%; max-height: 180px; border-radius: 8px; }

.scene-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.scene-card { display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 12px 8px; border: 2px solid #ebeef5; border-radius: 10px; cursor: pointer; transition: all 0.2s; }
.scene-card:hover { border-color: #f5576c; background: #fef0f0; }
.scene-card--active { border-color: #f5576c; background: linear-gradient(135deg, #fef0f0, #fff5f5); }
.scene-emoji { font-size: 28px; }
.scene-name { font-size: 12px; color: #606266; }

.panel-config { display: flex; align-items: center; gap: 24px; flex-wrap: wrap; margin-bottom: 20px; padding: 16px; background: #f5f7fa; border-radius: 8px; }
.config-item { display: flex; align-items: center; gap: 8px; }
.config-item label { font-size: 13px; color: #606266; white-space: nowrap; }
.generate-btn { width: 100%; margin-bottom: 20px; }

.results-area { margin-top: 8px; }
.results-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.results-header h4 { margin: 0; font-size: 15px; }
.results-compare-hint { font-size: 12px; color: #909399; }
.results-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.result-card { position: relative; cursor: pointer; border-radius: 8px; overflow: hidden; aspect-ratio: 1; background: #f5f7fa; }
.result-card img { width: 100%; height: 100%; object-fit: cover; }
.result-overlay { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.4); color: #fff; opacity: 0; transition: opacity 0.3s; }
.result-card:hover .result-overlay { opacity: 1; }
</style>
