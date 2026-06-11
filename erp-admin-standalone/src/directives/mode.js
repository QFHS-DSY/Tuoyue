/**
 * v-mode 自定义指令
 * 功能：按双模式（小白/资深）控制元素显隐
 * 用法：
 *   v-mode="'expert'"   → 仅资深模式显示
 *   v-mode="'beginner'" → 仅小白模式显示
 * 文档：前端开发功能与实现文档 v2.0 · 模块1
 */
import { useAppStore } from '@/stores/useAppStore'

export const modeDirective = {
  name: 'mode',

  mounted(el, binding) {
    const store = useAppStore()
    const requiredMode = binding.value  // 'expert' | 'beginner'

    // 初始状态
    updateVisibility()

    // 监听模式切换事件
    window.addEventListener('app:mode-change', updateVisibility)

    // 缓存清理函数
    el._modeUnwatch = () => {
      window.removeEventListener('app:mode-change', updateVisibility)
    }

    function updateVisibility() {
      if (!requiredMode) {
        el.style.display = ''
        return
      }
      if (requiredMode === 'expert' && store.isBeginner) {
        el.style.display = 'none'
      } else if (requiredMode === 'beginner' && store.isExpert) {
        el.style.display = 'none'
      } else {
        el.style.display = ''
      }
    }
  },

  updated(el, binding) {
    // 模式值变化时重新计算
    if (binding.value !== binding.oldValue) {
      const store = useAppStore()
      const requiredMode = binding.value
      if (!requiredMode) {
        el.style.display = ''
        return
      }
      if (requiredMode === 'expert' && store.isBeginner) {
        el.style.display = 'none'
      } else if (requiredMode === 'beginner' && store.isExpert) {
        el.style.display = 'none'
      } else {
        el.style.display = ''
      }
    }
  },

  unmounted(el) {
    // 清理事件监听
    if (el._modeUnwatch) {
      el._modeUnwatch()
    }
  },
}

// 全局注册指令（由 main.js 调用）
export function registerModeDirective(app) {
  app.directive('mode', modeDirective)
}
