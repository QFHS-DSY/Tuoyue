<template>
  <!-- 登录页：全屏展示 -->
  <RouterView v-if="route.meta.hideLayout" />

  <!-- 其他页面：带侧边栏布局 -->
  <el-container v-else class="layout-root">

    <!-- =============== 侧边栏 =============== -->
    <aside class="aside" :class="{ collapsed: isCollapse }">

      <!-- Logo -->
      <div class="logo-area">
        <img src="@/assets/logo.png" alt="辽宁跨境宝盒" class="logo-img" />
        <transition name="logo-fade">
          <span v-if="!isCollapse" class="logo-text">辽宁跨境宝盒</span>
        </transition>
      </div>

      <!-- 菜单（按经营链路: 准备→采集→运营→分析→管理） -->
      <nav class="nav-menu">

        <!-- ① 准备 -->
        <div class="nav-section-label" v-if="!isCollapse">准备</div>
        <div class="nav-item" :class="{ active: route.path === '/' }" @click="navigateTo('/')" :title="isCollapse ? '控制台' : ''">
          <el-icon><Odometer /></el-icon>
          <span v-if="!isCollapse">控制台</span>
        </div>
        <div class="nav-item" :class="{ active: route.path === '/shop' }" @click="navigateTo('/shop')" :title="isCollapse ? '店铺管理' : ''">
          <el-icon><Shop /></el-icon>
          <span v-if="!isCollapse">店铺管理</span>
        </div>

        <!-- ② 选品采集 -->
        <div class="nav-section-label" v-if="!isCollapse && appStore.isExpert">选品采集</div>
        <div class="nav-item nav-item--highlight" :class="{ active: route.path === '/goods/onestop' }" @click="navigateTo('/goods/onestop')" :title="isCollapse ? '一站式采集上货' : ''">
          <el-icon><MagicStick /></el-icon>
          <span v-if="!isCollapse">一站式上货</span>
          <span v-if="!isCollapse" class="nav-badge">核心</span>
        </div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/creator/search' }" @click="navigateTo('/creator/search')" :title="isCollapse ? '达人检索' : ''">
          <el-icon><UserFilled /></el-icon>
          <span v-if="!isCollapse">达人选品</span>
        </div>

        <!-- ③ 运营履约 -->
        <div class="nav-section-label" v-if="!isCollapse && appStore.isExpert">运营履约</div>
        <div class="nav-item" :class="{ active: route.path === '/orders' }" @click="navigateTo('/orders')" :title="isCollapse ? '订单管理' : ''">
          <el-icon><List /></el-icon>
          <span v-if="!isCollapse">订单管理</span>
        </div>
        <div class="nav-item nav-sub-item" :class="{ active: route.path === '/inventory' }" @click="navigateTo('/inventory')" :title="isCollapse ? '库存管理' : ''">
          <el-icon><Box /></el-icon>
          <span v-if="!isCollapse">库存管理</span>
        </div>
        <div class="nav-item nav-sub-item" :class="{ active: route.path === '/logistics' }" @click="navigateTo('/logistics')" :title="isCollapse ? '物流追踪' : ''">
          <el-icon><Van /></el-icon>
          <span v-if="!isCollapse">物流追踪</span>
        </div>

        <!-- ④ 数据分析 -->
        <div class="nav-section-label" v-if="!isCollapse && appStore.isExpert">数据分析</div>
        <div class="nav-item nav-sub-item" :class="{ active: route.path === '/reports' }" @click="navigateTo('/reports')" :title="isCollapse ? '数据报表' : ''">
          <el-icon><DataLine /></el-icon>
          <span v-if="!isCollapse">数据报表</span>
        </div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/creator/board' }" @click="navigateTo('/creator/board')" :title="isCollapse ? '达人看板' : ''">
          <el-icon><DataBoard /></el-icon>
          <span v-if="!isCollapse">达人看板</span>
        </div>

        <!-- ⑤ 管理与服务 -->
        <div class="nav-section-label" v-if="!isCollapse && appStore.isExpert">管理与服务</div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/settings/team' }" @click="navigateTo('/settings/team')" :title="isCollapse ? '团队管理' : ''">
          <el-icon><User /></el-icon>
          <span v-if="!isCollapse">团队管理</span>
        </div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/services/official' }" @click="navigateTo('/services/official')" :title="isCollapse ? '官方服务' : ''">
          <el-icon><Stamp /></el-icon>
          <span v-if="!isCollapse">官方服务</span>
        </div>

        <!-- ⑥ ERP 财务系统 -->
        <div class="nav-section-label" v-if="!isCollapse && appStore.isExpert">财务系统</div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/finance/payment-pool' }" @click="navigateTo('/finance/payment-pool')" :title="isCollapse ? '请款池' : ''">
          <el-icon><Money /></el-icon>
          <span v-if="!isCollapse">请款池</span>
        </div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/finance/payment-request' }" @click="navigateTo('/finance/payment-request')" :title="isCollapse ? '请款单' : ''">
          <el-icon><Document /></el-icon>
          <span v-if="!isCollapse">请款单</span>
        </div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/finance/transaction-flow' }" @click="navigateTo('/finance/transaction-flow')" :title="isCollapse ? '往来流水' : ''">
          <el-icon><List /></el-icon>
          <span v-if="!isCollapse">往来流水</span>
        </div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/finance/order-profit' }" @click="navigateTo('/finance/order-profit')" :title="isCollapse ? '订单利润' : ''">
          <el-icon><TrendCharts /></el-icon>
          <span v-if="!isCollapse">订单利润</span>
        </div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/finance/expense' }" @click="navigateTo('/finance/expense')" :title="isCollapse ? '费用管理' : ''">
          <el-icon><PriceTag /></el-icon>
          <span v-if="!isCollapse">费用管理</span>
        </div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/finance/cost' }" @click="navigateTo('/finance/cost')" :title="isCollapse ? '成本计价' : ''">
          <el-icon><Coin /></el-icon>
          <span v-if="!isCollapse">成本计价</span>
        </div>

        <!-- ⑦ ERP 采购/仓库 -->
        <div class="nav-section-label" v-if="!isCollapse && appStore.isExpert">采购 &amp; 仓库</div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/purchase/supplier' }" @click="navigateTo('/purchase/supplier')" :title="isCollapse ? '供应商' : ''">
          <el-icon><User /></el-icon>
          <span v-if="!isCollapse">供应商管理</span>
        </div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/purchase/order' }" @click="navigateTo('/purchase/order')" :title="isCollapse ? '采购单' : ''">
          <el-icon><Tickets /></el-icon>
          <span v-if="!isCollapse">采购单</span>
        </div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/wms/inventory' }" @click="navigateTo('/wms/inventory')" :title="isCollapse ? '库存' : ''">
          <el-icon><Box /></el-icon>
          <span v-if="!isCollapse">库存管理</span>
        </div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/wms/receipt' }" @click="navigateTo('/wms/receipt')" :title="isCollapse ? '收货' : ''">
          <el-icon><ShoppingBag /></el-icon>
          <span v-if="!isCollapse">收货单</span>
        </div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/wms/delivery' }" @click="navigateTo('/wms/delivery')" :title="isCollapse ? '出库' : ''">
          <el-icon><Sell /></el-icon>
          <span v-if="!isCollapse">出库单</span>
        </div>

        <!-- ⑧ ERP 产品/销售 -->
        <div class="nav-section-label" v-if="!isCollapse && appStore.isExpert">产品 &amp; 销售</div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/product/list' }" @click="navigateTo('/product/list')" :title="isCollapse ? '产品' : ''">
          <el-icon><Goods /></el-icon>
          <span v-if="!isCollapse">产品管理</span>
        </div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/sales/listing' }" @click="navigateTo('/sales/listing')" :title="isCollapse ? 'Listing' : ''">
          <el-icon><List /></el-icon>
          <span v-if="!isCollapse">Listing管理</span>
        </div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/logistics-sys/provider' }" @click="navigateTo('/logistics-sys/provider')" :title="isCollapse ? '物流商' : ''">
          <el-icon><Van /></el-icon>
          <span v-if="!isCollapse">物流商管理</span>
        </div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/tools/approval' }" @click="navigateTo('/tools/approval')" :title="isCollapse ? '审批' : ''">
          <el-icon><Check /></el-icon>
          <span v-if="!isCollapse">审批工作台</span>
        </div>

        <!-- ⑨ ERP 设置系统 -->
        <div class="nav-section-label" v-if="!isCollapse && appStore.isExpert">设置系统</div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/settings/departments' }" @click="navigateTo('/settings/departments')" :title="isCollapse ? '部门' : ''">
          <el-icon><OfficeBuilding /></el-icon>
          <span v-if="!isCollapse">部门管理</span>
        </div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/settings/roles' }" @click="navigateTo('/settings/roles')" :title="isCollapse ? '角色' : ''">
          <el-icon><Avatar /></el-icon>
          <span v-if="!isCollapse">角色管理</span>
        </div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/settings/permissions' }" @click="navigateTo('/settings/permissions')" :title="isCollapse ? '权限' : ''">
          <el-icon><Lock /></el-icon>
          <span v-if="!isCollapse">权限管理</span>
        </div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/settings/warehouse' }" @click="navigateTo('/settings/warehouse')" :title="isCollapse ? '仓库' : ''">
          <el-icon><Box /></el-icon>
          <span v-if="!isCollapse">仓库配置</span>
        </div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/settings/platform-auth' }" @click="navigateTo('/settings/platform-auth')" :title="isCollapse ? '授权' : ''">
          <el-icon><Connection /></el-icon>
          <span v-if="!isCollapse">平台授权</span>
        </div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/settings/assistant' }" @click="navigateTo('/settings/assistant')" :title="isCollapse ? '助手' : ''">
          <el-icon><Cpu /></el-icon>
          <span v-if="!isCollapse">助手任务</span>
        </div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/settings/system' }" @click="navigateTo('/settings/system')" :title="isCollapse ? '系统' : ''">
          <el-icon><Setting /></el-icon>
          <span v-if="!isCollapse">系统设置</span>
        </div>
        <div v-if="appStore.isExpert" class="nav-item nav-sub-item" :class="{ active: route.path === '/settings/audit-log' }" @click="navigateTo('/settings/audit-log')" :title="isCollapse ? '审计' : ''">
          <el-icon><DocumentChecked /></el-icon>
          <span v-if="!isCollapse">审计日志</span>
        </div>

      </nav>

      <button class="collapse-btn" @click="isCollapse = !isCollapse">
        <el-icon><ArrowLeft v-if="!isCollapse" /><ArrowRight v-else /></el-icon>
        <span v-if="!isCollapse">收起</span>
      </button>
    </aside>

    <div class="main-wrap">
      <header class="topbar">
        <div class="topbar-left">
          <nav class="breadcrumb" aria-label="breadcrumb">
            <span class="bc-home" @click="navigateTo('/')">首页</span>
            <template v-if="currentPageMeta.parent">
              <span class="bc-sep">/</span>
              <span class="bc-item">{{ currentPageMeta.parent }}</span>
            </template>
            <span class="bc-sep">/</span>
            <span class="bc-current">{{ currentPageMeta.title || '概览' }}</span>
          </nav>
        </div>
        <div class="topbar-right">
          <span class="env-chip" :class="envMode">{{ envTagText }}</span>
          <el-tooltip :content="`当前：${appStore.modeLabel}，点击切换`" placement="bottom">
            <div class="mode-switch" @click="toggleAppMode">
              <el-icon><component :is="appStore.isExpert ? 'UserFilled' : 'Star'" /></el-icon>
              <span>{{ appStore.modeLabel }}</span>
            </div>
          </el-tooltip>
          <el-dropdown trigger="click" @command="handleUserCommand">
            <div class="user-avatar">
              <el-icon><UserFilled /></el-icon>
              <span class="user-name">{{ userName }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon> 个人中心
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon> 退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      <main class="page-main">
        <RouterView :key="route.fullPath" />
      </main>
    </div>
  </el-container>

  <AiAssistant v-if="!route.meta.hideLayout" mascot-src="/images/tiger.png" />
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AiAssistant from '@/components/AiAssistant.vue'
import { setupGlobalScanner } from '@/composables/useScanner'
import { useAuthStore } from '@/stores/useAuthStore'
import { useAppStore } from '@/stores/useAppStore'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const appStore = useAppStore()
const isCollapse = ref(false)

function navigateTo(path) {
  router.push(path).catch(err => {
    console.error('[导航失败]', path, err)
    ElMessage.error(`页面「${path}」暂时无法打开`)
  })
}

const pageMetaMap = {
  '/': { title: '控制台', parent: '' },
  '/goods/onestop': { title: '一站式采集上货', parent: '' },
  '/shop': { title: '店铺管理', parent: '' },
  '/reports': { title: '数据报表', parent: '' },
  '/settings/team': { title: '团队管理', parent: '' },
  '/services/official': { title: '官方服务', parent: '' },
  '/orders': { title: '订单管理', parent: '' },
  '/inventory': { title: '库存管理', parent: '' },
  '/logistics': { title: '物流追踪', parent: '' },
  // ERP 财务
  '/finance/payment-pool': { title: '请款池', parent: '财务系统' },
  '/finance/payment-request': { title: '请款单', parent: '财务系统' },
  '/finance/receipt-order': { title: '收款单', parent: '财务系统' },
  '/finance/transaction-flow': { title: '往来流水', parent: '财务系统' },
  '/finance/order-profit': { title: '订单利润', parent: '财务系统' },
  '/finance/expense': { title: '费用管理', parent: '财务系统' },
  '/finance/cost': { title: '成本计价', parent: '财务系统' },
  // ERP 采购
  '/purchase/supplier': { title: '供应商管理', parent: '采购系统' },
  '/purchase/order': { title: '采购单', parent: '采购系统' },
  '/purchase/return': { title: '退货单', parent: '采购系统' },
  // ERP 仓库
  '/wms/inventory': { title: '库存管理', parent: '仓库管理' },
  '/wms/receipt': { title: '收货单', parent: '仓库管理' },
  '/wms/delivery': { title: '出库单', parent: '仓库管理' },
  // ERP 产品
  '/product/list': { title: '产品管理', parent: '产品系统' },
  // ERP 销售
  '/sales/listing': { title: 'Listing管理', parent: '销售系统' },
  // ERP 工具
  '/tools/approval': { title: '审批工作台', parent: '工具系统' },
  // ERP 物流
  '/logistics-sys/provider': { title: '物流商管理', parent: '物流系统' },
  // ERP 设置系统
  '/settings/departments': { title: '部门管理', parent: '设置系统' },
  '/settings/roles': { title: '角色管理', parent: '设置系统' },
  '/settings/permissions': { title: '权限管理', parent: '设置系统' },
  '/settings/warehouse': { title: '仓库配置', parent: '设置系统' },
  '/settings/platform-auth': { title: '平台授权', parent: '设置系统' },
  '/settings/assistant': { title: '助手任务', parent: '设置系统' },
  '/settings/system': { title: '系统设置', parent: '设置系统' },
  '/settings/audit-log': { title: '审计日志', parent: '设置系统' },
}
const currentPageMeta = computed(() => pageMetaMap[route.path] || { title: '', parent: '' })
const envMode = import.meta.env.MODE === 'production' ? 'prod' : 'dev'
const envTagText = import.meta.env.MODE === 'production' ? '生产环境' : '开发环境'
const userName = computed(() => {
  const phone = localStorage.getItem('user_phone') || ''
  return phone ? phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2') : '用户'
})
function toggleAppMode() { appStore.toggleMode() }

// 退出登录（JWT 无状态，清除本地 Token 即可）
function handleUserCommand(cmd) {
  if (cmd === 'logout') {
    localStorage.clear()
    router.push('/login')
  } else if (cmd === 'profile') {
    ElMessage.info('个人中心功能即将上线')
  }
}

onMounted(() => { setupGlobalScanner() })
</script>

<style scoped>
/* ============================================================
   全局布局样式 —— 侧边栏 + 顶栏 + 主内容
   ============================================================ */

.layout-root {
  height: 100vh;
  overflow: hidden;
}

/* ── 侧边栏 ── */
.aside {
  width: var(--aside-width, 220px);
  min-width: var(--aside-width, 220px);
  height: 100vh;
  background: var(--aside-bg, #fff);
  border-right: 1px solid var(--aside-border-r, #e5e7eb);
  display: flex;
  flex-direction: column;
  transition: width 0.22s var(--ease, ease), min-width 0.22s var(--ease, ease);
  overflow: hidden;
  position: relative;
  z-index: 100;
}
.aside.collapsed {
  width: var(--aside-width-sm, 60px);
  min-width: var(--aside-width-sm, 60px);
}

/* Logo */
.logo-area {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px 16px 14px;
  border-bottom: 1px solid var(--aside-border-r, #e5e7eb);
  min-height: 60px;
  flex-shrink: 0;
}
.logo-img {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  flex-shrink: 0;
  object-fit: contain;
}
.logo-text {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  white-space: nowrap;
  letter-spacing: -0.01em;
}
.logo-fade-enter-active,
.logo-fade-leave-active {
  transition: opacity 0.18s var(--ease, ease);
}
.logo-fade-enter-from,
.logo-fade-leave-to {
  opacity: 0;
}

/* 导航菜单 */
.nav-menu {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-section-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--aside-section, #9ca3af);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 14px 12px 6px;
  white-space: nowrap;
}

.nav-divider {
  height: 1px;
  background: var(--aside-border-r, #e5e7eb);
  margin: 6px 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 500;
  color: var(--aside-text, #374151);
  cursor: pointer;
  transition: all 0.16s var(--ease, ease);
  white-space: nowrap;
  user-select: none;
}
.nav-item:hover {
  background: var(--aside-hover, #e8f4fc);
  color: var(--brand);
}
.nav-item.active {
  background: var(--aside-active-bg, #e8f4fc);
  color: var(--aside-active-text, #085B9C);
  font-weight: 600;
}
.nav-item .el-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.nav-item--highlight {
  color: var(--brand);
  font-weight: 600;
}
.nav-item--highlight .el-icon {
  color: var(--brand);
}

.nav-badge {
  margin-left: auto;
  font-size: 10px;
  font-weight: 700;
  background: var(--brand);
  color: #fff;
  padding: 1px 6px;
  border-radius: 10px;
  letter-spacing: 0.5px;
}

.nav-sub-item {
  padding: 8px 12px;
  font-size: 13px;
}

/* 折叠按钮 */
.collapse-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 10px 0;
  border: none;
  border-top: 1px solid var(--aside-border-r, #e5e7eb);
  background: transparent;
  color: var(--aside-text-dim, #9ca3af);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.16s var(--ease, ease);
  flex-shrink: 0;
}
.collapse-btn:hover {
  color: var(--brand);
  background: var(--aside-hover, #e8f4fc);
}
.collapse-btn .el-icon {
  font-size: 16px;
}

/* ── 右侧主区域 ── */
.main-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  min-width: 0;
}

/* ── 顶栏 ── */
.topbar {
  height: var(--header-h, 56px);
  min-height: var(--header-h, 56px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: var(--bg-card, #fff);
  border-bottom: 1px solid var(--border, #e5e7eb);
  z-index: 50;
  flex-shrink: 0;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary, #6b7280);
}

.bc-home {
  cursor: pointer;
  color: var(--brand);
  font-weight: 500;
}
.bc-home:hover {
  text-decoration: underline;
}

.bc-sep {
  color: var(--text-muted, #9ca3af);
}

.bc-current {
  color: var(--text-primary, #111827);
  font-weight: 600;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 8px;
  transition: background .2s;
  color: #606266;
}
.user-avatar:hover { background: #f5f7fa; }
.user-name { font-size: 13px; max-width: 120px; overflow: hidden; text-overflow: ellipsis; }

.env-chip {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
}
.env-chip.dev {
  background: var(--brand-light);
  color: var(--brand);
}
.env-chip.prod {
  background: #fef2f2;
  color: #dc2626;
}

.mode-switch {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 6px;
  transition: all 0.16s ease;
  border: 1px solid var(--border);
}
.mode-switch:hover {
  color: var(--brand);
  border-color: var(--brand);
  background: var(--brand-light);
}

/* ── 页面主内容 ── */
.page-main {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  background: var(--bg-page, #f5f6fa);
  min-height: 0;
}
</style>
