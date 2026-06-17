/**
 * 拓岳 ERP 前端核心类型定义
 * TypeScript 强类型声明 — 评审报告红线整改
 */

// ==================== 通用 API 响应 ====================
export interface ApiResponse<T = unknown> {
  code: number
  data: T
  message?: string
  detail?: string
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// ==================== 用户 & 认证 ====================
export interface UserInfo {
  id: number
  username: string
  email: string
  phone?: string
  role: string
  is_superuser: boolean
  avatar?: string
}

export interface TokenPair {
  access_token: string
  refresh_token: string
}

export interface LoginParams {
  phone?: string
  password?: string
  sms_code?: string
}

// ==================== 平台授权（Shein 等）====================
export type PlatformCode = 'shein' | '1688' | 'tiktok' | 'amazon' | 'shopee' | 'temu' | 'lazada'

export type AuthStatus = 'unauthorized' | 'authorizing' | 'active' | 'expiring' | 'expired'

export interface PlatformAuthRecord {
  id: number
  platform: PlatformCode
  platform_name: string
  account_name: string
  account_id: string
  access_token: string
  refresh_token: string
  auth_status: AuthStatus
  token_expires_at: string
}

export interface PlatformConfig {
  id: number
  platform: PlatformCode
  platform_name: string
  description?: string
  is_active: boolean
}

// ==================== Shein 刊登 ====================
export interface SheinShop {
  id: number
  name: string
  expires_at?: string
}

export interface SkuVariant {
  sku_code: string
  properties: Record<string, string>
  price: number
  stock: number
}

export interface SheinListingForm {
  shop_id: number
  category_id: string
  spu_id: string
  price: number
  sku_list: SkuVariant[]
}

// ==================== 1688 商品采集 ====================
export interface PriceTier {
  min_qty: number
  max_qty?: number
  price: number
}

export interface Spec1688 {
  name: string  // 如 "颜色", "尺码"
  values: string[]
}

export interface Sku1688 {
  sku_code?: string
  properties: Record<string, string>  // { "颜色": "黑色", "尺码": "XL" }
  price: number
  stock: number
  price_tiers: PriceTier[]
}

export interface Product1688 {
  offer_id: string
  title: string
  price: number
  price_range?: string
  main_image: string
  images?: string[]
  supplier: string
  specs: Spec1688[]
  skus: Sku1688[]
  description?: string
}

/** 1688 规格映射 - 多级表头所需 */
export interface SpecMapping {
  source_spec: string       // 1688原始规格名 (e.g. "颜色")
  source_value: string      // 1688原始规格值 (e.g. "黑色")
  target_spec: string       // 目标平台规格名 (e.g. "Color")
  target_value: string      // 目标平台规格值 (e.g. "Black")
}

// ==================== 选品决策 ====================
export interface DecisionProduct {
  id: number
  sku: string
  name: string
  cost_price: number
  freight: number
  commission_rate: number
}

export interface DecisionParams {
  promotion_cost: number
  expected_gmv: number
}

export interface DecisionResult {
  roas: number
  decision_type: 'danger' | 'success' | 'warning'
  decision_text: string
  estimated_revenue: number
  total_investment: number
  fixed_cost: number
  variable_cost: number
  promotion_cost: number
}

// ==================== 入驻引导 ====================
export interface OnboardingSettings {
  category: string
  markets: string[]
  pricingType: string
  warehouse: string
  logisticsPref: string
}

export interface EnterpriseQualification {
  business_license: string    // 营业执照图片URL/Base64
  legal_person_name: string
  legal_person_id: string     // 法人身份证号
  company_name: string
  credit_code: string         // 统一社会信用代码
  contact_phone: string
  contact_email: string
}

// ==================== WebSocket 任务进度 ====================
export type TaskStatus = 'pending' | 'running' | 'success' | 'failed' | 'cancelled'

export interface TaskProgress {
  task_id: string
  status: TaskStatus
  progress: number          // 0-100
  message: string
  detail?: string
  created_at: string
  updated_at: string
}

export interface TaskQueueItem {
  task_id: string
  title: string
  status: TaskStatus
  progress: number
  message: string
}

// ==================== 商品通用 ====================
export interface GoodsItem {
  id: number
  sku: string
  name: string
  cost_price: number
  freight: number
  platform?: string
  shop_name?: string
  status?: string
  images?: string[]
  created_at?: string
  updated_at?: string
}

// ==================== 采集注入相关 ====================
export interface CollectInjection {
  url: string
  source_platform: PlatformCode
  auto_create_po?: boolean
}

export interface CollectTask {
  task_id: string
  status: TaskStatus
  product?: Product1688
  purchase_order_id?: string
  error?: string
}

// ==================== 双模式 ====================
export type UserMode = 'beginner' | 'expert'

// ==================== DEMO_MODE ====================
export interface DemoModeConfig {
  enabled: boolean
  features: Record<string, boolean>
}
