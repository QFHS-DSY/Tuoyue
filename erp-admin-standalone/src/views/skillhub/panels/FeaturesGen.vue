<template>
  <div class="panel-features-gen">
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
        <label class="panel-label">卖点数量</label>
        <el-select v-model="count" style="width: 100%">
          <el-option :value="3" label="3条" />
          <el-option :value="5" label="5条" />
          <el-option :value="7" label="7条" />
        </el-select>
      </div>
    </div>

    <div class="panel-section">
      <label class="panel-label">产品特性/材质（可选）</label>
      <el-input v-model="features" type="textarea" :rows="2" placeholder="简要描述产品核心特性..." maxlength="500" show-word-limit />
    </div>

    <el-button type="primary" size="large" class="generate-btn" :loading="generating" :disabled="!productName.trim()" @click="handleGenerate">
      <el-icon><MagicStick /></el-icon>
      {{ generating ? 'AI 正在分析...' : '提炼核心卖点' }}
    </el-button>

    <div v-if="results.length > 0" class="results-area">
      <h4>核心卖点（Bullet Points）</h4>
      <div v-for="(r, idx) in results" :key="idx" class="feature-card">
        <span class="feature-icon">{{ r.icon || '✅' }}</span>
        <div class="feature-content">
          <strong class="feature-title">{{ r.title || `卖点 ${idx + 1}` }}</strong>
          <p class="feature-desc">{{ r.desc || r }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { MagicStick } from '@element-plus/icons-vue'
import { generateFeatures } from '@/api/ai'

const productName = ref('')
const category = ref('')
const count = ref(5)
const features = ref('')
const generating = ref(false)
const results = ref([])

async function handleGenerate() {
  generating.value = true
  results.value = []
  try {
    const res = await generateFeatures({
      name: productName.value,
      category: category.value,
      features: features.value,
      count: count.value,
    })
    results.value = Array.isArray(res) ? res.slice(0, count.value) : []
    ElMessage.success('卖点提炼完成')
  } catch (e) {
    ElMessage.error('生成失败: ' + (e.message || '网络错误'))
  } finally {
    generating.value = false
  }
}
</script>

<style scoped>
.panel-features-gen { padding: 8px 0; }
.panel-section { margin-bottom: 16px; }
.panel-label { display: block; font-size: 14px; font-weight: 600; color: #303133; margin-bottom: 8px; }
.panel-row { display: flex; gap: 16px; }
.flex-1 { flex: 1; }
.generate-btn { width: 100%; margin-bottom: 20px; }

.results-area { margin-top: 8px; }
.results-area h4 { margin: 0 0 12px; font-size: 15px; }
.feature-card { display: flex; gap: 12px; padding: 14px; background: #f5f7fa; border-radius: 8px; margin-bottom: 8px; align-items: flex-start; }
.feature-icon { font-size: 20px; flex-shrink: 0; }
.feature-content { flex: 1; }
.feature-title { display: block; font-size: 14px; color: #303133; margin-bottom: 4px; }
.feature-desc { margin: 0; font-size: 13px; color: #606266; line-height: 1.6; }
</style>
