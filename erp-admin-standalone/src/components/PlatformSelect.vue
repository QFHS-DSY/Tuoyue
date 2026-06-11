<template>
  <div class="platform-select">
    <!-- 简化展示（已选平台标签） -->
    <div v-if="!isExpanded && modelValue && modelValue.length > 0" class="selected-tags">
      <el-tag
        v-for="platform in selectedPlatforms"
        :key="platform.key"
        :type="getPlatformType(platform.key)"
        size="small"
        closable
        @close="handleRemove(platform.key)"
      >
        <img :src="platform.icon" class="tag-icon" />
        {{ platform.label }}
      </el-tag>
      <el-button text size="small" @click="isExpanded = true">
        + 修改
      </el-button>
    </div>

    <!-- 展开选择面板 -->
    <div v-if="isExpanded" class="select-panel">
      <!-- 核心平台（小白模式默认展示） -->
      <div class="platform-group">
        <div class="group-title">
          <span>核心平台</span>
          <el-checkbox
            v-if="multiple"
            :indeterminate="coreIndeterminate"
            :model-value="coreAllSelected"
            @change="toggleCoreAll"
          >
            全选
          </el-checkbox>
        </div>
        <div class="platform-grid">
          <div
            v-for="platform in corePlatforms"
            :key="platform.key"
            :class="['platform-item', { selected: isSelected(platform.key) }]"
            @click="handleToggle(platform.key)"
          >
            <img :src="platform.icon" class="platform-icon" />
            <span class="platform-label">{{ platform.label }}</span>
            <el-icon v-if="isSelected(platform.key)" class="check-icon"><Check /></el-icon>
          </div>
        </div>
      </div>

      <!-- 全量平台（资深模式展开） -->
      <div v-if="store.isExpert" class="platform-group advanced">
        <div class="group-title">
          <span>全量平台</span>
          <el-checkbox
            v-if="multiple"
            :indeterminate="allIndeterminate"
            :model-value="allSelected"
            @change="toggleAll"
          >
            全选全部
          </el-checkbox>
        </div>
        <div class="platform-grid">
          <div
            v-for="platform in advancedPlatforms"
            :key="platform.key"
            :class="['platform-item', { selected: isSelected(platform.key) }]"
            @click="handleToggle(platform.key)"
          >
            <img :src="platform.icon" class="platform-icon" />
            <span class="platform-label">{{ platform.label }}</span>
            <el-icon v-if="isSelected(platform.key)" class="check-icon"><Check /></el-icon>
          </div>
        </div>
      </div>

      <!-- 底部操作 -->
      <div class="panel-footer">
        <span class="selected-count">
          已选 {{ selectedCount }} 个平台
        </span>
        <el-button size="small" @click="isExpanded = false">确定</el-button>
      </div>
    </div>

    <!-- 未选择时的触发按钮 -->
    <el-button
      v-if="(!modelValue || modelValue.length === 0) && !isExpanded"
      :type="buttonType"
      @click="isExpanded = true"
    >
      <el-icon><Shop /></el-icon>
      选择平台
    </el-button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Check, Shop } from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/useAppStore'
import {
  PLATFORM_ICONS,
  CORE_PLATFORMS as CORE_KEYS,
} from '@/utils/platformIcons'

// ── 平台定义（从共享工具生成）─────────────────────────────────
const CORE_PLATFORMS = CORE_KEYS.map(key => ({
  key,
  label: PLATFORM_ICONS[key].name,
  icon: PLATFORM_ICONS[key].icon,
  color: PLATFORM_ICONS[key].color,
}))

const ADVANCED_PLATFORMS = Object.keys(PLATFORM_ICONS)
  .filter(key => !CORE_KEYS.includes(key))
  .map(key => ({
    key,
    label: PLATFORM_ICONS[key].name,
    icon: PLATFORM_ICONS[key].icon,
    color: PLATFORM_ICONS[key].color,
  }))

// ── Props & Emits ──────────────────────────────────────────
const props = defineProps({
  modelValue: {
    type: [Array, String],
    default: () => []
  },
  multiple: {
    type: Boolean,
    default: true
  },
  buttonType: {
    type: String,
    default: 'primary'
  },
})

const emit = defineEmits(['update:modelValue', 'change'])

// ── State ──────────────────────────────────────────────────
const store = useAppStore()
const isExpanded = ref(false)

// ── Computed ───────────────────────────────────────────────
const allPlatforms = computed(() => [...CORE_PLATFORMS, ...ADVANCED_PLATFORMS])

const selectedPlatforms = computed(() => {
  const keys = Array.isArray(props.modelValue) ? props.modelValue : [props.modelValue]
  return allPlatforms.value.filter(p => keys.includes(p.key))
})

const selectedKeys = computed(() => {
  return Array.isArray(props.modelValue) ? props.modelValue : (props.modelValue ? [props.modelValue] : [])
})

const selectedCount = computed(() => selectedKeys.value.length)

const coreAllSelected = computed(() =>
  CORE_PLATFORMS.every(p => selectedKeys.value.includes(p.key))
)

const coreIndeterminate = computed(() => {
  const selected = CORE_PLATFORMS.filter(p => selectedKeys.value.includes(p.key)).length
  return selected > 0 && selected < CORE_PLATFORMS.length
})

const allSelected = computed(() =>
  allPlatforms.value.every(p => selectedKeys.value.includes(p.key))
)

const allIndeterminate = computed(() => {
  const selected = allPlatforms.value.filter(p => selectedKeys.value.includes(p.key)).length
  return selected > 0 && selected < allPlatforms.value.length
})

// ── Methods ─────────────────────────────────────────────────
function isSelected(key) {
  return selectedKeys.value.includes(key)
}

function handleToggle(key) {
  let newValue
  if (props.multiple) {
    const keys = [...selectedKeys.value]
    const index = keys.indexOf(key)
    if (index === -1) {
      keys.push(key)
    } else {
      keys.splice(index, 1)
    }
    newValue = keys
  } else {
    newValue = [key]
    isExpanded.value = false
  }
  emit('update:modelValue', newValue)
  emit('change', newValue)
}

function handleRemove(key) {
  if (!props.multiple) return
  const keys = selectedKeys.value.filter(k => k !== key)
  emit('update:modelValue', keys)
  emit('change', keys)
}

function toggleCoreAll(val) {
  if (val) {
    const keys = [...new Set([...selectedKeys.value, ...CORE_PLATFORMS.map(p => p.key)])]
    emit('update:modelValue', keys)
    emit('change', keys)
  } else {
    const keys = selectedKeys.value.filter(k => !CORE_PLATFORMS.find(p => p.key === k))
    emit('update:modelValue', keys)
    emit('change', keys)
  }
}

function toggleAll(val) {
  if (val) {
    emit('update:modelValue', allPlatforms.value.map(p => p.key))
    emit('change', allPlatforms.value.map(p => p.key))
  } else {
    emit('update:modelValue', [])
    emit('change', [])
  }
}

function getPlatformType(key) {
  const colors = {
    shopee: '', temu: 'danger', shein: 'info', tiktok: 'warning',
    aliexpress: 'danger', amazon: 'warning', ebay: '', lazada: '', wish: '', mercado: 'warning', ozon: '', allegro: 'warning'
  }
  return colors[key] || ''
}
</script>

<style scoped>
.platform-select {
  display: inline-block;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.tag-icon {
  width: 14px;
  height: 14px;
  margin-right: 4px;
  vertical-align: middle;
}

.select-panel {
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  padding: 12px;
  background: var(--el-bg-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  min-width: 400px;
  max-width: 600px;
}

.platform-group {
  margin-bottom: 12px;
}

.platform-group.advanced {
  border-top: 1px solid var(--el-border-color);
  padding-top: 12px;
}

.group-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}

.platform-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.platform-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px;
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  user-select: none;
}

.platform-item:hover {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.platform-item.selected {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.platform-icon {
  width: 28px;
  height: 28px;
  margin-bottom: 4px;
}

.platform-label {
  font-size: 11px;
  text-align: center;
  color: var(--el-text-color-regular);
}

.check-icon {
  position: absolute;
  top: 2px;
  right: 2px;
  color: var(--el-color-primary);
  font-size: 12px;
}

.panel-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid var(--el-border-color);
}

.selected-count {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
</style>
