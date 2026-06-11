<template>
  <div class="tiger-assistant" :style="floatingStyle" ref="widgetRef">
    <!-- 最小化悬浮按钮 -->
    <div
      v-if="!isOpen"
      class="tiger-fab"
      @mousedown.stop="startFabDrag"
      @click="openChat"
      title="小辽 · AI助手"
    >
      <img v-if="mascotSrc" :src="mascotSrc" class="tiger-avatar" alt="小辽" />
      <el-icon v-else :size="36"><MagicStick /></el-icon>
      <div v-if="unreadCount > 0" class="unread-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</div>
      <!-- 拖拽手柄 -->
      <div class="drag-handle" title="拖动">
        <el-icon><Rank /></el-icon>
      </div>
    </div>

    <!-- 展开大窗口 -->
    <Transition name="pop">
      <div v-if="isOpen" class="tiger-window">
        <!-- 可拖拽标题栏 -->
        <div class="tiger-header" @mousedown="startDrag">
          <div class="header-avatar">
            <img v-if="mascotSrc" :src="mascotSrc" class="header-mascot" alt="小辽" />
            <el-icon v-else :size="28"><MagicStick /></el-icon>
            <span class="online-dot" />
          </div>
          <div class="header-info">
            <span class="header-name">小辽</span>
            <span class="header-sub">Ruitalk AI · 智能助手</span>
          </div>
          <div class="header-controls">
            <el-button text size="small" @click.stop="minimize" title="最小化">
              <el-icon><Minus /></el-icon>
            </el-button>
            <el-button text size="small" @click.stop="closeChat" title="关闭">
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 上下文提示 -->
        <div v-if="contextTips.length > 0" class="context-tips">
          <div v-for="tip in contextTips" :key="tip.id" :class="['tip-chip', `tip-${tip.type}`]">
            <el-icon v-if="tip.type === 'warning'" :size="12"><Warning /></el-icon>
            <el-icon v-else-if="tip.type === 'success'" :size="12"><CircleCheck /></el-icon>
            <el-icon v-else :size="12"><InfoFilled /></el-icon>
            <span>{{ tip.content }}</span>
            <el-button v-if="tip.action" text size="small" type="primary" @click="doTipAction(tip)">
              {{ tip.actionLabel }}
            </el-button>
          </div>
        </div>

        <!-- 欢迎页 -->
        <div v-if="messages.length === 0 && !thinking" class="welcome-screen">
          <img v-if="mascotSrc" :src="mascotSrc" class="welcome-img" alt="小辽" />
          <div class="welcome-greet">你好，我是小辽 👋</div>
          <div class="welcome-sub">Ruitalk AI驱动，跨境电商全能助手</div>
          <div class="quick-prompts">
            <div class="quick-title">快捷指令</div>
            <div class="quick-grid">
              <button v-for="q in quickPrompts" :key="q.text" class="quick-btn" @click="quickAsk(q.text)">
                {{ q.icon }} {{ q.label }}
              </button>
            </div>
          </div>
        </div>

        <!-- 消息列表 -->
        <div class="chat-body" ref="bodyRef">
          <div v-for="msg in messages" :key="msg.id" :class="['msg-row', msg.role]">
            <div class="msg-avatar">
              <img v-if="msg.role === 'assistant' && mascotSrc" :src="mascotSrc" />
              <el-icon v-else><User /></el-icon>
            </div>
            <div class="msg-bubble">
              <div class="msg-text" v-html="renderMarkdown(msg.content)" />
              <div v-if="msg.actions?.length" class="msg-actions">
                <el-button
                  v-for="a in msg.actions" :key="a.label"
                  size="small" :type="a.type || 'primary'"
                  :disabled="a.loading" @click="doAction(a)"
                >
                  <el-icon v-if="a.icon"><component :is="a.icon" /></el-icon>
                  {{ a.label }}
                </el-button>
              </div>
            </div>
          </div>

          <!-- AI 思考中 -->
          <div v-if="thinking" class="msg-row assistant">
            <div class="msg-avatar">
              <img v-if="mascotSrc" :src="mascotSrc" />
            </div>
            <div class="msg-bubble">
              <div class="thinking-bars"><span /><span /><span /></div>
            </div>
          </div>
        </div>

        <!-- 输入区 -->
        <div class="chat-footer">
          <div class="input-row">
            <el-input
              v-model="inputText"
              placeholder="问小辽任何问题..."
              size="large"
              :rows="2"
              type="textarea"
              resize="none"
              @keydown.ctrl.enter="send"
              @keydown.meta.enter="send"
              :disabled="thinking"
            />
            <el-button type="primary" size="large" :loading="thinking" :disabled="!inputText.trim() || thinking" @click="send" class="send-btn">
              <el-icon v-if="!thinking"><Promotion /></el-icon>
              {{ thinking ? '思考中' : '发送' }}
            </el-button>
          </div>
          <div class="input-hint">Ctrl+Enter 发送 · 小辽由 Ruitalk AI 驱动</div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  MagicStick, Minus, Close, User, Warning, CircleCheck,
  InfoFilled, Promotion, Rank, Setting, List, Box, Shop,
  Document, TrendCharts, ChatDotRound
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { tuoyueChat } from '@/api/ai'

// ── Props ──────────────────────────────────────────────
defineProps({
  mascotSrc: { type: String, default: '' }
})

const route = useRoute()
const router = useRouter()

// ── 悬浮位置状态（可拖拽）─────────────────────────────────
const widgetRef = ref(null)
const posX = ref(window.innerWidth - 100 - 24)
const posY = ref(window.innerHeight - 100 - 24)

onMounted(() => {
  // 初始化位置：右下角
  if (widgetRef.value) {
    const rect = widgetRef.value.getBoundingClientRect()
    posX.value = window.innerWidth - rect.width - 24
    posY.value = window.innerHeight - rect.height - 24
  }
})
const dragging = ref(false)
const dragOffsetX = ref(0)
const dragOffsetY = ref(0)
const wasDragged = ref(false) // 区分拖拽和点击

const floatingStyle = computed(() => ({
  left: `${posX.value}px`,
  top: `${posY.value}px`,
  transition: dragging.value ? 'none' : 'all 0.2s ease',
}))

// 拖拽开始
function startDrag(e) {
  // 忽略点击按钮区域
  if (e.target.closest('.header-controls')) return
  dragging.value = true
  const rect = widgetRef.value.getBoundingClientRect()
  dragOffsetX.value = e.clientX - rect.left
  dragOffsetY.value = e.clientY - rect.top
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

// FAB 悬浮状态下的拖拽（整个按钮可拖，点击才打开）
function startFabDrag(e) {
  if (e.target.closest('.drag-handle') || e.target.closest('.unread-badge')) return
  wasDragged.value = false
  dragging.value = true
  const rect = widgetRef.value.getBoundingClientRect()
  dragOffsetX.value = e.clientX - rect.left
  dragOffsetY.value = e.clientY - rect.top
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

function onDrag(e) {
  if (!dragging.value || !widgetRef.value) return
  wasDragged.value = true
  const rect = widgetRef.value.getBoundingClientRect()
  const nx = e.clientX - dragOffsetX.value
  const ny = e.clientY - dragOffsetY.value
  // 左右边界：窗口不超出视口
  posX.value = Math.max(0, Math.min(nx, window.innerWidth - rect.width))
  // 上下边界：顶部留24px（确保标题栏按钮可见），底部不超出视口
  const TOP_MARGIN = 24
  posY.value = Math.max(TOP_MARGIN, Math.min(ny, window.innerHeight - rect.height))
}

function stopDrag() {
  dragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

// ── 聊天状态 ─────────────────────────────────────────────
const isOpen = ref(false)
const messages = ref([])
const inputText = ref('')
const thinking = ref(false)
const unreadCount = ref(0)
const bodyRef = ref(null)

// ── 系统提示词（必须放函数前，因 send() 引用它）──────────────
const SYSTEM_PROMPT = `你是「小辽」，辽宁跨境宝盒ERP系统的AI助手，基于Ruitalk金牌客服系统。

你的能力范围：
1. 商品运营：标题/描述/卖点生成（支持中英文）
2. 订单处理：订单查询、异常分析、发货建议
3. 库存管理：库存预警、补货建议
4. 平台选择：根据商品特性推荐最合适的跨境平台
5. 合规检测：检测商品是否符合目标平台规则
6. 数据分析：销售数据解读、经营日报生成

回复风格：专业、简洁、有条理。用 Markdown 格式，适当使用 emoji。
当用户提到具体商品或数据时，引导用户到对应页面操作。`

// ── 快捷指令 ─────────────────────────────────────────────
const quickPrompts = [
  { label: 'AI生成标题', icon: '✨', text: '帮我生成一个跨境电商商品标题' },
  { label: '今日订单',   icon: '📦', text: '查看今日待处理订单' },
  { label: '库存预警',   icon: '📊', text: '查看当前库存预警情况' },
  { label: '生成日报',   icon: '📈', text: '生成今日经营日报' },
]

// ── 上下文提示 ────────────────────────────────────────────
const tipConfigs = {
  '/goods/listing':  [{ id: 1, type: 'info', content: '💡 AI生成标题/描述/卖点', action: 'listing', actionLabel: '生成' }],
  '/orders':         [{ id: 1, type: 'warning', content: '⚠️ 有异常订单需处理', action: 'orders', actionLabel: '处理' }],
  '/inventory':      [{ id: 1, type: 'warning', content: '📦 5个SKU库存不足', action: 'inventory', actionLabel: '查看' }],
  '/goods/collect':  [{ id: 1, type: 'info', content: '🔫 支持扫码枪快速采集', action: 'scan', actionLabel: '扫码' }],
}
const contextTips = computed(() => tipConfigs[route.path] || [])

// ── 发送消息 ──────────────────────────────────────────────
async function send() {
  const text = inputText.value.trim()
  if (!text || thinking.value) return

  // 保存用户消息后再发，因为 catch 里要用原始消息
  const userMsg = { id: Date.now(), role: 'user', content: text }
  messages.value.push(userMsg)
  inputText.value = ''
  thinking.value = true
  await nextTick()
  scrollBottom()

  try {
    console.log('[小辽] 正在调用拓跃AI...')
    const history = messages.value.map(m => ({ role: m.role, content: m.content }))
    // 拼接系统提示词
    const fullMessages = [
      { role: 'system', content: SYSTEM_PROMPT },
      ...history
    ]
    const result = await tuoyueChat(fullMessages)
    console.log('[小辽] 拓跃AI 回复成功')
    messages.value.push({ id: Date.now(), role: 'assistant', content: result, actions: [] })
  } catch (err) {
    console.error('[小辽] Ruitalk AI 调用失败:', err.message)
    const reply = await localCommand(text)
    messages.value.push({
      id: Date.now(),
      role: 'assistant',
      content: reply + `\n\n⚠️ 小辽暂时不可用（${err.message}），已切换本地模式。`,
      actions: []
    })
  } finally {
    thinking.value = false
    await nextTick()
    scrollBottom()
  }
}

// ── 本地命令解析（API失败时降级，查询真实后端数据）────────────────
async function localCommand(text) {
  const t = text.toLowerCase()

  if (/标题|title|描述|description|卖点|features/.test(t)) {
    return '✨ 我可以帮你生成商品标题、描述和卖点。请在「商品上货」页面中选择商品后使用AI生成功能。'
  }

  if (/订单|order/.test(t)) {
    try {
      const { default: request } = await import('@/utils/request')
      const res = await request.get('/api/orders/', { params: { page: 1, pageSize: 1 } })
      const total = res?.data?.total || res?.total || 0
      const stats = await request.get('/api/orders/status-counts/')
      const sc = stats?.data || stats || {}
      return `📦 当前订单概况：\n- 总订单数：${total}\n- 待处理：${sc.pending || 0}单\n- 已发货：${sc.shipped || 0}单\n\n[查看订单管理 →](/orders)`
    } catch {
      return '📦 无法获取实时订单数据，请检查网络后重试。[查看订单管理 →](/orders)'
    }
  }

  if (/库存|inventory|补货/.test(t)) {
    try {
      const { default: request } = await import('@/utils/request')
      const res = await request.get('/api/inventory/alerts', { params: { threshold: 0 } })
      const alerts = res?.data?.results || res?.data || []
      if (alerts.length === 0) return '📊 当前库存状态良好，无预警商品。'
      const lines = alerts.slice(0, 5).map((a, i) => `- ${i === 0 ? '⚠️' : '·'} ${a.name || a.sku} 库存 ${a.stock} 件`)
      return `📊 库存预警（共${alerts.length}个）：\n${lines.join('\n')}\n\n[查看库存管理 →](/inventory)`
    } catch {
      return '📊 无法获取实时库存数据，请检查网络后重试。[查看库存管理 →](/inventory)'
    }
  }

  if (/日报|周报|report/.test(t)) {
    return '📈 经营日报功能可通过「数据报表」页面查看实时数据。[查看报表 →](/reports)'
  }

  if (/hello|你好|hi|嗨/.test(t)) {
    return '👋 你好！我是小辽，你的跨境电商AI助手。有什么我可以帮你的吗？'
  }

  return `收到！我是小辽，目前支持：\n✨ AI生成商品标题/描述（商品上货页）\n📦 订单查询\n📊 库存预警分析\n📈 数据报表查看\n\n请告诉我你想做什么？`
}

// ── Markdown 简化渲染 ─────────────────────────────────────
function renderMarkdown(text) {
  if (!text) return ''
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank">$1</a>')
    .replace(/^#{1,3} (.+)$/gm, '<strong>$&</strong>')
    .replace(/\n/g, '<br/>')
}

function quickAsk(text) {
  inputText.value = text
  send()
}

// ── 动作执行 ──────────────────────────────────────────────
function doAction(action) {
  if (action.action === 'navigate') router.push(action.path)
  else if (action.action === 'auto-replenish') router.push('/inventory?mode=replenish')
  else if (action.action === 'generate-report') router.push('/reports?type=daily')
}

function doTipAction(tip) {
  doAction({ action: tip.action })
}

// ── UI 操作 ──────────────────────────────────────────────
function openChat() {
  if (wasDragged.value) return
  isOpen.value = true
  unreadCount.value = 0
}

function minimize() {
  isOpen.value = false
}

function closeChat() {
  isOpen.value = false
}

function scrollBottom() {
  if (bodyRef.value) bodyRef.value.scrollTop = bodyRef.value.scrollHeight
}

// ── 扫码枪事件监听 ────────────────────────────────────────
onMounted(() => {
  window.addEventListener('global:scan', (e) => {
    const { barcode } = e.detail || {}
    if (barcode) {
      unreadCount.value++
      if (isOpen.value) {
        messages.value.push({
          id: Date.now(), role: 'assistant',
          content: `🔫 扫码枪识别到条码：${barcode}，正在匹配商品...`,
        })
        nextTick(scrollBottom)
      }
    }
  })
})
</script>

<style scoped>
/* 外层容器：可定位浮层 */
.tiger-assistant {
  position: fixed;
  z-index: 9999;
  cursor: default;
}

/* ── 悬浮按钮（大号老虎头像）───────────────────────────── */
.tiger-fab {
  width: auto;
  height: auto;
  background: transparent;
  box-shadow: none;
  display: inline-block;
  cursor: grab;
  position: relative;
  animation: fab-float 3s ease-in-out infinite;
  transition: transform 0.2s;
  user-select: none;
}

.tiger-fab:hover {
  transform: scale(1.08);
}

.tiger-avatar {
  width: auto;
  height: auto;
  max-width: 120px;
  max-height: 120px;
  object-fit: contain;
  display: block;
  /* 金色外轮廓 - drop-shadow 跟随图片实际形状 */
  filter: drop-shadow(0 0 4px #f5a623)
          drop-shadow(0 0 10px rgba(245, 166, 35, 0.6))
          drop-shadow(0 0 20px rgba(245, 166, 35, 0.35));
  transition: filter 0.3s ease;
}

.tiger-fab:hover .tiger-avatar {
  filter: drop-shadow(0 0 5px #f7c948)
          drop-shadow(0 0 14px rgba(247, 201, 72, 0.7))
          drop-shadow(0 0 28px rgba(247, 201, 72, 0.4));
}

.unread-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  background: #f56c6c;
  color: white;
  font-size: 11px;
  font-weight: bold;
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  border: 2px solid white;
}

.drag-handle {
  position: absolute;
  bottom: -4px;
  right: -4px;
  width: 20px;
  height: 20px;
  background: linear-gradient(135deg, #f5a623, #f7c948);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 2px 6px rgba(245,166,35,0.5), 0 1px 3px rgba(0,0,0,0.2);
  cursor: grab;
  opacity: 0;
  transition: opacity 0.2s, transform 0.2s;
  font-size: 10px;
}

.tiger-fab:hover .drag-handle {
  opacity: 1;
  transform: scale(1.1);
}

@keyframes fab-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

/* ── 大对话窗口 ─────────────────────────────────────────── */
.tiger-window {
  width: 420px;
  max-height: 620px;
  background: var(--el-bg-color, #fff);
  border-radius: 20px;
  box-shadow: 0 16px 60px rgba(0,0,0,0.18), 0 4px 16px rgba(0,0,0,0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: absolute;
  bottom: 84px;
  right: 0;
  border: 1px solid rgba(245, 166, 35, 0.3);
  resize: none;
}

/* ── 标题栏 ────────────────────────────────────────────── */
.tiger-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  background: linear-gradient(135deg, #f5a623, #f7c948);
  color: white;
  cursor: grab;
  user-select: none;
}

.tiger-header:active { cursor: grabbing; }

.header-avatar {
  position: relative;
  flex-shrink: 0;
}

.header-mascot {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  object-fit: contain;
}

.online-dot {
  position: absolute;
  bottom: 1px;
  right: 1px;
  width: 10px;
  height: 10px;
  background: #67c23a;
  border-radius: 50%;
  border: 2px solid white;
}

.header-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.header-name { font-size: 16px; font-weight: 700; }
.header-sub { font-size: 11px; opacity: 0.85; }

.header-controls {
  display: flex;
  gap: 2px;
}

.header-controls .el-button {
  color: white;
  opacity: 0.8;
  background: transparent;
}

.header-controls .el-button:hover {
  opacity: 1;
  background: rgba(255,255,255,0.2);
}

/* ── 上下文提示 ─────────────────────────────────────────── */
.context-tips {
  padding: 8px 12px;
  background: #fff8ed;
  border-bottom: 1px solid #fdf0d5;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tip-chip {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  padding: 4px 6px;
  border-radius: 6px;
}

.tip-info { color: #e6a23c; background: #fdf6ec; }
.tip-warning { color: #f56c6c; background: #fef0f0; }
.tip-success { color: #67c23a; background: #f0f9eb; }
.tip-chip span { flex: 1; }

/* ── 欢迎页 ────────────────────────────────────────────── */
.welcome-screen {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 24px;
  gap: 12px;
}

.welcome-img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: contain;
  box-shadow: 0 4px 16px rgba(245,166,35,0.3);
}

.welcome-greet { font-size: 20px; font-weight: 700; color: #333; }
.welcome-sub { font-size: 13px; color: #999; }

.quick-prompts { width: 100%; margin-top: 8px; }
.quick-title { font-size: 12px; color: #999; margin-bottom: 8px; text-align: center; }
.quick-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.quick-btn {
  background: #fff;
  border: 1px solid #f0e6d3;
  border-radius: 10px;
  padding: 10px 8px;
  font-size: 12px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  white-space: nowrap;
}

.quick-btn:hover {
  background: linear-gradient(135deg, #f5a623, #f7c948);
  color: white;
  border-color: transparent;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245,166,35,0.3);
}

/* ── 消息区域 ──────────────────────────────────────────── */
.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 340px;
  scroll-behavior: smooth;
}

.msg-row {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.msg-row.user {
  flex-direction: row-reverse;
}

.msg-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
}

.msg-avatar img { width: 100%; height: 100%; object-fit: contain; }
.msg-row.user .msg-avatar { background: #f5a623; color: white; }

.msg-bubble { max-width: 78%; }

.msg-text {
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 13px;
  line-height: 1.6;
  word-break: break-word;
}

.msg-row.assistant .msg-text {
  background: #f5f5f5;
  color: #333;
  border-bottom-left-radius: 4px;
}

.msg-row.user .msg-text {
  background: linear-gradient(135deg, #f5a623, #f7c948);
  color: white;
  border-bottom-right-radius: 4px;
}

.msg-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
}

/* ── 思考动画 ──────────────────────────────────────────── */
.thinking-bars {
  display: flex;
  gap: 4px;
  padding: 4px;
}

.thinking-bars span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #f5a623;
  animation: bounce-dot 1.2s ease-in-out infinite;
}

.thinking-bars span:nth-child(2) { animation-delay: 0.2s; }
.thinking-bars span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce-dot {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

/* ── 输入区 ────────────────────────────────────────────── */
.chat-footer {
  padding: 12px 16px 16px;
  border-top: 1px solid #f0f0f0;
  background: white;
}

.input-row {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.input-row :deep(.el-textarea__inner) {
  border-radius: 14px;
  padding: 10px 14px;
  font-size: 13px;
  line-height: 1.5;
}

.send-btn {
  border-radius: 14px;
  padding: 8px 16px;
  height: 42px;
  background: linear-gradient(135deg, #f5a623, #f7c948) !important;
  border: none !important;
  color: white !important;
  font-weight: 600;
  flex-shrink: 0;
  white-space: nowrap;
}

.send-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #e6951a, #f5a623) !important;
}

.input-hint {
  font-size: 11px;
  color: #ccc;
  margin-top: 5px;
  text-align: center;
}

/* ── 过渡动画 ──────────────────────────────────────────── */
.pop-enter-active, .pop-leave-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.pop-enter-from, .pop-leave-to {
  opacity: 0;
  transform: scale(0.8) translateY(20px);
}
</style>
