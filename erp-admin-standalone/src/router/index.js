import { createRouter, createWebHistory } from 'vue-router'

// 跨境ERP路由配置
// 核心页面使用直接导入（避免开发环境懒加载切换空白），非核心页面保留懒加载
import DashboardView from '@/views/DashboardView.vue'
import LoginView from '@/views/LoginView.vue'
import OneStopView from '@/views/goods/OneStopView.vue'
import OrderListView from '@/views/orders/ListView.vue'
import ShopIndexView from '@/views/shop/IndexView.vue'
import ReportsIndexView from '@/views/reports/IndexView.vue'
import InventoryIndexView from '@/views/inventory/IndexView.vue'
import LogisticsIndexView from '@/views/logistics/IndexView.vue'
import CreatorSearchView from '@/views/creator/CreatorSearch.vue'
import CreatorBoardView from '@/views/creator/CreatorBoard.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { title: '登录', hideLayout: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { title: '注册', hideLayout: true },
    },
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView,
      meta: { title: '控制台', icon: 'Odometer' },
    },
    {
      path: '/dashboard',
      redirect: '/',
    },
    // ==================== 商品模块 ====================
    {
      path: '/goods/collect',
      name: 'goods-collect',
      component: () => import('@/views/goods/CollectView.vue'),
      meta: { title: '商品采集', icon: 'ShoppingCart' },
    },
    {
      path: '/goods/manage',
      name: 'goods-manage',
      component: () => import('@/views/goods/ManageView.vue'),
      meta: { title: '商品管理', icon: 'Goods' },
    },
    {
      path: '/goods/listing',
      name: 'goods-listing',
      component: () => import('@/views/goods/ListingView.vue'),
      meta: { title: '商品上货', icon: 'Upload' },
    },
    {
      path: '/goods/hot',
      name: 'goods-hot',
      component: () => import('@/views/goods/HotProductsView.vue'),
      meta: { title: '爆品推荐', icon: 'Lightning' },
    },
    {
      path: '/goods/onestop',
      name: 'goods-onestop',
      component: OneStopView,
      meta: { title: '一站式采集上货', icon: 'MagicStick' },
    },
    {
      path: '/goods/decision',
      name: 'goods-decision',
      component: () => import('@/views/goods/DecisionView.vue'),
      meta: { title: '选品决策', icon: 'DataAnalysis' },
    },
    // ==================== 订单模块 ====================
    {
      path: '/orders',
      name: 'orders',
      component: OrderListView,
      meta: { title: '订单管理', icon: 'List' },
    },
    // ==================== 库存模块 ====================
    {
      path: '/inventory',
      name: 'inventory',
      component: InventoryIndexView,
      meta: { title: '库存管理', icon: 'Box' },
    },
    // ==================== 物流模块 ====================
    {
      path: '/logistics',
      name: 'logistics',
      component: LogisticsIndexView,
      meta: { title: '物流追踪', icon: 'Van' },
    },
    // ==================== 店铺模块 ====================
    {
      path: '/shop',
      name: 'shop',
      component: ShopIndexView,
      meta: { title: '店铺管理', icon: 'Shop' },
    },
    // ==================== 数据报表 ====================
    {
      path: '/reports',
      name: 'reports',
      component: ReportsIndexView,
      meta: { title: '数据报表', icon: 'DataLine' },
    },
    {
      path: '/settings/team',
      name: 'team',
      component: () => import('@/views/settings/TeamView.vue'),
      meta: { title: '团队管理', icon: 'User' },
    },
    // ==================== ERP 设置系统 ====================
    { path: '/settings/departments', name: 'settings-departments', component: () => import('@/views/settings/DepartmentManage.vue'), meta: { title: '部门管理', icon: 'OfficeBuilding' } },
    { path: '/settings/roles', name: 'settings-roles', component: () => import('@/views/settings/RoleManage.vue'), meta: { title: '角色管理', icon: 'Avatar' } },
    { path: '/settings/permissions', name: 'settings-permissions', component: () => import('@/views/settings/PermissionManage.vue'), meta: { title: '权限管理', icon: 'Lock' } },
    { path: '/settings/warehouse', name: 'settings-warehouse', component: () => import('@/views/settings/WarehouseSettings.vue'), meta: { title: '仓库配置', icon: 'Box' } },
    { path: '/settings/platform-auth', name: 'settings-platform-auth', component: () => import('@/views/settings/PlatformAuth.vue'), meta: { title: '平台授权', icon: 'Connection' } },
    { path: '/settings/assistant', name: 'settings-assistant', component: () => import('@/views/settings/AssistantTasks.vue'), meta: { title: '助手任务', icon: 'Cpu' } },
    { path: '/settings/system', name: 'settings-system', component: () => import('@/views/settings/SystemSettings.vue'), meta: { title: '系统设置', icon: 'Setting' } },
    { path: '/settings/audit-log', name: 'settings-audit-log', component: () => import('@/views/settings/AuditLog.vue'), meta: { title: '审计日志', icon: 'DocumentChecked' } },
    {
      path: '/services/official',
      name: 'official-services',
      component: () => import('@/views/services/OfficialServicesView.vue'),
      meta: { title: '官方服务', icon: 'Stamp' },
    },
    // ==================== 达人模块 ====================
    {
      path: '/creator/search',
      name: 'creator-search',
      component: CreatorSearchView,
      meta: { title: '达人检索', icon: 'User' },
    },
    {
      path: '/creator/board',
      name: 'creator-board',
      component: CreatorBoardView,
      meta: { title: '达人看板', icon: 'DataBoard' },
    },
    // ==================== ERP 财务系统 ====================
    { path: '/finance/payment-pool', name: 'finance-payment-pool', component: () => import('@/views/finance/PaymentPool.vue'), meta: { title: '请款池', icon: 'Money' } },
    { path: '/finance/payment-request', name: 'finance-payment-request', component: () => import('@/views/finance/PaymentRequest.vue'), meta: { title: '请款单', icon: 'Document' } },
    { path: '/finance/receipt-order', name: 'finance-receipt-order', component: () => import('@/views/finance/ReceiptOrder.vue'), meta: { title: '收款单', icon: 'Wallet' } },
    { path: '/finance/transaction-flow', name: 'finance-transaction-flow', component: () => import('@/views/finance/TransactionFlow.vue'), meta: { title: '往来流水', icon: 'List' } },
    { path: '/finance/order-profit', name: 'finance-order-profit', component: () => import('@/views/finance/OrderProfit.vue'), meta: { title: '订单利润', icon: 'TrendCharts' } },
    { path: '/finance/expense', name: 'finance-expense', component: () => import('@/views/finance/ExpenseOrder.vue'), meta: { title: '费用管理', icon: 'PriceTag' } },
    { path: '/finance/cost', name: 'finance-cost', component: () => import('@/views/finance/CostValuation.vue'), meta: { title: '成本计价', icon: 'Coin' } },
    // ==================== ERP 采购系统 ====================
    { path: '/purchase/supplier', name: 'purchase-supplier', component: () => import('@/views/purchase/SupplierList.vue'), meta: { title: '供应商管理', icon: 'User' } },
    { path: '/purchase/order', name: 'purchase-order', component: () => import('@/views/purchase/PurchaseOrder.vue'), meta: { title: '采购单', icon: 'Tickets' } },
    { path: '/purchase/return', name: 'purchase-return', component: () => import('@/views/purchase/ReturnOrder.vue'), meta: { title: '退货单', icon: 'Switch' } },
    // ==================== ERP 仓库管理 ====================
    { path: '/wms/inventory', name: 'wms-inventory', component: () => import('@/views/wms/InventoryList.vue'), meta: { title: '库存管理', icon: 'Box' } },
    { path: '/wms/receipt', name: 'wms-receipt', component: () => import('@/views/wms/ReceiptOrder.vue'), meta: { title: '收货单', icon: 'ShoppingBag' } },
    { path: '/wms/delivery', name: 'wms-delivery', component: () => import('@/views/wms/DeliveryOrder.vue'), meta: { title: '出库单', icon: 'Sell' } },
    // ==================== ERP 产品系统 ====================
    { path: '/product/list', name: 'product-list', component: () => import('@/views/product/ProductList.vue'), meta: { title: '产品管理', icon: 'Goods' } },
    // ==================== ERP 工具系统 ====================
    { path: '/tools/approval', name: 'tools-approval', component: () => import('@/views/tools/ApprovalWorkbench.vue'), meta: { title: '审批工作台', icon: 'Check' } },
    // ==================== ERP 物流系统 ====================
    { path: '/logistics-sys/provider', name: 'logistics-sys-provider', component: () => import('@/views/logistics/LogisticsProvider.vue'), meta: { title: '物流商管理', icon: 'Van' } },
    // ==================== ERP 销售系统 ====================
    { path: '/sales/listing', name: 'sales-listing', component: () => import('@/views/sales/ListingManage.vue'), meta: { title: 'Listing管理', icon: 'List' } },
    // 404 兜底路由：所有未匹配路径重定向到首页
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },

  ],
})

// 全局路由守卫：页面标题 + 登录拦截
router.beforeEach((to, from) => {
  // 更新页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 辽宁跨境宝盒`
  }
  
  // 登录页 & 注册页：若已登录则直接跳转工作台
  if (to.path === '/login' || to.path === '/register') {
    const token = localStorage.getItem('access_token')
    if (token) return '/'
    return true
  }
  
  // 其他页面：检查登录状态
  const token = localStorage.getItem('access_token')
  if (!token) {
    return '/login'
  }
  return true
})

export default router
