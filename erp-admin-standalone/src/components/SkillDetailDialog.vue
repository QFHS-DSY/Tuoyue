<template>
  <el-dialog
    v-model="visible"
    :title="skill?.name || '技能详情'"
    width="680px"
    :close-on-click-modal="false"
    class="skill-detail-dialog"
    @closed="handleClose"
  >
    <template v-if="skill">
      <div class="sd-header">
        <div class="sd-meta">
          <el-tag v-if="skill.priceType === 'paid' || skill.priceType === 'freeAndPaid'"
            type="warning" size="small" effect="plain">付费</el-tag>
          <el-tag v-else type="success" size="small" effect="plain">免费</el-tag>
          <el-tag v-if="skill.source" size="small" type="info" effect="plain">
            {{ skill.source === 'clawhub' ? 'ClawHub' : skill.source === 'skillhub' ? 'SkillHub' : skill.source }}
          </el-tag>
          <span v-if="skill.version" class="sd-version">v{{ skill.version }}</span>
        </div>
      </div>

      <!-- 描述 -->
      <div class="sd-section">
        <div class="sd-label">功能描述</div>
        <p class="sd-desc">{{ skill.description || '暂无描述' }}</p>
      </div>

      <!-- 标签 -->
      <div class="sd-section" v-if="skill.tags && skill.tags.length">
        <div class="sd-label">功能标签</div>
        <div class="sd-tags">
          <el-tag v-for="(tag, i) in skill.tags" :key="i" size="small" round>
            {{ tag }}
          </el-tag>
        </div>
      </div>

      <!-- 适用平台 -->
      <div class="sd-section" v-if="skill.platforms && skill.platforms.length">
        <div class="sd-label">适用平台</div>
        <div class="sd-tags">
          <el-tag v-for="(p, i) in skill.platforms" :key="i" size="small" effect="plain" round>
            {{ p }}
          </el-tag>
        </div>
      </div>

      <!-- 目标区域 -->
      <div class="sd-section" v-if="skill.regions && skill.regions.length">
        <div class="sd-label">目标区域</div>
        <div class="sd-tags">
          <el-tag v-for="(r, i) in skill.regions" :key="i" size="small" effect="plain" round>
            {{ r }}
          </el-tag>
        </div>
      </div>

      <!-- 安装提示 -->
      <div class="sd-section" v-if="skill.installSkillPrompt">
        <div class="sd-label">安装说明</div>
        <div class="sd-install-prompt">
          <el-input
            :model-value="skill.installSkillPrompt"
            type="textarea"
            :rows="3"
            readonly
            resize="none"
          />
          <el-button size="small" class="sd-copy-btn" @click="copyInstallPrompt">
            <el-icon><CopyDocument /></el-icon>
            复制安装命令
          </el-button>
        </div>
      </div>

      <!-- 来源 -->
      <div class="sd-section" v-if="skill.sourceUrl">
        <div class="sd-label">来源链接</div>
        <el-link :href="skill.sourceUrl" target="_blank" type="primary" :underline="false">
          {{ skill.sourceUrl }}
        </el-link>
      </div>
    </template>

    <template #footer>
      <div class="sd-footer">
        <el-button @click="visible = false">关闭</el-button>
        <el-button
          v-if="installed"
          type="danger"
          :loading="uninstalling"
          @click="handleUninstall"
        >
          卸载
        </el-button>
        <el-button
          v-else
          type="primary"
          :loading="installing"
          :disabled="skill?.priceType === 'paid'"
          @click="handleInstall"
        >
          {{ skill?.priceType === 'paid' ? '付费技能（请联系卖家）' : '一键安装' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { CopyDocument } from '@element-plus/icons-vue'
import { useSkillHubStore } from '@/stores/skillhub'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  skill: { type: Object, default: null },
})

const emit = defineEmits(['update:modelValue', 'installed', 'uninstalled'])

const store = useSkillHubStore()

const visible = ref(props.modelValue)
const installing = ref(false)
const uninstalling = ref(false)
const installed = ref(false)

watch(() => props.modelValue, (v) => { visible.value = v })
watch(visible, (v) => {
  emit('update:modelValue', v)
  if (v && props.skill) {
    installed.value = store.checkInstalled(props.skill.slug || props.skill.id)
  }
})

function handleClose() {
  visible.value = false
}

async function handleInstall() {
  if (!props.skill) return
  installing.value = true
  try {
    const ok = await store.installSkill(props.skill)
    installed.value = true
    emit('installed', props.skill)
    ElMessage.success(ok ? '技能已安装' : '技能已记录（下载暂不可用，已标记安装）')
  } catch (e) {
    ElMessage.error('安装失败: ' + (e.message || '未知错误'))
  } finally {
    installing.value = false
  }
}

async function handleUninstall() {
  if (!props.skill) return
  uninstalling.value = true
  try {
    store.uninstallSkill(props.skill.slug || props.skill.id)
    installed.value = false
    emit('uninstalled', props.skill)
    ElMessage.success('技能已卸载')
  } catch (e) {
    ElMessage.error('卸载失败')
  } finally {
    uninstalling.value = false
  }
}

function copyInstallPrompt() {
  if (!props.skill?.installSkillPrompt) return
  navigator.clipboard.writeText(props.skill.installSkillPrompt).then(() => {
    ElMessage.success('安装命令已复制到剪贴板')
  }).catch(() => {
    ElMessage.warning('复制失败，请手动复制')
  })
}
</script>

<style scoped>
.sd-header {
  margin-bottom: 16px;
}
.sd-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.sd-version {
  font-size: 12px;
  color: var(--text-secondary, #909399);
}
.sd-section {
  margin-bottom: 16px;
}
.sd-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary, #303133);
  margin-bottom: 8px;
}
.sd-desc {
  font-size: 14px;
  color: var(--text-regular, #606266);
  line-height: 1.7;
  margin: 0;
}
.sd-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.sd-install-prompt {
  position: relative;
}
.sd-copy-btn {
  position: absolute;
  right: 4px;
  bottom: 4px;
  z-index: 1;
}
.sd-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
