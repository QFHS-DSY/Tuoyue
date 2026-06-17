<template>
  <div class="panel-translate">
    <div class="panel-section">
      <label class="panel-label">输入文本</label>
      <el-input
        v-model="sourceText"
        type="textarea"
        :rows="4"
        placeholder="输入需要翻译的商品标题、描述或任何文本..."
        maxlength="2000"
        show-word-limit
      />
    </div>

    <div class="panel-row">
      <div class="panel-section flex-1">
        <label class="panel-label">源语言</label>
        <el-select v-model="sourceLang" style="width: 100%">
          <el-option v-for="l in languages" :key="l.value" :label="l.label" :value="l.value" />
        </el-select>
      </div>
      <div class="panel-section flex-1" style="display:flex;align-items:center;justify-content:center;padding-top:20px;">
        <el-icon :size="24" color="#909399"><Switch /></el-icon>
      </div>
      <div class="panel-section flex-1">
        <label class="panel-label">目标语言</label>
        <el-select v-model="targetLang" style="width: 100%">
          <el-option v-for="l in languages" :key="l.value" :label="l.label" :value="l.value" />
        </el-select>
      </div>
    </div>

    <el-button type="primary" size="large" class="generate-btn" :loading="translating" :disabled="!sourceText.trim()" @click="handleTranslate">
      <el-icon><MagicStick /></el-icon>
      {{ translating ? '翻译中...' : '开始翻译' }}
    </el-button>

    <div v-if="result" class="results-area">
      <div class="desc-card">
        <div class="desc-header">
          <h4>翻译结果</h4>
          <el-button size="small" text type="primary" @click="copyText(result)">
            <el-icon><CopyDocument /></el-icon> 复制
          </el-button>
        </div>
        <p class="desc-text">{{ result }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { MagicStick, Switch, CopyDocument } from '@element-plus/icons-vue'
import { translate } from '@/api/ai'

const sourceText = ref('')
const sourceLang = ref('zh')
const targetLang = ref('en')
const translating = ref(false)
const result = ref('')

const languages = [
  { label: '中文', value: 'zh' },
  { label: 'English', value: 'en' },
  { label: '日本語', value: 'ja' },
  { label: '한국어', value: 'ko' },
  { label: 'Deutsch', value: 'de' },
  { label: 'Français', value: 'fr' },
  { label: 'Español', value: 'es' },
  { label: 'Italiano', value: 'it' },
  { label: 'Português', value: 'pt' },
  { label: 'Русский', value: 'ru' },
  { label: 'العربية', value: 'ar' },
  { label: 'ไทย', value: 'th' },
  { label: 'Tiếng Việt', value: 'vi' },
  { label: 'Bahasa Indonesia', value: 'id' },
]

async function handleTranslate() {
  if (sourceLang.value === targetLang.value) {
    ElMessage.warning('源语言与目标语言相同，请重新选择')
    return
  }
  translating.value = true
  result.value = ''
  try {
    const res = await translate(sourceText.value, targetLang.value, sourceLang.value)
    result.value = res || ''
    ElMessage.success('翻译完成')
  } catch (e) {
    ElMessage.error('翻译失败: ' + (e.message || '网络错误'))
  } finally {
    translating.value = false
  }
}

function copyText(text) {
  navigator.clipboard.writeText(text).then(() => ElMessage.success('已复制'))
}
</script>

<style scoped>
.panel-translate { padding: 8px 0; }
.panel-section { margin-bottom: 16px; }
.panel-label { display: block; font-size: 14px; font-weight: 600; color: #303133; margin-bottom: 8px; }
.panel-row { display: flex; gap: 12px; align-items: flex-start; }
.flex-1 { flex: 1; }
.generate-btn { width: 100%; margin-bottom: 20px; }

.results-area { margin-top: 8px; }
.desc-card { background: #f5f7fa; border-radius: 8px; padding: 16px; }
.desc-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.desc-header h4 { margin: 0; font-size: 14px; color: #303133; }
.desc-text { margin: 0; font-size: 14px; color: #606266; line-height: 1.8; white-space: pre-wrap; }
</style>
