<template>
  <div class="ai-image-gen">
    <!-- ========== 顶部操作栏 ========== -->
    <header class="gen-header">
      <div class="gen-header-left">
        <h2 class="gen-title">
          <el-icon><PictureFilled /></el-icon>
          AI 智能生图
        </h2>
        <span class="gen-subtitle">一分钟打造跨境电商专业视觉素材</span>
      </div>
      <div class="gen-header-right">
        <el-button-group class="mode-switch-group">
          <el-button
            :type="genMode === 'text2image' ? 'primary' : 'default'"
            @click="genMode = 'text2image'"
            size="default"
          >
            <el-icon><EditPen /></el-icon> 文生图
          </el-button>
          <el-button
            :type="genMode === 'image2image' ? 'primary' : 'default'"
            @click="genMode = 'image2image'"
            size="default"
          >
            <el-icon><Upload /></el-icon> 图生图
          </el-button>
        </el-button-group>
        <el-button @click="showHistory = !showHistory" :type="showHistory ? 'primary' : 'default'" plain>
          <el-icon><Clock /></el-icon>
          历史记录
        </el-button>
      </div>
    </header>

    <div class="gen-body" :class="{ 'history-open': showHistory }">
      <!-- ========== 左侧：生成面板 ========== -->
      <section class="gen-panel">
        <!-- 文生图 -->
        <div v-if="genMode === 'text2image'" class="panel-content">
          <!-- 提示词输入 -->
          <div class="prompt-section">
            <label class="section-label">产品描述 / 场景提示词</label>
            <el-input
              v-model="textPrompt"
              type="textarea"
              :rows="4"
              placeholder="例如：一个银色的蓝牙音箱放在阳光明媚的沙滩上，旁边有一杯鸡尾酒，蓝天白云，专业商业摄影，高清分辨率"
              maxlength="1000"
              show-word-limit
              class="prompt-input"
            />
            <!-- 预设模板 -->
            <div class="template-bar">
              <span class="template-label">快捷模板：</span>
              <div class="template-chips">
                <el-tag
                  v-for="tpl in templates"
                  :key="tpl.id"
                  :type="activeTemplateId === tpl.id ? 'primary' : 'info'"
                  effect="plain"
                  class="template-chip"
                  @click="applyTemplate(tpl)"
                >
                  <el-icon v-if="tpl.icon" class="tpl-icon"><component :is="tpl.icon" /></el-icon>
                  {{ tpl.name }}
                </el-tag>
              </div>
            </div>
          </div>

          <!-- 图片配置 -->
          <div class="config-row">
            <div class="config-item">
              <label>图片比例</label>
              <el-select v-model="imageRatio" size="default" style="width: 180px">
                <el-option
                  v-for="r in ratioOptions"
                  :key="r.value"
                  :label="r.label"
                  :value="r.value"
                />
              </el-select>
            </div>
            <div class="config-item">
              <label>风格</label>
              <el-select v-model="imageStyle" size="default" style="width: 140px">
                <el-option
                  v-for="s in styleOptions"
                  :key="s.value"
                  :label="s.label"
                  :value="s.value"
                />
              </el-select>
            </div>
            <div class="config-item">
              <label>生成数量</label>
              <el-radio-group v-model="genCount" size="default">
                <el-radio-button :value="2">2张</el-radio-button>
                <el-radio-button :value="4">4张</el-radio-button>
                <el-radio-button :value="8">8张</el-radio-button>
              </el-radio-group>
            </div>
            <div class="config-item">
              <el-checkbox v-model="transparentBg" size="default">透明背景(PNG)</el-checkbox>
            </div>
          </div>

          <el-button
            type="primary"
            size="large"
            class="gen-btn"
            :loading="isGenerating"
            :disabled="!textPrompt.trim()"
            @click="handleTextToImage"
          >
            <el-icon v-if="!isGenerating"><MagicStick /></el-icon>
            {{ isGenerating ? 'AI 正在生成中...' : '开始生成图片' }}
          </el-button>
        </div>

        <!-- 图生图 -->
        <div v-if="genMode === 'image2image'" class="panel-content">
          <div class="upload-section">
            <label class="section-label">上传原始图片</label>
            <el-upload
              class="image-uploader"
              :auto-upload="false"
              :show-file-list="false"
              :on-change="handleImageChange"
              accept="image/*"
              drag
            >
              <div v-if="!uploadedImage" class="upload-placeholder">
                <el-icon class="upload-icon"><Plus /></el-icon>
                <p>点击或拖拽上传产品图片</p>
                <p class="upload-hint">{{ uploadHint }}</p>
              </div>
              <img v-else :src="uploadedImage" class="upload-preview" />
            </el-upload>
            <el-button v-if="uploadedImage" text type="danger" size="small" @click="uploadedImage = ''">
              移除图片
            </el-button>
          </div>

          <div class="prompt-section">
            <label class="section-label">修改指令 / 场景描述</label>
            <el-input
              v-model="textPrompt"
              type="textarea"
              :rows="3"
              placeholder="例如：为产品添加阳光沙滩背景、将背景替换为现代化厨房、增加光影质感、转换为3D渲染风格"
              maxlength="800"
              show-word-limit
              class="prompt-input"
            />
            <div class="template-bar">
              <span class="template-label">快捷指令：</span>
              <div class="template-chips">
                <el-tag
                  v-for="tpl in editTemplates"
                  :key="tpl.id"
                  :type="activeEditTplId === tpl.id ? 'primary' : 'info'"
                  effect="plain"
                  class="template-chip"
                  @click="applyEditTemplate(tpl)"
                >
                  {{ tpl.name }}
                </el-tag>
              </div>
            </div>
          </div>

          <div class="config-row">
            <div class="config-item">
              <label>输出比例</label>
              <el-select v-model="imageRatio" size="default" style="width: 180px">
                <el-option v-for="r in ratioOptions" :key="r.value" :label="r.label" :value="r.value" />
              </el-select>
            </div>
            <div class="config-item">
              <label>生成数量</label>
              <el-radio-group v-model="genCount" size="default">
                <el-radio-button :value="2">2张</el-radio-button>
                <el-radio-button :value="4">4张</el-radio-button>
              </el-radio-group>
            </div>
          </div>

          <el-button
            type="primary"
            size="large"
            class="gen-btn"
            :loading="isGenerating"
            :disabled="!textPrompt.trim() || !uploadedImage"
            @click="handleImageToImage"
          >
            <el-icon v-if="!isGenerating"><PictureFilled /></el-icon>
            {{ isGenerating ? 'AI 正在处理中...' : '开始优化图片' }}
          </el-button>
        </div>
      </section>

      <!-- ========== 右侧：生成结果展示 ========== -->
      <section class="result-panel" v-if="generatedImages.length > 0 || currentEditingImage">
        <!-- 当前正在编辑的图片（微调模式） -->
        <div v-if="currentEditingImage" class="refine-section">
          <div class="refine-header">
            <h4>继续编辑此图片</h4>
            <el-button text size="small" @click="currentEditingImage = null; refinePrompt = ''">取消</el-button>
          </div>
          <div class="refine-body">
            <img :src="currentEditingImage" class="refine-preview" />
            <div class="refine-controls">
              <el-input
                v-model="refinePrompt"
                type="textarea"
                :rows="2"
                placeholder="输入微调指令，如：让背景更亮一些、增加光影效果..."
                class="refine-input"
              />
              <el-button
                type="primary"
                size="small"
                :loading="isRefining"
                :disabled="!refinePrompt.trim()"
                @click="handleRefine"
              >
                微调生成
              </el-button>
            </div>
          </div>
          <el-divider />
        </div>

        <!-- 生成结果网格 -->
        <div v-if="generatedImages.length > 0" class="result-grid-section">
          <div class="result-header">
            <h4>生成结果（{{ generatedImages.length }} 张）</h4>
            <div class="result-actions">
              <el-button size="small" @click="selectAll" text>{{ allSelected ? '取消全选' : '全选' }}</el-button>
              <el-button size="small" type="primary" :disabled="selectedImages.length === 0" @click="showSkuDialog = true">
                <el-icon><FolderAdd /></el-icon>
                保存到 SKU（{{ selectedImages.length }}）
              </el-button>
              <el-button size="small" :disabled="selectedImages.length === 0" @click="batchDownload">
                <el-icon><Download /></el-icon>
                批量下载
              </el-button>
            </div>
          </div>

          <div class="result-grid">
            <div
              v-for="(img, idx) in generatedImages"
              :key="idx"
              class="result-card"
              :class="{ selected: selectedImages.includes(idx) }"
              @click="toggleSelect(idx)"
            >
              <div class="result-img-wrap">
                <img :src="img.url || img.base64" :alt="`生成图片 ${idx + 1}`" />
                <div class="result-overlay">
                  <el-checkbox :model-value="selectedImages.includes(idx)" @click.stop />
                  <div class="overlay-actions">
                    <el-button circle size="small" @click.stop="previewImage(img)">
                      <el-icon><ZoomIn /></el-icon>
                    </el-button>
                    <el-button circle size="small" @click.stop="downloadImage(img, idx)">
                      <el-icon><Download /></el-icon>
                    </el-button>
                    <el-button circle size="small" @click.stop="startRefine(img)">
                      <el-icon><Edit /></el-icon>
                    </el-button>
                  </div>
                </div>
              </div>
              <span class="result-index">#{{ idx + 1 }}</span>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="generatedImages.length === 0 && !isGenerating && !currentEditingImage" class="empty-state">
          <el-icon class="empty-icon"><Picture /></el-icon>
          <h3>等待生成</h3>
          <p>输入产品描述或上传图片，AI 将为您生成专业视觉素材</p>
          <div class="empty-features">
            <div class="feature-item">
              <el-icon><Checked /></el-icon> 商业摄影质感
            </div>
            <div class="feature-item">
              <el-icon><Checked /></el-icon> 多场景适配
            </div>
            <div class="feature-item">
              <el-icon><Checked /></el-icon> 一键关联SKU
            </div>
            <div class="feature-item">
              <el-icon><Checked /></el-icon> 透明背景输出
            </div>
          </div>
        </div>
      </section>

      <!-- ========== 历史记录侧栏 ========== -->
      <transition name="slide">
        <aside v-if="showHistory" class="history-panel">
          <div class="history-header">
            <h4>生成历史</h4>
            <el-button text size="small" @click="showHistory = false">
              <el-icon><Close /></el-icon>
            </el-button>
          </div>

          <!-- SKU 筛选 -->
          <div class="history-filter">
            <el-select
              v-model="historySkuFilter"
              filterable
              remote
              reserve-keyword
              placeholder="按SKU筛选"
              :remote-method="searchSkuRemote"
              :loading="skuSearchLoading"
              clearable
              size="small"
              style="width: 100%"
            >
              <el-option
                v-for="sku in skuOptions"
                :key="sku.sku_code || sku.id"
                :label="`${sku.sku_code || sku.id} - ${sku.name || ''}`"
                :value="sku.sku_code || sku.id"
              />
            </el-select>
          </div>

          <!-- 历史列表 -->
          <div class="history-list" v-loading="historyLoading">
            <div
              v-for="item in historyItems"
              :key="item.id"
              class="history-item"
              @click="loadHistoryConversation(item)"
            >
              <div class="history-thumb">
                <img v-if="item.thumbnail" :src="item.thumbnail" />
                <el-icon v-else><Picture /></el-icon>
              </div>
              <div class="history-info">
                <p class="history-prompt">{{ item.prompt?.substring(0, 50) || '无描述' }}{{ (item.prompt?.length || 0) > 50 ? '...' : '' }}</p>
                <p class="history-meta">
                  {{ item.mode === 'text2image' ? '文生图' : '图生图' }}
                  · {{ formatTime(item.created_at) }}
                  <span v-if="item.sku_code" class="history-sku">· {{ item.sku_code }}</span>
                </p>
              </div>
              <el-button text size="small" type="danger" @click.stop="deleteHistory(item.id)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-empty v-if="!historyLoading && historyItems.length === 0" description="暂无生成记录" :image-size="60" />
          </div>

          <!-- 分页 -->
          <div class="history-pagination" v-if="historyTotal > historyPageSize">
            <el-pagination
              v-model:current-page="historyPage"
              :page-size="historyPageSize"
              :total="historyTotal"
              small
              layout="prev, next"
              @current-change="loadHistory"
            />
          </div>
        </aside>
      </transition>
    </div>

    <!-- ========== 图片预览弹窗 ========== -->
    <el-dialog v-model="previewVisible" title="图片预览" width="80%" :close-on-click-modal="true" center>
      <div class="preview-dialog-body" v-if="previewImageData">
        <img :src="previewImageData.url || previewImageData.base64" class="preview-full-img" />
        <div class="preview-actions">
          <el-button @click="downloadImage(previewImageData)">
            <el-icon><Download /></el-icon> 下载
          </el-button>
          <el-button type="primary" @click="showSkuDialog = true; previewVisible = false">
            <el-icon><FolderAdd /></el-icon> 保存到SKU
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- ========== SKU 保存弹窗 ========== -->
    <el-dialog v-model="showSkuDialog" title="保存图片到 SKU" width="500px">
      <el-form label-width="80px">
        <el-form-item label="选择SKU">
          <el-select
            v-model="saveTargetSku"
            filterable
            remote
            reserve-keyword
            placeholder="搜索商品SKU"
            :remote-method="searchSkuRemote"
            :loading="skuSearchLoading"
            style="width: 100%"
          >
            <el-option
              v-for="sku in skuOptions"
              :key="sku.sku_code || sku.id"
              :label="`${sku.sku_code || sku.id} - ${sku.name || ''}`"
              :value="sku.sku_code || sku.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="保存图片">
          <span>{{ selectedImages.length }} 张已选图片</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSkuDialog = false">取消</el-button>
        <el-button type="primary" :loading="isSaving" @click="handleSaveToSku">
          确认保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  textToImage, imageToImage, refineImage, saveImageToSku,
  fetchHistory, fetchConversation, deleteHistoryItem, searchSku,
  LOCAL_TEMPLATES, RATIO_OPTIONS, STYLE_OPTIONS,
} from '@/api/aiImage'
import { AI_IMAGE_INPUT_HINT, validateAiImageFile } from '@/utils/aiStudio'

// ==================== 状态 ====================
const genMode = ref('text2image')         // 'text2image' | 'image2image'
const textPrompt = ref('')
const uploadedImage = ref('')             // base64
const imageRatio = ref('1:1')
const imageStyle = ref('photography')
const genCount = ref(4)
const transparentBg = ref(false)
const isGenerating = ref(false)
const generatedImages = ref([])
const currentRequestId = ref('')

// 微调
const currentEditingImage = ref('')
const refinePrompt = ref('')
const isRefining = ref(false)

// 选择
const selectedImages = ref([])
const allSelected = computed(() =>
  generatedImages.value.length > 0 && selectedImages.value.length === generatedImages.value.length
)

// 模板
const activeTemplateId = ref('')
const activeEditTplId = ref('')

// 历史记录
const showHistory = ref(false)
const historyItems = ref([])
const historyLoading = ref(false)
const historyPage = ref(1)
const historyPageSize = ref(20)
const historyTotal = ref(0)
const historySkuFilter = ref('')

// SKU
const showSkuDialog = ref(false)
const saveTargetSku = ref('')
const isSaving = ref(false)
const skuOptions = ref([])
const skuSearchLoading = ref(false)

// 预览
const previewVisible = ref(false)
const previewImageData = ref(null)

// ==================== 模板数据 ====================
const templates = LOCAL_TEMPLATES
const ratioOptions = RATIO_OPTIONS
const styleOptions = STYLE_OPTIONS
const uploadHint = AI_IMAGE_INPUT_HINT

// 图生图快捷指令模板
const editTemplates = [
  { id: 'e1', name: '添加白色背景', prompt: '为产品添加纯白色专业摄影背景，柔和灯光' },
  { id: 'e2', name: '户外自然场景', prompt: '将产品放置在阳光明媚的户外自然场景中' },
  { id: 'e3', name: '家居生活场景', prompt: '将产品融入现代简约家居生活场景' },
  { id: 'e4', name: '提升画质质感', prompt: '提升图片质量至专业商业摄影水准，增强光影质感' },
  { id: 'e5', name: '亚马逊主图标准', prompt: '转换为亚马逊标准主图：纯白背景RGB255,255,255，产品占85%以上' },
  { id: 'e6', name: '深色科技感', prompt: '将背景替换为深色科技感背景，增强产品高级感' },
  { id: 'e7', name: '去背景透明', prompt: '移除背景，输出透明PNG格式，仅保留产品主体' },
  { id: 'e8', name: '3D渲染风格', prompt: '将图片转换为高品质3D渲染风格' },
]

// ==================== 方法 ====================

// 文生图
async function handleTextToImage() {
  if (!textPrompt.value.trim()) return
  isGenerating.value = true
  generatedImages.value = []
  selectedImages.value = []
  try {
    const result = await textToImage({
      prompt: textPrompt.value.trim(),
      ratio: imageRatio.value,
      style: imageStyle.value,
      transparent: transparentBg.value,
      count: genCount.value,
    })
    generatedImages.value = result.images.map(img => ({
      url: img.url || '',
      base64: img.base64 || '',
    }))
    currentRequestId.value = result.requestId
    ElMessage.success(`成功生成 ${generatedImages.value.length} 张图片`)
    // 保存到本地历史（前端缓存）
    saveToLocalHistory(result)
  } catch (err) {
    ElMessage.error('图片生成失败：' + (err.message || '请稍后重试'))
  } finally {
    isGenerating.value = false
  }
}

// 图生图
async function handleImageToImage() {
  if (!textPrompt.value.trim() || !uploadedImage.value) return
  isGenerating.value = true
  generatedImages.value = []
  selectedImages.value = []
  try {
    const result = await imageToImage({
      image: uploadedImage.value,
      prompt: textPrompt.value.trim(),
      ratio: imageRatio.value,
      count: genCount.value,
    })
    generatedImages.value = result.images.map(img => ({
      url: img.url || '',
      base64: img.base64 || '',
    }))
    currentRequestId.value = result.requestId
    ElMessage.success(`成功生成 ${generatedImages.value.length} 张图片`)
    saveToLocalHistory(result)
  } catch (err) {
    ElMessage.error('图片优化失败：' + (err.message || '请稍后重试'))
  } finally {
    isGenerating.value = false
  }
}

// 微调
function startRefine(img) {
  currentEditingImage.value = img.url || img.base64
  refinePrompt.value = ''
  nextTick(() => {
    document.querySelector('.refine-input textarea')?.focus()
  })
}

async function handleRefine() {
  if (!refinePrompt.value.trim() || !currentEditingImage.value) return
  isRefining.value = true
  try {
    const result = await refineImage({
      imageBase64: currentEditingImage.value,
      prompt: refinePrompt.value.trim(),
      ratio: imageRatio.value,
      count: 1,
    })
    if (result.images.length > 0) {
      // 将微调结果插入到结果列表
      generatedImages.value.push({
        url: result.images[0].url || '',
        base64: result.images[0].base64 || '',
        refined: true,
      })
      ElMessage.success('微调完成')
    }
    currentEditingImage.value = null
    refinePrompt.value = ''
  } catch (err) {
    ElMessage.error('微调失败：' + (err.message || '请稍后重试'))
  } finally {
    isRefining.value = false
  }
}

// 图片上传
function handleImageChange(file) {
  const validation = validateAiImageFile(file.raw)
  if (!validation.valid) {
    ElMessage.error(validation.message)
    return
  }
  if (validation.severity === 'warning') {
    ElMessage.warning(validation.message)
  }
  const reader = new FileReader()
  reader.onload = (e) => {
    uploadedImage.value = e.target.result
  }
  reader.readAsDataURL(file.raw)
}

// 模板
function applyTemplate(tpl) {
  textPrompt.value = tpl.prompt
  activeTemplateId.value = tpl.id
}

function applyEditTemplate(tpl) {
  textPrompt.value = tpl.prompt
  activeEditTplId.value = tpl.id
}

// 选择
function toggleSelect(idx) {
  const pos = selectedImages.value.indexOf(idx)
  if (pos > -1) {
    selectedImages.value.splice(pos, 1)
  } else {
    selectedImages.value.push(idx)
  }
}

function selectAll() {
  if (allSelected.value) {
    selectedImages.value = []
  } else {
    selectedImages.value = generatedImages.value.map((_, i) => i)
  }
}

// 预览
function previewImage(img) {
  previewImageData.value = img
  previewVisible.value = true
}

// 下载
function downloadImage(img, idx) {
  const url = img.url || img.base64
  if (!url) return
  const a = document.createElement('a')
  a.href = url
  a.download = `ai-image-${idx != null ? idx + 1 : 'preview'}.png`
  a.click()
}

function batchDownload() {
  selectedImages.value.forEach(idx => {
    downloadImage(generatedImages.value[idx], idx)
  })
}

// 保存到 SKU
async function handleSaveToSku() {
  if (!saveTargetSku.value) {
    ElMessage.warning('请选择目标SKU')
    return
  }
  isSaving.value = true
  try {
    const imagesToSave = selectedImages.value.map(idx => {
      const img = generatedImages.value[idx]
      return (img.url || img.base64)
    })
    // 逐张保存（批量接口可用时改为批量）
    for (const imgData of imagesToSave) {
      await saveImageToSku({
        imageBase64: imgData,
        skuCode: saveTargetSku.value,
        prompt: textPrompt.value,
        requestId: currentRequestId.value,
      })
    }
    ElMessage.success(`已保存 ${imagesToSave.length} 张图片到 ${saveTargetSku.value}`)
    showSkuDialog.value = false
    saveTargetSku.value = ''
  } catch (err) {
    ElMessage.error('保存失败：' + (err.message || '请稍后重试'))
  } finally {
    isSaving.value = false
  }
}

// SKU 远程搜索
async function searchSkuRemote(query) {
  if (!query || query.length < 2) {
    skuOptions.value = []
    return
  }
  skuSearchLoading.value = true
  try {
    const results = await searchSku(query)
    skuOptions.value = results
  } catch {
    // 后端不可用时静默失败
    skuOptions.value = []
  } finally {
    skuSearchLoading.value = false
  }
}

// 历史记录
async function loadHistory() {
  historyLoading.value = true
  try {
    const result = await fetchHistory({
      page: historyPage.value,
      pageSize: historyPageSize.value,
      skuCode: historySkuFilter.value || undefined,
    })
    historyItems.value = result.items
    historyTotal.value = result.total
  } catch {
    // 后端不可用时从 localStorage 加载
    historyItems.value = loadLocalHistory()
    historyTotal.value = historyItems.value.length
  } finally {
    historyLoading.value = false
  }
}

async function loadHistoryConversation(item) {
  try {
    const records = await fetchConversation(item.request_id)
    if (records.length > 0) {
      // 恢复生成结果
      generatedImages.value = records
        .filter(r => r.image_url || r.image_base64)
        .map(r => ({ url: r.image_url || '', base64: r.image_base64 || '' }))
      textPrompt.value = item.prompt || ''
      currentRequestId.value = item.request_id
      showHistory.value = false
      ElMessage.success('已恢复历史生成结果')
    }
  } catch {
    ElMessage.warning('无法加载该对话记录')
  }
}

async function deleteHistory(id) {
  try {
    await ElMessageBox.confirm('确定删除这条记录？', '确认', { type: 'warning' })
    await deleteHistoryItem(id)
    historyItems.value = historyItems.value.filter(i => i.id !== id)
    removeLocalHistoryItem(id)
    ElMessage.success('已删除')
  } catch { /* 取消 */ }
}

// 本地历史缓存（后端不可用时兜底）
function saveToLocalHistory(result) {
  try {
    const list = JSON.parse(localStorage.getItem('ai_image_history') || '[]')
    list.unshift({
      id: Date.now().toString(),
      request_id: result.requestId,
      prompt: textPrompt.value,
      mode: genMode.value,
      thumbnail: generatedImages.value[0]?.url || generatedImages.value[0]?.base64 || '',
      created_at: new Date().toISOString(),
      image_count: generatedImages.value.length,
    })
    localStorage.setItem('ai_image_history', JSON.stringify(list.slice(0, 100)))
  } catch { /* ignore */ }
}

function loadLocalHistory() {
  try {
    return JSON.parse(localStorage.getItem('ai_image_history') || '[]')
  } catch {
    return []
  }
}

function removeLocalHistoryItem(id) {
  try {
    const list = JSON.parse(localStorage.getItem('ai_image_history') || '[]')
    localStorage.setItem('ai_image_history', JSON.stringify(list.filter(i => i.id !== id)))
  } catch { /* ignore */ }
}

// 格式化时间
function formatTime(isoStr) {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  const now = new Date()
  const diff = now - d
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

// ==================== 生命周期 ====================
onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.ai-image-gen {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-page, #f5f6fa);
}

/* ── 头部 ── */
.gen-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid var(--border, #e5e7eb);
  flex-shrink: 0;
}

.gen-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.gen-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary, #111827);
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.gen-title .el-icon {
  color: var(--brand, #085B9C);
  font-size: 22px;
}

.gen-subtitle {
  font-size: 13px;
  color: var(--text-secondary, #6b7280);
  padding-left: 12px;
  border-left: 1px solid var(--border, #e5e7eb);
}

.gen-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* ── 主体 ── */
.gen-body {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
}

/* ── 左侧面板 ── */
.gen-panel {
  width: 440px;
  min-width: 440px;
  background: #fff;
  border-right: 1px solid var(--border, #e5e7eb);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.panel-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary, #374151);
  margin-bottom: 8px;
  display: block;
}

.prompt-section {
  display: flex;
  flex-direction: column;
}

.prompt-input :deep(.el-textarea__inner) {
  font-size: 14px;
  line-height: 1.6;
}

/* 模板条 */
.template-bar {
  margin-top: 10px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.template-label {
  font-size: 12px;
  color: var(--text-muted, #9ca3af);
  white-space: nowrap;
  padding-top: 4px;
}

.template-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.template-chip {
  cursor: pointer;
  font-size: 12px;
  transition: all 0.15s;
}

.template-chip:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.08);
}

.tpl-icon {
  margin-right: 2px;
}

/* 配置行 */
.config-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 20px;
  align-items: center;
}

.config-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.config-item label {
  font-size: 12px;
  color: var(--text-secondary, #6b7280);
  white-space: nowrap;
}

/* 上传 */
.upload-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.image-uploader {
  width: 100%;
}

.image-uploader :deep(.el-upload) {
  width: 100%;
}

.image-uploader :deep(.el-upload-dragger) {
  width: 100%;
  padding: 30px 20px;
  border: 2px dashed var(--border, #d1d5db);
  border-radius: 10px;
  transition: all 0.2s;
}

.image-uploader :deep(.el-upload-dragger:hover) {
  border-color: var(--brand, #085B9C);
  background: var(--brand-light, #e8f4fc);
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.upload-icon {
  font-size: 36px;
  color: var(--text-muted, #9ca3af);
}

.upload-placeholder p {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary, #6b7280);
}

.upload-hint {
  font-size: 11px !important;
  color: var(--text-muted, #9ca3af) !important;
}

.upload-preview {
  max-width: 100%;
  max-height: 220px;
  object-fit: contain;
  border-radius: 8px;
}

/* 生成按钮 */
.gen-btn {
  width: 100%;
  height: 44px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 10px;
}

/* ── 右侧结果面板 ── */
.result-panel {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 微调区域 */
.refine-section {
  background: #fff;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 10px;
  padding: 16px;
}

.refine-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.refine-header h4 {
  margin: 0;
  font-size: 14px;
  color: var(--brand, #085B9C);
}

.refine-body {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.refine-preview {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid var(--border, #e5e7eb);
  flex-shrink: 0;
}

.refine-controls {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 结果网格 */
.result-grid-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-header h4 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary, #111827);
}

.result-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.result-card {
  background: #fff;
  border: 2px solid var(--border, #e5e7eb);
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.result-card:hover {
  border-color: var(--brand, #085B9C);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.result-card.selected {
  border-color: var(--brand, #085B9C);
  box-shadow: 0 0 0 3px rgba(8,91,156,0.15);
}

.result-img-wrap {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
  background: #f9fafb;
}

.result-img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.result-card:hover .result-img-wrap img {
  transform: scale(1.05);
}

.result-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.result-card:hover .result-overlay {
  opacity: 1;
}

.result-overlay .el-checkbox {
  position: absolute;
  top: 8px;
  left: 8px;
}

.overlay-actions {
  display: flex;
  gap: 8px;
}

.result-index {
  display: block;
  text-align: center;
  font-size: 11px;
  color: var(--text-muted, #9ca3af);
  padding: 6px 0;
}

/* 空状态 */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--text-muted, #9ca3af);
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  color: #d1d5db;
}

.empty-state h3 {
  margin: 0;
  font-size: 18px;
  color: var(--text-secondary, #6b7280);
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

.empty-features {
  display: flex;
  gap: 16px;
  margin-top: 8px;
  flex-wrap: wrap;
  justify-content: center;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  background: #fff;
  padding: 6px 14px;
  border-radius: 20px;
  border: 1px solid var(--border, #e5e7eb);
}

.feature-item .el-icon {
  color: var(--brand, #085B9C);
  font-size: 14px;
}

/* ── 历史记录侧栏 ── */
.history-panel {
  width: 320px;
  min-width: 320px;
  background: #fff;
  border-left: 1px solid var(--border, #e5e7eb);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.gen-body.history-open .result-panel {
  border-right: 1px solid var(--border, #e5e7eb);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border, #e5e7eb);
}

.history-header h4 {
  margin: 0;
  font-size: 14px;
}

.history-filter {
  padding: 10px 16px;
  border-bottom: 1px solid var(--border, #e5e7eb);
}

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}

.history-item:hover {
  background: var(--aside-hover, #e8f4fc);
}

.history-thumb {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  overflow: hidden;
  background: #f3f4f6;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.history-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.history-thumb .el-icon {
  font-size: 20px;
  color: #d1d5db;
}

.history-info {
  flex: 1;
  min-width: 0;
}

.history-prompt {
  margin: 0;
  font-size: 13px;
  color: var(--text-primary, #374151);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-meta {
  margin: 2px 0 0;
  font-size: 11px;
  color: var(--text-muted, #9ca3af);
}

.history-sku {
  color: var(--brand, #085B9C);
  font-weight: 500;
}

.history-pagination {
  padding: 10px 16px;
  border-top: 1px solid var(--border, #e5e7eb);
  display: flex;
  justify-content: center;
}

/* 滑入动画 */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

/* ── 预览弹窗 ── */
.preview-dialog-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.preview-full-img {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
  border-radius: 8px;
}

.preview-actions {
  display: flex;
  gap: 12px;
}
</style>
