<template>
  <div class="panel-desc-gen">
    <div class="panel-section">
      <label class="panel-label">产品名称</label>
      <el-input v-model="productName" placeholder="输入产品名称" />
    </div>

    <div class="panel-row">
      <div class="panel-section flex-1">
        <label class="panel-label">品类</label>
        <el-input v-model="category" placeholder="产品品类" />
      </div>
      <div class="panel-section flex-1">
        <label class="panel-label">目标语言</label>
        <el-select v-model="targetLang" style="width: 100%">
          <el-option v-for="l in languages" :key="l.value" :label="l.label" :value="l.value" />
        </el-select>
      </div>
    </div>

    <div class="panel-section">
      <label class="panel-label">产品特性/材质/规格（可选）</label>
      <el-input
        v-model="features"
        type="textarea"
        :rows="3"
        placeholder="例如：不锈钢材质、500ml容量、双层真空保温、食品级硅胶密封圈..."
        maxlength="800"
        show-word-limit
      />
    </div>

    <div class="panel-section">
      <label class="panel-label">描述风格</label>
      <el-radio-group v-model="tone" size="small">
        <el-radio-button value="professional">专业正式</el-radio-button>
          <el-radio-button value="emotional">感性转化</el-radio-button>
          <el-radio-button value="storytelling">故事叙述</el-radio-button>
          <el-radio-button value="concise">简洁明了</el-radio-button>
      </el-radio-group>
    </div>

    <el-button type="primary" size="large" class="generate-btn" :loading="generating" :disabled="!productName.trim()" @click="handleGenerate">
      <el-icon><MagicStick /></el-icon>
      {{ generating ? 'AI 正在生成...' : '生成描述' }}
    </el-button>

    <div v-if="descEn || descCn" class="results-area">
      <div v-if="descEn" class="desc-card">
        <div class="desc-header">
          <h4>{{ targetLanguageLabel }}描述</h4>
          <el-button size="small" text type="primary" @click="copyText(descEn)"><el-icon><CopyDocument /></el-icon> 复制</el-button>
        </div>
        <p class="desc-text">{{ descEn }}</p>
      </div>
      <div v-if="descCn" class="desc-card">
        <div class="desc-header">
          <h4>中文描述</h4>
          <el-button size="small" text type="primary" @click="copyText(descCn)"><el-icon><CopyDocument /></el-icon> 复制</el-button>
        </div>
        <p class="desc-text">{{ descCn }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { MagicStick, CopyDocument } from '@element-plus/icons-vue'
import { generateDescription } from '@/api/ai'

const productName = ref('')
const category = ref('')
const targetLang = ref('en')
const features = ref('')
const tone = ref('professional')
const generating = ref(false)
const descEn = ref('')
const descCn = ref('')

const languages = [
  { label: '中文', value: 'zh' },
  { label: '英语', value: 'en' },
  { label: '日语', value: 'ja' },
  { label: '韩语', value: 'ko' },
  { label: '德语', value: 'de' },
  { label: '法语', value: 'fr' },
  { label: '西班牙语', value: 'es' },
]
const targetLanguageLabel = computed(() => {
  return languages.find(item => item.value === targetLang.value)?.label || '目标语言'
})

async function handleGenerate() {
  generating.value = true
  descEn.value = ''
  descCn.value = ''
  try {
    const res = await generateDescription({
      name: productName.value,
      category: category.value,
      features: features.value,
      targetMarket: '跨境电商通用',
      targetLang: targetLang.value,
      tone: tone.value,
    })
    descEn.value = res.description || ''
    descCn.value = res.description_cn || ''
    ElMessage.success('描述生成完成')
  } catch (e) {
    ElMessage.error('生成失败: ' + (e.message || '网络错误'))
  } finally {
    generating.value = false
  }
}

function copyText(text) {
  navigator.clipboard.writeText(text).then(() => ElMessage.success('已复制'))
}
</script>

<style scoped>
.panel-desc-gen { padding: 8px 0; }
.panel-section { margin-bottom: 16px; }
.panel-label { display: block; font-size: 14px; font-weight: 600; color: #303133; margin-bottom: 8px; }
.panel-row { display: flex; gap: 16px; }
.flex-1 { flex: 1; }
.generate-btn { width: 100%; margin-bottom: 20px; }

.results-area { margin-top: 8px; display: flex; flex-direction: column; gap: 12px; }
.desc-card { background: #f5f7fa; border-radius: 8px; padding: 16px; }
.desc-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.desc-header h4 { margin: 0; font-size: 14px; color: #303133; }
.desc-text { margin: 0; font-size: 14px; color: #606266; line-height: 1.8; white-space: pre-wrap; }
</style>
