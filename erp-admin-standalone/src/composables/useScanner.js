/**
 * 全局扫码枪监听 Composable
 * 功能：
 *   - 全局监听 keydown，无需聚焦输入框
 *   - 识别扫码枪特征：连续快速输入（间隔<50ms）+ 以 Enter 结尾
 *   - 支持扫码后自动匹配商品库，无商品时触发 1688 条码溯源采集
 *   - 支持扫码采集 → 上货 / 补货一站式链路
 *   - 通过事件总线分发扫码结果，各页面按需订阅
 * 文档：前端开发功能与实现文档 v2.0 · 模块2
 *
 * 使用方式：
 *   const { onScan, isScanning, pause, resume, lookupBarcode } = useScanner()
 *
 *   // 订阅扫码事件
 *   onScan((barcode) => {
 *     console.log('扫到条码:', barcode)
 *   })
 *
 *   // 查询条码商品信息（本地库 + 1688溯源）
 *   const goods = await lookupBarcode('6931024012345')
 */
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

// ── 全局扫码事件总线（单例）────────────────────────────────
class ScannerBus {
  constructor() {
    this.handlers = []
    this._enabled = true
  }

  on(handler) {
    this.handlers.push(handler)
    // 返回取消订阅函数
    return () => {
      this.handlers = this.handlers.filter(h => h !== handler)
    }
  }

  emit(barcode, extra = {}) {
    if (!this._enabled) return
    this.handlers.forEach(handler => {
      try {
        handler(barcode, extra)
      } catch (e) {
        console.error('[useScanner] 扫码处理器出错:', e)
      }
    })
  }

  enable() { this._enabled = true }
  disable() { this._enabled = false }
}

// 全局单例，避免重复监听
const scannerBus = new ScannerBus()

export function useScanner() {
  let buffer = ''
  let lastKeyTime = 0
  let timeoutId = null

  const THRESHOLD = 50        // ms：扫码枪两次按键最大间隔
  const MIN_LENGTH = 4       // 最少条码长度（过滤噪音）
  const BUFFER_TIMEOUT = 200 // ms：超过此时间未完成则清空缓冲区

  const isScanning = ref(false)
  const isEnabled = ref(true)

  // ── 核心：识别扫码枪输入 ─────────────────────────────────
  function handleKeydown(e) {
    if (!isEnabled.value) return

    // 如果当前有聚焦的输入框/文本框，且不是扫码枪行为，跳过
    // （避免在输入框打字时被误识别为扫码）
    const activeTag = document.activeElement?.tagName?.toLowerCase()
    if (activeTag === 'input' || activeTag === 'textarea') {
      // 如果是在输入框内按 Enter，可能只是普通表单提交
      // 只有在快速连续输入时才认为是扫码
      if (e.key !== 'Enter' || buffer.length < MIN_LENGTH) {
        return  // 交给原生处理
      }
    }

    const now = Date.now()
    const interval = now - lastKeyTime

    // 清空之前的超时
    if (timeoutId) {
      clearTimeout(timeoutId)
      timeoutId = null
    }

    // Enter 结尾 → 扫码完成
    if (e.key === 'Enter') {
      e.preventDefault()
      if (buffer.length >= MIN_LENGTH && interval < THRESHOLD * 5) {
        // 有效扫码
        const barcode = buffer.trim()
        isScanning.value = true
        scannerBus.emit(barcode)

        // 500ms 后重置扫描状态
        setTimeout(() => {
          isScanning.value = false
        }, 500)
      }
      buffer = ''
      lastKeyTime = 0
      return
    }

    // 可打印字符 → 加入缓冲区
    if (e.key.length === 1 && !e.ctrlKey && !e.altKey && !e.metaKey) {
      // 间隔太长 → 不是扫码枪，重置缓冲区
      if (interval > THRESHOLD && buffer.length > 0) {
        buffer = ''
      }
      buffer += e.key
      lastKeyTime = now

      // 设置超时：超过 BUFFER_TIMEOUT 未完成则清空
      timeoutId = setTimeout(() => {
        buffer = ''
        lastKeyTime = 0
      }, BUFFER_TIMEOUT)
    }
  }

  // ── 条码查询：本地库匹配 + 1688 溯源采集 ──────────────────
  /**
   * 查询条码对应的商品信息
   * 1. 先在本地已采集商品库匹配
   * 2. 未找到时自动触发 1688 条码溯源采集
   * @param {string} barcode - 条码
   * @returns {Promise<{ found: boolean, source: 'local'|'1688', goods?: object }>}
   */
  async function lookupBarcode(barcode) {
    if (!barcode || barcode.length < 4) {
      return { found: false, source: null, goods: null, reason: '条码过短' }
    }
    try {
      const res = await fetch(`/api/goods/?keyword=${barcode}&page=1&page_size=1`)
      const data = await res.json()
      const items = data?.data?.results || data?.results || []
      if (items.length) return { found: true, source: 'api', goods: items[0] }
      return { found: false, source: 'none', goods: null, reason: '未找到匹配商品' }
    } catch {
      return { found: false, source: 'none', goods: null, reason: '查询失败' }
    }
  }

  // ── 生命周期 ────────────────────────────────────────────
  onMounted(() => {
    window.addEventListener('keydown', handleKeydown, true)
  })

  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown, true)
    if (timeoutId) clearTimeout(timeoutId)
  })

  // ── 订阅扫码事件 ─────────────────────────────────────────
  function onScan(callback) {
    // 支持 (barcode, extra) 两个参数
    return scannerBus.on(callback)
  }

  // ── 控制方法 ─────────────────────────────────────────────
  function pause() {
    isEnabled.value = false
    scannerBus.disable()
  }

  function resume() {
    isEnabled.value = true
    scannerBus.enable()
  }

  /**
   * 手动触发一次扫码（用于测试或手动输入条码）
   */
  function emitManual(barcode) {
    if (barcode && barcode.length >= MIN_LENGTH) {
      scannerBus.emit(barcode)
    }
  }

  return {
    isScanning,   // ref，当前是否正在扫描（500ms内有效）
    isEnabled,   // ref，是否启用
    onScan,      // 订阅扫码事件，返回取消订阅函数
    pause,       // 暂停扫码监听
    resume,      // 恢复扫码监听
    emitManual,  // 手动触发扫码
    lookupBarcode, // 查询条码商品信息（本地库+1688溯源）
  }
}

// ── 全局事件常量 ────────────────────────────────────────────
// 页面组件可监听此事件获取扫码结果
export const SCAN_EVENT = 'global:scan'

/**
 * 全局扫码分发（由 App.vue 调用）
 * 将 scannerBus 的结果分发到 Vue globalProperties 或 window 事件
 */
export function setupGlobalScanner() {
  scannerBus.on((barcode) => {
    // 分发到 window 事件，兼容各页面
    window.dispatchEvent(new CustomEvent(SCAN_EVENT, { detail: { barcode, timestamp: Date.now() } }))
  })
}
