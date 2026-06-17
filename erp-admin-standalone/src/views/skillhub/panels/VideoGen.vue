<template>
  <div class="panel-video-gen">
    <!-- 上传产品图 -->
    <div class="panel-section">
      <label class="panel-label">上传产品图片（可选多张）</label>
      <el-upload
        class="image-upload-area"
        :auto-upload="false"
        :show-file-list="false"
        :on-change="handleImageChange"
        accept="image/*"
        drag
        multiple
        :disabled="!isVideoEnabled"
      >
        <div v-if="uploadedImages.length === 0" class="upload-empty">
          <el-icon :size="48"><VideoCamera /></el-icon>
          <p>上传1-5张产品图片，AI将生成动态展示视频</p>
          <p class="upload-hint">{{ uploadHint }}</p>
        </div>
        <div v-else class="uploaded-preview-row">
          <img
            v-for="(img, idx) in uploadedImages"
            :key="idx"
            :src="img.url"
            class="uploaded-thumb"
            :alt="`图片 ${idx + 1}`"
          />
          <div class="add-more-btn" v-if="uploadedImages.length < 5">
            <el-icon :size="24"><Plus /></el-icon>
            <span>添加更多</span>
          </div>
        </div>
      </el-upload>
    </div>

    <!-- 视频配置 -->
    <div class="panel-section">
      <label class="panel-label">视频配置</label>
      <div class="video-config-grid">
        <div class="config-group">
          <span class="config-group-label">时长</span>
          <el-radio-group v-model="duration" size="small">
            <el-radio-button value="5">5秒</el-radio-button>
            <el-radio-button value="10">10秒</el-radio-button>
            <el-radio-button value="15">15秒</el-radio-button>
            <el-radio-button value="30">30秒</el-radio-button>
          </el-radio-group>
        </div>
        <div class="config-group">
          <span class="config-group-label">风格</span>
          <el-select v-model="videoStyle" style="width: 150px">
            <el-option v-for="s in videoStyles" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </div>
        <div class="config-group">
          <span class="config-group-label">背景音乐</span>
          <el-select v-model="bgm" style="width: 150px">
            <el-option v-for="b in bgmOptions" :key="b.value" :label="b.label" :value="b.value" />
          </el-select>
        </div>
      </div>
    </div>

    <!-- 描述 -->
    <div class="panel-section">
      <label class="panel-label">视频描述/卖点文字（可选）</label>
      <el-input
        v-model="description"
        type="textarea"
        :rows="2"
        placeholder="例如：展示产品360度旋转效果，突出材质质感和使用场景..."
        maxlength="500"
        show-word-limit
      />
    </div>

    <el-alert
      v-if="!isVideoEnabled"
      title="视频能力待开通"
      type="warning"
      :closable="false"
      show-icon
      style="margin-bottom: 16px;"
    >
      <template #default>
        <p style="margin:0;font-size:13px;">{{ videoUnavailableMessage }}</p>
      </template>
    </el-alert>

    <el-button
      type="primary"
      size="large"
      class="generate-btn"
      :loading="generating"
      :disabled="!isVideoEnabled || uploadedImages.length === 0"
      @click="handleGenerate"
    >
      <el-icon><VideoPlay /></el-icon>
      {{ generating ? 'AI 正在生成视频...' : '生成产品短视频' }}
    </el-button>

    <!-- 结果 -->
    <div v-if="videoResult" class="video-result">
      <h4>生成结果</h4>
      <video :src="videoResult" controls class="result-video" />
      <div class="video-actions">
        <el-button type="primary" size="small" @click="downloadVideo">
          <el-icon><Download /></el-icon> 下载视频
        </el-button>
      </div>
    </div>

    <!-- 提示 -->
    <el-alert
      v-if="!videoResult && !generating"
      title="视频生成说明"
      type="info"
      :closable="false"
      show-icon
      style="margin-top: 16px;"
    >
      <template #default>
        <p style="margin:0;font-size:13px;">
          上传产品图片后，AI将自动生成适合TikTok/Instagram Reels/YouTube Shorts等平台的产品展示短视频。<br/>
          支持动态运镜、文字叠加、背景音乐等功能。
        </p>
      </template>
    </el-alert>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, VideoCamera, VideoPlay, Download } from '@element-plus/icons-vue'
import { generateVideo } from '@/api/aiImage'
import {
  AI_IMAGE_INPUT_HINT,
  AI_VIDEO_ENABLED,
  AI_VIDEO_UNAVAILABLE_MESSAGE,
  validateAiImageFile,
} from '@/utils/aiStudio'

const uploadedImages = ref([])
const imageFiles = ref([])
const duration = ref('10')
const videoStyle = ref('cinematic')
const bgm = ref('none')
const description = ref('')
const generating = ref(false)
const videoResult = ref('')
const isVideoEnabled = AI_VIDEO_ENABLED
const videoUnavailableMessage = AI_VIDEO_UNAVAILABLE_MESSAGE
const uploadHint = AI_IMAGE_INPUT_HINT

const videoStyles = [
  { label: '电影质感', value: 'cinematic' },
  { label: '快节奏动感', value: 'dynamic' },
  { label: '柔和优雅', value: 'elegant' },
  { label: '科技未来', value: 'tech' },
  { label: '生活日常', value: 'lifestyle' },
]

const bgmOptions = [
  { label: '无音乐', value: 'none' },
  { label: '轻快电子', value: 'electronic' },
  { label: '舒缓钢琴', value: 'piano' },
  { label: '流行节奏', value: 'pop' },
  { label: '商务大气', value: 'corporate' },
]

async function handleImageChange(file) {
  if (uploadedImages.value.length >= 5) {
    ElMessage.warning('最多上传5张图片')
    return
  }

  const validation = validateAiImageFile(file.raw)
  if (!validation.valid) {
    ElMessage.error(validation.message)
    return
  }
  if (validation.severity === 'warning') {
    ElMessage.warning(validation.message)
  }

  imageFiles.value.push(file.raw)
  uploadedImages.value.push({ url: URL.createObjectURL(file.raw) })
}

async function handleGenerate() {
  if (!isVideoEnabled) {
    ElMessage.warning(videoUnavailableMessage)
    return
  }
  generating.value = true
  videoResult.value = ''
  try {
    const result = await generateVideo({
      images: imageFiles.value,
      duration: duration.value,
      style: videoStyle.value,
      bgm: bgm.value,
      description: description.value,
    })
    videoResult.value = result.videoUrl || ''
    if (videoResult.value) {
      ElMessage.success('视频生成成功')
    } else {
      ElMessage.warning(result.detail || '后端暂未返回视频地址，请稍后重试')
    }
  } catch (e) {
    ElMessage.error('视频生成失败: ' + (e.message || '网络错误'))
  } finally {
    generating.value = false
  }
}

function downloadVideo() {
  if (!videoResult.value) return
  const a = document.createElement('a')
  a.href = videoResult.value
  a.download = `product-video-${Date.now()}.mp4`
  a.click()
}
</script>

<style scoped>
.panel-video-gen { padding: 8px 0; }
.panel-section { margin-bottom: 16px; }
.panel-label { display: block; font-size: 14px; font-weight: 600; color: #303133; margin-bottom: 8px; }
.image-upload-area { width: 100%; }
.upload-empty { display: flex; flex-direction: column; align-items: center; padding: 24px; color: #c0c4cc; }
.upload-empty p { margin: 8px 0 0; }
.upload-hint { font-size: 12px; color: #c0c4cc; }

.uploaded-preview-row { display: flex; gap: 8px; align-items: center; padding: 12px; flex-wrap: wrap; }
.uploaded-thumb { width: 100px; height: 100px; object-fit: cover; border-radius: 8px; }
.add-more-btn { width: 100px; height: 100px; display: flex; flex-direction: column; align-items: center; justify-content: center; border: 2px dashed #dcdfe6; border-radius: 8px; color: #c0c4cc; cursor: pointer; font-size: 12px; gap: 4px; }
.add-more-btn:hover { border-color: #409eff; color: #409eff; }

.video-config-grid { display: flex; flex-direction: column; gap: 12px; }
.config-group { display: flex; align-items: center; gap: 12px; }
.config-group-label { font-size: 13px; color: #606266; width: 72px; flex-shrink: 0; }

.generate-btn { width: 100%; margin-bottom: 20px; }

.video-result { margin-top: 16px; }
.video-result h4 { margin: 0 0 12px; font-size: 15px; }
.result-video { width: 100%; max-height: 400px; border-radius: 8px; background: #000; }
.video-actions { margin-top: 12px; display: flex; gap: 12px; }
</style>
