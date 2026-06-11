# 辽宁跨境宝盒 ERP — 前端开发任务书 v1.0

> **致张竞祺**：本文档基于后端接口审计结果生成，目标是把当前 `backend` 的真实能力、Demo 占位能力与缺失能力，转化为前端可落地的开发任务。  
> 生成时间：2026-05-01  
> 依据：后端接口清单 + 现有前端 API 调用点

---

## 一、前端项目现状判断

从后端接口状态看，前端当前需要面对三类接口：

- **✅ 已真实实现**：可以直接做完整业务闭环
- **⚠️ Demo 占位**：前端必须做兼容，但业务结果不能依赖真实数据
- **❌ 完全缺失**：前端要么补 UI 入口并提示不可用，要么联动后端补接口

### 前端开发总体结论

1. **当前前端不是“补页面”问题，而是“补完整业务链路”问题。**
2. **核心主流程已经具备基础接口**，包括：
   - 登录认证
   - 商品管理
   - 订单管理
   - 库存部分能力
   - 物流追踪
   - AI 能力
   - 达人管理
   - SKU 管理
   - 选品引擎
3. **真正阻断前端体验的，是若干关键接口缺失与 Demo 占位接口过多。**
4. **前端任务优先级应围绕“能形成闭环的功能”展开**，先保主链路，再补增强能力。

---

## 二、前端模块建设总清单

### 2.1 账号与认证中心

#### 对应后端
- `/api/auth/register`
- `/api/auth/login`
- `/api/auth/refresh`
- `/api/auth/me`
- `/api/auth/send-sms`
- `/api/auth/verify-sms`
- `/api/auth/mobile/login`
- `/api/auth/captcha/challenge`
- `/api/auth/{platform}/login/`
- `/api/auth/{platform}/callback/`
- `/api/auth/{platform}/refresh/`

#### 前端任务
1. **登录页**
   - 手机号/用户名密码登录
   - 短信验证码登录
   - 图形验证码/人机验证展示
   - OAuth 平台登录入口
2. **注册页**
   - 账号注册、短信验证、密码校验
3. **用户状态管理**
   - Token 持久化
   - 刷新 Token 自动续期
   - `/me` 拉取用户信息
   - 退出登录与过期重登
4. **多平台登录回调页**
   - 处理 `callback`
   - 授权成功/失败提示
   - 自动跳转回原业务页

#### 前端交付要求
- 登录流程必须支持失效重试
- Token 过期后自动刷新，不可强制用户手动刷新页面
- 所有受保护路由需做统一鉴权拦截

---

### 2.2 商品管理中心

#### 对应后端
- `/api/goods/`
- `/api/goods/{id}`
- `/api/v1/goods/listing/` ✅
- `/api/v1/goods/listing/batch/` ✅
- `/api/v1/goods/list` ⚠️
- `/api/v1/goods/detail/{id}/` ⚠️
- `/api/v1/products/` ⚠️

#### 前端任务
1. **商品列表页**
   - 支持分页、筛选、搜索、排序
   - 商品状态、库存、价格、平台标识展示
2. **商品详情页**
   - 展示基础信息、SKU、图片、描述、平台关联信息
3. **商品创建/编辑页**
   - 基本表单编辑
   - 图片上传
   - 描述/标题 AI 生成入口
4. **商品上货页**
   - 单商品上货
   - 批量上货
   - 上货任务状态展示
5. **选品商品兼容页**
   - 对接 `/api/v1/products/` 的兼容数据源
   - Demo 数据与真实数据统一渲染

#### Demo 接口处理策略
- 对 `/api/v1/goods/list`、`detail`、`listing` 系列接口：
  - 前端必须显式标注“演示数据 / 任务已下发”
  - 不允许默认展示为“已成功同步”
  - 对任务型接口必须展示任务 ID 和轮询状态

#### 前端重点
- 商品是 ERP 的核心主入口，必须优先做到：
  - 列表可用
  - 详情可用
  - 创建可用
  - 上货可追踪

---

### 2.3 商品采集中心

#### 对应后端
- `/api/v1/collect/1688/single/` ✅
- `/api/v1/collect/1688/batch/` ⚠️
- `/api/v1/collect/task/` ✅
- `/api/v1/collect/task/list/` ⚠️
- `/api/v1/collect/task/{id}/` ⚠️
- `/api/v1/collect/task/{id}/status/` ⚠️
- `/api/v1/collect/task/{id}/cancel/` ⚠️
- `/api/v1/collect/task/{id}/` DELETE ⚠️

#### 前端任务
1. **1688 单品采集页**
   - 输入商品链接
   - 采集参数配置
   - 采集结果预览
2. **1688 批量采集页**
   - 批量 URL 导入
   - 采集队列展示
   - 失败重试
3. **采集任务中心**
   - 创建任务
   - 任务列表
   - 任务详情
   - 状态轮询
   - 取消任务
   - 删除任务

#### 交互要求
- 采集任务必须支持异步状态展示
- 前端不能只提示“成功提交”，必须有“处理中 / 成功 / 失败 / 已取消”状态
- 任务详情要能看见原始请求与返回结果摘要

---

### 2.4 平台授权管理

#### 对应后端
- `/api/v1/collect/1688/auth/*` ⚠️
- `/api/v1/collect/tiktok/auth/*` ⚠️
- `/api/v1/collect/amazon/auth/*` ⚠️

#### 前端任务
1. **平台授权管理页**
   - 1688 / TikTok / Amazon 三平台统一入口
   - 发起授权
   - 回调处理
   - 授权状态查询
   - 解绑/退出授权
2. **授权状态卡片**
   - 未授权 / 已授权 / 过期 / 失败
3. **授权引导页**
   - 根据平台展示不同说明文案

#### Demo 风险
- 当前授权相关接口多为 Demo，占位逻辑较多
- 前端需做“可用但不承诺真实授权成功”的状态提示
- 不建议把授权成功直接视为“已可采集”

---

### 2.5 订单管理中心

#### 对应后端
- `/api/orders/`
- `/api/orders/status-counts/`
- `/api/orders/export`
- `/api/orders/{id}/`
- `/api/orders/{id}/address`
- `/api/orders/{id}/status`
- `/api/orders/{id}/confirm/`
- `/api/orders/{id}/ship/`
- `/api/orders/{id}/cancel/`
- `/api/orders/{id}/remark/` ❌
- `/api/v1/orders/*` ⚠️ Demo

#### 前端任务
1. **订单列表页**
   - 支持状态筛选、时间筛选、关键字搜索
   - 支持订单统计卡片
2. **订单详情页**
   - 收件信息
   - 商品明细
   - 物流信息
   - 操作记录
3. **订单状态操作**
   - 确认订单
   - 发货
   - 取消
   - 修改地址
   - 修改状态
4. **订单导出**
   - 导出当前筛选条件订单
5. **订单备注**
   - 前端入口先预留
   - 后端缺失前需显示“功能待开放”

#### 缺失接口影响
- `/api/orders/{id}/remark/` 缺失会影响客服场景
- 前端应先做：
  - 备注输入框
  - 禁用提交按钮或提示待开放
  - 以避免交互断层

---

### 2.6 库存管理中心

#### 对应后端
- `/api/inventory/alerts`
- `/api/inventory/logs`
- `/api/inventory/sync`
- `/api/inventory/overview` ❌
- `/api/inventory/adjust` ❌
- `/api/inventory/warehouses` ❌
- `/api/v1/inventory/*` ⚠️

#### 前端任务
1. **库存看板**
   - 总库存、预警数、缺货数、SKU 总量
   - 当前库存趋势
2. **库存预警页**
   - 低库存商品列表
   - 缺货商品列表
3. **库存日志页**
   - 同步记录
   - 调整记录
   - 变更来源
4. **库存同步按钮**
   - 手动触发同步
   - 显示同步进度
5. **库存调整页**
   - 单个 SKU 调整
   - 批量调整
6. **仓库管理页**
   - 仓库列表
   - 仓库状态

#### 缺失接口策略
- `overview / adjust / warehouses` 三个核心接口缺失
- 前端可以先补页面壳子，但不要把完整库存分析当成可交付功能
- 建议明显区分：
  - 已接通后端数据
  - 仅 UI 预留
  - 待后端补齐

---

### 2.7 物流管理中心

#### 对应后端
- `/api/logistics/shipments/`
- `/api/logistics/track/{waybill}`
- `/api/logistics/webhook`
- `/api/logistics/freight-estimate`
- `/api/logistics/carriers/` ❌
- `/api/logistics/sync/` ❌
- `/api/logistics/subscribe/` ❌

#### 前端任务
1. **物流发货列表**
   - 发货单列表
   - 快递公司
   - 运单号
   - 物流状态
2. **物流轨迹查询**
   - 运单号搜索
   - 轨迹节点时间线
3. **运费预估**
   - 发货前估价
   - 多渠道比价展示
4. **物流商管理**
   - 物流商列表
   - 物流商状态
5. **同步/订阅入口**
   - 预留同步按钮
   - 预留订阅轨迹按钮

#### 缺失接口影响
- 物流商列表、同步、订阅缺失会影响完整物流闭环
- 前端应在 UI 上显示“暂未开放”而不是静默失败

---

### 2.8 店铺管理

#### 对应后端
- `/api/shops/`
- `/api/shops/unbind/` ❌

#### 前端任务
1. **店铺列表页**
   - 店铺名称
   - 平台
   - 授权状态
   - 绑定时间
2. **店铺解绑操作**
   - 二次确认
   - 操作结果提示
3. **店铺授权状态展示**
   - 已绑定 / 失效 / 未绑定

#### 缺失接口影响
- 解绑缺失会导致前端只能展示绑定，无法完成生命周期管理
- 必须在 UI 里加“暂不支持解绑”的兜底

---

### 2.9 Dashboard 与报表中心

#### 对应后端
- `/api/dashboard/stats`
- `/api/dashboard/recent-orders`
- `/api/dashboard/sales-trend`
- `/api/dashboard/new-orders-since` ❌
- `/api/reports/summary/`

#### 前端任务
1. **首页总览 Dashboard**
   - 核心指标卡片
   - 近7日/30日趋势图
   - 最近订单
2. **报表中心**
   - 汇总指标
   - 分类统计
   - 平台分布
3. **实时订单轮询**
   - 前端轮询新订单数
   - 用于顶部通知或待处理提醒

#### 缺失接口影响
- 实时新订单轮询缺失会影响首页即时性
- 可先用定时刷新模拟，但要明确标注为“非实时”

---

### 2.10 AI 助手中心

#### 对应后端
- `/api/ai/generate-title/`
- `/api/ai/generate-description/`
- `/api/ai/generate-features/`
- `/api/ai/chat/`
- `/api/ai/image/generate/`
- `/api/ai/image/edit/`
- `/api/ai/translate/`
- `/api/ai/refine-description/`
- `/api/ai/proxy`

#### 前端任务
1. **AI 商品文案生成**
   - 标题生成
   - 描述生成
   - 卖点生成
   - 描述润色
2. **AI 多语言翻译**
   - 翻译结果预览
   - 支持一键替换
3. **AI 图片生成/编辑**
   - 输入提示词
   - 图片结果展示
   - 编辑后的对比预览
4. **AI Chat 助手**
   - 对话式商品/运营助手
   - 历史上下文保留
5. **AI 代理转发**
   - 统一接入外部 AI 服务

#### 前端重点
- AI 是提高效率的辅助模块，建议放在商品编辑、达人管理、内容分析页作为浮层能力
- 不建议做成独立割裂的“聊天机器人页”，应与业务页面深度联动

---

### 2.11 达人管理中心

#### 对应后端
- `/api/creators/search/`
- `/api/creators/`
- `/api/creators/{id}/`
- `/api/creators/import/platform/`
- `/api/creators/auth/tiktok/login/`
- `/api/creators/auth/tiktok/callback/`
- `/api/creators/{id}/sync-audience/`
- `/api/creators/{id}/sync-ecom/`
- `/api/ai/multilingual-pitch/`
- `/api/ai/content-analysis/jobs/`
- `/api/ai/review-mining/jobs/`
- `/api/ai/jobs/{job_id}/`
- `/api/invitations/{id}/send/`
- `/api/invitations/{id}/history/`
- `/api/dashboard/creator-board/`
- `/api/creator-ecom-profiles/`
- `/api/creator-ai-insights/`
- `/api/fulfillment-assets/`
- `/api/fulfillment-orders/`
- `/api/fulfillment-orders/{id}/dispatch/`
- `/api/fulfillment-orders/{id}/tracking/`
- `/api/fulfillment-assets/{id}/authorize/`
- `/api/assets/upload-url/`
- `/api/assets/callback/`

#### 前端任务
1. **达人列表页**
   - 搜索、筛选、分页
   - 达人基础信息与标签
2. **达人详情页**
   - 基本资料
   - 粉丝画像
   - 电商资料
   - AI 洞察
3. **达人导入页**
   - 平台导入
   - 批量导入结果展示
4. **TikTok 授权页**
   - 发起授权
   - 回调处理
5. **受众同步与电商同步操作**
   - 同步状态展示
   - 同步日志查看
6. **邀请管理**
   - 发送邀请
   - 邀请历史
7. **履约与资产管理**
   - 履约订单管理
   - 资产授权
   - 上传回调
8. **AI 分析任务中心**
   - 内容分析任务
   - 评论挖掘任务
   - 任务状态轮询

#### 前端优先级
- 这是一个“高业务密度”模块，建议拆成：
  - 达人列表
  - 达人详情
  - 授权导入
  - AI分析
  - 履约资产
  五个子域分别开发

---

### 2.12 SKU 管理中心

#### 对应后端
- `/api/sku/detail/{sku_code}/`
- `/api/sku/list/`
- `/api/sku/bulk-create/`
- `/api/sku/bulk-update/`
- `/api/sku/bulk-delete/`
- `/api/sku/search/`
- `/api/sku/export/`

#### 前端任务
1. **SKU 列表页**
   - 支持游标分页/搜索
   - SKU 状态与库存展示
2. **SKU 详情页**
   - 编码、属性、价格、库存、关联商品
3. **SKU 批量创建/更新/删除**
   - Excel/表格导入
   - 批量操作结果反馈
4. **SKU 导出**
   - 当前筛选条件导出
5. **SKU 搜索框**
   - 前缀搜索/模糊搜索

#### 前端重点
- SKU 模块要兼容“高频搜索 + 批量操作”
- 列表性能和交互反馈要优先于页面视觉复杂度

---

### 2.13 任务管理中心

#### 对应后端
- `/api/auth/register/`
- `/api/auth/login/`
- `/api/auth/refresh/`
- `/api/tasks/`
- `/api/tasks/{pk}/`

#### 前端任务
1. **登录注册页**
   - 该模块可能是独立任务系统入口
2. **任务列表页**
   - 列表、筛选、状态
3. **任务详情页**
   - 任务信息展示
   - 编辑/删除
4. **任务管理交互**
   - 新建任务
   - 修改任务
   - 删除任务

---

### 2.14 选品引擎中心

#### 对应后端
- `/api/selection/calculate/`
- `/api/v1/decision/calculate/` ⚠️
- `/api/selection/influencer-batch/`
- `/api/selection/batch/{batch_id}/progress/`
- `/api/selection/batch/{batch_id}/preview/`

#### 前端任务
1. **ROAS/选品计算页**
   - 输入参数
   - 展示计算结果
2. **达人批量计算页**
   - 批量导入
   - 批量结果表
3. **批次进度页**
   - 进度条
   - 状态轮询
4. **结果预览页**
   - 批次预览
   - 可导出

#### Demo 接口策略
- `v1/decision/calculate/` 为 Demo 占位
- 前端要同时兼容真实接口和 Demo 回退接口
- 在 UI 上明确标注结果来源，避免误导业务判断

---

### 2.15 系统运维中心

#### 对应后端
- `/api/health/`
- `/api/ops/dead-letter/`
- `/api/ops/dead-letter/{id}/replay/`
- `/api/ops/replay-audit/`
- `/api/ops/whoami/`
- `/api/ops/sms/channel-stats`
- `/api/user/account/`
- `/api/user/phone-rebind-appeals`

#### 前端任务
1. **系统健康页**
   - 后端健康状态
   - 基础连通性展示
2. **死信队列管理**
   - 死信列表
   - 重放操作
   - 重放审计
3. **当前用户/权限信息页**
   - whoami 展示
4. **短信通道监控页**
   - 发送统计
   - 通道状态
5. **账号管理页**
   - 注销账号
   - 绑定手机申诉

---

### 2.16 核心采集与同步任务

#### 对应后端
- `/api/tasks/collect/`
- `/api/tasks/{task_id}/status/`
- `/api/sync/trigger/`
- `/api/sync/log/`

#### 前端任务
1. **采集任务入口**
   - 一键发起
2. **任务状态页**
   - 轮询状态
   - 展示进度、结果、失败原因
3. **同步日志页**
   - 同步时间
   - 同步结果
   - 错误详情

---

## 三、前端必须补齐的缺失功能清单

| 缺失接口 | 前端建议 |
|---|---|
| `/api/v1/upload/image/` | 商品编辑页、AI 图片页增加上传入口；接口未接通前先禁用上传或走临时本地预览 |
| `/api/logistics/carriers/` | 物流商下拉框预留，提示“待开放” |
| `/api/logistics/sync/` | 物流管理页保留同步按钮，点击给出待开放说明 |
| `/api/logistics/subscribe/` | 轨迹订阅入口先做 UI，不做真实提交 |
| `/api/orders/{id}/remark/` | 订单详情页备注模块先做展示，不做提交 |
| `/api/inventory/overview` | 库存看板先做静态壳子，数据区分真实/占位 |
| `/api/inventory/adjust` | 库存调整操作先做按钮与表单，不做最终确认 |
| `/api/inventory/warehouses` | 仓库选择器先预留 |
| `/api/shops/unbind/` | 店铺卡片保留解绑按钮，后端未开通前禁用 |
| `/api/dashboard/new-orders-since` | 首页实时轮询先用定时刷新模拟 |

---

## 四、前端开发优先级路线图

### P0：必须先完成的核心闭环

1. **登录/认证中心**
2. **商品列表、详情、创建、编辑**
3. **商品上货与批量上货**
4. **1688 商品采集与任务中心**
5. **订单列表、详情、状态操作**
6. **Dashboard 总览**
7. **AI 文案生成与图片能力入口**
8. **SKU 列表与批量管理**

### P1：增强业务闭环

1. **库存看板与库存日志**
2. **物流追踪与运费估算**
3. **店铺管理**
4. **达人管理基础功能**
5. **选品引擎计算页**
6. **系统运维页**

### P2：体验完善与运维补强

1. **实时轮询优化**
2. **任务状态统一中心**
3. **错误重试机制**
4. **批量导入/导出体验优化**
5. **权限与菜单动态渲染**
6. **空状态、异常状态、骨架屏统一设计**

---

## 五、建议前端页面结构

```text
src/
├── layouts/
│   ├── MainLayout.vue
│   ├── AuthLayout.vue
│   └── EmptyLayout.vue
├── pages/
│   ├── auth/
│   ├── dashboard/
│   ├── goods/
│   ├── collect/
│   ├── orders/
│   ├── inventory/
│   ├── logistics/
│   ├── shops/
│   ├── ai/
│   ├── creators/
│   ├── sku/
│   ├── selection/
│   └── ops/
├── components/
│   ├── DataTable/
│   ├── StatusTag/
│   ├── EmptyState/
│   ├── FileUploader/
│   ├── TaskStatusPanel/
│   └── ConfirmActionDialog/
├── api/
│   ├── auth.js
│   ├── goods.js
│   ├── collect.js
│   ├── orders.js
│   ├── inventory.js
│   ├── logistics.js
│   ├── shops.js
│   ├── ai.js
│   ├── creators.js
│   ├── sku.js
│   ├── selection.js
│   └── ops.js
└── stores/
    ├── auth.js
    ├── user.js
    └── app.js
```

---

## 六、前端必须统一的工程规范

1. **统一 API 响应处理**
   - 成功/失败结构统一解析
   - 兼容 Demo 与真实接口返回差异

2. **统一请求拦截器**
   - 自动带 Token
   - Token 过期自动刷新
   - 401 统一跳登录页

3. **统一状态展示**
   - 任务类接口统一 `pending / running / success / failed / canceled`
   - Demo 接口统一加“演示”标识

4. **统一权限控制**
   - 菜单、按钮、路由三级控制
   - 没权限不可见或不可点

5. **统一空状态与错误状态**
   - 无数据
   - 加载中
   - 请求失败
   - 功能未开放

---

## 七、前端验收标准

### 7.1 功能验收
- 核心菜单可完整进入
- 主要页面都能正常加载数据
- 关键操作均有明确反馈
- 任务型功能支持轮询/刷新/失败提示

### 7.2 体验验收
- 页面不出现“点了没反应”
- Demo 接口不伪装成真实成功
- 缺失接口有明确提示
- 表单校验与错误提示完整

### 7.3 工程验收
- API 封装统一
- 路由守卫统一
- 权限控制统一
- 复用组件沉淀到位

---

## 八、最终建议

如果按业务价值排序，前端应优先做成以下四条主链路：

1. **商品管理链路**  
   商品列表 → 商品详情 → 编辑 → 上货 → 结果反馈

2. **采集链路**  
   1688 单采 → 批采 → 任务中心 → 状态轮询

3. **订单链路**  
   订单列表 → 详情 → 状态操作 → 发货/取消

4. **运营链路**  
   Dashboard → AI 助手 → 达人管理 → 选品引擎

这四条链路做好，前端就不是“能打开页面”，而是“能支撑日常运营”。
