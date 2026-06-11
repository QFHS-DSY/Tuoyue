<template>
  <Teleport to="body">
    <Transition name="browser-slide">
      <div v-if="visible" class="platform-browser-overlay"
        @click.self="handleCloseOverlay"
        @dragover.prevent="onGlobalDragOver"
        @dragleave="onGlobalDragLeave"
        @drop.prevent="onGlobalDrop"
      >
        <!-- 跨窗口拖拽提示蒙层 -->
        <Transition name="indicator-fade">
          <div v-if="globalDragActive" class="global-drop-zone">
            <div class="drop-zone-content">
              <el-icon :size="48"><Download /></el-icon>
              <div class="drop-zone-title">松开鼠标采集商品</div>
              <div class="drop-zone-sub">从 1688 / 淘宝 / 拼多多 窗口拖拽商品到此区域</div>
            </div>
          </div>
        </Transition>

        <div class="platform-browser">
          <!-- 标签栏 -->
          <div class="browser-toolbar">
            <div class="toolbar-left">
              <div class="platform-logo">
                <span class="logo-text">🖥️ 平台浏览器</span>
              </div>
            </div>

            <div class="browser-tabs">
              <div
                v-for="tab in tabs"
                :key="tab.id"
                :class="['browser-tab', {
                  active: tab.id === activeTabId,
                  'is-source': isSourcePlatform(tab.platformKey),
                }]"
                @click="switchTab(tab.id)"
                @dragover.prevent="onDragOverTab(tab)"
                @dragleave="onDragLeaveTab(tab)"
                @drop="onDropExternal($event, tab)"
              >
                <span class="tab-platform-badge" :class="getPlatformIconClass(tab.platformKey)">
                  {{ getPlatformBadge(tab.platformKey) }}
                </span>
                <span class="tab-title">{{ tab.shopName || getPlatformName(tab.platformKey) }}</span>
                <span v-if="isSourcePlatform(tab.platformKey)" class="tab-source-badge">货源</span>
                <el-icon class="tab-close" @click.stop="closeTab(tab.id)"><Close /></el-icon>
              </div>
            </div>

            <div class="toolbar-right">
              <!-- 注入采集脚本按钮（仅货源平台显示） -->
              <el-tooltip v-if="currentTab && isSourcePlatform(currentTab.platformKey)" content="注入采集脚本，自动识别页面商品" placement="bottom">
                <el-button text size="small" type="primary" @click="injectCollectionScript">
                  <el-icon><MagicStick /></el-icon>
                  采集模式
                </el-button>
              </el-tooltip>
              <el-button text size="small" @click="handleMinimize">
                <el-icon><Minus /></el-icon>
              </el-button>
              <el-button text size="small" type="danger" @click="handleClose">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
          </div>

          <!-- ====== 采集面板 ====== -->
          <div v-if="collectedItems.length > 0" class="collect-panel">
            <div class="collect-panel-left">
              <el-tag type="success" size="small">
                <el-icon><CircleCheck /></el-icon>
                已采集 {{ collectedCount }}
              </el-tag>
              <el-tag v-if="selectedIds.length > 0" type="primary" size="small" style="margin-left:8px">
                已选 {{ selectedIds.length }}
              </el-tag>
            </div>
            <div class="collect-panel-right">
              <el-button size="small" :disabled="selectedIds.length === 0"
                @click="exportCollected('xlsx')">
                <el-icon><Download /></el-icon> 导出Excel
              </el-button>
              <el-button size="small" :disabled="selectedIds.length === 0"
                @click="exportCollected('csv')">
                <el-icon><List /></el-icon> 导出CSV
              </el-button>
              <el-button size="small" type="primary" @click="batchAddToOnestop">
                <el-icon><Upload /></el-icon> 推送到一站式
              </el-button>
              <el-divider direction="vertical" />
              <el-button size="small" type="info" text @click="toggleSelectAll">
                {{ isAllSelected ? '取消全选' : '全选' }}
              </el-button>
              <el-button size="small" type="danger" text @click="clearCollected">清空</el-button>
            </div>
          </div>

          <!-- 快速粘贴 URL 输入栏（货源平台显示）-->
          <div v-if="currentTab && isSourcePlatform(currentTab.platformKey)" class="quick-url-bar">
            <el-input
              v-model="quickUrl"
              size="small"
              placeholder="在此粘贴商品链接，回车一键采集..."
              clearable
              class="quick-url-input"
              @keyup.enter="quickScrapeUrl"
            >
              <template #prefix>
                <el-icon><Link /></el-icon>
              </template>
              <template #append>
                <el-button size="small" type="primary" :loading="quickScraping" @click="quickScrapeUrl">
                  一键采集
                </el-button>
              </template>
            </el-input>
          </div>

          <!-- 拖拽悬浮提示（货源平台拖拽采集） -->
          <Transition name="indicator-fade">
            <div v-if="isDraggingExternal" class="drag-indicator">
              <div class="indicator-inner">
                <el-icon><Aim /></el-icon>
                <span>检测到货源商品 → 放开即采集至一站式上货</span>
              </div>
            </div>
          </Transition>

          <!-- iframe容器 -->
          <div class="browser-content" ref="browserContent">
            <div v-if="tabs.length === 0" class="empty-browser">
              <img src="@/assets/logo.png" class="empty-logo" alt="logo" />
              <p class="empty-title">平台浏览器</p>
              <p class="empty-desc">
                打开货源平台（1688/淘宝）时<br/>
                拖拽商品卡片即可自动采集上货
              </p>
              <div class="empty-platforms">
                <span class="ep-label">支持的货源平台：</span>
                <el-tag size="small" effect="plain">1688</el-tag>
                <el-tag size="small" effect="plain">淘宝</el-tag>
                <el-tag size="small" effect="plain" type="info">拼多多</el-tag>
                <el-tag size="small" effect="plain" type="info">天猫</el-tag>
              </div>
              <div class="empty-actions">
                <el-button size="small" type="primary" @click="openSourcePlatform('1688')">
                  <el-icon><Shop /></el-icon> 打开1688
                </el-button>
                <el-button size="small" type="success" @click="openSourcePlatform('pdd')">
                  <el-icon><Present /></el-icon> 打开拼多多
                </el-button>
                <el-button size="small" @click="openSourcePlatform('taobao')">
                  打开淘宝
                </el-button>
              </div>
            </div>

            <iframe
              v-for="tab in tabs"
              v-show="tab.id === activeTabId && !tab.loading"
              :key="tab.id"
              :src="tab.url"
              :ref="el => iframeRefs[tab.id] = el"
              class="platform-iframe"
              :class="{ 'source-platform': isSourcePlatform(tab.platformKey) }"
              sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-top-navigation"
              @load="handleIframeLoad(tab.id)"
            />

            <!-- 加载状态 -->
            <div v-if="currentTab?.loading" class="iframe-loading">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>正在加载页面...</span>
            </div>
          </div>

          <!-- 拖拽采集确认悬浮卡（当 iframe 内拖拽时显示在标签上） -->
          <Transition name="float-fade">
            <div v-if="draggedExternalGoods" class="drop-float-card">
              <div class="float-card-header">
                <el-icon><Goods /></el-icon>
                检测到商品
                <el-tag size="small" type="success">可采集</el-tag>
              </div>
              <div class="float-card-body">
                <div class="float-goods-name">{{ draggedExternalGoods.name || draggedExternalGoods.title || '商品' }}</div>
                <div class="float-goods-price" v-if="draggedExternalGoods.price">
                  ¥{{ draggedExternalGoods.price }}
                </div>
              </div>
              <div class="float-card-actions">
                <el-button type="primary" size="small" @click="confirmExternalCollect">
                  <el-icon><Upload /></el-icon>
                  采集并上货
                </el-button>
                <el-button size="small" @click="draggedExternalGoods = null">
                  取消
                </el-button>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, reactive, watch, nextTick } from 'vue'
import { Close, Minus, Upload, Loading, MagicStick, Aim, Goods,
  CircleCheck, Download, List, Link, Shop, Present
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { collect1688Single } from '@/api/collect'
import { getCollectScript } from '@/utils/collectInjection'

// ── State ──────────────────────────────────────────────────
const visible = ref(false)
const tabs = ref([])
const activeTabId = ref(null)
const iframeRefs = reactive({})
const isDragOverAny = ref(false)
const isDraggingExternal = ref(false)   // 货源平台拖拽状态
const draggedExternalGoods = ref(null)   // 外部拖拽的商品数据
const globalDragActive = ref(false)      // 跨窗口拖拽激活
const globalDragCounter = ref(0)         // 嵌套 dragenter/leave 计数器
let tabIdCounter = 0

// ── 一键采集面板状态 ──
const quickUrl = ref('')
const quickScraping = ref(false)
const collectedItems = ref([])          // 已采集商品 [{ id, title, price, ... }]
const selectedIds = ref([])             // 勾选的商品ID集合
const collectedCount = computed(() => collectedItems.value.length)
const isAllSelected = computed(() =>
  collectedItems.value.length > 0 && selectedIds.value.length === collectedItems.value.length
)

// ── Computed ───────────────────────────────────────────────
const currentTab = computed(() => tabs.value.find(t => t.id === activeTabId.value))

// ── 货源平台判断 ──────────────────────────────────────────────
// 1688、淘宝等为货源平台，希音、Temu等既是货源也可上架
const SOURCE_PLATFORMS = ['1688', 'taobao', 'pdd', 'tmall']
const SELL_PLATFORMS = ['shopee', 'tiktok', 'temu', 'shein', 'aliexpress', 'amazon', 'ebay', 'lazada', 'wish', 'mercado', 'ozon', 'allegro']

function isSourcePlatform(platformKey) {
  return SOURCE_PLATFORMS.includes(platformKey) ||
    (platformKey && (platformKey.includes('1688') || platformKey.includes('taobao') || platformKey.includes('pinduoduo')))
}

// ── 快捷打开货源平台 ──
const SOURCE_PLATFORM_DIRECT_URLS = {
  '1688': 'https://detail.1688.com/offer/629584739214.html',
  'pdd': 'https://mobile.yangkeduo.com/search_result.html?search_key=蓝牙耳机',
  'taobao': 'https://world.taobao.com/',
}

function openSourcePlatform(key) {
  const directUrl = SOURCE_PLATFORM_DIRECT_URLS[key]
  if (!directUrl) return
  // 货源平台（1688/淘宝/拼多多）禁止 iframe 嵌入
  // 改为新窗口打开，通过全局拖拽区域跨窗口采集商品
  window.open(directUrl, '_blank')
  ElMessage.info('已在新窗口打开 ' + (key === '1688' ? '1688' : key === 'taobao' ? '淘宝' : '拼多多') + '，拖拽商品到弹窗中央区域即可采集')
}

// ── 平台URL映射 ────────────────────────────────────────────
const PLATFORM_URLS = {
  shopee: 'https://seller.shopee.cn/portal/home',
  temu: 'https://seller.temu.com/portal',
  shein: "https://seller.shein.com/portal/home",
  tiktok: 'https://seller.tiktok.com/portal/home',
  aliexpress: 'https://sell.aliexpress.com',
  amazon: 'https://sellercentral.amazon.com',
  ebay: 'https://www.ebay.com/sh/lst/manage',
  lazada: 'https://center.lazada.com',
}

// ── 平台图标（CSS文字徽章替代SVG）──
function getPlatformIcon(key) {
  // 不依赖外部SVG文件，直接返回null，模板用文字徽章
  return ''
}

function getPlatformIconClass(key) {
  const classes = {
    '1688': 'pi-1688', taobao: 'pi-tb', pdd: 'pi-pdd',
    shopee: 'pi-sp', tiktok: 'pi-tt', temu: 'pi-tm',
    amazon: 'pi-amz',
  }
  return classes[key] || ''
}

function getPlatformBadge(key) {
  const badges = {
    '1688': '阿', taobao: '淘', pdd: '拼', tmall: '猫',
    shopee: '虾', tiktok: 'TT', temu: 'TM', shein: 'S',
    amazon: 'A', ebay: 'eB', lazada: 'LZ',
  }
  return badges[key] || key?.slice(0, 2)?.toUpperCase() || '?'
}

function getPlatformName(key) {
  const names = {
    shopee: 'Shopee', temu: 'Temu', shein: '希音',
    tiktok: 'TikTok', aliexpress: '速卖通', amazon: 'Amazon',
    ebay: 'eBay', lazada: 'Lazada', wish: 'Wish', mercado: 'Mercado'
  }
  return names[key] || key
}

// ── Tab操作 ─────────────────────────────────────────────────
function openTab({ platformKey, shopId, shopName, url, authToken }) {
  const id = ++tabIdCounter
  const rawUrl = url || PLATFORM_URLS[platformKey] || `https://www.${platformKey}.com`

  // 货源平台（1688/淘宝/拼多多）禁止 iframe 嵌入，打开新窗口
  if (isSourcePlatform(platformKey)) {
    window.open(rawUrl, '_blank')
    ElMessage.info('货源平台已在新窗口打开')
    return id
  }

  const tab = {
    id,
    platformKey,
    shopId,
    shopName,
    url: rawUrl,
    authToken,
    loading: true,
  }

  tabs.value.push(tab)
  activeTabId.value = id
  visible.value = true

  // 通过 postMessage 注入授权信息
  nextTick(() => {
    setTimeout(() => {
      injectAuthToken(tab)
    }, 2000)  // 等待 iframe 加载完成
  })
}

function closeTab(id) {
  const index = tabs.value.findIndex(t => t.id === id)
  if (index === -1) return

  tabs.value.splice(index, 1)

  if (activeTabId.value === id) {
    activeTabId.value = tabs.value.length > 0 ? tabs.value[tabs.value.length - 1].id : null
  }

  if (tabs.value.length === 0) {
    visible.value = false
  }
}

function switchTab(id) {
  activeTabId.value = id
  emit('tab-change', currentTab.value)
}

function handleIframeLoad(tabId) {
  const tab = tabs.value.find(t => t.id === tabId)
  if (tab) tab.loading = false

  // 加载完成后注入授权
  nextTick(() => {
    injectAuthToken(tab)
  })
}

// ── 授权注入 ───────────────────────────────────────────────
function injectAuthToken(tab) {
  if (!tab?.authToken || !iframeRefs[tab.id]) return
  try {
    iframeRefs[tab.id].contentWindow?.postMessage({
      type: 'AUTH_TOKEN',
      token: tab.authToken,
    }, '*')
  } catch (e) {
    // 跨域限制无法注入，属正常
  }
}

// ── 拖拽处理（标签页级）───────────────────────────────────────
function onDragOverTab(tab) {
  if (isSourcePlatform(tab.platformKey)) {
    isDraggingExternal.value = true
  }
  isDragOverAny.value = true
}

function onDragLeaveTab(tab) {
  if (isSourcePlatform(tab.platformKey)) {
    // 简单处理：如果离开当前标签，则清除拖拽状态
    // 实际应用中可维护一个 Set 来精确跟踪每个 tab 的状态
    if (activeTabId.value === tab.id) {
      // 仍在当前活动标签内，不清除
    }
  }
  isDragOverAny.value = false
}

/**
 * 处理来自货源平台的外部拖拽（模式2核心）
 * 用户在内置浏览器中拖拽1688/淘宝商品时触发
 */
function onDropExternal(e, tab) {
  isDraggingExternal.value = false
  isDragOverAny.value = false

  if (!isSourcePlatform(tab.platformKey)) {
    // 非货源平台：走原有上货逻辑（内部商品拖拽）
    onDropInternal(e, tab)
    return
  }

  // 货源平台：尝试从 iframe 获取商品数据
  // 由于跨域限制，尝试通过 postMessage 从 iframe 获取数据
  try {
    // 向 iframe 发送采集请求
    iframeRefs[tab.id]?.contentWindow?.postMessage({
      type: 'ONESTOP_REQUEST_PRODUCT',
      tabId: tab.id,
      platformKey: tab.platformKey,
    }, '*')
  } catch (err) {
    // 跨域无法通信，显示手动提示
    ElMessage.info('由于跨域限制，请点击「采集模式」按钮启用自动采集，或使用一站式页面的粘贴链接功能')
  }
}

/**
 * 处理内部商品卡片的拖拽（原有逻辑）
 */
function onDropInternal(e, tab) {
  try {
    const jsonData = e.dataTransfer.getData('application/json')
    if (!jsonData) {
      ElMessage.warning('无法识别拖拽的数据格式')
      return
    }

    const payload = JSON.parse(jsonData)
    if (payload.type !== 'goods') {
      ElMessage.warning('仅支持拖拽商品卡片')
      return
    }

    // 触发上货确认
    emit('goods-dropped', {
      goods: payload.data,
      targetTab: tab,
    })

  } catch (err) {
    console.error('[PlatformBrowser] 解析拖拽数据失败:', err)
    ElMessage.error('数据解析失败')
  }
}

/**
 * 确认从外部采集商品，触发一站式上货流程
 */
function confirmExternalCollect() {
  if (!draggedExternalGoods.value) return
  emit('external-collect', {
    goods: draggedExternalGoods.value,
    platformKey: currentTab.value?.platformKey,
  })
  draggedExternalGoods.value = null
  ElMessage.success('已发送至一站式采集上货流程')
}

// ── 跨窗口拖拽（全局 Drop 区）──────────
function onGlobalDragOver() {
  globalDragActive.value = true
}

function onGlobalDragLeave() {
  globalDragActive.value = false
}

async function onGlobalDrop(e) {
  globalDragActive.value = false

  // 1. 尝试读取 JSON 数据（代理页面注入的标准化数据）
  try {
    const jsonStr = e.dataTransfer.getData('application/json')
    if (jsonStr) {
      const product = JSON.parse(jsonStr)
      if (product.title && product.sourceUrl) {
        awaitedDropProduct(product)
        return
      }
    }
  } catch (_) { /* fall through */ }

  // 2. 尝试读取 URL（从浏览器地址栏拖拽或链接拖拽）
  const uriList = e.dataTransfer.getData('text/uri-list') || e.dataTransfer.getData('URL')
  if (uriList) {
    var urls = uriList.split('\n').map(function(s) { return s.trim() }).filter(function(u) { return u })
    if (urls.length > 0) {
      await quickScrapeUrlFromDrop(urls[0])
      return
    }
  }

  // 3. 从纯文本中尝试提取 URL
  var plain = e.dataTransfer.getData('text/plain') || ''
  var httpIdx = plain.indexOf('http')
  if (httpIdx !== -1) {
    var spaceIdx = plain.indexOf(' ', httpIdx)
    var newlineIdx = plain.indexOf('\n', httpIdx)
    var endIdx = spaceIdx === -1 ? plain.length : spaceIdx
    if (newlineIdx !== -1 && newlineIdx < endIdx) endIdx = newlineIdx
    var extractedUrl = plain.slice(httpIdx, endIdx).trim()
    if (extractedUrl) {
      await quickScrapeUrlFromDrop(extractedUrl)
      return
    }
  }

  // 4. 从 HTML 中提取链接
  const html = e.dataTransfer.getData('text/html') || ''
  if (html) {
    // 用 indexOf 替代正则，避免 Vue SFC 解析冲突
    let idx = html.indexOf('href=')
    while (idx !== -1) {
      var rest = html.slice(idx + 5)
      var quote = rest.charAt(0)
      if (quote === "'" || quote === '"') {
        rest = rest.slice(1)
        var end = rest.indexOf(quote)
        if (end > 0) {
          var found = rest.slice(0, end)
          if (found.startsWith('http')) {
            await quickScrapeUrlFromDrop(found)
            return
          }
        }
      }
      idx = html.indexOf('href=', idx + 1)
    }
  }

  ElMessage.warning('未能识别拖拽内容，请尝试从商品页面拖拽链接或图片')
}

async function quickScrapeUrlFromDrop(url) {
  quickUrl.value = url
  await quickScrapeUrl()
}

async function awaitedDropProduct(product) {
  draggedExternalGoods.value = product
  const item = {
    id: Date.now(),
    title: product.title || product.name,
    price: product.price || 0,
    images: product.images || [],
    platform: product.platform || currentTab.value?.platformKey || '1688',
    sourceUrl: product.sourceUrl || '',
    _time: new Date().toLocaleTimeString(),
  }
  collectedItems.value.unshift(item)
  selectedIds.value.push(item.id)
  ElMessage.success(`${item.title.substring(0, 25)}... 已捕获`)
}

/**
 * 注入采集脚本到 iframe
 * 用于在货源平台页面自动识别商品 DOM 并采集数据
 */
function injectCollectionScript() {
  const tab = currentTab.value
  if (!tab || !iframeRefs[tab.id]) {
    ElMessage.warning('请先打开货源平台页面')
    return
  }

  try {
    const collectScript = getCollectScript(tab.platformKey)
    iframeRefs[tab.id].contentWindow?.postMessage({
      type: 'ONESTOP_INJECT_SCRIPT',
      script: collectScript,
    }, '*')
    ElMessage.success('采集脚本已注入，请在货源页面拖拽商品卡片')
  } catch (err) {
    ElMessage.warning('注入采集脚本失败，请尝试使用粘贴链接方式')
  }
}

// ── 浏览器控制 ──────────────────────────────────────────────
function handleMinimize() {
  visible.value = false
}

function handleClose() {
  tabs.value = []
  activeTabId.value = null
  visible.value = false
  emit('close')
}

function handleCloseOverlay() {
  // 点击遮罩层最小化而非关闭
  visible.value = false
}

// ── 监听跨窗口 postMessage ──────────────────────────────────
function setupPostMessageListener() {
  window.addEventListener('message', (e) => {
    const { type, url, platformKey, product, tabId } = e.data || {}

    if (type === 'OPEN_PLATFORM') {
      // 收到来自页面组件的请求，自动打开标签页
      openTab({ platformKey, url })
    }

    if (type === 'ONESTOP_COLLECT_PRODUCT') {
      // 收到 iframe 内采集脚本发来的商品数据（模式2核心）
      if (product) {
        draggedExternalGoods.value = product
        // 找到对应的 tab
        if (tabId) {
          switchTab(tabId)
        }
      }
    }

    if (type === 'ONESTOP_SCRIPT_READY') {
      ElMessage.success(`采集脚本已在 ${getPlatformName(platformKey)} 就绪，拖拽商品即可采集`)
    }
  })
}

setupPostMessageListener()

// ── 一键采集：快速抓取粘贴的URL ─────────────────────────
async function quickScrapeUrl() {
  const url = quickUrl.value.trim()
  if (!url) return
  quickScraping.value = true
  try {
    const res = await collect1688Single({ url })
    const data = res?.data || res
    const item = {
      id: data?.id || Date.now(),
      title: data?.title || '未知商品',
      price: data?.price || 0,
      images: data?.images || [],
      platform: data?.platform || currentTab.value?.platformKey || '1688',
      sourceUrl: url,
      _time: new Date().toLocaleTimeString(),
    }
    collectedItems.value.unshift(item)
    selectedIds.value.push(item.id)
    quickUrl.value = ''
    ElMessage.success(`采集成功: ${item.title.substring(0, 30)}...`)
  } catch {
    ElMessage.error('采集失败，请检查链接是否有效')
  } finally {
    quickScraping.value = false
  }
}

// ── 批量添加采集结果到一站式 ──
function batchAddToOnestop() {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先勾选商品')
    return
  }
  const selected = collectedItems.value.filter(i => selectedIds.value.includes(i.id))
  selected.forEach(item => {
    emit('external-collect', {
      goods: {
        name: item.title,
        title: item.title,
        price: item.price,
        images: item.images,
        sourceUrl: item.sourceUrl,
        platform: item.platform,
      },
      platformKey: item.platform,
    })
  })
  ElMessage.success(`已推送 ${selected.length} 个商品到一站式`)
}

// ── 导出 Excel/CSV ──
async function exportCollected(fmt) {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先勾选商品')
    return
  }
  try {
    const productIds = selectedIds.value
    const resp = await request.post('/api/v1/collect/export/', {
      product_ids: productIds,
      format: fmt,
    }, { responseType: 'blob' })

    const blob = resp instanceof Blob ? resp : new Blob([resp], {
      type: fmt === 'csv' ? 'text/csv' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = fmt === 'csv' ? '采集商品.csv' : '采集商品.xlsx'
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success(`已导出 ${productIds.length} 条数据`)
  } catch {
    ElMessage.error('导出失败')
  }
}

// ── 选择操作 ──
function toggleSelectAll() {
  if (isAllSelected.value) {
    selectedIds.value = []
  } else {
    selectedIds.value = collectedItems.value.map(i => i.id)
  }
}

function clearCollected() {
  collectedItems.value = []
  selectedIds.value = []
  ElMessage.info('已清空采集列表')
}

// ── 声明组件对外发射的事件（消除 Vue "Extraneous non-emits event listeners" 警告）
const emit = defineEmits(['tab-change', 'goods-dropped', 'external-collect', 'close'])

// ── 暴露方法给外部调用 ─────────────────────────────────────
defineExpose({
  openTab,
  closeTab,
  minimize: handleMinimize,
  show: () => { visible.value = true },
  hide: () => { visible.value = false },
  isSourcePlatform,  // 暴露货源判断函数
})
</script>

<style scoped>
.platform-browser-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 9000;
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
}

.platform-browser {
  width: 85vw;
  height: 80vh;
  background: #fff;
  border-radius: 12px 12px 0 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.15);
}

/* 工具栏 */
.browser-toolbar {
  display: flex;
  align-items: center;
  height: 44px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
  padding: 0 8px;
  gap: 8px;
  flex-shrink: 0;
}

.toolbar-left {
  flex-shrink: 0;
}

.logo-text {
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  white-space: nowrap;
}

/* 标签栏 */
.browser-tabs {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 2px;
  overflow-x: auto;
  min-width: 0;
}

.browser-tabs::-webkit-scrollbar {
  height: 0;
}

.browser-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 6px 6px 0 0;
  cursor: pointer;
  font-size: 12px;
  white-space: nowrap;
  background: #e8e8e8;
  color: var(--el-text-color-secondary);
  transition: all 0.15s;
  max-width: 180px;
  position: relative;
}

.browser-tab:hover {
  background: #d8d8d8;
}

.browser-tab.active {
  background: #fff;
  color: var(--el-text-color-primary);
  font-weight: 600;
  box-shadow: 0 -1px 0 #fff;
}

.browser-tab.drag-over {
  background: var(--el-color-primary-light-9);
  border: 2px dashed var(--el-color-primary);
}

.tab-platform-icon {
  width: 16px;
  height: 16px;
  border-radius: 2px;
  flex-shrink: 0;
}

/* 平台文字徽章 */
.tab-platform-badge {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #fff;
}
.pi-1688 { background: #ff6a00; }
.pi-tb   { background: #ff5000; }
.pi-pdd  { background: #e53e30; }
.pi-sp   { background: #ee4d2d; }
.pi-tt   { background: #000; }
.pi-tm   { background: #fb7701; }
.pi-amz  { background: #ff9900; }

.tab-title {
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.tab-close {
  font-size: 11px;
  opacity: 0.6;
  flex-shrink: 0;
}

.tab-close:hover {
  opacity: 1;
  color: #f56c6c;
}

.toolbar-right {
  display: flex;
  gap: 2px;
  flex-shrink: 0;
}

/* 拖拽指示器 */
.drag-indicator {
  position: absolute;
  top: 44px;
  left: 0;
  right: 0;
  height: 48px;
  background: var(--el-color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  pointer-events: none;
}

.indicator-inner {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
}

/* 内容区 */
.browser-content {
  flex: 1;
  position: relative;
  background: #f0f0f0;
  overflow: hidden;
}

.platform-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background: #fff;
}

.iframe-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
  background: rgba(255,255,255,0.9);
}

.empty-browser {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

.empty-logo {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  opacity: 0.6;
}

.empty-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  margin: 0;
}

.empty-desc {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  text-align: center;
  margin: 0;
  line-height: 1.6;
}

.empty-platforms {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
}
.ep-label { font-size: 12px; color: var(--text-muted); }
.empty-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

/* 货源平台标签 */
.tab-source-badge {
  font-size: 9px;
  background: #22c55e;
  color: white;
  padding: 1px 5px;
  border-radius: 8px;
  font-weight: 700;
  flex-shrink: 0;
}

/* 货源平台 iframe */
.platform-iframe.source-platform {
  border-top: 3px solid #22c55e;
}

/* 拖拽指示器动画 */
.indicator-fade-enter-active, .indicator-fade-leave-active {
  transition: opacity 0.2s ease;
}
.indicator-fade-enter-from, .indicator-fade-leave-to {
  opacity: 0;
}

/* 拖拽采集确认悬浮卡 */
.drop-float-card {
  position: absolute;
  bottom: 20px;
  right: 20px;
  width: 260px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,.15);
  border: 2px solid #22c55e;
  z-index: 100;
  overflow: hidden;
}

.float-card-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 14px 8px;
  font-size: 13px;
  font-weight: 700;
  color: #166534;
  background: rgba(34,197,94,.06);
}

.float-card-body {
  padding: 8px 14px;
}

.float-goods-name {
  font-size: 13px;
  color: var(--el-text-color-primary);
  font-weight: 500;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.float-goods-price {
  font-size: 16px;
  font-weight: 700;
  color: #ef4444;
}

.float-card-actions {
  display: flex;
  gap: 8px;
  padding: 8px 14px 12px;
}

.float-fade-enter-active, .float-fade-leave-active {
  transition: all 0.3s ease;
}
.float-fade-enter-from, .float-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* 动画 */

.browser-slide-enter-active,
.browser-slide-leave-active {
  transition: opacity 0.3s ease;
}

.browser-slide-enter-from,
.browser-slide-leave-to {
  opacity: 0;
}

/* ====== 采集面板 ====== */
.collect-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 40px;
  padding: 0 12px;
  background: linear-gradient(135deg, #f0faf4 0%, #ecfdf5 100%);
  border-bottom: 1px solid #bbf7d0;
  flex-shrink: 0;
  gap: 8px;
}
.collect-panel-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.collect-panel-right {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* ====== 快速URL输入栏 ====== */
.quick-url-bar {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  background: #fafafa;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}
.quick-url-input {
  flex: 1;
}

/* ====== 跨窗口 Drop 区 ====== */
.global-drop-zone {
  position: absolute;
  inset: 0;
  z-index: 9999;
  background: rgba(34, 197, 94, 0.12);
  border: 4px dashed #22c55e;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  pointer-events: none;
}
.drop-zone-content {
  text-align: center;
  color: #166534;
}
.drop-zone-title {
  font-size: 22px;
  font-weight: 700;
  margin: 12px 0 4px;
}
.drop-zone-sub {
  font-size: 13px;
  color: #15803d;
  opacity: 0.8;
}
</style>
