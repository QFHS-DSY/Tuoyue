<template>
  <div class="panel-title-gen">
    <div class="panel-section">
      <label class="panel-label">产品名称</label>
      <el-input v-model="productName" placeholder="输入产品名称，如：蓝牙音箱、瑜伽裤、不锈钢保温杯" />
    </div>

    <div class="panel-row">
      <div class="panel-section flex-1">
        <label class="panel-label">品类</label>
        <el-input v-model="category" placeholder="如：电子产品、服装、家居用品" />
      </div>
      <div class="panel-section flex-1">
        <label class="panel-label">目标平台</label>
        <el-select v-model="platform" style="width: 100%">
          <el-option v-for="p in platforms" :key="p.value" :label="p.label" :value="p.value" />
        </el-select>
      </div>
    </div>

    <div class="panel-section">
      <label class="panel-label">关键词（可选，逗号分隔）</label>
      <el-input v-model="keywords" placeholder="如：wireless, portable, waterproof, high quality" />
    </div>

    <el-button type="primary" size="large" class="generate-btn" :loading="generating" :disabled="!productName.trim()" @click="handleGenerate">
      <el-icon><MagicStick /></el-icon>
      {{ generating ? 'AI 正在生成...' : '生成标题' }}
    </el-button>

    <div v-if="results.length > 0" class="results-area">
      <h4>生成结果</h4>
      <div v-for="(r, idx) in results" :key="idx" class="title-card">
        <div class="title-rank">{{ idx + 1 }}</div>
        <div class="title-content">
          <p class="title-text">{{ r }}</p>
          <div class="title-actions">
            <el-button size="small" text type="primary" @click="copyText(r)">
              <el-icon><CopyDocument /></el-icon> 复制
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { MagicStick, CopyDocument } from '@element-plus/icons-vue'
import { generateTitle } from '@/api/ai'

const productName = ref('')
const category = ref('')
const platform = ref('Amazon')
const keywords = ref('')
const generating = ref(false)
const results = ref([])

const platforms = [
  { label: 'Amazon', value: 'Amazon' },
  { label: 'TikTok Shop', value: 'TikTok Shop' },
  { label: 'Shopee', value: 'Shopee' },
  { label: 'Temu', value: 'Temu' },
  { label: '1688', value: '1688' },
]

async function handleGenerate() {
  generating.value = true
  results.value = []
  try {
    const title = await generateTitle({
      name: productName.value,
      category: category.value,
      platform: platform.value,
      features: keywords.value,
      targetMarket: '跨境电商通用',
    })
    // 后端返回单个title，拆分为多条展示
    const titles = title ? [title] : ['未生成标题']
    results.value = titles
    ElMessage.success('标题生成完成')
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
.panel-title-gen { padding: 8px 0; }
.panel-section { margin-bottom: 16px; }
.panel-label { display: block; font-size: 14px; font-weight: 600; color: #303133; margin-bottom: 8px; }
.panel-row { display: flex; gap: 16px; }
.flex-1 { flex: 1; }
.generate-btn { width: 100%; margin-bottom: 20px; }

.results-area { margin-top: 8px; }
.results-area h4 { margin: 0 0 12px; font-size: 15px; }
.title-card { display: flex; gap: 12px; padding: 14px; background: #f5f7fa; border-radius: 8px; margin-bottom: 8px; align-items: flex-start; }
.title-rank { width: 28px; height: 28px; border-radius: 50%; background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; flex-shrink: 0; }
.title-content { flex: 1; }
.title-text { margin: 0 0 8px; font-size: 14px; color: #303133; line-height: 1.6; }
.title-actions { display: flex; gap: 8px; }
</style>
