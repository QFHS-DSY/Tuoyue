/**
 * API 统一导出
 * 所有接口模块统一从这里导出
 */

// 商品采集 + 平台授权 + 采集任务 + 库存同步
export * from './collect'

// 商品管理
export * from './goods'

// SKU 管理
export * from './sku'

// 用户认证（注册/登录/Token刷新）
export * from './auth'

// 通用任务管理
export * from './task'

// 运维接口（死信队列/审计/权限/健康检查）+ 系统接口
export * from './ops'

// 拓岳AI（标题生成/描述生成/翻译）
export * from './ai'

// 订单管理
export * from './order'

// 库存管理
export * from './inventory'

// 物流追踪
export * from './logistics'

// 店铺管理
export * from './shop'
