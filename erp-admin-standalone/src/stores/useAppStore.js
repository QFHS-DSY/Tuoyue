/**
 * 全局双模式状态管理
 * 功能：管理小白模式/资深模式状态，刷新不丢失
 * 文档：前端开发功能与实现文档 v2.0 · 模块1
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  // ── 模式状态 ──────────────────────────────────────────────
  // 从 localStorage 恢复，刷新不丢失
  const mode = ref(localStorage.getItem('app_mode') || 'beginner')
  const hardwareUnlocked = ref(false)

  // ── 计算属性 ─────────────────────────────────────────────
  const isBeginner = computed(() => mode.value === 'beginner')
  const isExpert = computed(() => mode.value === 'expert')
  const modeLabel = computed(() => mode.value === 'beginner' ? '🌟 小白模式' : '⚡ 资深模式')

  // ── 操作方法 ─────────────────────────────────────────────
  function setMode(m) {
    if (m !== 'beginner' && m !== 'expert') return
    mode.value = m
    localStorage.setItem('app_mode', m)
  }

  function toggleMode() {
    setMode(isBeginner.value ? 'expert' : 'beginner')
  }

  function setHardwareUnlocked(val) {
    hardwareUnlocked.value = val
  }

  // ── 全局事件总线（供各组件订阅模式切换）────────────────────
  // 使用原生 CustomEvent，兼容 Vue 无需额外依赖
  function emitModeChange() {
    window.dispatchEvent(new CustomEvent('app:mode-change', {
      detail: { mode: mode.value, isBeginner: isBeginner.value, isExpert: isExpert.value }
    }))
  }

  // 覆盖 setMode 以便自动广播
  const _setMode = setMode
  function setModeWithBroadcast(m) {
    _setMode(m)
    emitModeChange()
  }

  return {
    // 状态
    mode,
    hardwareUnlocked,
    // 计算
    isBeginner,
    isExpert,
    modeLabel,
    // 方法
    setMode: setModeWithBroadcast,
    setModeRaw: _setMode,   // 不触发广播的原始版本（内部用）
    toggleMode,
    setHardwareUnlocked,
    emitModeChange,
  }
})
